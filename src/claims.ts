/** Typed claims ledger over `algal.evaluation-evidence.v1` records.
 *
 * A claim is data: a bounded statement, the category of support it asks for,
 * and citations to evaluation-evidence records. The ledger never asks the
 * claimant whether the evidence suffices — `buildClaim` resolves every cited
 * record, grades its sufficiency, and derives `outcome` and `granted`
 * deterministically. `verifyClaimsLedger` re-derives the same fields from the
 * same records, so a ledger that overstates its evidence cannot pass.
 *
 * "insufficient-evidence" is a first-class retained result, like the extremal
 * lane's `control: not-run`: a claim with no resolvable support, with support
 * that never completed a held-out case, with only uncertain outcomes, or whose
 * evidence cannot carry the asked category stays in the ledger under that
 * outcome. Such a claim is never promotable: `promotableTo` is false at every
 * category unless the claim's own sufficient evidence supports the level.
 *
 * Promotion-strength order used for `asked`/`granted`:
 *   replay < qualified-boundary < effectiveness < mechanism < activation
 * replay attests internal consistency only; qualified-boundary adds a bounded,
 * tested scope; effectiveness a measured benefit inside that scope; mechanism
 * a supported explanation of why; activation the operational claim that needs
 * the most support. A claim granted at a lower category than it asked keeps
 * outcome "insufficient-evidence" — the gap between asked and granted is the
 * retained result.
 */
import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { canonicalize, parseEvaluationEvidence, type Digest, type EvaluationEvidence } from "@hraness/algal";
import { ArtifactStore, digest, digestString, readJsonFile } from "./artifacts";
import { equal, json, object, text } from "./contracts";

export const CLAIM_CONTRACT = "algal.lab.claim.v1";
export const CLAIMS_LEDGER_CONTRACT = "algal.lab.claims-ledger.v1";
export const CLAIM_BOUNDS = Object.freeze({ claims: 128, citations: 32, statementBytes: 2048 });

/** Same member set as `EvaluationEvidence["claimCategory"]`, ordered here by
 * the support a claim needs, not alphabetically. */
export const CLAIM_CATEGORIES = ["replay", "qualified-boundary", "effectiveness", "mechanism", "activation"] as const;
export type ClaimCategory = typeof CLAIM_CATEGORIES[number];
const rank = (category: ClaimCategory): number => CLAIM_CATEGORIES.indexOf(category);

export type ClaimCitation = { evidence: Digest; role: "support" | "contradict" };
export type ClaimOutcome = "supported" | "contradicted" | "insufficient-evidence";
export type Claim = {
  contract: typeof CLAIM_CONTRACT;
  id: string;
  statement: string;
  asked: ClaimCategory;
  citations: ClaimCitation[];
  outcome: ClaimOutcome;
  granted: ClaimCategory | null;
  digest: Digest;
};
export type ClaimsLedger = { contract: typeof CLAIMS_LEDGER_CONTRACT; claims: Claim[]; digest: Digest };
export type ClaimDraft = { id: string; statement: string; asked: ClaimCategory; citations: ClaimCitation[] };

/** Resolves a cited evidence reference — the content-addressed store digest of
 * a stored `algal.evaluation-evidence.v1` record, which itself carries the
 * record's signed digest — to a parsed record, or null when the citation
 * cannot be read or does not satisfy the shared contract. Unresolvable
 * citations are retained in the claim but can hold up nothing. */
export type EvidenceResolver = (reference: Digest) => Promise<EvaluationEvidence | null>;

export function storeEvidenceResolver(store: ArtifactStore): EvidenceResolver {
  return async (reference) => {
    try { return parseEvaluationEvidence(await store.get(reference)); }
    catch { return null; }
  };
}
export function recordsEvidenceResolver(records: Iterable<EvaluationEvidence>): EvidenceResolver {
  // Key by the same content address `ArtifactStore` would assign, so a claim
  // resolves identically whether its citations are read from a store or a list.
  const byDigest = new Map<Digest, EvaluationEvidence>();
  for (const record of records) byDigest.set(digest(record), record);
  return async (reference) => byDigest.get(reference) ?? null;
}

/** Grade one record's evidentiary sufficiency. A record where nothing
 * completed is insufficient; a record with any uncertain case is uncertain,
 * since that run's outcome is genuinely unknown; a measured record without a
 * completed held-out case is insufficient, because the study's frozen-portfolio
 * evaluation is the result a claim can stand on. Failed cases are measured
 * negatives, not uncertainty, so they do not downgrade. */
export type EvidenceSufficiency = "insufficient" | "uncertain" | "sufficient";
export function evidenceSufficiency(record: EvaluationEvidence): EvidenceSufficiency {
  const cases = [...record.outcomes.train.cases, ...record.outcomes.validation.cases, ...record.outcomes.holdout.cases];
  if (cases.length === 0 || !cases.some((item) => item.outcome === "complete")) return "insufficient";
  if (cases.some((item) => item.outcome === "uncertain")) return "uncertain";
  if (!record.outcomes.holdout.cases.some((item) => item.outcome === "complete")) return "insufficient";
  return "sufficient";
}

