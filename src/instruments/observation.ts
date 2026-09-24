import { randomUUID } from "node:crypto";
import { mkdir, readdir, readFile, unlink, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { builtinRegistry, canonicalize, manifestToJson, MemoryStore, parseOrganismManifest, parseRunReceipt, runOrganism, verifyReceipt, type Executor, type JsonValue, type RunReceipt, type ToolRegistry } from "@hraness/algal";
import { ArtifactStore, digest, digestString, readJsonFile } from "../artifacts";
import { equal, freeze, integer, json, object } from "../contracts";
import { boundedJson, identifier, parseObservation, parseObservationInput, parseObservationProposal, parseObservationProtocol, type Digest, type Observation, type ObservationInput, type ObservationInstrument, type ObservationProposal, type ObservationProtocol } from "./contracts";
import { observationIdentity, type ObservationIdentity } from "./sources";

const proposalManifest = parseOrganismManifest({
  contract: "algal.organism.v1", key: "organism:algal-lab-observation-proposal-v1", name: "Registered observation proposal",
  budgets: { maxSteps: 4, maxAgentCalls: 1, maxWork: 300000 },
  interface: { inputs: { context: { cell: "input", port: "context" } }, outputs: { proposal: { cell: "propose", port: "out" } } },
  cells: [
    { id: "input", kind: "input", outputs: { context: "json" } },
    { id: "propose", kind: "agent", inputs: { context: "json" }, view: { inputs: ["context"] },
      prompt: "Register one falsifiable prediction BEFORE measurement. Return JSON with design, hypothesis, prediction, rationale, parents. design and prediction are bounded JSON owned by the domain; hypothesis and rationale are claims, not evidence. parents may only name visible prior observation references. Do not request hidden evaluation inputs, tools, code execution, or changes to the protocol.",
      output: { kind: "json", schema: { type: "object" } }, budget: { maxContextBytes: 196608, maxOutputBytes: 8192, maxEffectMs: 120000 } },
  ], edges: [{ from: { cell: "input", port: "context" }, to: { cell: "propose", port: "context" } }],
});
const measurementManifest = parseOrganismManifest({
  contract: "algal.organism.v1", key: "organism:algal-lab-observation-measurement-v1", name: "Joined observation measurement",
  budgets: { maxSteps: 4, maxAgentCalls: 0, maxWork: 500000 },
  interface: { inputs: { request: { cell: "input", port: "request" } }, outputs: { observation: { cell: "measure", port: "observation" } } },
  cells: [{ id: "input", kind: "input", outputs: { request: "json" } }, { id: "measure", kind: "tool", tool: "lab.observation.measure.v1", budget: { maxEffectMs: 30000 } }],
  edges: [{ from: { cell: "input", port: "request" }, to: { cell: "measure", port: "request" } }],
});

type Study = { contract: "algal.lab.observation-archive.v1"; protocol: ObservationProtocol; identity: ObservationIdentity };
type Intent = { contract: "algal.lab.observation-intent.v1"; attemptId: string; sequence: number; input: ObservationInput; context: JsonValue; parents: Digest[] };
export type RegisteredObservationAttempt = { contract: "algal.lab.observation-registration.v1"; intentDigest: Digest; receipt: RunReceipt; proposal: ObservationProposal | null; rejection: string | null };
export type JoinedObservation = { contract: "algal.lab.observation-join.v1"; registrationDigest: Digest; inputDigest: Digest; instrumentDigest: Digest; receipt: RunReceipt; observation: Observation | null; mode: "computed" | "attached" };
type Snapshot = { attemptId: string; intent: Digest; registration: Digest; observation: Digest | null };
type FrozenSelection = { contract: "algal.lab.observation-freeze.v1"; studyDigest: Digest; attempts: Snapshot[]; selected: string[] };
type Loaded = { study: Study; store: ArtifactStore };

/** Immutable pointers are intentionally tiny. Partial writes fail closed; content
 * is always checked again through ArtifactStore before any dependent operation.
 */
async function pointer(path: string, value: Digest): Promise<void> { await writeFile(path, canonicalize({ artifact: value }) + "\n", { flag: "wx", mode: 0o600 }); }
async function ref(path: string): Promise<Digest> { return digestString(object(await readJsonFile(path), ["artifact"], "artifact pointer").artifact); }
async function maybeRef(path: string): Promise<Digest | null> {
  try { return await ref(path); } catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") return null; throw error; }
}
/** One host owns a study mutation at a time. A dead owner's lock is not silently
 * removed: recoverObservationStudyLock is an explicit, fail-closed recovery seam.
 */
async function locked<T>(directory: string, operation: () => Promise<T>): Promise<T> {
  const path = join(directory, ".observation-lock");
  const token = canonicalize({ pid: process.pid, nonce: randomUUID() });
  try { await writeFile(path, token, { flag: "wx", mode: 0o600 }); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === "EEXIST") throw new Error("study has an active or uncertain mutation owner; inspect/recover its lock before resuming"); throw error; }
  try { return await operation(); }
  finally { if (await readFile(path, "utf8") === token) await unlink(path); }
}
/** Call only with one recovery owner. The dead PID and exact lock contents must
 * still agree; a live process, malformed lock, or reused PID blocks recovery.
 * This removes no scientific evidence and does not retry a proposal.
 */
