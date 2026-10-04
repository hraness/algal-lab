import { stat } from "node:fs/promises";
import agenda from "../../examples/research-agenda.json";
import pkg from "../../package.json";
import { ALGAL_REVISION, object, text } from "../contracts";

const fields = ["id", "title", "status", "question", "application", "contribution", "existingEvidence", "baselines", "metrics", "nextExperiment", "confirmation", "priorArt", "stop", "references", "checks"] as const;
type TextField = Exclude<typeof fields[number], "baselines" | "metrics" | "references" | "checks">;
export type ResearchTrack = Record<TextField, string> & Record<"baselines" | "metrics" | "references" | "checks", string[]>;
export type Agenda = { contract: "algal.research-agenda.v1"; objective: string; tracks: ResearchTrack[] };

function requiredText(value: unknown, label: string): string {
  const result = text(value, 2400, label);
  if (!result.trim()) throw new Error(`${label}: must not be blank`);
  return result;
}
function list(value: unknown, label: string): string[] {
  if (!Array.isArray(value) || value.length < 1 || value.length > 12) throw new Error(`${label}: expected 1..12 entries`);
  return value.map(item => requiredText(item, label));
}
export function parseAgenda(value: unknown): Agenda {
  const raw = object(value, ["contract", "objective", "tracks"], "agenda");
  if (raw.contract !== "algal.research-agenda.v1") throw new Error("unsupported agenda contract");
  if (!Array.isArray(raw.tracks) || raw.tracks.length < 1 || raw.tracks.length > 12) throw new Error("agenda requires 1..12 tracks");
  const tracks = raw.tracks.map(value => {
    const raw = object(value, fields, "track");
    const track = Object.fromEntries(fields.map(field => [field, ["baselines", "metrics", "references", "checks"].includes(field) ? list(raw[field], field) : requiredText(raw[field], field)])) as ResearchTrack;
    if (!/^[a-z][a-z0-9-]{0,79}$/.test(track.id)) throw new Error("invalid track id");
    if (track.status !== "proposed") throw new Error("agenda tracks describe proposed work, not certified discoveries");
    if (track.references.some(path => !/^[a-zA-Z0-9_./-]+$/.test(path) || path.startsWith("/") || path.split("/").some(part => !part || part === "." || part === ".."))) throw new Error("references must be repository-relative paths");
    return track;
  });
  if (new Set(tracks.map(track => track.id)).size !== tracks.length) throw new Error("duplicate track id");
  return { contract: "algal.research-agenda.v1", objective: requiredText(raw.objective, "objective"), tracks };
}
export async function loadAgenda(): Promise<Agenda> {
  const result = parseAgenda(agenda);
  for (const track of result.tracks) for (const path of track.references) {
    if (!(await stat(new URL(`../../${path}`, import.meta.url))).isFile()) throw new Error(`agenda reference is not a file: ${path}`);
  }
  return result;
}
export async function doctor() {
  const expected = pkg.engines.bun.replace(/^>=/, "");
  const version = (value: string) => value.split(".").map(Number);
  const [actual, minimum] = [version(Bun.version), version(expected)];
  const supported = actual.length === 3 && actual.every(Number.isInteger) && (actual[0]! > minimum[0]! || actual[0] === minimum[0] && (actual[1]! > minimum[1]! || actual[1] === minimum[1] && actual[2]! >= minimum[2]!));
  if (!supported) throw new Error(`Bun ${expected} or newer is required; CI uses ${expected}`);
  if (pkg.dependencies["@hraness/algal"] !== `github:hraness/algal#${ALGAL_REVISION}`) throw new Error("runtime pin differs from the recorded application identity");
  const result = await loadAgenda();
  return { ready: true, bun: Bun.version, ciBun: expected, algalRevision: ALGAL_REVISION, tracks: result.tracks.map(track => track.id), pythonAvailable: Bun.which("python3") !== null, liveProviders: "not checked or activated", next: "Use agenda <track-id> for its controls. Python, Elixir, and native proof tools are track-specific; doctor does not qualify them." };
}
