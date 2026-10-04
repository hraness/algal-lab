import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { boundedFile, encode, foundationSourceHash, loadDevelopment, normalized, requireNewDirectory, sha256, type Row } from "./datasets";

const tokens = (value: string): string[] => normalized(value).split(" ").filter(Boolean);
const compare = (a: string, b: string): number => a < b ? -1 : a > b ? 1 : 0;
const order = (rows: Row[]): Row[] => [...rows].sort((a, b) => compare(sha256(`algal-clinc-dev-v1:${a.id}`), sha256(`algal-clinc-dev-v1:${b.id}`)));
function sample(rows: Row[], limit: number): Row[] {
  const counts = new Map<string, number>();
  return order(rows).filter(row => { const count = counts.get(row.label) ?? 0; counts.set(row.label, count + 1); return count < limit; });
}
export function developmentBaseline(train: Row[], validation: Row[]) {
  if (!train.length || train.length > 15100 || !validation.length || validation.length > 3100) throw new Error("baseline dataset size exceeds bounds");
  if (train.some(row => row.split !== "train") || validation.some(row => row.split !== "validation")) throw new Error("baseline cannot consume another split");
  const rows = [...train, ...validation];
  if (rows.some(row => row.group !== sha256(normalized(row.text)))) throw new Error("row group does not match its normalized text");
  if (new Set(rows.map(row => row.group)).size !== rows.length || new Set(rows.map(row => row.id)).size !== rows.length) throw new Error("duplicate source group or row across development data");
  const training = sample(train, 8), queries = sample(validation, 2);
  const labels = [...new Set(training.map(row => row.label))].sort();
  if (labels.length > 151 || queries.some(row => !labels.includes(row.label))) throw new Error("validation labels lack training support");
  const counts = new Map(labels.map(label => [label, training.filter(row => row.label === label).length]));
  const majority = [...labels].sort((a, b) => counts.get(b)! - counts.get(a)! || compare(a, b))[0]!;
  const df = new Map<string, number>();
  for (const row of training) for (const token of new Set(tokens(row.text))) df.set(token, (df.get(token) ?? 0) + 1);
  const idf = new Map([...df].map(([token, count]) => [token, Math.log((training.length + 1) / (count + 1)) + 1]));
  const vector = (message: string): Map<string, number> => {
    const result = new Map<string, number>();
    for (const token of tokens(message)) if (idf.has(token)) result.set(token, (result.get(token) ?? 0) + idf.get(token)!);
    const norm = Math.sqrt([...result.values()].reduce((n, value) => n + value * value, 0));
    if (norm) for (const [token, value] of result) result.set(token, value / norm);
    return result;
  };
  const vectors = training.map(row => vector(row.text));
  const predictions = queries.map(query => {
    const target = vector(query.text);
    let best = -1, similarity = 0;
    for (let index = 0; index < training.length; index++) {
      let score = 0; for (const [token, weight] of target) score += weight * (vectors[index]!.get(token) ?? 0);
      if (score > similarity) { similarity = score; best = index; }
    }
    const randomIndex = Number.parseInt(sha256(`random-label-v1:${query.id}`).slice(0, 8), 16) % labels.length;
    return { id: query.id, expected: query.label, majority, random: labels[randomIndex]!, nearest: best < 0 ? majority : training[best]!.label, neighbor: best < 0 ? null : training[best]!.id };
  });
  const metric = (arm: "majority" | "random" | "nearest") => {
    const correct = predictions.filter(row => row[arm] === row.expected).length;
    return { cases: predictions.length, correct, accuracy: correct / predictions.length };
  };
  return { contract: "algal.baseline.clinc150.v1", scope: "development-only", modelCalls: 0, protocol: { seed: "algal-clinc-dev-v1", trainPerLabel: 8, validationPerLabel: 2, fitting: "training-only TF-IDF cosine 1-nearest-neighbor; zero similarity falls back to majority" }, trainingRows: training.length, validationRows: queries.length, labels,
    trainingIds: training.map(row => row.id), vocabulary: [...idf.keys()].sort(), arms: { majority: metric("majority"), random: metric("random"), nearest: metric("nearest") }, predictions,
    limits: "A cheap development diagnostic, not a new retrieval method, source-disjoint generalization, out-of-scope detector qualification, Textbutler policy benchmark, or model result. No test rows are read or scored. Do not treat validation reuse as confirmation." };
}
export async function baselineReport(directory: string) {
  const data = await loadDevelopment(directory);
  return { ...developmentBaseline(data.train, data.validation), datasetDigest: data.manifestDigest, sourceHash: await foundationSourceHash(), bun: Bun.version };
}
export async function runBaseline(directory: string, out: string) {
  await requireNewDirectory(out);
  const report = await baselineReport(directory);
  await mkdir(out, { mode: 0o700 });
  await writeFile(join(out, "baseline.json"), encode(report), { flag: "wx", mode: 0o600 });
  return { report: join(out, "baseline.json"), digest: sha256(encode(report)), scope: report.scope, trainingRows: report.trainingRows, validationRows: report.validationRows, arms: report.arms };
}
export async function verifyBaseline(directory: string, out: string) {
  const report = await baselineReport(directory), expected = Buffer.from(encode(report));
  if (!(await boundedFile(join(out, "baseline.json"), 1000000)).equals(expected)) throw new Error("baseline reproduction mismatch");
  return { verified: true, digest: sha256(expected), scope: report.scope };
}
