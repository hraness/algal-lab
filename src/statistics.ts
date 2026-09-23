// Paired-difference inference for small replicate sets. Everything here is
// deterministic, dependency-free, and bounded: 4..64 differences in [-1, 1],
// at most 100,000 resamples. These are descriptive aids for a preregistered
// comparison; none of them establishes scientific validity on its own.

export type SignFlipResult = { count: number; mean: number; pValue: number; exact: boolean; permutations: number };
export type BootstrapInterval = { mean: number; lower: number; upper: number; resamples: number; seed: number; level: number };
export type WilcoxonResult = { statistic: number; nonZero: number; pValue: number | null };
export type Verdict = "exceeds-margin" | "below-margin" | "within-margin" | "inconclusive";
export type PairedInference = {
  count: number; mean: number; minimum: number; maximum: number; wins: number; ties: number; losses: number;
  signFlip: SignFlipResult; bootstrap: BootstrapInterval; wilcoxon: WilcoxonResult; margin: number; verdict: Verdict;
};

const MIN_COUNT = 4;
const MAX_COUNT = 64;
const TOLERANCE = 1e-12;
const EXACT_SIGN_FLIP = 20;
const ENUMERABLE_SIGN_FLIP = 22;
const SIGN_FLIP_DRAWS = 100_000;
const SIGN_FLIP_SEED = 0x51f1_0b5e;
const MAX_RESAMPLES = 100_000;
const MAX_WILCOXON = 30;
const UINT32_MAX = 0xffff_ffff;

function differencesOf(values: number[], maximum = MAX_COUNT): number[] {
  if (!Array.isArray(values) || values.length < MIN_COUNT || values.length > maximum) throw new Error(`paired differences must number ${MIN_COUNT}..${maximum}`);
  if (values.some((v) => typeof v !== "number" || !Number.isFinite(v) || Math.abs(v) > 1)) throw new Error("paired differences must be finite values in [-1, 1]");
  return [...values];
}

// Fixed left-to-right summation so identical inputs yield bit-identical means.
function sum(values: number[]): number { let total = 0; for (const v of values) total += v; return total; }
function average(values: number[]): number { return sum(values) / values.length; }

// Mulberry32, reimplemented identically to the unexported `random` in network.ts.
function mulberry32(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let mixed = Math.imul(state ^ (state >>> 15), state | 1);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), mixed | 61);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 0x1_0000_0000;
  };
}

// All signed subset sums of `values`, indexed by a bitmask of negated entries.
function signedSums(values: number[]): Float64Array {
  const sums = new Float64Array(1 << values.length);
  sums[0] = sum(values);
  for (let mask = 1; mask < sums.length; mask++) {
    const bit = 31 - Math.clz32(mask);
    sums[mask] = sums[mask ^ (1 << bit)]! - 2 * values[bit]!;
  }
  return sums;
}

/** Exact two-sided sign-flip p over all 2^n assignments (n <= 22), by meet-in-the-middle. Exposed for tests. */
export function enumerateSignFlipP(differences: number[]): number {
  const values = differencesOf(differences, ENUMERABLE_SIGN_FLIP);
  const half = values.length >> 1;
  const left = signedSums(values.slice(0, half)), right = signedSums(values.slice(half));
  const threshold = Math.abs(left[0]! + right[0]!) - TOLERANCE * values.length;
  let hits = 0;
  for (const a of left) for (const b of right) if (Math.abs(a + b) >= threshold) hits++;
  return hits / (left.length * right.length);
}

/**
 * Two-sided Fisher-Pitman sign-flip test of H0: differences symmetric about zero,
 * statistic |mean|. Exact enumeration for n <= 20; otherwise 100,000 fixed-seed
 * Monte Carlo draws with p = (hits + 1) / (draws + 1), counting the observed
 * assignment once. Zeros are kept; they cannot change |mean| under flipping.
 */
export function signFlipTest(differences: number[]): SignFlipResult {
  const values = differencesOf(differences);
  const mean = average(values);
  if (values.length <= EXACT_SIGN_FLIP) return { count: values.length, mean, pValue: enumerateSignFlipP(values), exact: true, permutations: 2 ** values.length };
  const next = mulberry32(SIGN_FLIP_SEED);
  const threshold = Math.abs(sum(values)) - TOLERANCE * values.length;
  let hits = 0;
  for (let draw = 0; draw < SIGN_FLIP_DRAWS; draw++) {
    let total = 0;
    for (const v of values) total += next() < 0.5 ? -v : v;
    if (Math.abs(total) >= threshold) hits++;
  }
  return { count: values.length, mean, pValue: (hits + 1) / (SIGN_FLIP_DRAWS + 1), exact: false, permutations: SIGN_FLIP_DRAWS };
}

// Linear interpolation between order statistics (Hyndman-Fan type 7).
function quantile(sorted: Float64Array, probability: number): number {
  const position = probability * (sorted.length - 1), low = Math.floor(position), high = Math.ceil(position);
  return sorted[low]! + (sorted[high]! - sorted[low]!) * (position - low);
}

