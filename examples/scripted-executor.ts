// A credential-free example of the command executor wire protocol. This is
// deterministic search, not an LLM. Replace it with your own provider wrapper.
import { scriptedProposal } from "../src/researcher";
import type { ResearchContext } from "../src/contracts";
const input = await Bun.stdin.text();
if (Buffer.byteLength(input) > 131072) throw new Error("request exceeds bound");
const request = JSON.parse(input);
if (request.contract !== "algal.effect.v1" || request.kind !== "agent" || !["algal.lab.context.v1", "algal.lab.context.v2", "algal.lab.context.v3"].includes((request.context?.inputs?.context as { contract?: string })?.contract ?? "")) throw new Error("unexpected ALGAL request");
console.log(JSON.stringify(scriptedProposal(request.context.inputs.context as ResearchContext)));
