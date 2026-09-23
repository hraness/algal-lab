import { describe, expect, test } from "bun:test";
import { randomGraph, type Graph } from "./network";
import { canonicalForm, isomorphic, topologyClasses, topologyDigest } from "./topology";

/** Mulberry32, seeded, so relabelings are reproducible. */
function generator(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let mixed = Math.imul(state ^ (state >>> 15), state | 1);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), mixed | 61);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 0x1_0000_0000;
  };
}

function relabel(graph: Graph, seed: number): Graph {
  const next = generator(seed);
  const image = Array.from({ length: graph.nodes }, (_, node) => node);
  for (let index = image.length - 1; index > 0; index--) {
    const other = Math.floor(next() * (index + 1));
    [image[index], image[other]] = [image[other]!, image[index]!];
  }
  const edges = graph.edges.map(([a, b]): [number, number] => next() < 0.5 ? [image[a]!, image[b]!] : [image[b]!, image[a]!]);
  for (let index = edges.length - 1; index > 0; index--) {
    const other = Math.floor(next() * (index + 1));
    [edges[index], edges[other]] = [edges[other]!, edges[index]!];
  }
  return { nodes: graph.nodes, edges };
}

function graph(nodes: number, edges: [number, number][]): Graph {
  return { nodes, edges };
}

function ring(nodes: number): Graph {
  return graph(nodes, Array.from({ length: nodes }, (_, node): [number, number] => [node, (node + 1) % nodes]));
}

function connected(nodes: number, edges: readonly [number, number][]): boolean {
  const parent = Array.from({ length: nodes }, (_, node) => node);
  const find = (node: number): number => parent[node] === node ? node : (parent[node] = find(parent[node]!));
  let components = nodes;
  for (const [a, b] of edges) {
    const x = find(a);
    const y = find(b);
    if (x !== y) {
      parent[x] = y;
      components--;
    }
  }
  return components === 1;
}

/** Number of isomorphism classes among all connected labeled graphs on `nodes`. */
function exhaustiveClasses(nodes: number): { classes: number; labeled: number } {
  const pairs: [number, number][] = [];
  for (let a = 0; a < nodes; a++) for (let b = a + 1; b < nodes; b++) pairs.push([a, b]);
  const forms = new Set<string>();
  let labeled = 0;
  for (let mask = 0; mask < 1 << pairs.length; mask++) {
    const edges = pairs.filter((_, index) => (mask >> index) & 1);
    if (!connected(nodes, edges)) continue;
    labeled++;
    forms.add(canonicalForm(graph(nodes, edges)));
  }
  return { classes: forms.size, labeled };
}

function elapsed(run: () => void): number {
  const start = performance.now();
  run();
  return performance.now() - start;
}

const k33 = graph(6, [[0, 3], [0, 4], [0, 5], [1, 3], [1, 4], [1, 5], [2, 3], [2, 4], [2, 5]]);
const prism = graph(6, [[0, 1], [1, 2], [0, 2], [3, 4], [4, 5], [3, 5], [0, 3], [1, 4], [2, 5]]);
const cube = graph(8, [[0, 1], [0, 2], [0, 4], [1, 3], [1, 5], [2, 3], [2, 6], [3, 7], [4, 5], [4, 6], [5, 7], [6, 7]]);
const wagner = graph(8, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [0, 7], [0, 4], [1, 5], [2, 6], [3, 7]]);
/** Two diamonds (K4 minus an edge) joined at their degree-2 vertices: cubic, 4 triangles. */
const diamonds = graph(8, [[0, 1], [0, 2], [1, 2], [1, 3], [2, 3], [4, 5], [4, 6], [5, 6], [5, 7], [6, 7], [0, 4], [3, 7]]);
const petersen = graph(10, [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4], [0, 5], [1, 6], [2, 7], [3, 8], [4, 9], [5, 7], [7, 9], [6, 9], [6, 8], [5, 8]]);

/** Rook's graph K4 x K4 and the Shrikhande graph: both strongly regular (16, 6, 2, 2). */
function torusGraph(adjacentOffsets: readonly [number, number][]): Graph {
  const edges = new Map<string, [number, number]>();
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      for (const [di, dj] of adjacentOffsets) {
        const a = i * 4 + j;
        const b = ((i + di + 4) % 4) * 4 + ((j + dj + 4) % 4);
        const edge: [number, number] = a < b ? [a, b] : [b, a];
        edges.set(edge.join(), edge);
      }
    }
  }
  return graph(16, [...edges.values()]);
}
const rook = torusGraph([[1, 0], [2, 0], [3, 0], [0, 1], [0, 2], [0, 3]]);
const shrikhande = torusGraph([[1, 0], [3, 0], [0, 1], [0, 3], [1, 1], [3, 3]]);

