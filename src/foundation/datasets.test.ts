import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { CLINC, deriveClinc, encode, fetchPinned, loadDevelopment, prepareClinc, sha256 } from "./datasets";
import { baselineReport, developmentBaseline } from "./retrieval";
import { main } from "../../scripts/foundation";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map(root => rm(root, { recursive: true, force: true }))); });
const raw = () => ({ train: [["apple red", "fruit"], ["plane flight", "travel"]], val: [["red apple please", "fruit"], ["flight plane please", "travel"]], test: [["test-only-private-text", "fruit"]], oos_train: [["cloud unknown", "oos"]], oos_val: [["unknown cloud please", "oos"]], oos_test: [["test-only-oos", "oos"]] });

test("dataset transform preserves upstream partitions and quarantines normalized duplicates", () => {
  const fixture = raw(); fixture.val.push(["APPLE, RED!", "fruit"]);
  const result = deriveClinc(fixture);
  expect(result.quarantined).toHaveLength(1);
  expect(result.splits.train.some(row => row.text === "apple red")).toBe(false);
  expect(result.splits.validation.some(row => row.text === "APPLE, RED!")).toBe(false);
  expect(result.splits.test).toHaveLength(2);
  expect(JSON.stringify(result.splits.train)).not.toContain("test-only");
  expect(() => deriveClinc({ ...fixture, command: "no" })).toThrow("unknown field");
  expect(() => deriveClinc({ ...raw(), train: [["bad", "oos"]] })).toThrow("label");
});

test("development baselines cannot consume test rows or fit features to validation", () => {
  const data = deriveClinc(raw()).splits;
  const result = developmentBaseline(data.train, data.validation);
  expect(result.scope).toBe("development-only");
  expect(result.modelCalls).toBe(0);
  expect(result.arms.nearest.accuracy).toBe(1);
  expect(result.arms.majority.accuracy).toBeLessThan(1);
  expect(result.trainingRows).toBe(3);
  expect(result.vocabulary).not.toContain("please");
  expect(JSON.stringify(result)).not.toContain("test-only");
  expect(() => developmentBaseline(data.train, data.test)).toThrow("split");
  expect(developmentBaseline(data.train, data.validation)).toEqual(result);
});

test("downloads reject redirects, oversized bytes, and altered source identities", async () => {
  const file = CLINC.files[0]!;
  await expect(fetchPinned(file, async () => new Response("", { status: 302 }))).rejects.toThrow("HTTP");
  await expect(fetchPinned(file, async (_url, init) => {
    expect(init?.redirect).toBe("error");
    expect(init?.headers).toBeUndefined();
    return new Response("bad");
  })).rejects.toThrow("identity");
  await expect(fetchPinned(file, async () => new Response("", { headers: { "content-length": String(file.bytes + 1) } }))).rejects.toThrow("size");
});

test("a locally self-consistent replacement cannot impersonate the pinned dataset", async () => {
  const root = await mkdtemp(join(tmpdir(), "algal-foundation-files-")); roots.push(root);
  const data = deriveClinc(raw());
  const partitions = Object.fromEntries((["train", "validation", "test"] as const).map(split => [split, { file: `${split}.json`, rows: data.splits[split].length, sha256: sha256(encode(data.splits[split])) }]));
  await writeFile(join(root, "manifest.json"), encode({ contract: "algal.dataset.clinc150.v1", source: CLINC, transform: "unit-test fixture only", rawCounts: data.rawCounts, partitions, quarantined: [], limits: "fixture" }));
  for (const split of ["train", "validation"] as const) await writeFile(join(root, `${split}.json`), encode(data.splits[split]));
  await expect(loadDevelopment(root)).rejects.toThrow("prepared manifest digest");
  await expect(baselineReport(root)).rejects.toThrow("prepared manifest digest");
});

test("CLI rejects unknown options before downloads or subprocess builds", async () => {
  await expect(main(["fetch", "other", "--out", "/unused"])).rejects.toThrow("unknown dataset");
  await expect(main(["fetch", "clinc150", "--url", "https://example.invalid"])).rejects.toThrow("invalid");
  await expect(main(["import", "clinc150", "--out", "/unused"])).rejects.toThrow("--source");
  await expect(main(["setup-proofs", "--out", "/unused", "--jobs", "0"])).rejects.toThrow("jobs");
  await expect(main(["verify-dataset", "/unused", "--live"])).rejects.toThrow("unexpected");
});

test("preparation never overwrites a directory or fetches when it already exists", async () => {
  const out = await mkdtemp(join(tmpdir(), "algal-foundation-")); roots.push(out);
  let calls = 0;
  await expect(prepareClinc(out, { fetch: async () => { calls++; throw Error("unexpected fetch"); } })).rejects.toThrow("exists");
  expect(calls).toBe(0);
});
