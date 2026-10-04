import { createHash } from "node:crypto";
import { lstat, mkdir, open, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { object, text } from "../contracts";

export const CLINC = {
  id: "clinc150-full", revision: "828f8093932c8fe6ca7936c3d2e52903b1c523de", license: "CC-BY-3.0",
  source: "https://github.com/clinc/oos-eval", paper: "https://www.aclweb.org/anthology/D19-1131/",
  attribution: "Larson, Mahendran, Peper, Clarke, Lee, Hill, Kummerfeld, Leach, Laurenzano, Tang, and Mars (2019), An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction, EMNLP-IJCNLP.",
  inspected: "2026-10-04",
  files: [
    { path: "data/data_full.json", stored: "upstream.json", bytes: 2495390, sha256: "36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0" },
    { path: "LICENSE", stored: "LICENSE", bytes: 19467, sha256: "e6bc9e9c474700b708f568bac9e5a8a9bcb2b1dad53442f5ba449fcb848b8e76" },
    { path: "README.md", stored: "upstream-readme.txt", bytes: 2668, sha256: "8a8df26c4de3d25b6c4cff385ca23602c30e4e56828b015206cbc202f6db363a" },
  ],
} as const;
export const CLINC_MANIFEST_SHA256 = "09035c10fc6caa16b596d281758e2cf885db8504e8fbedd924eba0209a4335e5";
export type Split = "train" | "validation" | "test";
type Fetch = (input: string | URL | Request, init?: RequestInit) => Promise<Response>;
export type Row = { id: string; group: string; split: Split; text: string; label: string };
export const sha256 = (bytes: string | Uint8Array): string => createHash("sha256").update(bytes).digest("hex");
export const encode = (value: unknown): string => `${JSON.stringify(value, null, 2)}\n`;
export const normalized = (value: string): string => value.normalize("NFKC").toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();
export async function boundedFile(path: string, max: number): Promise<Buffer> {
  const file = await open(path, "r");
  try {
    const info = await file.stat();
    if (!info.isFile() || info.size > max) throw new Error("file exceeds size bound or is not regular");
    const bytes = Buffer.alloc(info.size + 1);
    let size = 0;
    while (size < bytes.length) { const read = await file.read(bytes, size, bytes.length - size); if (!read.bytesRead) break; size += read.bytesRead; }
    if (size > info.size) throw new Error("file grew while reading");
    return bytes.subarray(0, size);
  } finally { await file.close(); }
}
export async function requireNewDirectory(out: string): Promise<void> {
  try { await lstat(out); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") return; throw error; }
  throw new Error("output already exists; choose a new directory");
}
function checkBytes(file: typeof CLINC.files[number], bytes: Uint8Array): void {
  if (bytes.length !== file.bytes || sha256(bytes) !== file.sha256) throw new Error(`upstream identity mismatch: ${file.path}`);
}
export async function fetchPinned(file: typeof CLINC.files[number], fetcher: Fetch = fetch): Promise<Uint8Array> {
  const url = `https://raw.githubusercontent.com/clinc/oos-eval/${CLINC.revision}/${file.path}`;
  const response = await fetcher(url, { redirect: "error", signal: AbortSignal.timeout(30000) });
  if (response.status !== 200) throw new Error(`dataset HTTP status ${response.status}`);
  if (Number(response.headers.get("content-length") ?? 0) > file.bytes) { await response.body?.cancel(); throw new Error("dataset size exceeds pin"); }
  if (!response.body) throw new Error("missing dataset body");
  const reader = response.body.getReader(), chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const chunk = await reader.read(); if (chunk.done) break;
      size += chunk.value.length;
      if (size > file.bytes) throw new Error("dataset size exceeds pin");
      chunks.push(chunk.value);
    }
  } finally { await reader.cancel(); }
  const bytes = Buffer.concat(chunks); checkBytes(file, bytes); return bytes;
}
export function deriveClinc(value: unknown) {
  const keys = ["train", "val", "test", "oos_train", "oos_val", "oos_test"] as const;
  const raw = object(value, keys, "CLINC data");
  const rows: Row[] = [];
  const rawCounts: Record<string, number> = {};
  for (const key of keys) {
    const entries = raw[key];
    if (!Array.isArray(entries) || entries.length < 1 || entries.length > 15100) throw new Error("invalid CLINC partition size");
    rawCounts[key] = entries.length;
    const split: Split = key.endsWith("train") ? "train" : key.endsWith("val") ? "validation" : "test";
    entries.forEach((entry, index) => {
      if (!Array.isArray(entry) || entry.length !== 2) throw new Error("invalid CLINC row");
      const message = text(entry[0], 4096, "utterance"), label = text(entry[1], 100, "label");
      if (!/^[a-z][a-z0-9_]*$/.test(label) || (label === "oos") !== key.startsWith("oos_")) throw new Error("invalid CLINC label");
      const group = sha256(normalized(message));
      if (!normalized(message)) throw new Error("empty normalized utterance");
      rows.push({ id: `clinc150-${key}-${index}`, group, split, text: message, label });
    });
  }
  if (rows.length > 23700) throw new Error("CLINC total exceeds bound");
  const groups = new Map<string, Row[]>();
  for (const row of rows) groups.set(row.group, [...(groups.get(row.group) ?? []), row]);
  const quarantined = [...groups].filter(([, group]) => group.length > 1).map(([group, rows]) => ({ group, ids: rows.map(row => row.id) })).sort((a, b) => a.group.localeCompare(b.group));
  const unique = rows.filter(row => groups.get(row.group)!.length === 1);
  const splits = Object.fromEntries((["train", "validation", "test"] as const).map(split => [split, unique.filter(row => row.split === split)])) as Record<Split, Row[]>;
  return { rawCounts, splits, quarantined };
}
function materialize(bytes: Uint8Array) {
  const derived = deriveClinc(JSON.parse(Buffer.from(bytes).toString("utf8")) as unknown);
  const partitions = Object.fromEntries((["train", "validation", "test"] as const).map(split => [split, { file: `${split}.json`, rows: derived.splits[split].length, sha256: sha256(encode(derived.splits[split])) }]));
  const manifest = { contract: "algal.dataset.clinc150.v1", source: CLINC, transform: "nfkc-lowercase-alphanumeric-v1; quarantine every normalized duplicate, including within-split duplicates", rawCounts: derived.rawCounts, partitions, quarantined: derived.quarantined,
    limits: "Public crowdsourced English single-intent benchmark. Normalized-text groups are not conversation/source groups; paraphrases and model-training contamination are not excluded. The public test partition is reserved, not a fresh scientific holdout. Prepared data is an adaptation under CC-BY-3.0; retain the license, attribution, source, and transformation when redistributing." };
  return { ...derived, manifest };
}
export async function prepareClinc(out: string, options: { source?: string; fetch?: Fetch } = {}) {
  await requireNewDirectory(out);
  const files: Uint8Array[] = [];
  for (const file of CLINC.files) {
    const bytes = options.source ? await boundedFile(join(options.source, file.path), file.bytes) : await fetchPinned(file, options.fetch);
    checkBytes(file, bytes); files.push(bytes);
  }
  const data = materialize(files[0]!);
  if (sha256(encode(data.manifest)) !== CLINC_MANIFEST_SHA256) throw new Error("prepared dataset identity changed; review and version the transformation");
  await mkdir(out, { mode: 0o700 });
  for (const [index, file] of CLINC.files.entries()) await writeFile(join(out, file.stored), files[index]!, { flag: "wx", mode: 0o600 });
  for (const split of ["train", "validation", "test"] as const) await writeFile(join(out, `${split}.json`), encode(data.splits[split]), { flag: "wx", mode: 0o600 });
  await writeFile(join(out, "manifest.json"), encode(data.manifest), { flag: "wx", mode: 0o600 });
  return { dataset: CLINC.id, manifestDigest: sha256(encode(data.manifest)), partitions: data.manifest.partitions, quarantinedGroups: data.quarantined.length, license: CLINC.license };
}
export async function verifyDataset(directory: string) {
  let upstream: Uint8Array | undefined;
  for (const file of CLINC.files) { const bytes = await boundedFile(join(directory, file.stored), file.bytes); checkBytes(file, bytes); if (file.stored === "upstream.json") upstream = bytes; }
  const data = materialize(upstream!);
  if (!(await boundedFile(join(directory, "manifest.json"), 200000)).equals(Buffer.from(encode(data.manifest)))) throw new Error("dataset manifest differs from pinned sources");
  for (const split of ["train", "validation", "test"] as const) {
    if (!(await boundedFile(join(directory, `${split}.json`), 10000000)).equals(Buffer.from(encode(data.splits[split])))) throw new Error(`dataset partition differs: ${split}`);
  }
  return { verified: true, dataset: CLINC.id, manifestDigest: sha256(encode(data.manifest)), partitions: data.manifest.partitions };
}
export async function loadDevelopment(directory: string): Promise<{ train: Row[]; validation: Row[]; manifestDigest: string }> {
  const manifestBytes = await boundedFile(join(directory, "manifest.json"), 200000);
  if (sha256(manifestBytes) !== CLINC_MANIFEST_SHA256) throw new Error("prepared manifest digest does not match the pinned dataset");
  const raw = JSON.parse(manifestBytes.toString("utf8")) as unknown;
  const manifest = object(raw, ["contract", "source", "transform", "rawCounts", "partitions", "quarantined", "limits"], "manifest");
  if (manifest.contract !== "algal.dataset.clinc150.v1" || encode(manifest.source) !== encode(CLINC)) throw new Error("unsupported dataset identity");
  const partitions = object(manifest.partitions, ["train", "validation", "test"], "partitions");
  const read = async (split: "train" | "validation"): Promise<Row[]> => {
    const record = object(partitions[split], ["file", "rows", "sha256"], "partition");
    if (record.file !== `${split}.json`) throw new Error("invalid partition path");
    const bytes = await boundedFile(join(directory, `${split}.json`), 10000000);
    if (sha256(bytes) !== record.sha256) throw new Error("development partition digest mismatch");
    const rows = JSON.parse(bytes.toString("utf8")) as unknown;
    if (!Array.isArray(rows) || rows.length !== record.rows || rows.length < 1 || rows.length > 15100) throw new Error("invalid partition rows");
    return rows.map(value => {
      const row = object(value, ["id", "group", "split", "text", "label"], "prepared row");
      const message = text(row.text, 4096, "text"), label = text(row.label, 100, "label"), id = text(row.id, 100, "id");
      if (row.split !== split || row.group !== sha256(normalized(message)) || !/^[a-z][a-z0-9_]*$/.test(label)) throw new Error("invalid prepared row");
      return { id, group: row.group as string, split, text: message, label };
    });
  };
  return { train: await read("train"), validation: await read("validation"), manifestDigest: sha256(manifestBytes) };
}
export async function foundationSourceHash(): Promise<string> {
  const files = ["datasets.ts", "retrieval.ts"];
  return sha256(encode({ files: await Promise.all(files.map(async file => [file, sha256(await readFile(new URL(file, import.meta.url)))])), bun: Bun.version }));
}
