import { expect, test } from "bun:test";
import { CORPUS, parseCorpus, score, taskInput } from "./corpus";

test("public corpus is source-disjoint and task model never receives labels or split metadata", () => {
  const corpus = parseCorpus(CORPUS);
  expect(corpus.length).toBe(28);
  for (const row of corpus) expect(taskInput(row)).toEqual({ message: row.message });
  expect(corpus.filter(row => row.split === "holdout").length).toBe(12);
});

test("source reuse across partitions, duplicate text and unknown fields fail before execution", () => {
  const copy = CORPUS.map(row => ({ ...row }));
  copy[8]!.sourceId = copy[0]!.sourceId;
  expect(() => parseCorpus(copy)).toThrow("source crosses");
  expect(() => parseCorpus([...CORPUS, { ...CORPUS[0], id: "duplicate" }])).toThrow("duplicate message");
  expect(() => parseCorpus(CORPUS.map((row, i) => i === 0 ? { ...row, secret: "hidden" } : row))).toThrow("unknown fields");
});

test("invalid output counts against total accuracy and is separate from valid-answer quality", () => {
  expect(score([
    { caseId: "a", expected: "respond", output: "respond", completed: true },
    { caseId: "b", expected: "silent", output: "respond", completed: true },
    { caseId: "c", expected: "silent", output: { label: "silent" }, completed: true },
    { caseId: "d", expected: "silent", output: "silent", completed: false },
  ])).toEqual({ cases: 4, valid: 2, invalid: 2, correct: 1, accuracy: 0.25, accuracyGivenValid: 0.5, falseResponses: 1 });
  expect(score([{ caseId: "a", expected: "silent", output: null, completed: false }]).accuracyGivenValid).toBeNull();
});

test("split tags are exact strings, never coerced from arrays", () => {
  expect(() => parseCorpus(CORPUS.map((row, i) => i === 0 ? { ...row, split: ["train"] } : row))).toThrow("invalid split");
});
