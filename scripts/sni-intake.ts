import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { encode, requireNewDirectory } from "../src/foundation/datasets";
import { pinTaskIndex, SNI } from "../src/foundation/sni-intake";

/** Index only. Neither this command nor its URLs request any task JSON. */
const raw = `https://raw.githubusercontent.com/allenai/natural-instructions/${SNI.commit}/splits/default/`;
export const indexUrls = {
  tree: `https://api.github.com/repos/allenai/natural-instructions/git/trees/${SNI.tree}?recursive=1`,
  train: `${raw}train_tasks.txt`, test: `${raw}test_tasks.txt`, excluded: `${raw}excluded_tasks.txt`,
} as const;
async function fetchBounded(url: string, max: number): Promise<Uint8Array> {
  const response = await fetch(url, { redirect: "error", headers: { "User-Agent": "algal-sni-intake" }, signal: AbortSignal.timeout(30000) });
  if (response.status !== 200 || !response.body) throw Error(`source index HTTP status ${response.status}`);
  if (Number(response.headers.get("content-length") ?? 0) > max) { await response.body.cancel(); throw Error("source index exceeds bound"); }
  const reader = response.body.getReader(), chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const next = await reader.read(); if (next.done) break;
      size += next.value.length;
      if (size > max) throw Error("source index exceeds bound");
      chunks.push(next.value);
    }
  } finally { await reader.cancel(); }
  return Buffer.concat(chunks);
}
export async function main(args: string[]) {
  if (args.length !== 2 || args[0] !== "--out" || !args[1]?.startsWith("runs/") || !/^runs\/[a-zA-Z0-9_-]+$/.test(args[1])) throw Error("usage: bun scripts/sni-intake.ts --out runs/NEW-NAME");
  const out = args[1];
  await requireNewDirectory(out);
  const tree = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(await fetchBounded(indexUrls.tree, 2_000_000))) as unknown;
  const files = {
    train: await fetchBounded(indexUrls.train, 100_000),
    test: await fetchBounded(indexUrls.test, 100_000),
    excluded: await fetchBounded(indexUrls.excluded, 100_000),
  };
  const index = pinTaskIndex(tree, files);
  // A Git blob OID is SHA-1 over Git's blob framing, not a SHA-256 of raw task bytes.
  // This reproducible index pins each task without downloading test instances.
  if (index.sha256 !== "2e54d1a3c0ff5887ffbaf5fabdeafab5cdadd97e674f167de7359b9304185f38") throw Error("task index changed");
  await requireNewDirectory(out);
  await mkdir(out, { mode: 0o700 });
  await writeFile(join(out, "task-blob-oids.tsv"), index.tsv, { flag: "wx", mode: 0o600 });
  const report = { contract: "algal.sni.index.v1", source: "allenai/natural-instructions", commit: SNI.commit, tree: SNI.tree, splitPins: SNI.splits,
    taskIndexSha256: index.sha256, counts: SNI.splits, testFileAccess: "none; Git tree OIDs and split filenames only", disposition: "blocked: no authenticated metadata-only test-task license and Source export; no instances fetched" };
  await writeFile(join(out, "report.json"), encode(report), { flag: "wx", mode: 0o600 });
  return report;
}
if (import.meta.main) main(Bun.argv.slice(2)).then(report => console.log(encode(report))).catch(error => { console.error(error); process.exitCode = 1; });
