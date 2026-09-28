/** Evaluation-evidence projection.
 *
 * Wraps a completed study archive in the shared `algal.evaluation-evidence.v1`
 * envelope from the pinned runtime. Construction is a read-only projection over
 * retained attempts and frozen-portfolio evaluations: it runs after the study
 * has finished, reads the content-addressed archive, and never feeds holdout
 * outcomes back into any researcher context or selection step.
 *
 * Split mapping, by what actually informed selection in `runStudy`:
 *   train      — primed and discovery-phase attempts, each measured on the
 *                protocol's discovery schedules; these scores froze the
 *                portfolio and chose the champion.
 *   validation — held-out-budget transfer proposals measured on the same
 *                discovery schedules. v1 protocols have no such phase, so the
 *                split is empty and a limitation says so.
 *   holdout    — per-design evaluations of the frozen portfolios on the
 *                protocol's holdout schedules, all computed after freezing.
 *
 * The record is data-only. Its `claimCategory` is "replay" for every backend:
 * the envelope attests that these receipts and measurements exist and replay
 * bit-for-bit, and nothing more. Stronger categories require independent
 * review and evidence this projection does not produce.
 */
import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import {
  buildEvaluationEvidence, canonicalize, HOST_CONTRACT_BOUNDS, parseEvaluationEvidence, parseRunReceipt, receiptDigest,
  type Digest, type EvaluationEvidence, type EvaluationOutcome, type EvaluationOutcomeCase, type RunReceipt,
} from "@hraness/algal";
import { ArtifactStore, digest, digestString, readJsonFile, readRuntimeSources, runtimeDigest, sourceIdentities } from "./artifacts";
import {
  ALGAL_REVISION, CONDITIONS, equal, instrumentOf, integer, json, MAX_REPLICATES, MAX_TRANSFER_REGIMES, object, parseProtocol,
  protocolSettings, type Condition, type Phase, type Protocol,
} from "./contracts";
import { mean, researchManifest, researchManifestV2 } from "./researcher";

export const STUDY_EVIDENCE_CONTRACT = "algal.lab.study-evidence.v1";

/** A study-evidence envelope: the content-addressed store references of every
 * `algal.evaluation-evidence.v1` record projected from one study archive. Each
 * reference is the digest of the complete stored record, which itself carries
 * the record's own signed digest, so one address binds both. */
export type StudyEvidence = {
  contract: typeof STUDY_EVIDENCE_CONTRACT;
  reportDigest: Digest;
  backend: "scripted" | "random" | "command";
  instrumentDigest: Digest;
  applicationDigest: Digest;
  records: Digest[];
  digest: Digest;
};

/** The report fields the projection reads. `runStudy`'s report and the
 * admitted archive view both satisfy it; unknown fields are rejected on
 * admission so the projection cannot silently depend on drifted data. */
export type EvidenceStudyView = {
  backend: "scripted" | "random" | "command";
  protocol: Protocol;
  instrumentDigest: Digest;
  applicationDigest: Digest;
  attempts: Digest[];
  summaries: {
    replicate: number; condition: Condition; portfolioDigest: Digest; evaluation: Digest;
    transfers: { portfolioDigest: Digest; evaluation: Digest }[];
  }[];
};

const REPORT_KEYS = ["contract", "algalRevision", "backend", "protocol", "instrumentDigest", "applicationDigest", "researcherManifest", "conditionOrders", "attempts", "summaries"];
const SUMMARY_KEYS = ["replicate", "condition", "attempts", "primedDesigns", "validExperiments", "uniqueDesigns", "predictionMae", "meanHoldoutAuc", "bestHoldoutAuc", "coverageAt075", "selectedAttempt", "selectedScore", "selectedRandomAuc", "selectedTargetedAuc", "portfolioDigest", "evaluation", "transfers"];
const TRANSFER_KEYS = ["regime", "attempts", "validExperiments", "uniqueDesigns", "predictionMae", "selectedAttempt", "selectedScore", "selectedRandomAuc", "selectedTargetedAuc", "portfolioDigest", "evaluation"];
const ATTEMPT_KEYS = ["contract", "context", "instrumentDigest", "receipt", "measurement"];
const CONTEXT_KEYS: Record<string, string[]> = {
  "algal.lab.context.v1": ["contract", "replicate", "condition", "round", "researcher", "nodes", "edges", "failureSteps", "discoverySeeds", "evidence", "messages"],
  "algal.lab.context.v2": ["contract", "replicate", "condition", "round", "researcher", "nodes", "edges", "failureSteps", "discoverySeeds", "evidence", "messages", "phase"],
  "algal.lab.context.v3": ["contract", "replicate", "condition", "round", "researcher", "nodes", "edges", "failureSteps", "discoverySeeds", "evidence", "messages", "phase", "environment"],
};
const PHASES = ["primed", "discovery", "transfer"] as const;

