import { closeSync, constants, fstatSync, openSync, readSync } from "node:fs";
import { join } from "node:path";
import { auditFixtureEffects, auditProbe, auditRawRss } from "./prospective";

// Read-only, test-only join. Neither a missing file nor a failed replay authorizes
// recreating evidence, repeating a callback, or running the exhausted v1 study.
function readEvidence(path: string, maximum: number, emptyAllowed: boolean): string {
  const fd = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const stat = fstatSync(fd);
    if (!stat.isFile() || stat.size > maximum || (!emptyAllowed && stat.size === 0))
      throw new Error("missing, unsafe, or oversized evidence file");
    const bytes = Buffer.allocUnsafe(maximum + 1);
    let length = 0;
    while (length < bytes.length) {
      const count = readSync(fd, bytes, length, bytes.length - length, null);
      if (count === 0) break;
      length += count;
    }
    if (length !== stat.size || length > maximum) throw new Error("evidence changed during read or exceeds limit");
    return bytes.toString("utf8", 0, length);
  } finally { closeSync(fd); }
}

/** Witness, raw host-PID readings, and the original fixture effect file all must replay. */
export function auditProspectiveEvidence(
  probeDir: string, witnessedDigest: string, spawnedHostPid: number, effectLogPath: string,
  journalTerminals: readonly unknown[], expectedRss: { count: number; baselineBytes: number; peakBytes: number },
): { rss: { count: number; baselineBytes: number; peakBytes: number }; effects: { uncertainIds: string[]; completeIds: string[] } } {
  auditProbe(probeDir, witnessedDigest);
  const rss = auditRawRss(readEvidence(join(probeDir, "rss.jsonl"), 1024 * 1024, false), spawnedHostPid, expectedRss);
  // A present zero-byte effect file can represent a before-effect uncertain job;
  // an absent file cannot establish that it was empty. Never synthesize one.
  const effects = auditFixtureEffects(readEvidence(effectLogPath, 4_000_000, true), journalTerminals);
  return { rss, effects };
}
