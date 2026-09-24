import { canonicalize, type JsonValue } from "@hraness/algal";
import { digestString } from "../artifacts";
import { integer, json, object, text } from "../contracts";

export type Digest = `sha256:${string}`;
export type ArtifactReference = { name: string; digest: Digest; bytes: number; mediaType: string };
export type ObservationInput = { contract: string; data: JsonValue; artifacts: ArtifactReference[] };
export type ObservationProposal = { design: JsonValue; hypothesis: string; prediction: JsonValue; rationale: string; parents: Digest[] };
export type Measurement = { name: string; value: number; unit: string; uncertainty: { method: string; lower: number | null; upper: number | null; level: number | null } };
export type Observation = { contract: string; realizedDesign: JsonValue; values: JsonValue; measurements: Measurement[]; artifacts: ArtifactReference[]; limitations: string[] };
export type ObservationProtocol = {
  contract: "algal.lab.observation-study.v1";
  name: string;
  maxAttempts: number;
  evaluation: { inputDigest: Digest; specification: JsonValue };
};
/** Complete, recursively hashed source trees plus individual lockfiles, binaries,
 * interpreter identities or configuration. Labels, never local paths, are archived.
 * The trusted adapter owner must include its entire executable dependency closure.
 */
export type SourceBinding = { trees: Record<string, URL>; files: Record<string, URL> };
export type ObservationInstrument = {
  contract: "algal.lab.instrument.v1";
  id: string;
  inputContract: string;
  outputContract: string;
  execution: "pure" | "attachment";
  sources: SourceBinding;
  parseInput(value: unknown): ObservationInput;
  verify(input: ObservationInput, proposal: ObservationProposal, observation: Observation): void | Promise<void>;
  /** Only pure, bounded, deterministic local measurements may implement this.
   * External jobs use attachment; their reconciled result is supplied by the owner.
   */
  measure?(input: ObservationInput, proposal: ObservationProposal): Observation | Promise<Observation>;
};

export function boundedJson(value: unknown, bytes = 65536): JsonValue {
  const data = json(value);
  const visit = (item: JsonValue, depth: number): void => {
    if (depth > 16) throw new Error("observation JSON exceeds depth bound");
    if (item !== null && typeof item === "object") for (const child of Object.values(item)) visit(child, depth + 1);
  };
  visit(data, 0);
  if (Buffer.byteLength(canonicalize(data)) > bytes) throw new Error("observation JSON exceeds byte bound");
  // Detach caller-owned objects before they can change between admission and use.
  return JSON.parse(canonicalize(data)) as JsonValue;
}
export function identifier(value: unknown): string {
  const id = text(value, 64, "identifier");
  if (!/^[a-z0-9][a-z0-9._-]*$/.test(id)) throw new Error("invalid identifier");
  return id;
}
function finite(value: unknown): number {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new Error("expected finite measurement");
  return value;
}
function references(value: unknown): ArtifactReference[] {
  if (!Array.isArray(value) || value.length > 32) throw new Error("artifact manifest exceeds bounds");
  const result = value.map((entry) => {
    const r = object(entry, ["name", "digest", "bytes", "mediaType"], "artifact reference");
    return { name: identifier(r.name), digest: digestString(r.digest), bytes: integer(r.bytes, 0, Number.MAX_SAFE_INTEGER, "artifact bytes"), mediaType: text(r.mediaType, 128, "media type") };
  });
  if (new Set(result.map((r) => r.name)).size !== result.length) throw new Error("duplicate artifact name");
  return result;
}
export function parseObservationInput(value: unknown): ObservationInput {
  const p = object(boundedJson(value), ["contract", "data", "artifacts"], "observation input");
  return { contract: text(p.contract, 128, "input contract"), data: boundedJson(p.data), artifacts: references(p.artifacts) };
}
export function parseObservationProposal(value: unknown, parents: readonly string[]): ObservationProposal {
  const p = object(boundedJson(value, 8192), ["design", "hypothesis", "prediction", "rationale", "parents"], "observation proposal");
  if (!Array.isArray(p.parents) || p.parents.length > 8 || new Set(p.parents).size !== p.parents.length) throw new Error("invalid proposal parents");
  const admittedParents = p.parents.map((ref) => {
    const id = digestString(ref);
    if (!parents.includes(id)) throw new Error("parent is not visible prior evidence");
    return id;
  });
  return { design: boundedJson(p.design, 4096), hypothesis: text(p.hypothesis, 1000, "hypothesis"), prediction: boundedJson(p.prediction, 2048), rationale: text(p.rationale, 1000, "rationale"), parents: admittedParents };
}
export function parseObservation(value: unknown): Observation {
  const p = object(boundedJson(value), ["contract", "realizedDesign", "values", "measurements", "artifacts", "limitations"], "observation");
  if (!Array.isArray(p.measurements) || p.measurements.length > 64) throw new Error("measurement count exceeds bounds");
  const measurements = p.measurements.map((entry): Measurement => {
    const m = object(entry, ["name", "value", "unit", "uncertainty"], "measurement");
    const u = object(m.uncertainty, ["method", "lower", "upper", "level"], "uncertainty");
    const lower = u.lower === null ? null : finite(u.lower);
    const upper = u.upper === null ? null : finite(u.upper);
    const level = u.level === null ? null : finite(u.level);
    if ((lower === null) !== (upper === null) || (lower !== null && upper !== null && lower > upper) || (level !== null && (level <= 0 || level >= 1 || lower === null))) throw new Error("invalid uncertainty interval");
    return { name: identifier(m.name), value: finite(m.value), unit: text(m.unit, 128, "unit"), uncertainty: { method: text(u.method, 512, "uncertainty method"), lower, upper, level } };
  });
  if (new Set(measurements.map((m) => m.name)).size !== measurements.length) throw new Error("duplicate measurement name");
  if (!Array.isArray(p.limitations) || p.limitations.length > 16) throw new Error("invalid limitations");
  return { contract: text(p.contract, 128, "output contract"), realizedDesign: boundedJson(p.realizedDesign), values: boundedJson(p.values), measurements, artifacts: references(p.artifacts), limitations: p.limitations.map((v) => text(v, 1000, "limitation")) };
}
export function parseObservationProtocol(value: unknown): ObservationProtocol {
  const p = object(boundedJson(value, 8192), ["contract", "name", "maxAttempts", "evaluation"], "observation protocol");
  if (p.contract !== "algal.lab.observation-study.v1") throw new Error("unsupported observation protocol");
  const e = object(p.evaluation, ["inputDigest", "specification"], "evaluation");
  return { contract: p.contract, name: identifier(p.name), maxAttempts: integer(p.maxAttempts, 1, 64, "maxAttempts"), evaluation: { inputDigest: digestString(e.inputDigest), specification: boundedJson(e.specification, 4096) } };
}
