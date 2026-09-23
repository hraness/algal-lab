import { describe, expect, test } from "bun:test";
import { bootstrapMeanInterval, enumerateSignFlipP, pairedInference, signFlipTest, wilcoxonSignedRank } from "./statistics";

// Brute-force reference: average ranks of |d|, then all 2^m sign assignments.
function bruteWilcoxon(differences: number[]): number {
  const values = differences.filter((v) => v !== 0);
  const ranks = values.map((v) => {
    const below = values.filter((w) => Math.abs(w) < Math.abs(v)).length, equal = values.filter((w) => Math.abs(w) === Math.abs(v)).length;
    return below + (equal + 1) / 2;
  });
  const total = ranks.reduce((a, b) => a + b, 0), observed = values.reduce((a, v, i) => a + (v > 0 ? ranks[i]! : 0), 0);
  let hits = 0;
  for (let mask = 0; mask < 1 << values.length; mask++) {
    const w = ranks.reduce((a, r, i) => a + (mask & (1 << i) ? r : 0), 0);
    if (Math.abs(w - total / 2) >= Math.abs(observed - total / 2) - 1e-9) hits++;
  }
  return hits / 2 ** values.length;
}

describe("sign-flip test", () => {
  test("known exact values", () => {
    expect(signFlipTest([1, 1, 1, 1, 1, 1])).toEqual({ count: 6, mean: 1, pValue: 2 / 64, exact: true, permutations: 64 });
    expect(signFlipTest([0.1, -0.1, 0.2, -0.2]).pValue).toBe(1);
    // |sum| >= 4 for [1,1,1,1,0]: only all-plus or all-minus of the nonzero entries, times 2 for the zero.
    expect(signFlipTest([1, 1, 1, 1, 0]).pValue).toBe(4 / 32);
    // [3,1,1,1]: |sum| >= 6 requires the 3 and all ones aligned, or 3 with two ones and one opposed (sum 4 < 6).
    expect(signFlipTest([0.3, 0.1, 0.1, 0.1]).pValue).toBe(2 / 16);
  });

  test("Monte Carlo branch agrees with exact enumeration when zeros make it feasible", () => {
    const nonzero = [0.12, -0.05, 0.08, 0.2, -0.1, 0.03, 0.07, -0.02, 0.15, 0.01, -0.06, 0.09, 0.04, -0.11, 0.05, 0.02, 0.1, -0.03, 0.06, 0.13, -0.01, 0.02];
    const padded = [...nonzero, 0, 0, 0];
    const exact = enumerateSignFlipP(nonzero), sampled = signFlipTest(padded);
    expect(sampled.exact).toBe(false);
    expect(sampled.permutations).toBe(100_000);
    expect(exact).toBeGreaterThan(0.01); expect(exact).toBeLessThan(0.5);
    expect(Math.abs(sampled.pValue - exact)).toBeLessThan(0.01);
    expect(signFlipTest(padded)).toEqual(sampled);
  });

  test("exact branch at n = 20 matches the enumeration helper", () => {
    const values = Array.from({ length: 20 }, (_, i) => ((i * 7) % 11 - 4) / 20);
    expect(signFlipTest(values).pValue).toBe(enumerateSignFlipP(values));
    expect(() => enumerateSignFlipP([...values, 0, 0, 0])).toThrow();
  });
});

describe("Wilcoxon signed-rank", () => {
  test("known exact values", () => {
    expect(wilcoxonSignedRank([1, 2, 3, 4, 5, 6].map((v) => v / 10))).toEqual({ statistic: 21, nonZero: 6, pValue: 2 / 64 });
    // Hand-computed tie case: ranks 1.5, 1.5, 3, 4; W+ = 8.5; 6 of 16 subsets are as extreme.
    expect(wilcoxonSignedRank([0.1, -0.1, 0.2, 0.3])).toEqual({ statistic: 8.5, nonZero: 4, pValue: 6 / 16 });
    expect(wilcoxonSignedRank([0, 0, 0, 0])).toEqual({ statistic: 0, nonZero: 0, pValue: null });
    expect(wilcoxonSignedRank(Array.from({ length: 31 }, () => 0.1)).pValue).toBeNull();
    expect(wilcoxonSignedRank(Array.from({ length: 30 }, () => 0.1)).pValue).toBe(2 / 2 ** 30);
  });

  test("dynamic programming agrees with brute-force enumeration, including ties and zeros", () => {
    const cases = [[0.2, -0.1, 0.4, 0.1, -0.3, 0.5, 0.0, 0.2], [0.05, 0.05, -0.05, 0.1, -0.2, 0.3], [-0.4, -0.1, 0.1, -0.2, 0.3, -0.5, 0.2, 0.6, -0.7, 0.8, 0.1, -0.1]];
    for (const values of cases) expect(wilcoxonSignedRank(values).pValue).toBeCloseTo(bruteWilcoxon(values), 12);
  });
});