describe("topology canonical forms", () => {
  test("random relabelings of 243 random graphs keep the canonical form", () => {
    let checked = 0;
    for (let nodes = 4; nodes <= 12; nodes++) {
      const maximum = (nodes * (nodes - 1)) / 2;
      for (let sample = 0; sample < 27; sample++) {
        const edgeCount = nodes - 1 + (sample * 7919) % (maximum - nodes + 2);
        const original = randomGraph(nodes, edgeCount, nodes * 1000 + sample);
        const form = canonicalForm(original);
        for (let relabeling = 0; relabeling < 3; relabeling++) {
          const copy = relabel(original, nodes * 1_000_003 + sample * 17 + relabeling);
          expect(canonicalForm(copy)).toBe(form);
          expect(isomorphic(original, copy)).toBe(true);
        }
        checked++;
      }
    }
    expect(checked).toBe(243);
  });

  test("large admitted designs are relabeling invariant", () => {
    for (const [nodes, edges] of [[16, 30], [20, 40], [24, 23], [24, 60], [24, 96]] as const) {
      const original = randomGraph(nodes, edges, nodes + edges);
      expect(canonicalForm(relabel(original, 7))).toBe(canonicalForm(original));
    }
    expect(canonicalForm(relabel(rook, 3))).toBe(canonicalForm(rook));
    expect(canonicalForm(relabel(shrikhande, 3))).toBe(canonicalForm(shrikhande));
  });

  test("regular graphs with equal degree sequences are separated", () => {
    expect(isomorphic(k33, prism)).toBe(false);
    expect(isomorphic(cube, wagner)).toBe(false);
    expect(isomorphic(cube, diamonds)).toBe(false);
    expect(isomorphic(wagner, diamonds)).toBe(false);
    expect(isomorphic(rook, shrikhande)).toBe(false);
    expect(isomorphic(ring(10), relabel(ring(10), 11))).toBe(true);
    expect(isomorphic(petersen, relabel(petersen, 5))).toBe(true);
  });

  test("the form is a relabeled copy of the input", () => {
    expect(canonicalForm(graph(4, [[2, 3], [1, 2], [0, 1]]))).toBe("topology.v1:4:0-2,1-3,2-3");
    expect(canonicalForm(ring(4))).toBe(canonicalForm(graph(4, [[0, 2], [2, 1], [1, 3], [3, 0]])));
  });

  test("exhaustive enumeration matches known connected unlabeled counts", () => {
    expect(exhaustiveClasses(4)).toEqual({ classes: 6, labeled: 38 });
    expect(exhaustiveClasses(5)).toEqual({ classes: 21, labeled: 728 });
    expect(exhaustiveClasses(6)).toEqual({ classes: 112, labeled: 26_704 });
  }, 30_000);

  test("symmetric graphs canonicalize within bounded time", () => {
    const cubic10 = relabel(petersen, 1);
    canonicalForm(ring(10));
    expect(elapsed(() => canonicalForm(ring(10)))).toBeLessThan(100);
    expect(elapsed(() => canonicalForm(cubic10))).toBeLessThan(100);
    expect(elapsed(() => canonicalForm(ring(16)))).toBeLessThan(1000);
    const star = graph(24, Array.from({ length: 23 }, (_, leaf): [number, number] => [0, leaf + 1]));
    const complete: [number, number][] = [];
    for (let a = 0; a < 14; a++) for (let b = a + 1; b < 14; b++) complete.push([a, b]);
    expect(elapsed(() => canonicalForm(star))).toBeLessThan(1000);
    expect(elapsed(() => canonicalForm(graph(14, complete)))).toBeLessThan(1000);
    expect(elapsed(() => canonicalForm(rook))).toBeLessThan(1000);
  });

  test("digests and classes group isomorphic designs", () => {
    const digest = topologyDigest(ring(6));
    expect(digest).toMatch(/^sha256:[0-9a-f]{64}$/);
    expect(topologyDigest(relabel(ring(6), 9))).toBe(digest);
    const classes = topologyClasses([ring(6), k33, relabel(ring(6), 2), prism, relabel(k33, 4)]);
    expect(classes.map((entry) => entry.members).sort()).toEqual([[0, 2], [1, 4], [3]]);
    expect(classes.map((entry) => entry.digest)).toEqual(classes.map((entry) => entry.digest).sort());
    expect(classes.find((entry) => entry.members.includes(0))!.digest).toBe(digest);
    expect(topologyClasses([])).toEqual([]);
  });

  test("invalid designs are rejected", () => {
    expect(() => canonicalForm(graph(6, [[0, 1], [1, 2], [0, 2], [3, 4], [4, 5], [3, 5]]))).toThrow("connected");
    expect(() => canonicalForm(graph(3, [[0, 1], [1, 2]]))).toThrow("graph.nodes");
    expect(() => canonicalForm(graph(4, [[0, 0], [0, 1], [1, 2], [2, 3]]))).toThrow("self loops");
    expect(() => canonicalForm(graph(4, [[0, 1], [1, 0], [1, 2], [2, 3]]))).toThrow("duplicates");
    expect(() => canonicalForm(graph(4, [[0, 1], [1, 2], [2, 4]]))).toThrow("edge node");
    expect(() => canonicalForm({ ...ring(4), extra: true } as Graph)).toThrow("exactly");
    expect(() => topologyDigest(JSON.parse('{"nodes":4}') as Graph)).toThrow();
    expect(() => isomorphic(ring(4), graph(25, []))).toThrow("graph.nodes");
  });
});
