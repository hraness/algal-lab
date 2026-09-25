# Contributing

Read [AGENTS.md](AGENTS.md), [architecture](docs/architecture.md), and
[research method](docs/research-method.md) before changing experiment semantics.
Use Bun 1.3.14, the version pinned in CI, and install the committed lockfile:

```sh
bun install --frozen-lockfile
bun run check
bun run demo
bun run lab verify runs/demo
bun run qualify:instrument
bun run qualify
bun run lab verify-qualification runs/qualification
```

The demo needs no credentials or paid inference. Studies require a new output
directory; they do not overwrite or resume earlier evidence, and
`qualify:instrument` likewise refuses to overwrite `runs/instrument-qualification.json`
(pass another path to `bun scripts/qualify-instrument.ts`, or no path for
stdout). To keep another run, select an unused path:

```sh
bun run lab study --protocol examples/network-study.json --out runs/custom
bun run lab verify runs/custom
```

An optional model run uses a wrapper you control:

```sh
bun run lab study --protocol examples/network-study.json --out runs/model-study \
  --executor-command './my-provider-wrapper'
```

The wrapper reads ALGAL request JSON from stdin and writes only the required
proposal JSON to stdout. Research context is at `request.context.inputs.context`;
[the scripted executor example](examples/scripted-executor.ts) shows the wire
shape without a provider. The wrapper owns provider authentication. Read
[SECURITY.md](SECURITY.md) before using it. Do not commit generated runs, private
wrapper configuration, credentials, local paths, or provider secrets.

Keep changes focused. Update contracts, instrument identity, fixtures, tests,
and method documentation together when altering an experiment's meaning.
Old runs require their recorded source version for verification; changing a
source file bound by the instrument or application identity changes that
verification target. The archive contains full receipts and has no `.algal`
directory dependency. See [artifact verification](docs/architecture.md#artifact-boundary).
Preserve requested and realized designs, failed attempts, exact parent
references, predictions, and observations. Do not edit recorded outcomes to
match a new implementation or reuse holdouts silently. Tests should exercise
mathematical examples, contract rejection, evidence tampering, or study
invariants rather than merely copy implementation logic.

Use a feature branch and a pull request. The repository follows checked-PR
delivery: an independent agent review and the required `Check` CI job must pass
before merge. The integration owner runs the aggregate check after workers
converge and owns the CI wait; focused checks belong to their implementers.
Record exact commands, outcomes, and limitations in the PR. Do not force-push or
bypass repository protections.

Delivery is public source in this repository. A hosted deployment or package
release is not required for this headless application. Describe proposed
follow-up work as proposed, and describe live model results only when a retained
run supports the claim.

The credential-free [weighted-tree research](docs/weighted-tree-discovery.md)
also has exact Python certificates, run by CI in addition to `bun run check`:

```sh
python3 research/spikes/structural/verify.py
python3 research/spikes/weighted-tree/verify.py
python3 -m unittest research.test_tree_certificate research.test_certify_policy_results research.test_terminal_tree research.test_terminal_sampling research.test_terminal_hybrid research.test_survivor_order research.test_ordered_pairing research.test_frugal_experiment research.test_rank_selection research.test_two_failure_groups research.test_intact_groups research.test_context_certificate research.test_stochastic_groups research.test_robust_stochastic_groups research.test_mixture_stochastic_groups research.test_softmax_partition_dp research.test_softmax_partition
python3 -m research.spikes.ordered.verify
python3 -m research.spikes.rank.verify
python3 -m research.spikes.groups.verify
python3 -m research.spikes.intact.verify
python3 -m research.spikes.context.verify
python3 -m research.spikes.stochastic.verify
python3 -m research.spikes.softmax_partitions.experiment --out research/spikes/context/runs/softmax-partition-study
```

The [certified softmax occupancy solver](docs/certified-softmax-partitions.md)
uses rational interval arithmetic, bounded occupancy scans for two agents
or at most three tasks, and an exact-budget DP for the remaining cases. Its
[universal purity theorem](docs/softmax-universal-purity.md) makes every
admitted positive-temperature result continuous; historical v1/v2 receipts
retain their original `pure-only` labels. Its solver unit-test modules are
included above; the fixed 20-case study also runs in CI. Choose an unused
output path for each local study.

The [additive-boundary theorem](docs/softmax-additive-boundary.md) and
[constrained flow optimizer](docs/softmax-additive-flow.md) concern an additive
outer reward. Their checks run as
`python3 -m unittest research.test_softmax_additive_boundary research.test_softmax_additive_flow`.
The flow API takes exact rational `exp(t_j)` values and supplies a residual
optimality certificate. The [negative-outer-temperature note](docs/softmax-negative-outer.md)
covers `τ≤0`; its exact-witness checks run as
`python3 -m unittest research.test_softmax_negative_outer`. This is separate from v3's positive-outer-temperature
input contract.

Proof text, finite exhaustive checks, policy holdouts, and novelty claims are
separate evidence. Keep research TypeScript in the aggregate typecheck and tests.
Keep generated experimental archives under ignored `runs/` directories; commit
the reproducible protocol, source, and an honest findings report.

The [terminal-tree optimizer](docs/terminal-tree-discovery.md) is a separate
two-survivor endpoint. Its exact and sampling algorithms use the Python standard
library and are covered by the same CI unit-test command. Its frozen experiment
is reproducible separately; local timing thresholds are not CI performance gates.

The [ordered-survival theorem](docs/ordered-survival-discovery.md) concerns all
fixed horizons and the expected number of working pairs. Its pairing solver
needs no probability estimates. The separate small-model conjecture pilot keeps
its protocol and source frozen before inference, records provider failures,
and compares against a zero-model enumeration control. Offline CI uses mocked
transport and never performs paid inference. Model receipts cannot establish
literature priority or credit a model with investigator-supplied ideas.

The [rank-selection and group results](docs/rank-selection-and-triples.md)
add independent polynomial and categorical probability calculations, exact
countermodels, and bounded examples of a complexity reduction. The two-failure
group oracle computes a universal additive regret bound; this is a proved bound,
not a measured regret. Keep the unbounded theorem distinct from executable
input caps and finite checks. Track source-reading coverage in the
[novelty ledger](docs/novelty-ledger.md).