export async function recoverObservationStudyLock(directory: string): Promise<void> {
  const path = join(directory, ".observation-lock");
  const contents = await readFile(path, "utf8");
  const lock = object(JSON.parse(contents), ["pid", "nonce"], "mutation owner");
  if (!Number.isInteger(lock.pid) || (lock.pid as number) <= 0 || typeof lock.nonce !== "string") throw new Error("malformed mutation owner; inspect manually");
  try { process.kill(lock.pid as number, 0); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ESRCH") throw error;
    if (await readFile(path, "utf8") !== contents) throw new Error("mutation owner changed during recovery");
    await unlink(path); return;
  }
  throw new Error("mutation owner is still alive; recovery refused");
}
async function load(directory: string, instrument: ObservationInstrument): Promise<Loaded> {
  const envelope = object(await readJsonFile(join(directory, "observation-study.json")), ["study", "digest"], "observation archive");
  if (digest(envelope.study) !== digestString(envelope.digest)) throw new Error("study digest mismatch");
  const raw = object(envelope.study, ["contract", "protocol", "identity"], "observation study");
  if (raw.contract !== "algal.lab.observation-archive.v1") throw new Error("unsupported observation archive");
  const protocol = parseObservationProtocol(raw.protocol);
  const identity = await observationIdentity(instrument);
  if (!equal(raw.identity, identity)) throw new Error("source or instrument identity changed; verify with the recorded source version and pinned environment");
  return { study: { contract: raw.contract, protocol, identity }, store: new ArtifactStore(directory) };
}
function inputFor(instrument: ObservationInstrument, value: unknown): ObservationInput {
  const input = parseObservationInput(instrument.parseInput(parseObservationInput(value)));
  if (input.contract !== instrument.inputContract) throw new Error("instrument input contract mismatch");
  return freeze(input);
}
function proposalContext(study: Study, intent: Intent): JsonValue {
  return json({ protocol: study.protocol, instrument: study.identity.instrument, input: intent.input, context: intent.context, parents: intent.parents });
}
function admittedExecutor(executor: Executor): Executor {
  return { ...executor, retryable: false,
    execute: async (request, signal) => boundedJson(await executor.execute(request, signal), 8192),
    ...(executor.executeEffect ? { executeEffect: async (request, signal) => {
      const result = await executor.executeEffect!(request, signal);
      return { ...result, output: boundedJson(result.output, 8192) };
    } } : {}),
  };
}
function registrationResult(receipt: RunReceipt, parents: Digest[]): Pick<RegisteredObservationAttempt, "proposal" | "rejection"> {
  if (receipt.outcome !== "complete") return { proposal: null, rejection: "proposal execution did not complete; inspect retained receipt" };
  try { return { proposal: parseObservationProposal(receipt.cells.propose?.outputs?.out, parents), rejection: null }; }
  catch { return { proposal: null, rejection: "proposal failed the registered bounded contract" }; }
}
async function ids(directory: string, maximum: number): Promise<string[]> {
  const entries = await readdir(join(directory, "attempts"), { withFileTypes: true });
  if (entries.length > maximum || entries.some((entry) => !entry.isDirectory() || entry.isSymbolicLink())) throw new Error("attempt directory violates protocol");
  return entries.map((entry) => identifier(entry.name)).sort();
}
async function ensureOpen(directory: string): Promise<void> { if (await maybeRef(join(directory, "freeze.json"))) throw new Error("selection is frozen; no further proposals, measurements, or selection changes are admitted"); }
async function loadIntent(store: ArtifactStore, id: Digest): Promise<Intent> {
  const raw = object(await store.get(id), ["contract", "attemptId", "sequence", "input", "context", "parents"], "intent");
  if (raw.contract !== "algal.lab.observation-intent.v1" || !Array.isArray(raw.parents) || raw.parents.length > 64) throw new Error("invalid attempt intent");
  return { contract: raw.contract, attemptId: identifier(raw.attemptId), sequence: integer(raw.sequence, 0, 63, "attempt sequence"), input: parseObservationInput(raw.input), context: boundedJson(raw.context, 32768), parents: raw.parents.map(digestString) };
}
async function loadRegistration(store: ArtifactStore, id: Digest): Promise<RegisteredObservationAttempt> {
  const raw = object(await store.get(id), ["contract", "intentDigest", "receipt", "proposal", "rejection"], "registration");
  if (raw.contract !== "algal.lab.observation-registration.v1") throw new Error("unsupported registration");
  const intentDigest = digestString(raw.intentDigest);
  const intent = await loadIntent(store, intentDigest);
  const receipt = parseRunReceipt(json(raw.receipt));
  const result = registrationResult(receipt, intent.parents);
  if (!equal(result, { proposal: raw.proposal, rejection: raw.rejection })) throw new Error("registration differs from proposal receipt");
  return { contract: raw.contract, intentDigest, receipt, ...result };
}
function measurementRequest(input: ObservationInput, proposal: ObservationProposal, attached: Observation | null): JsonValue { return json({ input, proposal, attached }); }
function measurementTools(instrument: ObservationInstrument, identity: ObservationIdentity, replay = false): ToolRegistry {
  return new Map([["lab.observation.measure.v1", {
    configurationDigest: identity.instrumentDigest,
    signature: { inputs: { request: { type: "json" } }, outputs: { observation: { type: "json" } }, effect: "read", cost: 100, maxOutputBytes: 65536 },
    tool: async (inputs) => {
      if (replay) throw new Error("receipt replay attempted fresh measurement");
      const request = object(inputs.request, ["input", "proposal", "attached"], "measurement request");
      const input = inputFor(instrument, request.input);
      const proposal = freeze(parseObservationProposal(request.proposal, ((request.proposal as ObservationProposal).parents ?? [])));
      const result = instrument.execution === "pure" ? await instrument.measure!(input, proposal) : request.attached;
      const observation = freeze(parseObservation(result));
      if (observation.contract !== instrument.outputContract) throw new Error("instrument output contract mismatch");
      await instrument.verify(input, proposal, observation);
      return { observation: json(observation) };
    },
  }]]);
}
async function measure(study: Study, instrument: ObservationInstrument, registrationDigest: Digest, proposal: ObservationProposal, input: ObservationInput, attached?: unknown): Promise<JoinedObservation> {
  if (instrument.execution === "pure" && attached !== undefined) throw new Error("pure instruments do not accept attached outcomes");
  const attachment = attached === undefined ? null : parseObservation(attached);
  const receipt = await runOrganism({ manifest: measurementManifest, args: { input: { request: measurementRequest(input, proposal, attachment) } }, fns: builtinRegistry(), store: new MemoryStore(), executors: [], tools: measurementTools(instrument, study.identity) });
  return { contract: "algal.lab.observation-join.v1", registrationDigest, inputDigest: digest(input), instrumentDigest: study.identity.instrumentDigest, receipt, observation: receipt.outcome === "complete" ? parseObservation(receipt.cells.measure?.outputs?.observation) : null, mode: instrument.execution === "pure" ? "computed" : "attached" };
}

