/** A local repeated-measurement fixture, not biological inference. */
export function meanAndStandardError(values: readonly number[]): { mean: number; standardError: number } {
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const variance = values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (values.length - 1);
  return { mean, standardError: Math.sqrt(variance / values.length) };
}
