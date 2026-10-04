import { expect, test } from "bun:test";
import agenda from "../../examples/research-agenda.json";
import { loadAgenda, parseAgenda } from "./agenda";
import { main } from "../../scripts/discovery";

test("the practical-CS agenda has runnable references and distinct research questions", async () => {
  const result = await loadAgenda();
  expect(result.tracks.length).toBeGreaterThanOrEqual(3);
  expect(new Set(result.tracks.map(track => track.id)).size).toBe(result.tracks.length);
  expect(await main(["agenda"])).toEqual(result);
  expect(await main(["agenda", result.tracks[0]!.id])).toEqual(result.tracks[0]);
  await expect(main(["agenda", "missing"])).rejects.toThrow("unknown research track");
  await expect(main(["agenda", result.tracks[0]!.id, "--live"])).rejects.toThrow("unexpected");
});

test("agenda admission requires practical tests, primary-source work, and stopping rules", () => {
  expect(() => parseAgenda({ ...agenda, run: "arbitrary shell" })).toThrow("unknown field");
  for (const field of ["application", "contribution", "priorArt", "nextExperiment", "stop"] as const) {
    const copy = structuredClone(agenda);
    copy.tracks[0]![field] = "";
    expect(() => parseAgenda(copy)).toThrow();
  }
  const duplicate = structuredClone(agenda);
  duplicate.tracks.push(duplicate.tracks[0]!);
  expect(() => parseAgenda(duplicate)).toThrow("duplicate");
  const path = structuredClone(agenda);
  path.tracks[0]!.references = ["../private.json"];
  expect(() => parseAgenda(path)).toThrow("repository-relative");
});

test("doctor reports offline setup without activating a provider", async () => {
  const result = await main(["doctor"]) as { ready: boolean; bun: string; liveProviders: string };
  expect(result.ready).toBe(true);
  expect(result.bun).toBe(Bun.version);
  expect(result.liveProviders).toBe("not checked or activated");
  await expect(main(["doctor", "--live"])).rejects.toThrow("unexpected");
});