export async function createObservationStudy(protocolValue: unknown, directory: string, instrument: ObservationInstrument): Promise<Study> {
  const protocol = parseObservationProtocol(protocolValue);
  const identity = await observationIdentity(instrument);
  const study: Study = { contract: "algal.lab.observation-archive.v1", protocol, identity };
  await mkdir(dirname(directory), { recursive: true });
  await mkdir(directory);
  await new ArtifactStore(directory).initialize();
  await mkdir(join(directory, "attempts"));
  await mkdir(join(directory, "evaluation"));
  await writeFile(join(directory, "observation-study.json"), canonicalize(json({ study, digest: digest(study) })) + "\n", { flag: "wx", mode: 0o600 });
  return freeze(study);
}

/** Registration is a one-shot operation, not a retry API. Existing intent without
 * registered.json is an ambiguous provider call; it must be retained and resolved
 * externally, never blindly dispatched again under this or a fresh attempt ID.
 */
export async function registerObservationAttempt(directory: string, instrument: ObservationInstrument, options: { attemptId: string; input: unknown; context: unknown; executor: Executor }): Promise<{ registrationDigest: Digest; registration: RegisteredObservationAttempt }> {
  return locked(directory, async () => {
    const { study, store } = await load(directory, instrument);
    await ensureOpen(directory);
    const attemptId = identifier(options.attemptId);
    const existing = await ids(directory, study.protocol.maxAttempts);
    if (existing.length >= study.protocol.maxAttempts) throw new Error("registered attempt budget exhausted");
    const parents: Digest[] = [];
    for (const id of existing) {
      if (!await maybeRef(join(directory, "attempts", id, "registered.json"))) throw new Error("ambiguous proposal intent requires reconciliation before any new proposal");
      const observation = await maybeRef(join(directory, "attempts", id, "observed.json"));
      if (observation) parents.push(observation);
    }
    const intent: Intent = { contract: "algal.lab.observation-intent.v1", attemptId, sequence: existing.length, input: inputFor(instrument, options.input), context: boundedJson(options.context, 32768), parents };
    const attemptDirectory = join(directory, "attempts", attemptId);
    await mkdir(attemptDirectory);
    const intentDigest = await store.put(intent);
    await pointer(join(attemptDirectory, "intent.json"), intentDigest);
    const receipt = await runOrganism({ manifest: proposalManifest, args: { input: { context: proposalContext(study, intent) } }, fns: builtinRegistry(), store: new MemoryStore(), executors: [admittedExecutor(options.executor)] });
    const registration: RegisteredObservationAttempt = { contract: "algal.lab.observation-registration.v1", intentDigest, receipt, ...registrationResult(receipt, parents) };
    const registrationDigest = await store.put(registration);
    await pointer(join(attemptDirectory, "registered.json"), registrationDigest);
    return freeze({ registrationDigest, registration });
  });
}