/** Admission bounds derived from the protocol contract. A legal report carries
 * one summary per replicate/condition cell (at most MAX_REPLICATES seeds times
 * CONDITIONS.length conditions = 8 x 3 = 24 summaries), and each summary names
 * one primary portfolio plus at most MAX_TRANSFER_REGIMES transfer portfolios.
 * The maximal legal projection therefore lists at most 24 x (1 + 2) = 72
 * distinct portfolio digests — a protocol such as `replicateSeeds: 8,
 * researchers: 2, rounds: 4` with two transfer regimes reaches exactly the
 * MAX_ATTEMPTS cap and that count. */
const MAX_SUMMARIES = MAX_REPLICATES * CONDITIONS.length;
const MAX_PORTFOLIO_REFERENCES = MAX_SUMMARIES * (1 + MAX_TRANSFER_REGIMES);
/** Matches the records bound in `parseStudyEvidence`. */
const MAX_EVIDENCE_RECORDS = 64;

function condition(value: unknown, label: string): Condition {
  if (typeof value !== "string" || !(CONDITIONS as readonly string[]).includes(value)) throw new Error(`${label}: unknown condition`);
  return value as Condition;
}

function admitContext(value: unknown): { replicate: number; condition: Condition; phase: Phase } {
  const version = value !== null && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>).contract : undefined;
  const keys = typeof version === "string" ? CONTEXT_KEYS[version] : undefined;
  if (keys === undefined) throw new Error("attempt context: unsupported contract");
  const context = object(value, keys, "attempt context");
  const replicate = integer(context.replicate, 0, 0xffffffff, "attempt context.replicate");
  if (context.contract !== "algal.lab.context.v1" && (typeof context.phase !== "string" || !(PHASES as readonly string[]).includes(context.phase))) {
    throw new Error("attempt context.phase: unknown phase");
  }
  const phase: Phase = context.contract === "algal.lab.context.v1" ? "discovery" : context.phase as Phase;
  return { replicate, condition: condition(context.condition, "attempt context.condition"), phase };
}

type LoadedAttempt = { id: Digest; replicate: number; condition: Condition; phase: Phase; receipt: RunReceipt; score: number | null };

/** Admit one archived attempt. The store already binds every artifact by
 * content digest; this checks the shape the projection reads and that the
 * embedded receipt still parses under the pinned runtime's contract. */
function admitAttempt(id: Digest, value: unknown, instrumentDigest: Digest): LoadedAttempt {
  const raw = object(value, ATTEMPT_KEYS, "attempt");
  if (raw.contract !== "algal.lab.attempt.v1") throw new Error("attempt: unsupported contract");
  if (digestString(raw.instrumentDigest) !== instrumentDigest) throw new Error("attempt: instrument identity differs");
  const context = admitContext(raw.context);
  const receipt = parseRunReceipt(json(raw.receipt));
  if (receiptDigest(receipt) !== receipt.digest) throw new Error("attempt: receipt body does not match its digest");
  let score: number | null = null;
  if (raw.measurement !== null) {
    const measurement = object(raw.measurement, ["proposal", "results", "score", "predictionError"], "attempt.measurement");
    if (typeof measurement.score !== "number" || !Number.isFinite(measurement.score) || measurement.score < 0 || measurement.score > 1) {
      throw new Error("attempt.measurement.score: expected a finite AUC in [0,1]");
    }
    score = measurement.score;
  }
  return { id, ...context, receipt, score };
}

/** Admit one frozen design evaluation (`algal.lab.design-evaluation.v1`). */
function admitDesignEvaluation(value: unknown): { attempt: Digest; meanAuc: number } {
  const raw = object(value, ["contract", "instrumentDigest", "attempt", "graphDigest", "results", "meanAuc"], "design evaluation");
  if (raw.contract !== "algal.lab.design-evaluation.v1") throw new Error("design evaluation: unsupported contract");
  if (typeof raw.meanAuc !== "number" || !Number.isFinite(raw.meanAuc) || raw.meanAuc < 0 || raw.meanAuc > 1) {
    throw new Error("design evaluation.meanAuc: expected a finite AUC in [0,1]");
  }
  return { attempt: digestString(raw.attempt), meanAuc: raw.meanAuc };
}