/** Percentile bootstrap interval for the mean; deterministic for a given seed. */
export function bootstrapMeanInterval(differences: number[], options: { resamples?: number; seed?: number; level?: number } = {}): BootstrapInterval {
  const values = differencesOf(differences);
  const resamples = options.resamples ?? 10_000, seed = options.seed ?? 0x5eed, level = options.level ?? 0.95;
  if (!Number.isInteger(resamples) || resamples < 100 || resamples > MAX_RESAMPLES) throw new Error(`resamples must be an integer 100..${MAX_RESAMPLES}`);
  if (!Number.isInteger(seed) || seed < 0 || seed > UINT32_MAX) throw new Error("seed must be a uint32");
  if (!Number.isFinite(level) || level < 0.5 || level > 0.999) throw new Error("level must be in [0.5, 0.999]");
  const next = mulberry32(seed), means = new Float64Array(resamples), sample = new Array<number>(values.length);
  for (let r = 0; r < resamples; r++) {
    for (let i = 0; i < values.length; i++) sample[i] = values[Math.floor(next() * values.length)]!;
    means[r] = average(sample);
  }
  means.sort();
  const alpha = (1 - level) / 2;
  return { mean: average(values), lower: quantile(means, alpha), upper: quantile(means, 1 - alpha), resamples, seed, level };
}

/**
 * Exact two-sided Wilcoxon signed-rank test. Zeros (|d| <= 1e-12) are dropped;
 * tied |d| receive average ranks. The null distribution of W+ over the realized
 * (possibly tied) ranks is enumerated by dynamic programming on doubled ranks;
 * p = P(|W+ - T/2| >= |observed - T/2|). p is null when nonZero is 0 or > 30.
 */
export function wilcoxonSignedRank(differences: number[]): WilcoxonResult {
  const values = differencesOf(differences).filter((v) => Math.abs(v) > TOLERANCE).sort((a, b) => Math.abs(a) - Math.abs(b));
  const doubled = new Array<number>(values.length);
  for (let start = 0; start < values.length;) {
    let end = start + 1;
    while (end < values.length && Math.abs(values[end]!) - Math.abs(values[start]!) <= TOLERANCE) end++;
    for (let i = start; i < end; i++) doubled[i] = start + end + 1; // 2 * mean of ranks start+1..end
    start = end;
  }
  const observed = values.reduce((total, v, i) => total + (v > 0 ? doubled[i]! : 0), 0);
  const nonZero = values.length;
  if (nonZero < 1 || nonZero > MAX_WILCOXON) return { statistic: observed / 2, nonZero, pValue: null };
  const total = nonZero * (nonZero + 1);
  let counts = new Float64Array(total + 1); counts[0] = 1; // exact: counts <= 2^30
  for (const rank of doubled) {
    const updated = Float64Array.from(counts);
    for (let s = rank; s <= total; s++) updated[s]! += counts[s - rank]!;
    counts = updated;
  }
  let extreme = 0;
  for (let s = 0; s <= total; s++) if (Math.abs(s - total / 2) >= Math.abs(observed - total / 2)) extreme += counts[s]!;
  return { statistic: observed / 2, nonZero, pValue: extreme / 2 ** nonZero };
}

/**
 * Descriptive paired inference with a preregistered practical margin. Verdicts
 * read only the 95% percentile bootstrap interval [lower, upper] for the mean:
 * - "exceeds-margin": lower > margin (a positive effect larger than the margin);
 * - "within-margin": -margin < lower and upper < margin (confidently smaller than
 *   the margin in either direction);
 * - "below-margin": upper < -margin (a negative effect larger than the margin);
 * - "inconclusive": anything else.
 * This is a fixed decision rule over small, replicate-level samples, not a proof;
 * the sign-flip and Wilcoxon p-values are reported alongside and do not change it.
 */
export function pairedInference(differences: number[], margin: number): PairedInference {
  const values = differencesOf(differences);
  if (typeof margin !== "number" || !Number.isFinite(margin) || margin < 0 || margin > 0.5) throw new Error("margin must be in [0, 0.5]");
  const bootstrap = bootstrapMeanInterval(values);
  const verdict: Verdict = bootstrap.lower > margin ? "exceeds-margin" : bootstrap.upper < -margin ? "below-margin"
    : bootstrap.upper < margin && bootstrap.lower > -margin ? "within-margin" : "inconclusive";
  return { count: values.length, mean: average(values), minimum: Math.min(...values), maximum: Math.max(...values),
    wins: values.filter((v) => v > TOLERANCE).length, ties: values.filter((v) => Math.abs(v) <= TOLERANCE).length,
    losses: values.filter((v) => v < -TOLERANCE).length,
    signFlip: signFlipTest(values), bootstrap, wilcoxon: wilcoxonSignedRank(values), margin, verdict };
}
