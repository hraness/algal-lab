/** Research-only repeated-design evaluator for the unchanged network.v2 objective.
 * Removal probabilities depend on the environment, not the graph. Compile them
 * once, then use bit-set flood fill for each candidate. "Exact" means expectation
 * over the whole finite distribution; arithmetic here is still IEEE-754.
 */
import { parseEnvironment, type FailureEnvironment } from "../src/heterogeneous";
import { parseGraph, type Graph } from "../src/network";

export type CompiledObjective = {
  nodes: number;
  steps: number;
  environment: FailureEnvironment;
  ceiling: number;
  stateCount: number;
  score: (graph: Graph) => number;
};

export function compileObjective(input: FailureEnvironment, steps: number): CompiledObjective {
  const nodes = input?.weights?.length;
  if (!Number.isInteger(nodes) || nodes < 4 || nodes > 10) throw new Error("research scorer requires 4..10 nodes");
  if (!Number.isInteger(steps) || steps < 1 || steps > nodes - 2) throw new Error("research scorer horizon must be 1..nodes-2");
  const environment = parseEnvironment(input, nodes);
  const { weights, values } = environment;
  const size = 1 << nodes;
  const full = size - 1;
  const totalWeight = weights.reduce((a, b) => a + b, 0);
  const totalValue = values.reduce((a, b) => a + b, 0);
  const probability = new Float64Array(size);
  const removedWeight = new Float64Array(size);
  const value = new Float64Array(size);
  const counts = new Uint8Array(size);
  probability[0] = 1;
  for (let mask = 1; mask < size; mask++) {
    const bit = mask & -mask;
    const vertex = 31 - Math.clz32(bit);
    const previous = mask ^ bit;
    removedWeight[mask] = removedWeight[previous]! + weights[vertex]!;
    value[mask] = value[previous]! + values[vertex]!;
    counts[mask] = counts[previous]! + 1;
    if (counts[mask]! > steps) continue;
    for (let rest = mask; rest !== 0; rest &= rest - 1) {
      const nextBit = rest & -rest;
      const prior = mask ^ nextBit;
      probability[mask]! += probability[prior]! * weights[31 - Math.clz32(nextBit)]! / (totalWeight - removedWeight[prior]!);
    }
  }
  const states: { active: number; coefficient: number; value: number }[] = [];
  let ceiling = 0;
  for (let removed = 0; removed < size; removed++) {
    const count = counts[removed]!;
    if (count > steps) continue;
    const active = full ^ removed;
    const coefficient = probability[removed]! * (count === 0 || count === steps ? 1 : 2) / (2 * steps * totalValue);
    states.push({ active, coefficient, value: value[active]! });
    ceiling += coefficient * value[active]!;
  }
  return {
    nodes, steps,
    // Return copies: caller edits must not change the compiled objective.
    environment: { weights: [...weights], values: [...values] },
    ceiling, stateCount: states.length,
    score(inputGraph: Graph): number {
      const graph = parseGraph(inputGraph);
      if (graph.nodes !== nodes) throw new Error("candidate node count differs from compiled environment");
      const adjacency = new Uint16Array(nodes);
      for (const [a, b] of graph.edges) { adjacency[a]! |= 1 << b; adjacency[b]! |= 1 << a; }
      let loss = 0;
      for (const state of states) {
        let unseen = state.active;
        let largest = 0;
        while (unseen !== 0) {
          let frontier = unseen & -unseen;
          let component = frontier;
          unseen ^= frontier;
          while (frontier !== 0) {
            let neighbors = 0;
            for (let rest = frontier; rest !== 0; rest &= rest - 1) neighbors |= adjacency[31 - Math.clz32(rest & -rest)]!;
            frontier = neighbors & unseen;
            unseen ^= frontier;
            component |= frontier;
          }
          largest = Math.max(largest, value[component]!);
        }
        loss += state.coefficient * (state.value - largest);
      }
      return ceiling - loss;
    },
  };
}
