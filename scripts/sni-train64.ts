import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { encode, requireNewDirectory, sha256 } from "../src/foundation/datasets";
import { SNI } from "../src/foundation/sni-intake";
import { extractTrainMetadata, freezeTrain64, TRAIN64 } from "../src/foundation/sni-train64";

const indexPath = "runs/sni-index-20261008-01/task-blob-oids.tsv";
const timeoutMs = 30_000;
async function fetchBounded(url: string): Promise<Uint8Array> {
  const response = await fetch(url, { redirect: "error", headers: { "User-Agent": "algal-sni-train64" }, signal: AbortSignal.timeout(timeoutMs) });
  if (response.status !== 200 || !response.body) throw Error(`http-${response.status}`);
  if (Number(response.headers.get("content-length") ?? 0) > TRAIN64.maxBlobBytes) {
    await response.body.cancel(); throw Error("blob-too-large");
  }
  const reader = response.body.getReader(), chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const next = await reader.read();
      if (next.done) break;
      size += next.value.length;
      if (size > TRAIN64.maxBlobBytes) throw Error("blob-too-large");
      chunks.push(next.value);
    }
  } finally { await reader.cancel(); }
  return Buffer.concat(chunks);
}
const safeErrors = new Set(["blob-too-large", "blob-OID-mismatch", "index SHA-256 mismatch", "task-not-object", "metadata-only fields required; instances and outputs forbidden",
  "invalid task id", "invalid Source", "invalid Categories", "invalid Instance License"]);
function failureCode(error: unknown): string {
  if (error instanceof Error) {
    if (safeErrors.has(error.message) || /^http-[0-9]{3}$/.test(error.message)) return error.message;
    if (error.name === "TimeoutError" || error.name === "AbortError") return "timeout";
    if (error instanceof SyntaxError) return "invalid-JSON";
  }
  return "fetch-or-extract-error"; // Never log upstream JSON, examples, URLs or response bodies.
}
export async function main(args: string[]) {
  if (args.length !== 2 || args[0] !== "--out" || !/^runs\/[a-zA-Z0-9_-]+$/.test(args[1] ?? "")) throw Error("usage: bun scripts/sni-train64.ts --out runs/NEW-NAME");
  const out = args[1]!;
  await requireNewDirectory(out);
  const { selected, tsv, testNames } = freezeTrain64(await readFile(indexPath));
  await requireNewDirectory(out);
  await mkdir(out, { mode: 0o700 });
  await writeFile(join(out, "selection.tsv"), tsv, { flag: "wx", mode: 0o600 });
  // These are metadata only. Do not open test-task JSON, even for license checks.
  await writeFile(join(out, "plan.json"), encode({ contract: "algal.sni.train64.v1", commit: SNI.commit, indexSha256: TRAIN64.indexSha256,
    selectionSha256: TRAIN64.selectionSha256, count: selected.length, testNamesSha256: sha256(testNames.join("\n") + "\n"),
    fetchLimitBytes: TRAIN64.maxBlobBytes, fetchTimeoutMs: timeoutMs, maxFetches: selected.length,
    paidUsd: 0, disposition: "review-required; no test bodies or model calls" }), { flag: "wx", mode: 0o600 });
  const statuses = { extracted: 0, failed: 0 };
  for (let i = 0; i < selected.length; i++) {
    const ref = selected[i]!;
    const id = String(i + 1).padStart(2, "0");
    // On a process interruption an unmatched attempt is an unresolved fetch,
    // not a license to repeat or silently omit it.
    await writeFile(join(out, `${id}.attempt.json`), encode({ task: ref.task, blobOid: ref.blobOid, status: "started" }), { flag: "wx", mode: 0o600 });
    try {
      const url = `https://raw.githubusercontent.com/allenai/natural-instructions/${SNI.commit}/tasks/${ref.task}.json`;
      const bytes = await fetchBounded(url);
      const metadata = extractTrainMetadata(ref, bytes);
      await writeFile(join(out, `${id}.sidecar.json`), encode(metadata), { flag: "wx", mode: 0o600 });
      statuses.extracted++;
    } catch (error) {
      // A file-write failure also enters here: its outcome may be uncertain.
      await writeFile(join(out, `${id}.failure.json`), encode({ task: ref.task, blobOid: ref.blobOid, code: failureCode(error),
        disposition: "failed or unresolved; no automatic retry" }), { flag: "wx", mode: 0o600 });
      statuses.failed++;
    }
  }
  const report = { contract: "algal.sni.train64.v1", commit: SNI.commit, selectionSha256: TRAIN64.selectionSha256,
    statuses, disposition: "review-required; no corpus admission or holdout access; failed attempts retained", paidUsd: 0 };
  await writeFile(join(out, "report.json"), encode(report), { flag: "wx", mode: 0o600 });
  return report;
}
if (import.meta.main) main(Bun.argv.slice(2)).then(report => console.log(encode(report))).catch(error => { console.error(error); process.exitCode = 1; });