/** Resume only the measurement side of a retained registration. Completed joins
 * return unchanged. Attachment adapters accept collected bytes, never dispatch jobs.
 */
export async function completeObservationAttempt(directory: string, instrument: ObservationInstrument, attemptIdValue: string, attached?: unknown): Promise<{ observationDigest: Digest; observation: JoinedObservation }> {
  return locked(directory, async () => {
    const { study, store } = await load(directory, instrument);
    const attemptId = identifier(attemptIdValue);
    const path = join(directory, "attempts", attemptId);
    const registrationDigest = await maybeRef(join(path, "registered.json"));
    if (!registrationDigest) throw new Error("no durable registration; proposal call is absent or ambiguous and cannot be replayed");
    const registration = await loadRegistration(store, registrationDigest);
    if (!registration.proposal) throw new Error("rejected proposal has no pending measurement");
    const intent = await loadIntent(store, registration.intentDigest);
    if (intent.attemptId !== attemptId || registration.intentDigest !== await ref(join(path, "intent.json"))) throw new Error("attempt identity mismatch");
    const existing = await maybeRef(join(path, "observed.json"));
    if (existing) return freeze({ observationDigest: existing, observation: await verifyJoin(await store.get(existing), registrationDigest, registration.proposal, inputFor(instrument, intent.input), study, instrument, false) });
    await ensureOpen(directory);
    const observation = await measure(study, instrument, registrationDigest, registration.proposal, inputFor(instrument, intent.input), attached);
    const observationDigest = await store.put(observation);
    await pointer(join(path, "observed.json"), observationDigest);
    return freeze({ observationDigest, observation });
  });
}
async function snapshot(directory: string, study: Study, store: ArtifactStore): Promise<Snapshot[]> {
  const result: Snapshot[] = [];
  for (const attemptId of await ids(directory, study.protocol.maxAttempts)) {
    const path = join(directory, "attempts", attemptId);
    const registration = await maybeRef(join(path, "registered.json"));
    if (!registration) throw new Error("ambiguous proposal intent prevents freezing");
    const record = await loadRegistration(store, registration);
    const observation = await maybeRef(join(path, "observed.json"));
    if (record.proposal && !observation) throw new Error("pending measurement prevents freezing");
    if (!record.proposal && observation) throw new Error("rejected proposal has an observation");
    result.push({ attemptId, intent: await ref(join(path, "intent.json")), registration, observation });
  }
  return result;
}
export async function freezeObservationStudy(directory: string, instrument: ObservationInstrument, attemptIds: string[]): Promise<Digest> {
  return locked(directory, async () => {
    const { study, store } = await load(directory, instrument);
    await ensureOpen(directory);
    await verifyObservationStudy(directory, instrument);
    if (attemptIds.length > study.protocol.maxAttempts || new Set(attemptIds).size !== attemptIds.length) throw new Error("invalid frozen selection");
    const selected = attemptIds.map(identifier);
    const attempts = await snapshot(directory, study, store);
    for (const id of selected) {
      const entry = attempts.find((attempt) => attempt.attemptId === id);
      if (!entry?.observation || !(await store.get(entry.observation) as unknown as JoinedObservation).observation) throw new Error("selection must reference a successful completed observation");
    }
    const frozen: FrozenSelection = { contract: "algal.lab.observation-freeze.v1", studyDigest: digest(study), attempts, selected };
    const id = await store.put(frozen);
    await pointer(join(directory, "freeze.json"), id);
    return id;
  });
}
async function frozenSelection(directory: string, study: Study, store: ArtifactStore): Promise<FrozenSelection> {
  const raw = object(await store.get(await ref(join(directory, "freeze.json"))), ["contract", "studyDigest", "attempts", "selected"], "frozen selection");
  if (raw.contract !== "algal.lab.observation-freeze.v1" || raw.studyDigest !== digest(study) || !Array.isArray(raw.selected) || raw.selected.length > study.protocol.maxAttempts) throw new Error("invalid frozen selection");
  const attempts = await snapshot(directory, study, store);
  if (!equal(attempts, raw.attempts)) throw new Error("attempts changed after selection froze");
  const selected = raw.selected.map(identifier);
  if (new Set(selected).size !== selected.length || selected.some((id) => !attempts.some((a) => a.attemptId === id && a.observation))) throw new Error("invalid selected attempt");
  return { contract: raw.contract, studyDigest: digest(study), attempts, selected };
}

