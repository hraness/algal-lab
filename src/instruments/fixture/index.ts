import { equal, object } from "../../contracts";
import { parseObservationInput, type ObservationInput, type ObservationInstrument, type ObservationProposal } from "../contracts";
import { meanAndStandardError } from "./statistics";

function values(input: ObservationInput): number[] {
  const data = object(input.data, ["replicates"], "fixture input");
  if (!Array.isArray(data.replicates) || data.replicates.length < 2 || data.replicates.length > 64 || data.replicates.some((v) => typeof v !== "number" || !Number.isFinite(v) || Math.abs(v) > 1000000)) throw new Error("fixture needs 2..64 bounded replicates");
  return data.replicates as number[];
}
function scale(proposal: ObservationProposal): number {
  const design = object(proposal.design, ["scale"], "fixture design");
  if (typeof design.scale !== "number" || !Number.isFinite(design.scale) || Math.abs(design.scale) > 10) throw new Error("invalid fixture scale");
  return design.scale;
}
export const observationFixtureInstrument: ObservationInstrument = {
  contract: "algal.lab.instrument.v1", id: "repeated-measurement.v1", inputContract: "algal.lab.replicates.v1", outputContract: "algal.lab.mean-observation.v1", execution: "pure",
  sources: { trees: { fixture: new URL("./", import.meta.url) }, files: {} },
  parseInput(value) {
    const input = parseObservationInput(value);
    if (input.contract !== "algal.lab.replicates.v1" || input.artifacts.length) throw new Error("invalid fixture input contract");
    values(input);
    return input;
  },
  measure(input, proposal) {
    const replicates = values(input).map((v) => v * scale(proposal));
    const { mean, standardError } = meanAndStandardError(replicates);
    return { contract: "algal.lab.mean-observation.v1", realizedDesign: proposal.design, values: { replicates },
      measurements: [{ name: "mean", value: mean, unit: "fixture-unit", uncertainty: { method: "sample standard error (not a confidence interval)", lower: mean - standardError, upper: mean + standardError, level: null } }],
      artifacts: [], limitations: ["Synthetic arithmetic fixture; repeated numbers do not establish biological replication or a scientific discovery."] };
  },
  verify(input, proposal, observation) {
    if (!equal(observation.realizedDesign, proposal.design) || observation.measurements.length !== 1 || observation.measurements[0]?.name !== "mean" || observation.measurements[0].unit !== "fixture-unit") throw new Error("fixture observation metadata mismatch");
    scale(proposal);
    const output = object(observation.values, ["replicates"], "fixture output");
    if (!Array.isArray(output.replicates) || output.replicates.length !== values(input).length || observation.artifacts.length) throw new Error("fixture replicate manifest mismatch");
  },
};
