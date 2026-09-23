/** Proven sufficient cases for tree design under network.v2 random failure.
 * These functions construct designs; they do not change the instrument or claim
 * that a null result means no optimal star exists. Proofs are in the research note.
 */
import { parseEnvironment, type FailureEnvironment } from "../src/heterogeneous";
import type { Graph } from "../src/network";

export type CertifiedTree = {
  graph: Graph;
  center: number;
  theorem: "one-failure" | "dominant-hub";
  /** Exact normalized trapezoid AUC when the horizon is one; otherwise absent. */
  auc?: { numerator: number; denominator: number };
};

function environment(input: FailureEnvironment): FailureEnvironment {
  return parseEnvironment(input, input?.weights?.length);
}

function star(nodes: number, center: number): Graph {
  return {
    nodes,
    edges: Array.from({ length: nodes }, (_, i) => i).filter((i) => i !== center)
      .map((i): [number, number] => i < center ? [i, center] : [center, i]),
  };
}

function fraction(numerator: number, denominator: number): { numerator: number; denominator: number } {
  let a = numerator;
  let b = denominator;
  while (b !== 0) [a, b] = [b, a % b];
  return { numerator: numerator / a, denominator: denominator / a };
}

/** O(n) arithmetic and output: globally optimal among all labeled trees for h=1. */
export function optimalSingleFailureTree(input: FailureEnvironment): CertifiedTree {
  const { weights, values } = environment(input);
  const nodes = weights.length;
  const totalValue = values.reduce((a, b) => a + b, 0);
  const totalWeight = weights.reduce((a, b) => a + b, 0);
  let largest = -1;
  let second = -1;
  let largestIndex = -1;
  for (let i = 0; i < nodes; i++) {
    if (values[i]! > largest) { second = largest; largest = values[i]!; largestIndex = i; }
    else second = Math.max(second, values[i]!);
  }
  let center = 0;
  let bestLoss = Infinity;
  let removedValue = 0;
  for (let i = 0; i < nodes; i++) {
    const otherMaximum = i === largestIndex ? second : largest;
    const loss = weights[i]! * (totalValue - values[i]! - otherMaximum);
    if (loss < bestLoss) { bestLoss = loss; center = i; }
    removedValue += weights[i]! * values[i]!;
  }
  const denominator = 2 * totalWeight * totalValue;
  return {
    graph: star(nodes, center), center, theorem: "one-failure",
    auc: fraction(denominator - removedValue - bestLoss, denominator),
  };
}

/**
 * O(n) sufficient optimality guard. For h>1 the theorem applies when a node
 * simultaneously minimizes failure weight and maximizes service value. It
 * certifies a common optimum at EVERY removal count, hence this AUC too.
 */
export function certifiedOptimalTree(input: FailureEnvironment, steps: number): CertifiedTree | null {
  const env = environment(input);
  const nodes = env.weights.length;
  if (!Number.isInteger(steps) || steps < 1 || steps > nodes - 2) throw new Error("tree solver horizon must be 1..nodes-2");
  if (steps === 1) return optimalSingleFailureTree(env);
  const minWeight = Math.min(...env.weights);
  const maxValue = Math.max(...env.values);
  const center = env.weights.findIndex((weight, i) => weight === minWeight && env.values[i] === maxValue);
  return center < 0 ? null : { graph: star(nodes, center), center, theorem: "dominant-hub" };
}