/** The caller supplies evaluator-only data after selection, checked against the
 * protocol's original commitment. This library is not a filesystem sandbox.
 */
export async function evaluateObservationStudy(directory: string, instrument: ObservationInstrument, evaluationInput: unknown, attachments: Record<string, unknown> = {}): Promise<Digest[]> {
  return locked(directory, async () => {
    const { study, store } = await load(directory, instrument);
    await verifyObservationStudy(directory, instrument);
    const frozen = await frozenSelection(directory, study, store);
    const input = inputFor(instrument, evaluationInput);
    if (digest(input) !== study.protocol.evaluation.inputDigest) throw new Error("evaluation input does not match preregistered commitment");
    if (Object.keys(attachments).some((id) => !frozen.selected.includes(id)) || (instrument.execution === "pure" && Object.keys(attachments).length)) throw new Error("unexpected evaluation attachment");
    const inputPointer = join(directory, "evaluation", "input.json");
    const existingInput = await maybeRef(inputPointer);
    if (existingInput && existingInput !== digest(input)) throw new Error("evaluation input changed");
    if (!existingInput) await pointer(inputPointer, await store.put(input));
    const result: Digest[] = [];
    for (const attemptId of frozen.selected) {
      const path = join(directory, "evaluation", `observation-${attemptId}.json`);
      const existing = await maybeRef(path);
      if (existing) { await store.get(existing); result.push(existing); continue; }
      const registered = frozen.attempts.find((a) => a.attemptId === attemptId)!;
      const registration = await loadRegistration(store, registered.registration);
      if (!registration.proposal) throw new Error("frozen selection contains a rejected proposal");
      const id = await store.put(await measure(study, instrument, registered.registration, registration.proposal, input, attachments[attemptId]));
      await pointer(path, id);
      result.push(id);
    }
    return result;
  });
}