describe("bootstrap interval", () => {
  const values = [0.05, 0.12, -0.03, 0.08, 0.02, 0.1, 0.06, -0.01];

  test("is deterministic per seed and close across seeds", () => {
    const a = bootstrapMeanInterval(values), b = bootstrapMeanInterval(values), c = bootstrapMeanInterval(values, { seed: 7 });
    expect(a).toEqual(b);
    expect(a).toMatchObject({ resamples: 10_000, seed: 0x5eed, level: 0.95 });
    expect(c).not.toEqual(a);
    expect(Math.abs(c.lower - a.lower)).toBeLessThan(0.01); expect(Math.abs(c.upper - a.upper)).toBeLessThan(0.01);
    expect(a.lower).toBeLessThan(a.mean); expect(a.upper).toBeGreaterThan(a.mean);
  });

  test("constant data has a degenerate interval", () => {
    const result = bootstrapMeanInterval([0.1, 0.1, 0.1, 0.1, 0.1, 0.1]);
    expect(result.lower).toBe(result.mean); expect(result.upper).toBe(result.mean);
  });

  test("interval shrinks with more data", () => {
    const base = [0.05, 0.15, 0.0, 0.1];
    const width = (n: number) => { const r = bootstrapMeanInterval(Array.from({ length: n }, (_, i) => base[i % 4]!)); return r.upper - r.lower; };
    expect(width(16)).toBeLessThan(width(4)); expect(width(64)).toBeLessThan(width(16));
  });

  test("rejects unbounded options", () => {
    expect(() => bootstrapMeanInterval(values, { resamples: 100_001 })).toThrow();
    expect(() => bootstrapMeanInterval(values, { resamples: 1.5 })).toThrow();
    expect(() => bootstrapMeanInterval(values, { seed: -1 })).toThrow();
    expect(() => bootstrapMeanInterval(values, { level: 1 })).toThrow();
  });
});

describe("paired inference", () => {
  test("verdict branches", () => {
    const large = pairedInference([0.2, 0.25, 0.3, 0.22, 0.28, 0.24], 0.05);
    expect(large.verdict).toBe("exceeds-margin");
    expect(large.bootstrap.lower).toBeGreaterThan(0.05);
    expect(pairedInference([0.01, -0.01, 0.02, -0.02, 0.0, 0.01, -0.01, 0.0], 0.05).verdict).toBe("within-margin");
    expect(pairedInference([0.3, -0.3, 0.2, -0.1, 0.25, -0.2], 0.05).verdict).toBe("inconclusive");
    // A confidently negative effect gets its own verdict.
    expect(pairedInference([-0.2, -0.25, -0.3, -0.22, -0.28, -0.24], 0.05).verdict).toBe("below-margin");
    // Zero margin cannot establish "within-margin".
    expect(pairedInference([0, 0, 0, 0], 0).verdict).toBe("inconclusive");
  });

  test("reports descriptive counts alongside all tests", () => {
    const result = pairedInference([0.1, 0, -0.05, 0.2, 0.1], 0.02);
    expect(result).toMatchObject({ count: 5, minimum: -0.05, maximum: 0.2, wins: 3, ties: 1, losses: 1, margin: 0.02 });
    expect(result.mean).toBeCloseTo(0.07, 12);
    expect(result.signFlip.exact).toBe(true); expect(result.wilcoxon.nonZero).toBe(4);
  });

  test("input validation", () => {
    for (const bad of [[0.1, 0.1, 0.1], Array.from({ length: 65 }, () => 0), [0.1, 0.1, 0.1, 1.5], [0.1, 0.1, 0.1, Number.NaN], [0.1, 0.1, 0.1, Infinity]]) {
      expect(() => pairedInference(bad, 0.05)).toThrow();
      expect(() => signFlipTest(bad)).toThrow();
      expect(() => wilcoxonSignedRank(bad)).toThrow();
      expect(() => bootstrapMeanInterval(bad)).toThrow();
    }
    for (const margin of [-0.01, 0.51, Number.NaN]) expect(() => pairedInference([0.1, 0.1, 0.1, 0.1], margin)).toThrow();
  });
});
