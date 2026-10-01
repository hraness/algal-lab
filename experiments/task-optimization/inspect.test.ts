import { expect, test } from "bun:test";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { FileStore } from "@hraness/algal";
import { inspectStudyArm } from "./inspect";
import { CONTEXT_ARM, runArm, scriptedExecutor } from "./study";

test("offline study reproduction rejects edited scores and frozen programs", async () => {
  const directory = await mkdtemp(join(tmpdir(), "algal-task-replay-"));
  try {
    const result = await runArm("fixed", 11, new FileStore(join(directory, "11-fixed", "store")), scriptedExecutor());
    const path = join(directory, "11-fixed.json");
    await writeFile(path, JSON.stringify(result));
    expect((await inspectStudyArm(directory, 11, "fixed")).ok).toBe(true);
    await writeFile(path, JSON.stringify({ ...result, metrics: { ...result.metrics, correct: result.metrics.correct - 1 } }));
    await expect(inspectStudyArm(directory, 11, "fixed")).rejects.toThrow("does not reproduce");
    await writeFile(path, JSON.stringify({ ...result, frozenTask: { ...result.frozenTask, instructions: "edited after evaluation" } }));
    await expect(inspectStudyArm(directory, 11, "fixed")).rejects.toThrow("does not reproduce");
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test("exact-context arm reproduces its model selection and read receipt offline", async () => {
  const directory = await mkdtemp(join(tmpdir(), "algal-context-replay-"));
  try {
    const store = new FileStore(join(directory, `11-${CONTEXT_ARM}`, "store"));
    const result = await runArm(CONTEXT_ARM, 11, store, scriptedExecutor());
    const path = join(directory, `11-${CONTEXT_ARM}.json`);
    await writeFile(path, JSON.stringify(result));
    expect((await inspectStudyArm(directory, 11, CONTEXT_ARM)).ok).toBe(true);
    await writeFile(path, JSON.stringify({ ...result, calls: result.calls - 1 }));
    await expect(inspectStudyArm(directory, 11, CONTEXT_ARM)).rejects.toThrow("does not reproduce");
  } finally { await rm(directory, { recursive: true, force: true }); }
}, 20_000);
