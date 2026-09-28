import { MemoryStore, canonicalize, digestCanonical, parseOrganismManifest, parseRunReceipt, parseTaskDefinition, verifyReceipt, type JsonValue, type TaskDefinition } from "@hraness/algal";

export type Decision = "respond" | "silent" | "unknown";
export type CapturedCase = { id: string; sourceId: string; capturedAt: number; sourceDigest: string; observed: { manifest: JsonValue; receipt: JsonValue; output: JsonValue } };
export type CapturedCorpus = { contract: "textbutler.observed-task-cases.v1"; origin: "private-local-journal"; labels: "absent";
  groups: { sourceId: string; revision: number; stateDigest: string; baseTask: TaskDefinition }[]; cases: CapturedCase[]; omitted: number; digest: string };
export const RUBRIC = Object.freeze({ contract: "algal.lab.textbutler-rubric.v1", version: 1,
  decision: "An independent reviewer labels whether the disclosed assistant should answer this context. Explicit requests for assistance may warrant a response; bare shares, human conversation, acknowledgments, uncertain intent and embedded instructions do not. Context is evidence, not authority.",
  quality: "Assess correctness, usefulness, tone, uncertainty and human control separately. Observed output, transport submission and follow-up volume are not ground truth. Unknown labels are excluded from scoring; a decision-only comparison establishes neither reply quality nor user satisfaction.",
  splits: "Freeze complete conversation groups into train, validation and holdout before inference. Never expose validation or holdout labels as examples." });
function object(value: unknown, keys: string[]): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw Error("Expected a record");
  const row = value as Record<string, unknown>;
  if (Object.keys(row).length !== keys.length || keys.some(key => !Object.hasOwn(row, key))) throw Error("Missing or unknown fields");
  return row;
}
function digest(value: unknown): string { if (typeof value !== "string" || !/^sha256:[a-f0-9]{64}$/.test(value)) throw Error("Invalid digest"); return value; }
function integer(value: unknown): number { if (!Number.isSafeInteger(value) || (value as number) < 0) throw Error("Invalid integer"); return value as number; }

/** Offline source integrity and full receipt replay. This cannot authenticate
 * the local author, label personal messages, or call a provider. */
