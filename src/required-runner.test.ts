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
  for (const EVENT of ["pull_request", "push", "workflow_dispatch"])
    for (const CHANGES of ["success", "failure", "cancelled", "skipped", ""])
      for (const CI of ["true", "false", ""])
        for (const changed of ["true", "false", ""])
          for (const status of ["success", "failure", "cancelled", "skipped", ""])
            for (const selected of jobs) {
              const RESULTS = jobs.map(job => `${job}=${job === selected ? status : "success"}:${changed}`).join(" ");
              const result = spawnSync("/bin/bash", ["--noprofile", "--norc", "-eo", "pipefail", "-c", script], { env: { PATH: "/nonexistent", EVENT, CHANGES, CI, RESULTS }, timeout: 1000 });
              expect(result.error).toBeUndefined();
              expect(result.status === 0).toBe(CHANGES === "success" && (status === "success" || (status === "skipped" && EVENT === "pull_request" && changed === "false" && CI === "false")));
            }
}, 30000);