export function claimCategory(value: unknown, label: string): ClaimCategory {
  if (typeof value !== "string" || !(CLAIM_CATEGORIES as readonly string[]).includes(value)) throw new Error(`${label}: unknown claim category`);
  return value as ClaimCategory;
}

function admitCitations(value: unknown): ClaimCitation[] {
  if (!Array.isArray(value) || value.length > CLAIM_BOUNDS.citations) throw new Error(`claim citations: expected at most ${CLAIM_BOUNDS.citations}`);
  const citations = value.map((entry, index): ClaimCitation => {
    const citation = object(entry, ["evidence", "role"], `claim citations[${index}]`);
    if (citation.role !== "support" && citation.role !== "contradict") throw new Error(`claim citations[${index}].role: support or contradict`);
    return { evidence: digestString(citation.evidence), role: citation.role };
  });
  // One record, one role: a citation cannot count for and against at once, and
  // the list must be sorted so the same claim always serializes identically.
  if (citations.some((citation, index) => index > 0 && citation.evidence <= citations[index - 1]!.evidence)) {
    throw new Error("claim citations: evidence digests must be sorted and unique");
  }
  return citations;
}

export function admitClaimDraft(value: unknown): ClaimDraft {
  const raw = object(value, ["id", "statement", "asked", "citations"], "claim draft");
  const id = text(raw.id, 64, "claim id");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(id)) throw new Error("claim id: use lowercase letters, digits, and hyphens");
  return { id, statement: text(raw.statement, CLAIM_BOUNDS.statementBytes, "claim statement"), asked: claimCategory(raw.asked, "claim asked"), citations: admitCitations(raw.citations) };
}

/** Derive a claim's outcome from the records its citations resolve to.
 * Contradiction wins first: one sufficient record cited against defeats the
 * claim at any asked category. Otherwise at least one sufficient supporting
 * record must reach the asked category; anything less is insufficient. */
export async function assessClaim(draft: ClaimDraft, resolve: EvidenceResolver): Promise<{ outcome: ClaimOutcome; granted: ClaimCategory | null }> {
  const cited = new Map<Digest, EvaluationEvidence | null>();
  for (const citation of draft.citations) if (!cited.has(citation.evidence)) cited.set(citation.evidence, await resolve(citation.evidence));
  const resolved = (role: ClaimCitation["role"]) => draft.citations.filter((c) => c.role === role).map((c) => cited.get(c.evidence) ?? null);
  if (resolved("contradict").some((record) => record !== null && evidenceSufficiency(record) === "sufficient")) {
    return { outcome: "contradicted", granted: null };
  }
  const sufficient = resolved("support").filter((record): record is EvaluationEvidence => record !== null && evidenceSufficiency(record) === "sufficient");
  if (sufficient.length === 0) return { outcome: "insufficient-evidence", granted: null };
  const ceiling = Math.max(...sufficient.map((record) => rank(record.claimCategory)));
  const granted = CLAIM_CATEGORIES[Math.min(rank(draft.asked), ceiling)]!;
  return granted === draft.asked ? { outcome: "supported", granted } : { outcome: "insufficient-evidence", granted };
}

export async function buildClaim(draft: unknown, resolve: EvidenceResolver): Promise<Claim> {
  const admitted = admitClaimDraft(draft);
  const { outcome, granted } = await assessClaim(admitted, resolve);
  const body: Omit<Claim, "digest"> = { contract: CLAIM_CONTRACT, ...admitted, outcome, granted };
  return { ...body, digest: digest(body) };
}

/** The promotion gate: only a supported claim promotes, and never beyond the
 * category its own evidence granted. Claims retained as insufficient-evidence
 * or contradicted return false at every category. */
export function promotableTo(claim: Claim, category: ClaimCategory): boolean {
  return claim.outcome === "supported" && claim.granted !== null && rank(category) <= rank(claim.granted);
}

export function parseClaim(value: unknown): Claim {
  const raw = object(value, ["contract", "id", "statement", "asked", "citations", "outcome", "granted", "digest"], "claim");
  if (raw.contract !== CLAIM_CONTRACT) throw new Error("claim: unsupported contract");
  const draft = admitClaimDraft({ id: raw.id, statement: raw.statement, asked: raw.asked, citations: raw.citations });
  if (raw.outcome !== "supported" && raw.outcome !== "contradicted" && raw.outcome !== "insufficient-evidence") throw new Error("claim: unknown outcome");
  const granted = raw.granted === null ? null : claimCategory(raw.granted, "claim granted");
  if (raw.outcome === "supported" && granted !== draft.asked) throw new Error("claim: a supported outcome must grant the asked category");
  if (raw.outcome === "contradicted" && granted !== null) throw new Error("claim: a contradicted outcome grants nothing");
  if (raw.outcome === "insufficient-evidence" && granted === draft.asked) throw new Error("claim: fully granted evidence is not insufficient");
  if (granted !== null && rank(granted) > rank(draft.asked)) throw new Error("claim: granted exceeds asked");
  const body: Omit<Claim, "digest"> = { contract: CLAIM_CONTRACT, ...draft, outcome: raw.outcome, granted };
  if (digest(body) !== digestString(raw.digest)) throw new Error("claim: digest mismatch");
  return { ...body, digest: digestString(raw.digest) };
}

