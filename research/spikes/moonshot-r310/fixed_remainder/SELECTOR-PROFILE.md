# SAT certificates for the column-cover obstruction

The implemented `fixed-h-column-selector-v1` profile encodes a necessary
condition for extensions of the seven pair-deletion remainders. Its column
catalogues agree with an independent enumeration; the mathematical reduction
is documented in [STRUCTURAL-NOTE.md](STRUCTURAL-NOTE.md). Solver results
count as exclusions only after both independent proof checkers succeed.

For a triangle-free 40-vertex graph with independence number at most 9,
choose a degree-six vertex and write its neighbours as `A` and its 33-vertex
anti-neighbourhood as `H`. Require centre coverage: every vertex of `H`
meets `A`. The profile applies only when `H` is one of the pair deletions
of the checked 35-vertex source graph.

Adding triangle-free edges between `A` and `H` until none remain preserves
the centre, `H`, coverage, and the absence of an independent ten-set.
The maximum degree remains at most 9, as every neighbourhood is independent.
This reduces existence in the stated scope to existence with saturated
attachment sets. Full maximality of the graph is a sufficient condition,
but is not needed for this reduction.

After saturation, each of the six attachment sets `S_a` is a maximal independent set of `H`:
otherwise an additional edge from `a` to an undominated vertex of `H` would
preserve triangle-freeness. The finite enumeration reports that all these
sets have size 7 or 8. A vertex with degree 8 inside `H` belongs to exactly
one attachment set, by centre coverage and the graph's maximum degree 9.
Thus it is a private neighbour. Any attachment set has at most four private
neighbours, since five together with the other five vertices of `A` would
form an independent ten-set. Every eligible column therefore contains at
most four of the degree-eight vertices of `H`.

The six columns must be distinct. Write `c` for the number of attachment
edges and `N_1` for the number of `H` vertices with a unique attachment.
Coverage gives `c >= N_1 + 2*(33-N_1)`, so `N_1 >= 66-c >= 18`, because
`c <= 6*8 = 48`. Equal columns would both have no private neighbour,
leaving at most `4*4 = 16` private neighbours in total, a contradiction.

## Necessary-condition formula

Use one Boolean selector `y_S` for each distinct eligible column `S`.
Require exactly six selectors to be true, and add:

- For every `v` with `d_H(v)=8`, exactly one selected column contains `v`.
- For every `v` with `d_H(v)=7`, at most two selected columns contain `v`.
- For every `v` with `d_H(v)=6`, at most three selected columns contain `v`.
- For every pair of columns `S,T` for which `H-(S union T)` has an
  independent eight-set, add `(-y_S OR -y_T)`.

The pair clause is necessary because the eight-set together with the two
corresponding vertices of `A` would be independent. The lower coverage
bounds for degree-six and degree-seven vertices can be omitted: this only
weakens a necessary-condition formula. There is no ordering restriction
and no special treatment of columns avoiding the degree-eight vertices.
All such columns must remain available as ordinary selectors.

Every graph in the stated scope yields a satisfying selector assignment.
Therefore UNSAT excludes that scope. A satisfying assignment proves only
that this relaxation has a cover; it does not by itself produce a Ramsey
graph. The remaining independent-set constraints would still need checking.

This representation avoids dependence on the column search's branching
heuristic, its stopping cases, or the argument for postponing columns that
avoid the degree-eight vertices. It retains the same mathematical catalogue
and reduction assumptions, which require their own independent checks.

## Formula sizes and limits

Independent enumeration confirms that the largest eligible catalogue has
`N=1,427` columns. Conservative bounds are:

- There are at most `N*(N-1)/2 = 1,017,451` pair clauses.
- The existing full-equivalence unary counter for exactly six columns uses
  at most `7*N` auxiliary variables.
- Each selected column belongs to at most eight row constraints, whose
  counters use at most four auxiliaries per input. These contribute at
  most `32*N` auxiliaries.
- Including the selector variables gives at most `40*N = 57,080`
  variables. Four clauses per auxiliary, two bounds for each of 34 counters,
  and all possible pair clauses give at most 1,240,131 clauses.
- Even using four literals per counter clause and the maximum decimal
  variable width, this DIMACS representation is under 24 MiB.

The actual complete formulas have the following inventories. Counting every
emitted clause took 4.579 CPU seconds in total and used 46,727,168 peak
bytes; this measurement did not invoke a solver.

