# Architecture

Algal Lab is a headless Bun/TypeScript application that uses ALGAL for typed
researcher execution and receipts. The laboratory owns the experiment contract,
simulator, study protocol, artifact archive, and interpretation of results.
It does not fork ALGAL or require Valhalla.

The runtime dependency is pinned to
[`f899456e497656eb292d97d7c0aef5e06f1437dc`](https://github.com/hraness/algal/tree/f899456e497656eb292d97d7c0aef5e06f1437dc)
in [package.json](../package.json) and the lockfile. Upgrading it is a reviewed
compatibility change, not part of a researcher's search space.
The lab's [contracts](../src/contracts.ts) define protocol and proposal admission.

## Execution and evidence

```text
study protocol + prior-round evidence
                |
                v
ALGAL researcher: design + hypothesis + prediction + rationale + parents
                |
                v
strict lab admission -> fixed simulator tool -> measured trajectories
                |                                  |
                +---------- experiment ------------+
                                |
                                v
content-addressed artifacts + complete ALGAL receipts
                                |
                  frozen condition portfolios
                                |
             held-out random schedules + targeted control
```

A proposal is data. The host validates its fields and graph budget before the
simulator accepts it. The hypothesis and prediction are recorded in the agent
effect before the tool observation they concern. Parent references identify the
prior experiments used by the researcher; they do not themselves prove a causal
influence or an improvement. Failed attempts remain part of the study record.

Each round starts from a fixed snapshot. Researchers cannot see a peer's output
from the same round. The protocol determines whether the next round exposes only
the researcher's own graphs and discovery scores, all researchers' graphs and
scores, or those fields plus bounded messages. Context retains at most the last
24 visible successful experiments and, in the message-enabled condition, the
last 12 messages. The simulator and proposal budgets stay the same across these
conditions. All replicate/condition portfolios freeze before any held-out
evaluation begins. See [research method](research-method.md).

The first instrument operates on small undirected graphs. It does not execute
generated programs. Its inputs, random choices, failure rule, and metric
definition determine its observations. Requested designs and realized graphs
are retained separately so an instrument or generator discrepancy can be
investigated rather than hidden by a summary score.

## Artifact boundary

Each run has a new output directory:

| Path | Contents |
| --- | --- |
| `protocol.json` | Admitted protocol intent, written before experiments begin. |
| `study.json` | The final report object and its canonical-content digest. |
| `artifacts/<sha256 hex>.json` | The researcher manifest, complete attempts, frozen portfolios, per-design evaluations, and evaluation batches. References use the `sha256:` prefix; filenames omit it. |
| `report.md` | A generated human-readable summary. Its text is not verified by the CLI. |

Each attempt retains its context, full ALGAL receipt, and either its measurement
or `null` after a failed run. `boundedResearcher` admits at most 8,192 canonical
JSON bytes and structural depth 16 before ALGAL records output. Rejected output
becomes a bounded effect error. Admitted output that later fails proposal
validation remains in the receipt; successful measurements carry the admitted
proposal and canonical realized graph.
An `algal.lab.evaluation.v1` batch stores per-design digests in `designs`.
Each resolves to an `algal.lab.design-evaluation.v1` artifact containing that
design's trajectories and mean AUC, keeping individual artifacts bounded.
ALGAL uses an in-memory store during execution. There is no `.algal` directory
to copy or provider connection to reopen for verification.

[`verifyStudy`](../src/study.ts) reconstructs the whole study with ALGAL's
`runOrganism`, using `replayExecutor` for recorded agent effects and executing the
admitted simulator tool afresh. It compares complete regenerated attempts,
including their receipts, portfolios, evaluations, and the report against the
content-addressed evidence. It also reconstructs researcher visibility rather
than trusting the saved context. The CLI uses this application-level
reconstruction; ALGAL's standalone `verifyReceipt` is not its verification path.
It does not call a model provider or the original executor.

These are distinct checks:

| Check | Evidence it provides |
| --- | --- |
| Artifact integrity | Canonical JSON values match their content references; whitespace and key order are not significant. |
| Full receipt reconstruction | ALGAL execution with recorded agent effects reproduces each complete attempt and its receipt. |
| Fresh simulator run | The retained graph and failure schedule reproduce the recorded numerical result with this instrument. |
| Scientific validation | Requires additional domain evidence; none of the checks above establishes it. |

Verification requires the recorded source identities. The instrument identity
binds `network.ts` and `network.v1`; the application identity binds `network.ts`,
`contracts.ts`, `researcher.ts`, `study.ts`, `artifacts.ts`, and the root `cli.ts`,
`package.json`, and `bun.lock`. Use the recorded source revision and pinned
dependency when verifying an older run. The digest field named
`applicationDigest` is not a hash of every repository file.

Hashes do not authenticate the author, establish an external timestamp, or prove
that no unrecorded trial occurred. An operator who controls the files can replace
an entire internally consistent history. Precommitment and portfolio freezing
are enforced within this application workflow, not by an external notarization
service.

## Executor boundary

The default executor is a deterministic, credential-free script. It exercises
the same lab contract and evidence path as a model executor, but its behavior is
not evidence of LLM reasoning or scientific discovery. It uses visible graphs
and scores, but ignores message text. Its message-enabled condition therefore
does not test whether an LLM benefits from communication.

`--executor-command` explicitly selects an operator-owned wrapper through
ALGAL's `commandExecutor`. The wrapper receives request JSON on stdin and
returns response JSON on stdout. It owns model selection, authentication, and
provider interaction. The lab admits only bounded proposal data from that
response; it never turns a proposed command into host authority. The wrapper
itself is ordinary host code, not sandboxed generated code. See
[security](../SECURITY.md).

This version has no persistent service, browser UI, distributed workers, resume
workflow, automatic instrument installation, or autonomous generator evolution.
Those require separate contracts and evidence described in the
[roadmap](roadmap.md).
