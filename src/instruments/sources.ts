import { createHash } from "node:crypto";
import { lstat, readdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { assertRuntimePinned, digest, readRuntimeSources, runtimeDigest } from "../artifacts";
import { ALGAL_REVISION } from "../contracts";
import { identifier, type Digest, type ObservationInstrument, type SourceBinding } from "./contracts";

/** No extension filter: nested non-TS helpers, data tables, binaries and lockfiles
 * in declared trees affect identity too. Symlinks cannot escape a bound tree.
 */
export async function bindSources(binding: SourceBinding): Promise<Record<string, Digest>> {
  const result: Record<string, Digest> = {};
  let totalBytes = 0;
  const add = async (name: string, url: URL): Promise<void> => {
    if (Object.hasOwn(result, name)) throw new Error("duplicate source name");
    const stat = await lstat(fileURLToPath(url));
    if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 16 * 1024 * 1024) throw new Error("source must be a bounded regular file");
    if (Object.keys(result).length >= 2048 || (totalBytes += stat.size) > 64 * 1024 * 1024) throw new Error("source manifest exceeds bounds");
    result[name] = `sha256:${createHash("sha256").update(await readFile(url)).digest("hex")}`;
  };
  const tree = async (name: string, url: URL, depth: number): Promise<void> => {
    if (depth > 24) throw new Error("source tree exceeds depth bound");
    const stat = await lstat(fileURLToPath(url));
    if (!stat.isDirectory() || stat.isSymbolicLink()) throw new Error("source tree must be a directory without symlinks");
    const entries = (await readdir(url, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name));
    for (const entry of entries) {
      const child = new URL(encodeURIComponent(entry.name) + (entry.isDirectory() ? "/" : ""), url);
      if (entry.isDirectory()) await tree(`${name}/${entry.name}`, child, depth + 1);
      else await add(`${name}/${entry.name}`, child);
    }
  };
  for (const [label, root] of Object.entries(binding.trees).sort()) {
    identifier(label);
    if (!root.pathname.endsWith("/")) throw new Error("source tree URL requires trailing slash");
    await tree(label, root, 0);
  }
  for (const [label, file] of Object.entries(binding.files).sort()) { identifier(label); await add(label, file); }
  if (!Object.keys(result).length) throw new Error("instrument requires bound sources");
  return result;
}
export type ObservationIdentity = { algalRevision: string; verifierEnvironment: { bun: string }; instrument: { id: string; inputContract: string; outputContract: string; execution: "pure" | "attachment" }; instrumentDigest: Digest; applicationDigest: Digest; sources: Record<string, Digest> };
export async function observationIdentity(instrument: ObservationInstrument): Promise<ObservationIdentity> {
  if (instrument.contract !== "algal.lab.instrument.v1" || !["pure", "attachment"].includes(instrument.execution)) throw new Error("unsupported instrument");
  identifier(instrument.id);
  if (instrument.execution === "pure" && !instrument.measure) throw new Error("pure instrument requires measurement");
  if (instrument.execution === "attachment" && instrument.measure) throw new Error("attachment instrument cannot launch work");
  const root = new URL("../../", import.meta.url);
  const [sources, application, runtime, lock, manifest] = await Promise.all([
    bindSources(instrument.sources),
    bindSources({ trees: { src: new URL("src/", root) }, files: { package: new URL("package.json", root), lock: new URL("bun.lock", root) } }),
    readRuntimeSources(), readFile(new URL("bun.lock", root), "utf8"), readFile(new URL("package.json", root), "utf8"),
  ]);
  assertRuntimePinned(lock, manifest);
  const metadata = { id: instrument.id, inputContract: instrument.inputContract, outputContract: instrument.outputContract, execution: instrument.execution };
  return { algalRevision: ALGAL_REVISION, verifierEnvironment: { bun: Bun.version }, instrument: metadata, instrumentDigest: digest({ metadata, sources }), applicationDigest: digest({ application, runtime: runtimeDigest(runtime) }), sources };
}
