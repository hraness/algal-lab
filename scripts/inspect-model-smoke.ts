/** Offline acceptance inspection. Transport metadata is checked for consistency,
 * not authenticated independently; a self-consistent archive is not authorship. */
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ArtifactStore, digest, digestString, readJsonFile } from "../src/artifacts";
import { CONDITIONS, equal, integer, object, parseProtocol, text } from "../src/contracts";
import { exactRandomAuc } from "../src/oracle";
import { verifyStudy, type Attempt, type StudyReport } from "../src/study";

function configuration(value: unknown) {
  const c = object(value, ["contract", "provider", "model", "accountDigest", "runtimeVersion", "runtimeDigest", "qualificationEvidenceDigest", "qualificationExpiresAt", "modelObservedAtMs", "timeoutMs", "maxOutputBytes", "maxInputBytes", "maxCalls", "zeroTools", "zeroHooks", "ephemeral", "tokenUsage"], "xcb configuration");
  if (c.contract !== "algal.lab.xcb-executor.v1" || !["claude", "codex", "devin"].includes(c.provider as string) || c.zeroTools !== true || c.zeroHooks !== true || c.ephemeral !== true || c.tokenUsage !== "unavailable") throw new Error("invalid XCB configuration");
  const model = text(c.model, 512, "model");
  if (!/^(claude|codex|devin)\/[a-zA-Z0-9._-]+(?:\/[a-zA-Z0-9._-]+)?$/.test(model) || !model.startsWith(`${c.provider}/`)) throw new Error("invalid XCB model identity");
  for (const key of ["accountDigest", "runtimeDigest", "qualificationEvidenceDigest"]) digestString(c[key]);
  text(c.runtimeVersion, 64, "runtime version");
  for (const key of ["qualificationExpiresAt", "modelObservedAtMs"]) integer(c[key], 1, Number.MAX_SAFE_INTEGER, key);
  integer(c.timeoutMs, 1000, 60000, "timeout"); integer(c.maxOutputBytes, 1, 8192, "output bytes");
  integer(c.maxInputBytes, 1, 131072, "input bytes"); integer(c.maxCalls, 1, 12, "call budget");
  return { value: c, model, executor: `algal-lab:xcb.v1:${model}` };
}

function observation(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("invalid transport observation");
  const optional = ["requestId", "code"].filter((key) => Object.hasOwn(value, key));
  const o = object(value, ["requestDigest", "elapsedMs", "status", "joined", "effects", ...optional], "transport observation");
  digestString(o.requestDigest); integer(o.elapsedMs, 0, Number.MAX_SAFE_INTEGER, "elapsed time");
  if (!["completed", "failed"].includes(o.status as string) || typeof o.joined !== "boolean" || !["none", "unknown"].includes(o.effects as string)) throw new Error("invalid transport observation");
  if (o.requestId !== undefined && (typeof o.requestId !== "string" || !/^application_[a-zA-Z0-9_-]{1,128}$/.test(o.requestId))) throw new Error("invalid transport request ID");
  if (o.status === "completed" && (o.requestId === undefined || o.code !== undefined)) throw new Error("invalid completed observation");
  if (o.status === "failed") text(o.code, 64, "failure code");
  return o;
}

