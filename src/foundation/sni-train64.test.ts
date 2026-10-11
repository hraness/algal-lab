import { createHash } from "node:crypto";
import { expect, test } from "bun:test";
import { extractTrainMetadata, freezeTrain64, TRAIN64 } from "./sni-train64";
import type { TaskRef } from "./sni-intake";

const task = "task001_quoref_question_generation";
const raw = {
  Source: ["Quoref"], Categories: ["Question Generation"], "Instance License": ["CC BY 4.0"],
  Instances: [{ input: "PRIVATE TRAIN EXAMPLE", output: ["PRIVATE TRAIN ANSWER"] }],
  "Positive Examples": [{ input: "PRIVATE TRAIN DEMO", output: "PRIVATE TRAIN LABEL" }],
};
const bytes = Buffer.from(JSON.stringify(raw));
const blobOid = createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex");
const ref: TaskRef = { task, split: "train", blobOid };

test("an OID-bound train sidecar exposes only the three metadata fields", () => {
  const sidecar = extractTrainMetadata(ref, bytes);
  expect(sidecar).toEqual({ blobOid, task, Source: ["Quoref"], Categories: ["Question Generation"], "Instance License": ["CC BY 4.0"] });
  const serialized = JSON.stringify(sidecar);
  expect(serialized).not.toContain("PRIVATE");
  expect(serialized).not.toContain("Instances");
  expect(() => extractTrainMetadata({ ...ref, split: "test" }, bytes)).toThrow("train");
  expect(() => extractTrainMetadata({ ...ref, blobOid: "0".repeat(40) }, bytes)).toThrow("OID");
  expect(() => extractTrainMetadata(ref, Buffer.alloc(TRAIN64.maxBlobBytes + 1))).toThrow("large");
});

test("invalid metadata, even with valid Git identity, cannot produce a sidecar", () => {
  const bad = Buffer.from(JSON.stringify({ ...raw, "Instance License": [" "] }));
  const badRef = { ...ref, blobOid: createHash("sha1").update(`blob ${bad.length}\0`).update(bad).digest("hex") };
  expect(() => extractTrainMetadata(badRef, bad)).toThrow("Instance License");
});

test("the sample cannot be selected from a substituted index", () => {
  expect(() => freezeTrain64(Buffer.from("train\t" + task + "\t" + blobOid + "\n"))).toThrow("index SHA-256");
});