async function verifyJoin(value: JsonValue, registrationDigest: Digest, proposal: ObservationProposal, input: ObservationInput, study: Study, instrument: ObservationInstrument, recompute: boolean): Promise<JoinedObservation> {
  const raw = object(value, ["contract", "registrationDigest", "inputDigest", "instrumentDigest", "receipt", "observation", "mode"], "observation join");
  if (raw.contract !== "algal.lab.observation-join.v1" || raw.registrationDigest !== registrationDigest || raw.inputDigest !== digest(input) || raw.instrumentDigest !== study.identity.instrumentDigest || raw.mode !== (instrument.execution === "pure" ? "computed" : "attached")) throw new Error("observation join identity mismatch");
  const receipt = parseRunReceipt(json(raw.receipt));
  const request = object(receipt.args.input?.request, ["input", "proposal", "attached"], "recorded measurement request");
  const attachment = request.attached === null ? null : parseObservation(request.attached);
  if (instrument.execution === "pure" && attachment !== null) throw new Error("pure receipt contains attached measurement");
  if (!equal(receipt.args, { input: { request: measurementRequest(input, proposal, attachment) } })) throw new Error("measurement receipt arguments do not match registration");
  const replay = await verifyReceipt(json(receipt), manifestToJson(measurementManifest), new MemoryStore(), builtinRegistry(), undefined, measurementTools(instrument, study.identity, true));
  if (!replay.ok) throw new Error("measurement receipt replay failed");
  const observation = receipt.outcome === "complete" ? parseObservation(receipt.cells.measure?.outputs?.observation) : null;
  if (!equal(observation, raw.observation)) throw new Error("observation differs from receipt");
  if (observation) {
    if (observation.contract !== instrument.outputContract) throw new Error("observation output contract mismatch");
    await instrument.verify(freeze(input), freeze(proposal), freeze(observation));
  }
  if (recompute) {
    if (instrument.execution !== "pure") throw new Error("fresh recomputation requires a pure adapter; attached external results need independent domain reproduction");
    const fresh = await measure(study, instrument, registrationDigest, proposal, input);
    if (!equal(fresh.observation, observation) || fresh.receipt.outcome !== receipt.outcome) throw new Error("fresh computation differs from recorded observation");
  }
  return { contract: raw.contract, registrationDigest, inputDigest: digest(input), instrumentDigest: study.identity.instrumentDigest, receipt, observation, mode: raw.mode as JoinedObservation["mode"] };
}

