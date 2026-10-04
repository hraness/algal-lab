# Contributing

## Choose and continue a research question

Start with [the practical-CS strategy](docs/roadmap.md#research-objective).
After installing the frozen lockfile, `bun run discovery doctor` checks the
no-key entry point and `bun run discovery agenda [track-id]` lists proposed
questions, baselines, references, stopping rules, and focused checks. The agenda
is data; listing it never runs its commands or starts inference.

Contribute a small falsifiable experiment, replication, stronger baseline,
counterexample, primary-source comparison, verifier test, or application
measurement. Preserve null results. A useful contribution need not claim a new
theorem. Before claiming novelty, compare exact assumptions and conclusions with
primary sources; before claiming usefulness, test a named workload and account
for integration and verification costs.

Use a branch from current `main` and a unique private run directory. For work
shared between machines, claim one campaign owner in its handoff record before
running anything, avoid simultaneous writers, and preserve consumed budgets.
Run `bun run discovery verify <run-directory>` on both sides of a copied graph
run; follow the [handoff procedure](docs/discovery-loop.md#verify-before-a-machine-handoff).
`runs/` is not synchronized by a Git pull. Historical archives need their
recorded source and Bun version; a newly cloned `main` can start new work but
must not silently reinterpret old evidence.

The outer-agent skill is a plain Markdown procedure at
`.agents/skills/algal-discovery/SKILL.md`. Read it directly if your agent host does
not discover repository skills. No global agent configuration or sibling
repository is required for local experiments. Publication to a separate website
and optional live providers have their own setup and authorization requirements.

For completed `lab study` archives, reuse the existing evidence and claims
commands rather than inventing another ledger. `bun run lab evidence <study>`
writes the run-local evidence record; `bun run lab verify-evidence <study>`
checks it. `bun run lab claims <study> <drafts.json>` derives claims from cited
records, and `bun run lab verify-claims <study>` checks their support. Drafts
follow `src/claims.ts`. Run `bun run lab verify <study>` for fresh numerical
reproduction as well. These commands do not accept `discovery` directories, and
replay-level evidence cannot justify a stronger scientific or practical claim.

## Prepare tools and datasets

The graph demo needs Bun. Allocation controls also need Python 3.10 or newer
and use only its standard library. Check the available tools before choosing a
track:

```sh
bun install --frozen-lockfile
bun run foundation doctor
mkdir -p runs
```

The readiness report separates core tools, optional native proof builds, and
Elixir/OTP comparisons. It checks versions and availability, not scientific
validity. It installs nothing and does not activate a model provider. On hosts
with a scheduler, use it for builds and broad checks; a scheduler is not a
portable dependency of the repository.

### Public intent data and retrieval controls

CLINC150 is a crowdsourced English single-intent benchmark from Larson et al.,
[EMNLP-IJCNLP 2019](https://www.aclweb.org/anthology/D19-1131/). The preparation
command downloads only its full JSON, license, and README from the pinned
upstream revision. It verifies every file's SHA-256 and length before creating
the output directory. Its upstream license is **CC BY 3.0**, separate from this
repository's MIT code license. Keep the copied license, attribution, source
identity, and transformation record when sharing prepared data.

```sh
bun run foundation fetch clinc150 --out runs/clinc150
bun run foundation verify-dataset runs/clinc150
bun run foundation baseline runs/clinc150 --out runs/clinc150-baseline
bun run foundation verify-baseline runs/clinc150 runs/clinc150-baseline
```

For an offline machine, transfer the prepared directory and verify it there.
Alternatively, `foundation import clinc150 --source PATH --out NEW_PATH`
imports the exact pinned upstream checkout without network access. Existing
outputs are never overwritten; a failed operation keeps any partial directory.

The transform preserves upstream training, validation, and test assignments.
It quarantines **every occurrence** of a duplicate after NFKC normalization,
lowercasing, and replacement of non-letter/non-number runs with spaces. The
manifest records removed IDs and text hashes, source hashes, and partition
hashes. These are text groups, not source/conversation identities: paraphrase
leakage and model-training contamination remain possible. Use this public corpus
for development. A new generalization claim still needs a separately frozen,
source-disjoint evaluation corpus with a defensible access history.

The no-model diagnostic selects at most eight training and two validation
examples per label using a fixed hash order, including the `oos` label. It fits
TF-IDF on training text only, compares cosine nearest-neighbor classification
with majority and seeded random-label controls, and saves predictions and
identities. It requires the pinned prepared-manifest digest and matching training
and validation hashes without reading or scoring `test.json`. `verify-dataset`
also checks the raw sources and reserved test partition.
`verify-baseline` repeats only that development computation, requiring the
recorded source and Bun version. It is not an out-of-scope detection benchmark or
a model-quality claim. CLINC labels are not Textbutler's respond/silent policy;
do not substitute this dataset into that study without a separately reviewed
intent-classification task and protocol. Model-driven selection, context-byte
matched retrieval comparisons, and fresh consumer data remain follow-up work.

### Exact allocation controls

```sh
python3 -m research.foundation_allocation --out runs/allocation-controls
python3 -m research.foundation_allocation --verify runs/allocation-controls
```

This generates 24 small allocation instances from a fixed SHA-256 recipe,
including empty eligibility and zero-capacity cases. It compares the existing
rational flow solver against exhaustive assignment search and a greedy control,
checks each optimality certificate, and rejects an altered certificate. Inputs,
source identities, Python version, and exact rational results are saved. The
sixteen development and eight regression cases are public synthetic model
controls, not a fresh holdout or production scheduling trace. Establish a
workload-supported objective and constraints before claiming practical value.

### Optional native proof tools

A local proof build needs Git, the GitHub CLI, C and C++ compilers, Make, Python,
and network access to the two public source repositories. It downloads the same
CaDiCaL and lrat-trim commits pinned in CI, verifies the checked-out identities
before building, and runs the repository's native and fixed-remainder controls.
It refuses skipped controls and never installs globally.

```sh
bun run foundation setup-proofs --out runs/proof-tools --jobs 2
bun run foundation check-proofs runs/proof-tools
```

On a scheduled host, wrap the setup command with
`host-run --mode=shared --lane=compute --label=algal-proof-tools --`.
Jobs are limited to one through four. Each owned process group has a ten-minute
limit and four-megabyte output limit; interruption stops that group and retains
partial outputs and logs. A complete build writes `toolchain.json` and
`environment.json`. `check-proofs` checks recorded binaries, census, intent,
environment, control-log hashes, and platform. It prints the environment paths
to use with the documented research controls. It does not rerun the tests or authenticate a build made by someone
else. Rebuild native tools on a different OS or architecture. Preserve failed
outputs and choose a new directory for another setup attempt.

Elixir/OTP is optional and is not installed by this command. Follow the
[host comparison requirements](experiments/host-comparison/README.md) if that
experiment is the selected question. No Lean installation, GPU stack, private
conversation import, cloud service, or paid inference is needed for the starting
profiles above. Those are task-specific choices, not prerequisites to fill in
speculatively.

## Validate the software

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
delivery: an independent agent review and the required `Required` CI job must pass
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
python3 -m unittest $(ls research/test_*.py | sed 's#/#.#; s#\.py$##')
python3 -m research.spikes.ordered.verify
python3 -m research.spikes.rank.verify
python3 -m research.spikes.groups.verify
python3 -m research.spikes.intact.verify
python3 -m research.spikes.context.verify
python3 -m research.spikes.stochastic.verify
python3 -m research.spikes.softmax_partitions.experiment --out research/spikes/context/runs/softmax-partition-study
```

The unit-test line runs every `research/test_*.py` module (research/ has no `__init__.py`, so plain `discover`
does not apply). CI runs `research.test_extremal` in its own job; its claim re-verification uses a process pool
capped by `ALGAL_LAB_CLAIM_WORKERS` (default: the lower of the CPU count and 4; set 1 to run serially).

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

The [extremal-construction loop](docs/extremal-discovery.md) keeps its
target registry, verifiers, seed programs, and protocols under
`research/extremal/`. A registry entry must carry the source URL and retrieval
date of its best-known value; an `improves-recorded-best` status is a claim
against that snapshot and needs a same-day re-read of the source before it is
reported. The unit tests run in CI without any model; the local-model protocol
is run by hand and its archive stays under an ignored `runs/` directory.
Reported improvements live in `research/extremal/claims/` with the registry
value they beat, the claim date, and the derivation; `claims.check` re-verifies
each one, so changing a registry value means re-examining its claims. A
registry entry also states its `significance` (how crowded the cell is, with
dated evidence and any open question it bears on), and every claim carries an
unseeded `control` run at the seeded budget; `claims.check` labels a claim
`under-searched` when the cold start reached the recorded value and
`control-missing` when no control exists. The native searches in
`research/extremal/native/` are compiled by the tests when a C compiler is
present.

The [degree-six Ramsey pilot](research/spikes/moonshot-r310/degree_six/README.md)
has native SAT controls as well as small exhaustive checks. CI builds
CaDiCaL 3.0.1 from commit
`c60730422e758ef1cebe7aeddf2dda31c996bf04` with `./configure -fPIC`, links its
static library through the checked local helper, and sets `CADICAL_LIBRARY`
before running every `test_*.py` in that directory. Follow its README for the
local commands. Without that variable, unittest explicitly skips the native
controls; such a run does not replace the complete check. The CI tests use
short controls, not the long research experiments.

The [fixed-remainder exclusion](research/spikes/moonshot-r310/fixed_remainder/README.md)
also checks small SAT models and saved proof handling. CI reuses the pinned
CaDiCaL build, compiles lrat-trim 0.2.0 from commit
`b30f400f4ee5c32b77ee566a7c006081b521534f`, and independently enumerates the
seven input graphs. Its full unittest command sets `CADICAL_LIBRARY`,
`CADICAL_BINARY`, `LRAT_TRIM`, and `SELECTOR_INDEPENDENT_CENSUS`. Missing
variables produce explicit skips and do not replace the full native check.
The independently replayable research proofs are separate release artifacts.

The [nine demand certificates](research/spikes/moonshot-r310/demand_certificates/README.md)
use only Python's standard library. CI runs their five control tests and then
verifies every published certificate, including all 150,902 required
endpoint unions. Their README gives the same two commands for local use.

The [expanded sample](research/spikes/moonshot-r310/demand_certificates/SAMPLE.md)
contains integer certificates for 113 of 128 specified graphs, including the
original nine. CI runs `test_verify_sample.py` and `verify_sample.py` in the
same directory: six controls and 311,618 endpoint-union checks. The proof
uses only the standard library and exact integer arithmetic. The other
15 sample graphs remain unresolved by these certificates.

The [fixed incidence proof](research/spikes/moonshot-r310/incidence_extension/README.md)
excludes sample 19 under an additional minimum-degree-six condition. CI runs
its seven historical model controls from the `incidence_extension` directory
with `python3 -B -m unittest -v test_focused`, then five portable-wrapper
control groups from the repository root:

```sh
python3 -I -B research/spikes/moonshot-r310/incidence_extension/portable/test_verify.py -v
```

Four further control groups explicitly skip without a release packet. Release
validation runs all nine groups with `--packet PATH`, reconstructs the exact
formula and replays its full proof. The result README gives those commands.
Ordinary CI needs no solver run or release download for these new controls.

The [weighted-digit sum-difference construction](papers/sparse-sum-difference/README.md)
proves an exponent greater than 1.18565 for the small-sumset problem. CI checks
the original rational certificate, reconstructs the stronger four-digit
certificate, and runs their controls using only Python's standard library:

```sh
python3 -m unittest discover -s papers/sparse-sum-difference -p 'test_verify.py' -v
python3 papers/sparse-sum-difference/verify.py
python3 -m unittest discover -s papers/sparse-sum-difference -p 'test_carry_verify.py' -v
python3 papers/sparse-sum-difference/carry_verify.py
```

These computations verify the finite inequality used in the manuscript's
asymptotic proof. The proof and its comparison with prior results require
separate mathematical and source review.

The [fivefold sumset counterexample](papers/fivefold-sumset/README.md) gives
integer sets violating the fivefold inequality stated by Gyarmati, Hennecart
and Ruzsa (2007). CI checks two exact counting formulas and their literal
small-set controls using Python's standard library:

```sh
python3 -m unittest discover -s papers/fivefold-sumset -p 'test_verify.py' -v
python3 papers/fivefold-sumset/verify.py
```
