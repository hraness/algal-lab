import { test, expect } from "bun:test";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";

test("Required preserves PR-only filtered skips with Bash only on slim", () => {
  const block = readFileSync(new URL("../.github/workflows/check.yml", import.meta.url), "utf8").split("  required:\n")[1]!;
  expect(block).toBe(`    name: Required
    if: always()
    needs: [changes, ts, pyunit, extremal, research, pipeline]
    runs-on: ubuntu-slim
    timeout-minutes: 5
    steps:
      - name: Require every selected job
        env:
          EVENT: \${{ github.event_name }}
          CHANGES: \${{ needs.changes.result }}
          CI: \${{ needs.changes.outputs.ci }}
          RESULTS: >-
            ts=\${{ needs.ts.result }}:\${{ needs.changes.outputs.ts }}
            pyunit=\${{ needs.pyunit.result }}:\${{ needs.changes.outputs.pyunit }}
            extremal=\${{ needs.extremal.result }}:\${{ needs.changes.outputs.extremal }}
            research=\${{ needs.research.result }}:\${{ needs.changes.outputs.spikes }}
            pipeline=\${{ needs.pipeline.result }}:\${{ needs.changes.outputs.ts }}
        run: |
          set -euo pipefail
          if [[ "$CHANGES" != success ]]; then
            printf 'Change detection did not succeed: %s\\n' "$CHANGES"
            exit 1
          fi
          status=0
          for entry in $RESULTS; do
            job="\${entry%%=*}"
            rest="\${entry#*=}"
            result="\${rest%%:*}"
            changed="\${rest#*:}"
            if [[ "$result" == success ]]; then
              continue
            fi
            # A job may skip only on a pull request whose change filter reported its inputs unchanged.
            if [[ "$result" == skipped && "$EVENT" == pull_request && "$changed" == false && "$CI" == false ]]; then
              printf '%s skipped: inputs unchanged\\n' "$job"
              continue
            fi
            printf 'Unexpected required job result for %s: %s (changed=%s)\\n' "$job" "$result" "$changed"
            status=1
          done
          exit "$status"
`);
  const script = block.split("        run: |\n")[1]!.replace(/^          /gm, "");
  const jobs = ["ts", "pyunit", "extremal", "research", "pipeline"];
  const cases: Array<{ event: string; changes: string; ci: string; changed: string; status: string; results: string }> = [];
  for (const event of ["pull_request", "push", "workflow_dispatch"])
    for (const changes of ["success", "failure", "cancelled", "skipped", ""])
      for (const ci of ["true", "false", ""])
        for (const changed of ["true", "false", ""])
          for (const status of ["success", "failure", "cancelled", "skipped", ""])
            for (const selected of jobs)
              cases.push({
                event, changes, ci, changed, status,
                results: jobs.map(job => `${job}=${job === selected ? status : "success"}:${changed}`).join(" "),
              });

  // Keep every case isolated (the workflow calls exit), but start Bash only once.
  // The delimiter cannot occur in these enumerated inputs or their RESULTS fields.
  const input = cases.map(({ event, changes, ci, results }) => [event, changes, ci, results].join("|")).join("\n") + "\n";
  const batch = `while IFS='|' read -r EVENT CHANGES CI RESULTS; do
  (eval "$1") >/dev/null 2>&1
  printf '%s\\n' "$?"
done`;
  const result = spawnSync("/bin/bash", ["--noprofile", "--norc", "-c", batch, "batch", script], {
    env: { PATH: "/nonexistent" }, input, encoding: "utf8", timeout: 28000,
  });
  expect(result.error).toBeUndefined();
  expect(result.status).toBe(0);
  const actual = result.stdout.trimEnd().split("\n");
  expect(actual).toHaveLength(cases.length);
  for (const [index, { event, changes, ci, changed, status }] of cases.entries()) {
    expect(actual[index]).toMatch(/^[01]$/);
    expect(actual[index] === "0").toBe(changes === "success" && (status === "success" || (status === "skipped" && event === "pull_request" && changed === "false" && ci === "false")));
  }
}, 30000);