| Case | Deleted pair | Selectors | Total variables | Clauses | DIMACS bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | `(0,1)` | 1,416 | 41,671 | 1,061,033 | 13,960,717 |
| 1 | `(0,2)` | 1,332 | 39,688 | 937,386 | 12,302,987 |
| 2 | `(0,4)` | 1,023 | 31,230 | 550,012 | 7,115,830 |
| 3 | `(0,5)` | 1,300 | 38,642 | 895,064 | 11,723,253 |
| 4 | `(0,7)` | 1,427 | 42,209 | 1,080,366 | 14,218,610 |
| 5 | `(0,8)` | 1,236 | 35,654 | 805,904 | 10,501,252 |
| 6 | `(0,14)` | 1,222 | 35,142 | 788,920 | 10,265,877 |

For each column, the encoder precomputes the bitset of independent eight-sets that it
misses. Two columns are incompatible exactly when their missed-set bitsets
intersect. This avoids scanning all eight-sets anew for each column pair.
An independent reconstruction should regenerate the source graph, every
eligible maximal independent set, all row incidences, and every pair
condition before comparing the exact emitted formula.

`selector_run.py` attempts exactly one case. It snapshots and hashes its
source, inventories, solver, and proof checker. Construction has a 60 CPU
second limit. The solver, Python RUP replay, and `lrat-trim` each have a
separate 90 CPU second limit, with 30 additional wall seconds per stage.
Every stage has a 1 GiB RSS threshold and uses the reviewed owned-child
supervisor. The memory threshold is cooperative on macOS; Linux also has
an address-space limit. Interrupted or failed stages remain unresolved.

The explicitly named selector proof reader accepts at most 60,000
variables, 1,500,000 clauses, a 32 MiB CNF, and a 256 MiB textual LRAT proof.
Ordinary proof records are limited to 1,000,000 bytes. Selector deletion
records may occupy up to 2 MiB, including the newline; the reader limits
the allocation before parsing. This allowance covers the retained case-four
proof's 1,331,144-byte deletion record without changing any proof semantics.
The original fixed-attachment reader's smaller bounds remain unchanged.
CaDiCaL uses `--lrat --no-binary --no-factor`. Python checks every RUP step;
`lrat-trim --no-trim` supplies a second implementation. The runner requires
both checkers to pass, including `lrat-trim` exit status 20 and `s VERIFIED`.
Independent reconstruction of the particular CNF and review of the finite
catalogue premise remain part of reporting a mathematical exclusion.

```sh
python3 research/spikes/moonshot-r310/fixed_remainder/selector_run.py \
  --solver /path/to/installed/cadical \
  --lrat-trim /path/to/installed/lrat-trim \
  --case 0 --output runs/moonshot-r310/selector-case0
```

Use a new output directory and follow host execution controls. Add
`--construct-only` to stop after formula construction. Each invocation
attempts one case; the program does not increase its own budget.

## Controls

Eight focused tests passed in 2.070 seconds with all optional evidence
enabled. They compare every one of 96,000 selector assignments over 375
small formulas with direct necessary-condition checks; match every eligible
and maximal-set catalogue hash against an independent Bron–Kerbosch
enumeration; reject unsupported profiles, oversized inputs, corrupted
proofs, and incomplete construction; preserve the original parser bounds;
and exercise both SAT and UNSAT through the actual solver and proof checkers.
A SAT result is labelled `necessary_cover_found` and carries no graph claim.

```sh
CADICAL_LIBRARY=/path/to/libcadical \
CADICAL_BINARY=/path/to/cadical \
LRAT_TRIM=/path/to/lrat-trim \
SELECTOR_INDEPENDENT_CENSUS=/path/to/independent-census.json \
python3 -m unittest discover \
  -s research/spikes/moonshot-r310/fixed_remainder -p 'test_selector.py' -v
```

Missing optional inputs cause explicit skips, which are not evidence that
the corresponding checks passed.

Four focused proof-reader controls subsequently passed in 0.024 seconds.
They accept a valid deletion record at exactly 2 MiB, reject one byte over
that limit, reject an invalid deletion terminator, preserve the ordinary
record and total-file limits, and confirm that the original attachment
reader still rejects the enlarged record. No solver rerun was required.