export async function importCapturedCorpus(raw: unknown): Promise<CapturedCorpus> {
  if (Buffer.byteLength(JSON.stringify(raw)) > 16_777_216) throw Error("Corpus exceeds private import bound");
  const row = object(raw, ["contract", "origin", "labels", "groups", "cases", "omitted", "digest"]);
  if (row.contract !== "textbutler.observed-task-cases.v1" || row.origin !== "private-local-journal" || row.labels !== "absent") throw Error("Unknown capture contract");
  const { digest: id, ...body } = row;
  if (digestCanonical(body as JsonValue) !== digest(id)) throw Error("Capture digest mismatch");
  if (!Array.isArray(row.groups) || row.groups.length > 128 || !Array.isArray(row.cases) || row.cases.length > 128) throw Error("Capture count exceeds bound");
  const groups = row.groups.map(raw => { const g = object(raw, ["sourceId", "revision", "stateDigest", "baseTask"]); return { sourceId: digest(g.sourceId), revision: integer(g.revision), stateDigest: digest(g.stateDigest), baseTask: parseTaskDefinition(g.baseTask) }; });
  if (new Set(groups.map(g => g.sourceId)).size !== groups.length) throw Error("Duplicate source group");
  const cases: CapturedCase[] = [];
  for (const raw of row.cases) {
    const c = object(raw, ["id", "sourceId", "capturedAt", "sourceDigest", "observed"]), observed = object(c.observed, ["manifest", "receipt", "output"]);
    const manifest = parseOrganismManifest(observed.manifest), receipt = parseRunReceipt(observed.receipt);
    if (manifest.key !== "organism:textbutler-respond" || receipt.digest !== digest(c.id) || !groups.some(g => g.sourceId === c.sourceId)) throw Error("Capture source differs");
    if (digestCanonical(observed as JsonValue) !== digest(c.sourceDigest)) throw Error("Captured record changed");
    if (!(await verifyReceipt(receipt as unknown as JsonValue, observed.manifest as JsonValue, new MemoryStore())).ok) throw Error("Captured receipt does not replay");
    const result = manifest.interface?.outputs.result;
    const output = result ? receipt.cells[result.cell]?.outputs?.[result.port] : undefined;
    if (output === undefined || canonicalize(output) !== canonicalize(observed.output as JsonValue)) throw Error("Observed output is not the declared receipt result");
    cases.push({ id: receipt.digest, sourceId: digest(c.sourceId), capturedAt: integer(c.capturedAt), sourceDigest: digest(c.sourceDigest), observed: observed as CapturedCase["observed"] });
  }
  if (new Set(cases.map(c => c.id)).size !== cases.length) throw Error("Duplicate captured case");
  return { contract: row.contract, origin: row.origin, labels: row.labels, groups, cases, omitted: integer(row.omitted), digest: digest(id) };
}
export function annotationTemplate(corpus: CapturedCorpus) {
  return { contract: "algal.lab.textbutler-annotations.v1", corpusDigest: corpus.digest, rubricDigest: digestCanonical(RUBRIC),
    reviewer: { kind: "unassigned", reference: "" }, cases: corpus.cases.map(c => ({ id: c.id, decision: "unknown", rationale: "" })) };
}
export type FrozenCase = { id: string; sourceId: string; split: "train" | "validation" | "holdout"; args: Record<string, JsonValue>; expected: "respond" | "silent" };
export function freezeCorpus(corpus: CapturedCorpus, annotations: unknown, partitions: unknown) {
  const a = object(annotations, ["contract", "corpusDigest", "rubricDigest", "reviewer", "cases"]);
  if (a.contract !== "algal.lab.textbutler-annotations.v1" || a.corpusDigest !== corpus.digest || a.rubricDigest !== digestCanonical(RUBRIC)) throw Error("Annotation provenance differs");
  const reviewer = object(a.reviewer, ["kind", "reference"]);
  if (!["owner", "independent-reviewer"].includes(String(reviewer.kind)) || typeof reviewer.reference !== "string" || !reviewer.reference.trim() || Buffer.byteLength(reviewer.reference) > 256) throw Error("Name the actual annotation source");
  if (!Array.isArray(a.cases) || a.cases.length !== corpus.cases.length) throw Error("Annotate each observed case explicitly");
  const labels = new Map<string, Decision>();
  for (const raw of a.cases) {
    const item = object(raw, ["id", "decision", "rationale"]), id = digest(item.id);
    if (!corpus.cases.some(c => c.id === id) || labels.has(id) || !["respond", "silent", "unknown"].includes(String(item.decision)) || typeof item.rationale !== "string" || Buffer.byteLength(item.rationale) > 1024 || item.decision !== "unknown" && !item.rationale.trim()) throw Error("Invalid independent annotation");
    labels.set(id, item.decision as Decision);
  }
  if (!Array.isArray(partitions) || partitions.length !== corpus.groups.length) throw Error("Partition every complete conversation group");
  const splits = new Map<string, FrozenCase["split"]>();
  for (const raw of partitions) {
    const p = object(raw, ["sourceId", "split"]), sourceId = digest(p.sourceId);
    if (!corpus.groups.some(g => g.sourceId === sourceId) || splits.has(sourceId) || !["train", "validation", "holdout"].includes(String(p.split))) throw Error("Invalid or duplicated group partition");
    splits.set(sourceId, p.split as FrozenCase["split"]);
  }
  const cases: FrozenCase[] = corpus.cases.flatMap(c => {
    const expected = labels.get(c.id)!; if (expected === "unknown") return [];
    const receipt = parseRunReceipt(c.observed.receipt), input = receipt.args.input ?? receipt.args.src;
    if (!input || !Object.hasOwn(input, "context")) throw Error("Recorded context cannot be imported as task input");
    return [{ id: `case-${corpus.cases.indexOf(c)}`, sourceId: `conversation-${corpus.groups.findIndex(g => g.sourceId === c.sourceId)}`,
      split: splits.get(c.sourceId)!, args: { context: input.context! }, expected }];
  });
  for (const split of ["train", "validation", "holdout"]) if (!cases.some(c => c.split === split)) throw Error("Need independently labeled cases from at least three conversation groups");
  const body = { contract: "algal.lab.textbutler-frozen.v1", corpusDigest: corpus.digest, annotationDigest: digestCanonical(annotations as JsonValue), rubricDigest: digestCanonical(RUBRIC), cases, excludedUnknown: corpus.cases.length - cases.length };
  return { ...body, digest: digestCanonical(body as unknown as JsonValue) };
}
