import { createHash } from "node:crypto";
import { sha256 } from "./datasets";
import { parseTaskMetadata, SNI, type TaskRef } from "./sni-intake";

// Frozen BEFORE the first train blob was fetched; see docs/sni-train64-freeze.md.
export const TRAIN64 = {
  indexSha256: "2e54d1a3c0ff5887ffbaf5fabdeafab5cdadd97e674f167de7359b9304185f38",
  selectionSha256: "97cb7f38b55869de58e4667f28458d2c1d15799211bfdb9e25d795b9444f0728",
  count: 64,
  maxBlobBytes: 1_000_000,
} as const;
const rowPattern = /^(train|test|excluded)\t(task[0-9]{3,4}_[a-zA-Z0-9_.-]+)\t([0-9a-f]{40})$/;
const lexical = (a: string, b: string) => a < b ? -1 : a > b ? 1 : 0;

/** Checks the complete pinned index; the caller receives only selected train OIDs and test names. */
export function freezeTrain64(index: Uint8Array) {
  if (sha256(index) !== TRAIN64.indexSha256) throw Error("index SHA-256 mismatch");
  const rows = new TextDecoder("utf-8", { fatal: true }).decode(index).split("\n");
  if (rows.pop() !== "") throw Error("index is not newline terminated");
  const refs: TaskRef[] = [], testNames: string[] = [];
  const counts = { train: 0, test: 0, excluded: 0 }, ids = new Set<string>();
  for (const line of rows) {
    const m = rowPattern.exec(line);
    if (!m || ids.has(m[2]!)) throw Error("invalid or duplicate index row");
    const split = m[1]! as TaskRef["split"], task = m[2]!, blobOid = m[3]!;
    counts[split]++; ids.add(task);
    if (split === "train") refs.push({ split, task, blobOid });
    if (split === "test") testNames.push(task); // Never construct a test-task URL.
  }
  for (const split of ["train", "test", "excluded"] as const) {
    if (counts[split] !== SNI.splits[split].count) throw Error("split count mismatch");
  }
  const selected = refs.sort((a, b) => lexical(a.task, b.task)).slice(0, TRAIN64.count);
  const tsv = selected.map(ref => `${ref.split}\t${ref.task}\t${ref.blobOid}\n`).join("");
  if (selected.length !== TRAIN64.count || sha256(tsv) !== TRAIN64.selectionSha256) throw Error("frozen selection mismatch");
  return { selected, tsv, testNames: testNames.sort(lexical) };
}

/** Raw task data is never returned or written. Check the Git blob framing before parsing. */
export function extractTrainMetadata(ref: TaskRef, bytes: Uint8Array) {
  if (ref.split !== "train" || !rowPattern.test(`train\t${ref.task}\t${ref.blobOid}`)) throw Error("not a pinned train ref");
  if (bytes.length > TRAIN64.maxBlobBytes) throw Error("blob-too-large");
  const oid = createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex");
  if (oid !== ref.blobOid) throw Error("blob-OID-mismatch");
  const raw: unknown = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) throw Error("task-not-object");
  const obj = raw as Record<string, unknown>;
  // Select only these three exact metadata fields; do not serialize raw, Instances,
  // examples, labels, outputs, or error bodies. Closed sidecar parser rejects more.
  const metadata = parseTaskMetadata({ task: ref.task, Source: obj.Source, Categories: obj.Categories, "Instance License": obj["Instance License"] });
  return { blobOid: ref.blobOid, ...metadata };
}
