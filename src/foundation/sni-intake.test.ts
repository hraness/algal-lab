import { expect, test } from "bun:test";
import { auditMetadata, parseTaskMetadata, pinTaskIndex, SNI, sourceKey, type TaskRef } from "./sni-intake";
import { indexUrls } from "../../scripts/sni-intake";

const oid = "a".repeat(40);
const refs: TaskRef[] = [
  ["task001_dev_wsc", "train"], ["task002_test_wsc", "test"],
  ["task003_dev_squad", "train"], ["task004_test_squad", "test"],
  ["task005_dev_qasc", "train"], ["task006_test_qasc", "test"],
  ["task007_dev_alpha", "train"], ["task008_test_beta", "test"],
  ["task009_excluded_bridge", "excluded"],
  ["task010_dev_unique", "train"], ["task011_test_unknown_license", "test"],
].map(([task, split]) => ({ task: task!, split: split as TaskRef["split"], blobOid: oid }));
const sources = ["wsc; enhanced_wsc", "wscfixed", "squad_1.1", "squad_2.0", "eqasc-perturbed", "qasc", "source_alpha", "source_beta", "source_alpha; source_beta", "unique_source", "new_source"];
const metadata = refs.map((ref, i) => ({ task: ref.task, Source: [sources[i]!], Categories: ["Classification"], "Instance License": [i === 10 ? "unknown" : "CC BY 4.0"] }));

test("metadata-only boundary rejects instances, example outputs, missing fields, and loose types", () => {
  const row = metadata[0]!;
  expect(parseTaskMetadata(row).Source).toEqual(["wsc; enhanced_wsc"]);
  for (const key of ["Instances", "Output", "Positive Examples", "secret"]) {
    expect(() => parseTaskMetadata({ ...row, [key]: [{ input: "holdout" }] })).toThrow("metadata-only");
  }
  expect(() => parseTaskMetadata({ ...row, Source: [] })).toThrow("Source");
  expect(() => parseTaskMetadata({ ...row, "Instance License": "CC BY 4.0" })).toThrow("Instance License");
  expect(() => parseTaskMetadata({ ...row, Categories: ["valid", 1] })).toThrow("Categories");
  expect(() => parseTaskMetadata({ task: row.task, Source: row.Source, Categories: row.Categories })).toThrow("metadata-only");
});

test("derived WSC, SQuAD, QASC aliases and an excluded bridge quarantine entire cross-split groups", () => {
  const result = auditMetadata(refs, metadata);
  expect(result.collisions).toEqual([
    ["task001_dev_wsc", "task002_test_wsc"],
    ["task003_dev_squad", "task004_test_squad"],
    ["task005_dev_qasc", "task006_test_qasc"],
    ["task007_dev_alpha", "task008_test_beta", "task009_excluded_bridge"],
  ]);
  expect(result.unknownLicense).toEqual(["task011_test_unknown_license"]);
  expect(result.eligible).toEqual({ train: 1, test: 0 });
  expect(result.disposition).toBe("review-required");
  expect(sourceKey("superglue_wsc")).toBe("family:wsc");
  expect(sourceKey("squad_1.1")).toBe(sourceKey("squad_2.0"));
});

test("no incomplete or inconsistent metadata set can establish separation", () => {
  expect(() => auditMetadata(refs, metadata.slice(1))).toThrow("incomplete");
  expect(() => auditMetadata(refs, [...metadata.slice(0, -1), metadata[0]])).toThrow("duplicate");
  expect(() => auditMetadata(refs, metadata.map((row, i) => i === 0 ? { ...row, task: "task999_not_in_index" } : row))).toThrow("unindexed");
  expect(() => auditMetadata(refs, metadata.map((row, i) => i === 0 ? { ...row, Source: [" "] } : row))).toThrow("Source");
});

test("pinned index refuses incomplete or substituted sources and has no test-task URL", () => {
  expect(SNI.splits.train.count).toBe(756);
  expect(Object.values(indexUrls).every(url => !url.includes("/tasks/") && url.startsWith("https://"))).toBe(true);
  const badFiles = { train: new Uint8Array(), test: new Uint8Array(), excluded: new Uint8Array() };
  expect(() => pinTaskIndex({ sha: SNI.tree, truncated: true, tree: [] }, badFiles)).toThrow("completeness");
  expect(() => pinTaskIndex({ sha: "0".repeat(40), truncated: false, tree: [] }, badFiles)).toThrow("identity");
  expect(() => pinTaskIndex({ sha: SNI.tree, truncated: false, tree: [] }, badFiles)).toThrow("split digest");
});
