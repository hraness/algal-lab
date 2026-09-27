import { appendFileSync, closeSync, fsyncSync, openSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { builtinRegistry, canonicalize, digestCanonical, manifestToJson, MemoryStore, parseOrganismManifest, runOrganism, type ToolRegistry } from "@hraness/algal";
import { parseJob } from "./protocol";

const job = parseJob(JSON.parse(process.argv[2]!));
const directory = process.argv[3]!;
// A pipe is the owner's lease. Host/port death closes it; no detached worker lives on.
process.stdin.resume();
process.stdin.on("end", () => process.exit(71));
if (job.fault === "before_dispatch") process.exit(72);
const manifest = parseOrganismManifest({
  contract: "algal.organism.v1", key: "organism:host-comparison", name: "Host comparison fixture",
  budgets: { maxSteps: 4, maxAgentCalls: 0, maxWork: 1000 },
  interface: { inputs: { value: { cell: "input", port: "value" } }, outputs: { value: { cell: "effect", port: "value" } } },
  cells: [{ id: "input", kind: "input", outputs: { value: "text" } }, { id: "effect", kind: "tool", tool: "host.fixture.v1", budget: { maxEffectMs: 30000 } }],
  edges: [{ from: { cell: "input", port: "value" }, to: { cell: "effect", port: "value" } }],
});
writeFileSync(join(directory, `${job.id}.manifest.json`), canonicalize(manifestToJson(manifest)) + "\n", { flag: "wx", mode: 0o600 });
const tools: ToolRegistry = new Map([["host.fixture.v1", {
  signature: { inputs: { value: { type: "text" } }, outputs: { value: { type: "text" } }, effect: "write", cost: 1, maxOutputBytes: 256 },
  configurationDigest: digestCanonical({ contract: "host.fixture.v1" }),
  tool: async (inputs) => {
    await Bun.sleep(job.delay_ms);
    // The local append stands in for a non-idempotent remote effect. It is intentionally
    // separate from the host journal: a crash can leave an unknown outcome.
    const fd = openSync(join(directory, "effects.jsonl"), "a", 0o600);
    try { appendFileSync(fd, JSON.stringify({ id: job.id }) + "\n"); fsyncSync(fd); } finally { closeSync(fd); }
    process.stdout.write(JSON.stringify({ event: "effect", id: job.id }) + "\n");
    if (job.fault === "after_effect") process.exit(73);
    if (job.fault === "hold_after_effect") await Bun.sleep(5000);
    return { value: inputs.value! };
  },
}]]);
const receipt = await runOrganism({ manifest, args: { input: { value: job.id } }, fns: builtinRegistry(), store: new MemoryStore(), executors: [], tools });
writeFileSync(join(directory, `${job.id}.receipt.json`), canonicalize(receipt) + "\n", { flag: "wx", mode: 0o600 });
if (receipt.outcome !== "complete") throw new Error("fixture did not complete: " + JSON.stringify(receipt.failure));
process.stdout.write(JSON.stringify({ event: "result", id: job.id, digest: receipt.digest }) + "\n");
process.exit(0);