/** Admit the per-portfolio evaluation batch (`algal.lab.evaluation.v1`). */
function admitEvaluationBatch(value: unknown): { portfolioDigest: Digest; designs: Digest[] } {
  const raw = object(value, ["contract", "instrumentDigest", "portfolioDigest", "holdoutSeeds", "designs"], "evaluation batch");
  if (raw.contract !== "algal.lab.evaluation.v1") throw new Error("evaluation batch: unsupported contract");
  if (!Array.isArray(raw.designs) || raw.designs.length > 2048) throw new Error("evaluation batch.designs: invalid design list");
  return { portfolioDigest: digestString(raw.portfolioDigest), designs: raw.designs.map(digestString) };
}

/** Admit the report fields the projection reads (closed schema, current
 * revision only — older archives are projected at their recorded source
 * revision, exactly as `verifyStudy` treats them). */
export function admitStudyView(value: unknown): EvidenceStudyView {
  const raw = object(value, REPORT_KEYS, "study report");
  if (raw.contract !== "algal.lab.report.v3" || raw.algalRevision !== ALGAL_REVISION) throw new Error("study report: unsupported identity or revision");
  if (raw.backend !== "scripted" && raw.backend !== "random" && raw.backend !== "command") throw new Error("study report: unknown backend");
  const protocol = parseProtocol(raw.protocol);
  const instrumentDigest = digestString(raw.instrumentDigest);
  const applicationDigest = digestString(raw.applicationDigest);
  if (!Array.isArray(raw.attempts) || raw.attempts.length > 2048) throw new Error("study report.attempts: invalid attempt list");
  const attempts = raw.attempts.map(digestString);
  if (new Set(attempts).size !== attempts.length) throw new Error("study report.attempts: repeated attempt digest");
  if (!Array.isArray(raw.summaries) || raw.summaries.length > MAX_SUMMARIES) throw new Error(`study report.summaries: expected at most ${MAX_SUMMARIES} entries`);
  const summaries = raw.summaries.map((entry) => {
    const summary = object(entry, SUMMARY_KEYS, "study summary");
    if (!Array.isArray(summary.transfers) || summary.transfers.length > MAX_TRANSFER_REGIMES) throw new Error(`study summary.transfers: expected at most ${MAX_TRANSFER_REGIMES} entries`);
    return {
      replicate: integer(summary.replicate, 0, 0xffffffff, "study summary.replicate"),
      condition: condition(summary.condition, "study summary.condition"),
      portfolioDigest: digestString(summary.portfolioDigest),
      evaluation: digestString(summary.evaluation),
      transfers: summary.transfers.map((transfer) => {
        const t = object(transfer, TRANSFER_KEYS, "transfer summary");
        return { portfolioDigest: digestString(t.portfolioDigest), evaluation: digestString(t.evaluation) };
      }),
    };
  });
  return { backend: raw.backend as EvidenceStudyView["backend"], protocol, instrumentDigest, applicationDigest, attempts, summaries };
}

function cellGroup(replicate: number, conditionName: Condition): string {
  return `r${replicate}:${conditionName}`;
}

function outcomeCases(cases: EvaluationOutcomeCase[]): EvaluationOutcome {
  return { passed: cases.filter((c) => c.passed).length, total: cases.length, score: mean(cases.map((c) => c.score)), cases };
}

/** Map one retained attempt to a case outcome. `passed` records that the
 * measurement completed — it is not a quality threshold — and the case
 * receipt binds the attempt's actual run receipt. */
function attemptCase(attempt: LoadedAttempt, group: string): EvaluationOutcomeCase {
  const phaseLabel = `phase:${attempt.phase}`;
  if (attempt.receipt.outcome === "complete" && attempt.score !== null) {
    return { id: attempt.id, group, outcome: "complete", passed: true, score: attempt.score, receipt: attempt.receipt.digest, feedback: phaseLabel };
  }
  if (attempt.receipt.outcome === "stuck" || attempt.receipt.outcome === "suspended") {
    return { id: attempt.id, group, outcome: "uncertain", passed: false, score: 0, receipt: attempt.receipt.digest,
      feedback: `${phaseLabel}; run outcome ${attempt.receipt.outcome}` };
  }
  return { id: attempt.id, group, outcome: "failed", passed: false, score: 0, receipt: attempt.receipt.digest,
    feedback: `${phaseLabel}; ${attempt.receipt.failure?.message ?? "run failed before measurement"}`.slice(0, 4096) };
}

