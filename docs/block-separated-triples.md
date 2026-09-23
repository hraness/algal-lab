# Three triples need only ordering between groups

For nine independent atomless scores, three target triples are optimal even
when the CDFs cross **inside** each triple. Every member of an earlier target
triple must stochastically dominate every member of a later one. This weakens
the full CDF-chain assumption in the [general grouping theorem](stochastic-intact-groups.md).

The result has an exact finite certificate. Its algebra covers all selected
label sets, so the conclusion applies to arbitrary admitted score laws and
independent backgrounds, rather than a finite list of numerical examples.
It proves only the three-triple extension. Larger configurations with
internal crossings remain unresolved here.

## Statement and proof reduction

Label the target triples `012`, `345`, `678`, and let `T` be their partition.
Assume independent proper atomless focal scores, with

\[
 \max_{i\in T_1}F_i(t)\le\min_{i\in T_2}F_i(t),\qquad
 \max_{i\in T_2}F_i(t)\le\min_{i\in T_3}F_i(t)
 \quad\text{for every }t.
\]

Append any finite background vector independent of the focal scores; its
coordinates may depend on one another. Retain the largest `k` scores for
a fixed `k`, and let `N_P` count intact groups in a partition `P` into
triples. Then, for every such partition and every integer `j`,

\[
 P(N_T\ge j)\ge P(N_P\ge j). \tag{1}
\]

Arbitrary atomic focal laws are also permitted when all labels, including
backgrounds, have independent identically distributed continuous tie keys
independent of the scores. The common-noise approximation in the
[tie corollary](stochastic-intact-groups.md#atoms-and-tie-breaking) preserves
the between-group CDF cuts and proves this extension.

Write `Y_i` for the selected-label indicator. For distinct labels `a,b,c,d`
whose first two lie in target blocks strictly earlier than the blocks of the
last two, the cut-separated quartet contrasts are

\[
 h_0=(Y_a-Y_d)(Y_b-Y_c),\qquad
 h_1=(Y_a-Y_c)(Y_b-Y_d).
\]

Each has nonnegative expectation after multiplication by any nonnegative
function of indicators outside its quartet. This is the proved
[outside-factor lift](stochastic-intact-groups.md#nonnegative-outside-factors-can-be-retained).

For a subset `B` of the other five focal labels, define the **exact** pattern
indicator

\[
 I_B(Y)=\prod_{i\in B}Y_i
        \prod_{i\notin B\cup\{a,b,c,d\}}(1-Y_i).
\]

This includes excluded as well as selected labels. Thus `E[I_B h_s]≥0`.
Since `h_s` vanishes unless exactly two quartet labels are selected,
`I_B h_s` is supported on the focal cardinality layer `|B|+2`.

The [checked-in certificate](../research/spikes/stochastic/block_triples_certificate.json)
expresses, for every competing partition and tail threshold,

\[
 1\{N_T(Y)\ge j\}-1\{N_P(Y)\ge j\}
   =\sum_{\ell}c_\ell I_{B_\ell}(Y)h_{s_\ell}(Y),
 \qquad c_\ell\ge0, \tag{2}
\]

as an identity on **all** `2^9` Boolean selection vectors. Taking expectation
term by term proves (1) at any global horizon and with any admitted
background. We do not condition on the focal survivor count, which could
change the focal distribution. The layer-specific identities are first
summed into the unconditional identity (2).

## What the checker proves

There are `9! / ((3!)^3 3!) = 280` unlabeled partitions into triples.
Permuting labels within the three target blocks produces ten partition
orbits. Two partitions have the same orbit precisely when the multisets
of their groups' three block-intersection counts agree: pair groups with
matching counts, then biject the labels in each group/block intersection.
These disjoint cells give a permutation of all nine labels that preserves
each target block.

The [standard-library checker](../research/spikes/stochastic/block_triples.py)
constructs these bijections explicitly for every partition. It admits
only distinct quartet labels, correctly separated cuts, positive rational
coefficients, and outside patterns disjoint from the quartet. It verifies
all representative identities and transports them to every partition,
checking all 512 masks and thresholds `0..4`, including trivial cases.

The fixed artifact has 60 layer/tail certificates, containing 533 positive
rational terms. The coefficients have denominators dividing six, so the
checker verifies the identities using scaled integers. It checks 716,800
partition/mask/tail combinations and rejects seven deliberate corruptions,
including an incorrect positive coefficient, a missing case, and a quartet
cut through an internally unordered block.

```sh
python3 -m research.spikes.stochastic.block_triples
python3 -m research.spikes.stochastic.verify
```

The exploratory search used linear programming to propose the coefficients.
No optimizer status or floating-point residual is part of the proof. Runtime
verification needs neither that solver nor its numerical library. The finite
identity check plus the analytic quartet lemma establishes the stated
distributional theorem. It is not a proof for arbitrary numbers of groups.

## Scope and discovery record

Plain two-group sorting does not establish this extension. In the interleaved
partition `036/147/258`, every union of two groups contains two labels from
each target block. Splitting that union into its strongest and weakest
three labels cuts through the middle target block, whose members may have
crossing CDFs. The earlier sorting proof cannot justify that cut. The
certificate bypasses this particular proof obstruction; it is not a
counterexample to the broader conjecture.

The discovery spike proposed and exactly checked 60 finite linear-program
certificates. It did not run a histogram search. The separate executable
test uses overlapping, positive three-bin densities with internal crossings
and checks all 280 partition tails at five horizons. These calculations,
the finite proof, and literature priority are different evidence.

The [histogram optimizer](../research/stochastic_groups.py) now admits this
specific nine-label case using only target-block cuts. It keeps the full
CDF-chain guard for other configurations with at least three groups of size
greater than two. The certificate method uses established nonnegative-cone
and symmetry ideas; priority of this particular rank-grouping result remains
unresolved in the [novelty ledger](novelty-ledger.md). No small-model discovery
advantage was measured in this spike.