export async function verifyObservationStudy(directory: string, instrument: ObservationInstrument, options: { recompute?: boolean } = {}): Promise<{ ok: true; attempts: number; pending: number; rejected: number; observations: number; evaluated: number; frozen: boolean; receiptReplay: true; freshComputation: "passed" | "not-requested" }> {
  const { study, store } = await load(directory, instrument);
  if (options.recompute && instrument.execution !== "pure") throw new Error("fresh recomputation requires a pure adapter; attached external results need independent domain reproduction");
  let pending = 0, rejected = 0, observations = 0, evaluated = 0;
  const attempted = await ids(directory, study.protocol.maxAttempts);
  const priorObservations = new Map<string, number>();
  const sequences = new Set<number>();
  for (const attemptId of attempted) {
    const intent = await loadIntent(store, await ref(join(directory, "attempts", attemptId, "intent.json")));
    if (sequences.has(intent.sequence) || intent.sequence >= attempted.length) throw new Error("attempt registration order is invalid");
    sequences.add(intent.sequence);
    const observation = await maybeRef(join(directory, "attempts", attemptId, "observed.json"));
    if (observation) priorObservations.set(observation, intent.sequence);
  }
  for (const attemptId of attempted) {
    const path = join(directory, "attempts", attemptId);
    const intentId = await ref(join(path, "intent.json"));
    const intent = await loadIntent(store, intentId);
    if (intent.attemptId !== attemptId || new Set(intent.parents).size !== intent.parents.length || intent.parents.some((p) => !priorObservations.has(p) || priorObservations.get(p)! >= intent.sequence)) throw new Error("intent identity or parent evidence mismatch");
    const input = inputFor(instrument, intent.input);
    if (!equal(input, intent.input)) throw new Error("input normalization changed");
    const registrationDigest = await maybeRef(join(path, "registered.json"));
    if (!registrationDigest) throw new Error("ambiguous proposal intent: receipt was not durably registered; do not retry automatically");
    const registration = await loadRegistration(store, registrationDigest);
    if (registration.intentDigest !== intentId || !equal(registration.receipt.args, { input: { context: proposalContext(study, intent) } })) throw new Error("proposal receipt does not match prior registration intent");
    const replay = await verifyReceipt(json(registration.receipt), manifestToJson(proposalManifest), new MemoryStore());
    if (!replay.ok) throw new Error("proposal receipt replay failed");
    const joined = await maybeRef(join(path, "observed.json"));
    if (!registration.proposal) { if (joined) throw new Error("rejected proposal has measurement"); rejected++; continue; }
    if (!joined) { pending++; continue; }
    await verifyJoin(await store.get(joined), registrationDigest, registration.proposal, input, study, instrument, options.recompute === true);
    observations++;
  }
  const frozen = await maybeRef(join(directory, "freeze.json"));
  const evaluationFiles = await readdir(join(directory, "evaluation"));
  if (frozen) {
    const selection = await frozenSelection(directory, study, store);
    for (const id of selection.selected) {
      const entry = selection.attempts.find((a) => a.attemptId === id)!;
      if (!(await store.get(entry.observation!) as unknown as JoinedObservation).observation) throw new Error("failed observation was selected");
    }
    if (evaluationFiles.some((name) => name !== "input.json" && !selection.selected.some((id) => name === `observation-${id}.json`))) throw new Error("evaluation contains unfrozen candidate");
    const inputId = await maybeRef(join(directory, "evaluation", "input.json"));
    if (inputId) {
      if (inputId !== study.protocol.evaluation.inputDigest) throw new Error("evaluation input commitment mismatch");
      const input = inputFor(instrument, await store.get(inputId));
      for (const id of selection.selected) {
        const entry = selection.attempts.find((a) => a.attemptId === id)!;
        const output = await maybeRef(join(directory, "evaluation", `observation-${id}.json`));
        if (!output) continue;
        const registration = await loadRegistration(store, entry.registration);
        await verifyJoin(await store.get(output), entry.registration, registration.proposal!, input, study, instrument, options.recompute === true);
        evaluated++;
      }
    } else if (evaluationFiles.length) throw new Error("evaluation lacks committed input");
  } else if (evaluationFiles.length) throw new Error("evaluation occurred before selection froze");
  return { ok: true, attempts: attempted.length, pending, rejected, observations, evaluated, frozen: frozen !== null, receiptReplay: true, freshComputation: options.recompute ? "passed" : "not-requested" };
}

export { digest as observationDigest } from "../artifacts";
export { bindSources, observationIdentity } from "./sources";
export { boundedJson, parseObservationInput, parseObservation, parseObservationProposal, parseObservationProtocol } from "./contracts";
export type { Digest, ArtifactReference, Measurement, Observation, ObservationInput, ObservationInstrument, ObservationProposal, ObservationProtocol, SourceBinding } from "./contracts";
export type { ObservationIdentity } from "./sources";