function sortedUnique(values: Iterable<string>, label: string, max: number): string[] {
  const result = [...new Set(values)].sort();
  if (result.length > max) throw new Error(`${label}: exceeds bound ${max}`);
  return result;
}

/** Build the `algal.evaluation-evidence.v1` record and the study-evidence
 * envelope for one admitted study view. Pure projection: every field is a
 * deterministic function of the archived artifacts and the installed runtime
 * sources; nothing is sampled, retried, or recomputed against a provider. */
export async function studyEvidence(report: unknown, store: ArtifactStore): Promise<{ records: EvaluationEvidence[]; envelope: StudyEvidence }> {
  // The digest covers the complete report object, so it equals the study.json
  // envelope digest; the admitted view then bounds what the projection reads.
  const reportDigest = digest(report);
  const view = admitStudyView(report);
  const settings = protocolSettings(view.protocol);
  const instrument = instrumentOf(view.protocol);
  const manifest = instrument === "network.v2" ? researchManifestV2 : researchManifest;
  // The record binds two source states: the study-time identities recorded in
  // the report (instrumentDigest, and the runtime embedded in the scorer's
  // applicationDigest) and evaluator.runtimeDigest, the runtime installed at
  // projection time. When they differ the projection still runs — the record
  // discloses the drift — and verification refuses the result.
  const runtimeSources = await readRuntimeSources();
  const projectionIdentities = await sourceIdentities(instrument);
  const attempts = new Map<Digest, LoadedAttempt>();
  for (const id of view.attempts) attempts.set(id, admitAttempt(id, await store.get(id), view.instrumentDigest));

  const train: EvaluationOutcomeCase[] = [];
  const validation: EvaluationOutcomeCase[] = [];
  const holdout: EvaluationOutcomeCase[] = [];
  for (const attempt of attempts.values()) {
    const group = cellGroup(attempt.replicate, attempt.condition);
    (attempt.phase === "transfer" ? validation : train).push(attemptCase(attempt, group));
  }
  const portfolios: Digest[] = [];
  let emptyHoldoutGroups = 0;
  for (const summary of view.summaries) {
    const group = cellGroup(summary.replicate, summary.condition);
    const batches: { evaluation: Digest; portfolioDigest: Digest; scope: string }[] = [
      { evaluation: summary.evaluation, portfolioDigest: summary.portfolioDigest, scope: "primary" },
      ...summary.transfers.map((transfer, index) => ({ evaluation: transfer.evaluation, portfolioDigest: transfer.portfolioDigest, scope: `transfer-${index}` })),
    ];
    let designs = 0;
    for (const batch of batches) {
      const admitted = admitEvaluationBatch(await store.get(batch.evaluation));
      if (admitted.portfolioDigest !== batch.portfolioDigest) throw new Error("evaluation batch does not bind its portfolio");
      portfolios.push(admitted.portfolioDigest);
      for (const reference of admitted.designs) {
        const design = admitDesignEvaluation(await store.get(reference));
        const source = attempts.get(design.attempt);
        if (source === undefined) throw new Error("design evaluation names an attempt outside the study");
        // The receipt binds the run that produced this design; the case id binds
        // the design-evaluation artifact that measured it on held-out schedules.
        holdout.push({ id: reference, group, outcome: "complete", passed: true, score: design.meanAuc, receipt: source.receipt.digest, feedback: `scope:${batch.scope}` });
        designs++;
      }
    }
    if (designs === 0) emptyHoldoutGroups++;
  }

  const groups = sortedUnique(view.summaries.map((summary) => cellGroup(summary.replicate, summary.condition)), "dataset.groups", MAX_SUMMARIES);
  const agentEffects = [...attempts.values()].flatMap((attempt) => attempt.receipt.effects.filter((effect) => !effect.executor.startsWith("tool:")));
  const routeDigests = new Set(agentEffects.map((effect) => effect.configurationDigest).filter((d): d is Digest => d !== undefined));
  const usageUnits = `${view.backend}-agent-effects`;
  const limitations: string[] = [
    "Receipt replay and this projection establish internal consistency of the archived run, not physical validity, label truth, or provider attestation.",
    "Numerical outcomes describe a small deterministic graph instrument only; they are not evidence about real networks or materials.",
    "Case passed records that the measurement completed; it is not a quality threshold and the record makes no significance claim.",
    "Portfolios and champions were frozen on discovery-phase scores before any holdout measurement; holdout outcomes never entered a researcher context or selection step.",
    "The holdout aggregate mixes unseen random schedules with a repeated deterministic targeted control, so it is not entirely out-of-sample.",
    "No independent review has examined this record; independentReview stays not-reviewed.",
    view.backend === "command"
      ? "usage counts bounded agent effects to an operator-owned command executor; provider calls inside the wrapper are not independently attested."
      : "usage counts bounded agent effects; the scripted and random backends are local deterministic controls that make no model calls.",
    "charges are recorded ALGAL work units under each attempt's declared work bound; no monetary billing is represented.",
    settings.transferRegimes.length === 0
      ? "The protocol defines no validation split: champions were selected on discovery scores directly and the validation outcome is empty by design."
      : "validation cases are held-out-budget transfer proposals measured on the same discovery schedule seeds, not an independently labeled validation split.",
    "labelProvenance: scores are deterministic instrument measurements; hypothesis, rationale, and message text are unverified researcher claims.",
  ];
  if (settings.primedDesigns > 0) limitations.push("train cases include host-primed control designs identical across conditions by construction; they are not researcher discoveries.");
  if (emptyHoldoutGroups > 0) limitations.push(`${emptyHoldoutGroups} replicate/condition group(s) froze empty portfolios; their holdout outcomes contain no cases.`);
  if (routeDigests.size !== 1) limitations.push("no single executor configuration digest binds the agent effects, so routeDigest is null.");
  if (projectionIdentities.instrumentDigest !== view.instrumentDigest || projectionIdentities.applicationDigest !== view.applicationDigest) {
    limitations.push("the installed laboratory and runtime sources at projection time differ from the study's recorded instrumentDigest/applicationDigest; evaluator.runtimeDigest names the projection-time runtime, not the study-time install.");
  }

  const record = buildEvaluationEvidence({
    contract: "algal.evaluation-evidence.v1",
    baseArtifact: view.instrumentDigest,
    candidateArtifact: digest({ contract: "algal.lab.evaluation-candidate.v1", reportDigest, portfolios: sortedUnique(portfolios, "portfolios", MAX_PORTFOLIO_REFERENCES) }),
    dataset: {
      digest: digest(view.protocol),
      groups,
      splitPolicy: settings.transferRegimes.length === 0
        ? "train = discovery attempts measured on the protocol's discoverySeeds; no validation split exists; holdout = frozen-portfolio designs evaluated on holdoutSeeds after selection froze"
        : "train = primed and discovery attempts measured on the protocol's discoverySeeds; validation = held-out-budget transfer proposals measured on the same discovery schedules; holdout = frozen-portfolio designs evaluated on holdoutSeeds after selection froze",
      labelProvenance: "scores are instrument measurements produced by the lab simulator, not human or model labels",
      redactionPolicy: "no personal data is collected; researcher text is bounded protocol content and nothing is redacted",
    },
    evaluator: { scorerDigest: view.applicationDigest, runtimeDigest: runtimeDigest(runtimeSources), routeDigest: routeDigests.size === 1 ? [...routeDigests][0]! : null },
    usage: {
      modelCalls: attempts.size === 0 ? 0 : [...attempts.values()].reduce((sum, attempt) => sum + attempt.receipt.work.agentCalls, 0),
      tokensIn: agentEffects.reduce((sum, effect) => sum + (effect.usage?.tokensIn ?? 0), 0),
      tokensOut: agentEffects.reduce((sum, effect) => sum + (effect.usage?.tokensOut ?? 0), 0),
      units: usageUnits,
    },
    charges: {
      reserved: attempts.size * manifest.budgets.maxWork,
      settled: [...attempts.values()].reduce((sum, attempt) => sum + attempt.receipt.work.units, 0),
      unit: "algal-work-units",
    },
    outcomes: { train: outcomeCases(train), validation: outcomeCases(validation), holdout: outcomeCases(holdout) },
    independentReview: { status: "not-reviewed", reviewer: null, notes: null },
    claimCategory: "replay",
    limitations: sortedUnique(limitations, "limitations", HOST_CONTRACT_BOUNDS.maxLimitEntries),
  });
  const records = [record];
  // Records list the artifact-store reference of each record: the digest of the
  // stored object including its signed `digest` field, which is the name
  // `ArtifactStore.get` retrieves and re-verifies.
  const body: Omit<StudyEvidence, "digest"> = { contract: STUDY_EVIDENCE_CONTRACT, reportDigest, backend: view.backend, instrumentDigest: view.instrumentDigest, applicationDigest: view.applicationDigest,
    records: sortedUnique(records.map((r) => digest(r)), "records", MAX_EVIDENCE_RECORDS) as Digest[] };
  return { records, envelope: { ...body, digest: digest(body) } };
}

