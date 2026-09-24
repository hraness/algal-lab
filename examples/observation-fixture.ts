import type { Executor } from "@hraness/algal";
import { readJsonFile } from "../src/artifacts";
import { json, object } from "../src/contracts";
import { observationFixtureInstrument } from "../src/instruments/fixture";
import { completeObservationAttempt, createObservationStudy, evaluateObservationStudy, freezeObservationStudy, registerObservationAttempt, verifyObservationStudy } from "../src/instruments/observation";

const directory = Bun.argv[2];
if (!directory || Bun.argv.length !== 3) throw new Error("usage: bun examples/observation-fixture.ts <new-output-directory>");
const fixture = object(await readJsonFile(new URL("./observation-fixture.json", import.meta.url).pathname), ["protocol", "discoveryInput", "evaluationInput", "proposal"], "fixture");
const executor: Executor = { id: "algal-lab:scripted-observation.v1", capabilities: { effects: ["agent"] }, retryable: false, execute: async () => json(fixture.proposal) };
await createObservationStudy(fixture.protocol, directory, observationFixtureInstrument);
await registerObservationAttempt(directory, observationFixtureInstrument, { attemptId: "first", input: fixture.discoveryInput, context: { baseline: "fixed arithmetic proposal" }, executor });
await completeObservationAttempt(directory, observationFixtureInstrument, "first");
await freezeObservationStudy(directory, observationFixtureInstrument, ["first"]);
await evaluateObservationStudy(directory, observationFixtureInstrument, fixture.evaluationInput);
console.log(JSON.stringify(await verifyObservationStudy(directory, observationFixtureInstrument, { recompute: true })));