export async function inspectModelSmoke(directory: string) {
  const study = join(directory, "study");
  const verification = await verifyStudy(study);
  const envelope = object(await readJsonFile(join(study, "study.json")), ["report", "digest"], "study envelope");
  if (digest(envelope.report) !== verification.reportDigest || envelope.digest !== verification.reportDigest) throw new Error("study changed after verification");
  const report = envelope.report as StudyReport;
  if (report.backend !== "command" || report.attempts.length > 12 || report.protocol.nodes > 10) throw new Error("not a bounded model smoke study");
  const sidecar = object(await readJsonFile(join(directory, "xcb.json")), ["configuration", "configurationDigest", "observations", "cancelled"], "transport sidecar");
  const config = object(await readJsonFile(join(directory, "executor.json")), ["configuration", "configurationDigest"], "executor configuration");
  if (!equal(sidecar.configuration, config.configuration) || sidecar.configurationDigest !== config.configurationDigest || digest(config.configuration) !== config.configurationDigest) throw new Error("configuration identity mismatch");
  const selected = configuration(config.configuration);
  const intent = object(await readJsonFile(join(directory, "intent.json")), ["protocol", "model", "accountDigest", "maxCalls"], "smoke intent");
  if (!equal(parseProtocol(intent.protocol), report.protocol) || intent.model !== selected.model || intent.accountDigest !== selected.value.accountDigest || intent.maxCalls !== report.attempts.length || intent.maxCalls !== selected.value.maxCalls) throw new Error("frozen intent mismatch");
  if (!Array.isArray(sidecar.observations) || sidecar.observations.length > 12 || typeof sidecar.cancelled !== "boolean") throw new Error("invalid transport observations");
  const store = new ArtifactStore(study);
  const attempts = new Map<string, Attempt>();
  for (const id of report.attempts) attempts.set(id, await store.get(id) as unknown as Attempt);
  const effects = [...attempts.values()].flatMap((a) => a.receipt.effects.filter((e) => !e.executor.startsWith("tool:")));
  const observations = sidecar.observations.map(observation);
  const inherited: { child: string; parent: string; condition: string; researcher: number; parentResearcher: number; round: number }[] = [];
  for (const [childId, child] of attempts) {
    if (!child.measurement) continue;
    for (const parentId of child.measurement.proposal.parents) {
      const parent = attempts.get(parentId);
      if (parent?.measurement && parent.context.round < child.context.round && parent.context.researcher !== child.context.researcher &&
          child.context.evidence.some((e) => e.id === parentId) && digest(parent.measurement.proposal.graph) !== digest(child.measurement.proposal.graph)) {
        inherited.push({ child: childId, parent: parentId, condition: child.context.condition, researcher: child.context.researcher,
          parentResearcher: parent.context.researcher, round: child.context.round });
      }
    }
  }
  const shape = report.protocol.replicateSeeds.length === 1 && report.protocol.researchers === 2 && report.protocol.rounds === 2 && report.attempts.length === 12;
  const transportMatches = effects.length === 12 && observations.length === effects.length && observations.every((o, i) => o.requestDigest === effects[i]?.requestDigest && o.status === "completed" && o.joined === true && o.effects === "none");
  const configurationMatches = effects.every((e) => e.configurationDigest === config.configurationDigest && e.executor === selected.executor && e.usage?.model === selected.model);
  const requestIds = observations.filter((o) => o.status === "completed").map((o) => o.requestId);
  const controls = { boundedTwelveCallStudy: shape, everyProposalMeasured: verification.experiments === 12,
    transportReportsCompletedJoined: transportMatches, receiptConfigurationMatches: configurationMatches,
    distinctTransportRequests: new Set(requestIds).size === requestIds.length,
    notCancelled: sidecar.cancelled === false, changedDesignFromVisiblePeer: inherited.length > 0 };
  const source = await readFile(new URL(import.meta.url), "utf8");
  return {
    contract: "algal.lab.model-smoke-inspection.v1", reportDigest: verification.reportDigest,
    analysisDigest: `sha256:${createHash("sha256").update(source).digest("hex")}`,
    passed: Object.values(controls).every(Boolean), controls, configuration: config.configuration,
    models: [...new Set(effects.map((e) => e.usage?.model ?? "unreported"))], tokenUsage: "unavailable unless explicitly present on effect receipts",
    proposals: verification.experiments, attempts: report.attempts.length, inheritance: inherited,
    champions: CONDITIONS.map((condition) => {
      const summary = report.summaries.find((s) => s.condition === condition)!;
      const graph = summary.selectedAttempt ? attempts.get(summary.selectedAttempt)?.measurement?.proposal.graph : undefined;
      return { condition, graphDigest: graph ? digest(graph) : null, exactRandomAuc: graph ? exactRandomAuc(graph, report.protocol.failureSteps) : null, targetedAuc: summary.selectedTargetedAuc };
    }),
    limits: "This checks archived operational inheritance and internally consistent transport reports. It does not authenticate provider claims or establish a sharing advantage, causal influence, or a transferable discovery.",
  };
}

if (import.meta.main) {
  if (Bun.argv.length !== 3) throw new Error("usage: bun scripts/inspect-model-smoke.ts RUN_DIRECTORY");
  const result = await inspectModelSmoke(Bun.argv[2]!);
  console.log(JSON.stringify(result, null, 2));
  if (!result.passed) process.exitCode = 1;
}