export function parseStudyEvidence(value: unknown): StudyEvidence {
  const raw = object(value, ["contract", "reportDigest", "backend", "instrumentDigest", "applicationDigest", "records", "digest"], "study evidence");
  if (raw.contract !== STUDY_EVIDENCE_CONTRACT) throw new Error("study evidence: unsupported contract");
  if (raw.backend !== "scripted" && raw.backend !== "random" && raw.backend !== "command") throw new Error("study evidence: unknown backend");
  if (!Array.isArray(raw.records) || raw.records.length === 0 || raw.records.length > MAX_EVIDENCE_RECORDS) throw new Error(`study evidence.records: expected 1..${MAX_EVIDENCE_RECORDS} digests`);
  const records = raw.records.map(digestString);
  if (records.some((record, index) => index > 0 && record <= records[index - 1]!)) throw new Error("study evidence.records: must be sorted and unique");
  const body: Omit<StudyEvidence, "digest"> = { contract: STUDY_EVIDENCE_CONTRACT, reportDigest: digestString(raw.reportDigest), backend: raw.backend as StudyEvidence["backend"],
    instrumentDigest: digestString(raw.instrumentDigest), applicationDigest: digestString(raw.applicationDigest), records };
  if (digest(body) !== digestString(raw.digest)) throw new Error("study evidence: digest mismatch");
  return { ...body, digest: digestString(raw.digest) };
}