export function buildClaimsLedger(claims: Claim[]): ClaimsLedger {
  if (claims.length > CLAIM_BOUNDS.claims) throw new Error(`claims ledger: at most ${CLAIM_BOUNDS.claims} claims`);
  const sorted = [...claims].sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  if (sorted.some((claim, index) => index > 0 && claim.id === sorted[index - 1]!.id)) throw new Error("claims ledger: repeated claim id");
  const body: Omit<ClaimsLedger, "digest"> = { contract: CLAIMS_LEDGER_CONTRACT, claims: sorted };
  return { ...body, digest: digest(body) };
}

export function parseClaimsLedger(value: unknown): ClaimsLedger {
  const raw = object(value, ["contract", "claims", "digest"], "claims ledger");
  if (raw.contract !== CLAIMS_LEDGER_CONTRACT) throw new Error("claims ledger: unsupported contract");
  if (!Array.isArray(raw.claims) || raw.claims.length > CLAIM_BOUNDS.claims) throw new Error(`claims ledger: at most ${CLAIM_BOUNDS.claims} claims`);
  const claims = raw.claims.map(parseClaim);
  if (claims.some((claim, index) => index > 0 && claim.id <= claims[index - 1]!.id)) throw new Error("claims ledger: claims must be sorted by unique id");
  const body: Omit<ClaimsLedger, "digest"> = { contract: CLAIMS_LEDGER_CONTRACT, claims };
  if (digest(body) !== digestString(raw.digest)) throw new Error("claims ledger: digest mismatch");
  return { ...body, digest: digestString(raw.digest) };
}

/** Re-derive every claim's outcome and granted category from the cited records.
 * A ledger whose recorded outcomes no longer match its evidence fails closed. */
export async function verifyClaimsLedger(value: unknown, resolve: EvidenceResolver): Promise<{ ok: true; claims: number; insufficient: number; contradicted: number }> {
  const ledger = parseClaimsLedger(value);
  let insufficient = 0, contradicted = 0;
  for (const claim of ledger.claims) {
    const rebuilt = await buildClaim({ id: claim.id, statement: claim.statement, asked: claim.asked, citations: claim.citations }, resolve);
    if (!equal(rebuilt, claim)) throw new Error(`claim ${claim.id}: recorded outcome differs from the cited evidence`);
    if (claim.outcome === "insufficient-evidence") insufficient++;
    if (claim.outcome === "contradicted") contradicted++;
  }
  return { ok: true, claims: ledger.claims.length, insufficient, contradicted };
}

/** Read `{ drafts: [claim drafts] }`, assess each against the evidence records
 * in one run directory's artifact store, and write claims.json once. Drafts
 * name asked categories and citations only; outcomes are always derived. */
export async function writeStudyClaims(directory: string, draftsFile: string): Promise<ClaimsLedger> {
  const raw = object(await readJsonFile(draftsFile), ["drafts"], "claims drafts");
  if (!Array.isArray(raw.drafts) || raw.drafts.length > CLAIM_BOUNDS.claims) throw new Error(`claims drafts: at most ${CLAIM_BOUNDS.claims}`);
  const resolve = storeEvidenceResolver(new ArtifactStore(directory));
  const claims: Claim[] = [];
  for (const draft of raw.drafts) claims.push(await buildClaim(draft, resolve));
  const ledger = buildClaimsLedger(claims);
  await writeFile(join(directory, "claims.json"), canonicalize(json({ ledger, digest: ledger.digest })) + "\n", { flag: "wx", mode: 0o600 });
  return ledger;
}

/** Check a run directory's claims.json: the envelope digest binds the ledger
 * and every claim's recorded outcome re-derives from the archived evidence. */
export async function verifyStudyClaims(directory: string): Promise<{ ok: true; claims: number; insufficient: number; contradicted: number; claimsDigest: Digest }> {
  const file = object(await readJsonFile(join(directory, "claims.json")), ["ledger", "digest"], "claims file");
  const ledger = parseClaimsLedger(file.ledger);
  if (ledger.digest !== digestString(file.digest)) throw new Error("claims digest mismatch");
  const result = await verifyClaimsLedger(ledger, storeEvidenceResolver(new ArtifactStore(directory)));
  return { ...result, claimsDigest: ledger.digest };
}