/** Project a completed run directory: reads study.json, rebuilds every evidence
 * record into the content-addressed store, and writes evidence.json once.
 * Existing evidence files are never overwritten. */
export async function writeStudyEvidence(directory: string): Promise<StudyEvidence> {
  const raw = object(await readJsonFile(join(directory, "study.json")), ["report", "digest"], "study envelope");
  if (digest(raw.report) !== digestString(raw.digest)) throw new Error("study report digest mismatch");
  const store = new ArtifactStore(directory);
  const { records, envelope } = await studyEvidence(raw.report, store);
  for (const record of records) await store.put(record);
  await writeFile(join(directory, "evidence.json"), canonicalize(json({ envelope, digest: envelope.digest })) + "\n", { flag: "wx", mode: 0o600 });
  return envelope;
}

/** Check that evidence.json is exactly the deterministic projection of the
 * archived report and artifacts. This is projection fidelity, not a fresh
 * reproduction of the run; `verifyStudy` remains the reconstruction gate. */
export async function verifyStudyEvidence(directory: string): Promise<{ ok: true; records: number; cases: number; evidenceDigest: Digest }> {
  const file = object(await readJsonFile(join(directory, "evidence.json")), ["envelope", "digest"], "evidence file");
  const envelope = parseStudyEvidence(file.envelope);
  if (envelope.digest !== digestString(file.digest)) throw new Error("evidence digest mismatch");
  const raw = object(await readJsonFile(join(directory, "study.json")), ["report", "digest"], "study envelope");
  if (digest(raw.report) !== digestString(raw.digest)) throw new Error("study report digest mismatch");
  if (envelope.reportDigest !== digestString(raw.digest)) throw new Error("evidence binds a different report");
  // The envelope's recorded source identities must still describe the installed
  // laboratory and runtime: evaluator.runtimeDigest is projection-time while
  // scorerDigest embeds the study-time runtime, so a drifted install fails here
  // rather than silently reproducing a record that describes another state.
  const identities = await sourceIdentities(instrumentOf(admitStudyView(raw.report).protocol));
  if (envelope.instrumentDigest !== identities.instrumentDigest || envelope.applicationDigest !== identities.applicationDigest) {
    throw new Error("source identity changed; verify evidence with the exact recorded source version");
  }
  const store = new ArtifactStore(directory);
  const rebuilt = await studyEvidence(raw.report, store);
  if (!equal(rebuilt.envelope, envelope)) throw new Error("evidence differs from reproduced projection");
  let cases = 0;
  for (const id of envelope.records) {
    const record = parseEvaluationEvidence(await store.get(id));
    cases += record.outcomes.train.total + record.outcomes.validation.total + record.outcomes.holdout.total;
  }
  return { ok: true, records: envelope.records.length, cases, evidenceDigest: envelope.digest };
}
