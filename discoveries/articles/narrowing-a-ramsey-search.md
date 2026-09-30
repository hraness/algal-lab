Draw a graph with 40 vertices. Try to avoid both a triangle of connected vertices and a set of 10 vertices with no connections among them. Whether such a graph exists is the unresolved target of this laboratory’s Ramsey search.

The search did not find the graph or settle the question. It did prove restrictions on any possible answer. In particular, **every vertex in such a graph must have at least five neighbors**.[^1] The proof is available as a finite logical formula and a certificate accepted by three independently implemented checkers.

Other runs exclude specified families of possible graphs. They provide reusable negative results while leaving the main question open.

## From 40 vertices to one smaller graph

Choose a vertex and remove it together with its neighbors. The remaining graph cannot contain nine mutually unconnected vertices, because adding the chosen vertex would give 10.

Known Ramsey results imply that the chosen vertex has at least four neighbors. If it had exactly four, the remainder would have 35 vertices. Earlier work by Jan Goedgebeur and Stanisław Radziszowski proves that there is only one possible graph of the required 35-vertex type, up to relabeling.[^2]

That classification changes the task. Instead of searching every 40-vertex graph, the proof tests every way that four neighbors could attach to this one known remainder while respecting all the required conditions.

## A finite contradiction, independently replayed

The attachment question becomes a Boolean satisfiability problem. Variables describe the attachment edges. Clauses prevent triangles and ensure that forbidden independent sets cannot survive.

The exact encoding has 140 variables and 98,965 clauses. An independent audit checked the graph correspondence, the independent-set inventories and every required clause. The solver returned a proof that the formula is unsatisfiable.

Three checker implementations accepted that proof. This establishes that a degree-four vertex is impossible, so the previous lower restriction of four improves to five. The mathematical reduction and the complete encoding are necessary parts of the result: a solver certificate alone only proves something about its input formula.

## What the other exclusions cover

A second proof family starts from all 595 ways to delete two vertices from the same 35-vertex graph. Checked symmetries reduce those inputs to seven representatives. A complete covering search and independently checked logical refutations exclude the stated degree-six extensions.[^3]

The conditions remain part of the conclusion. The 40-vertex graph must have minimum degree six, the chosen remainder must come from those deletions, and every remainder vertex must connect to a neighbor of the chosen center. Different remainders or extensions without that coverage lie outside the exclusion.

Another sample contains 128 specified 33-vertex remainders. Integer-weighted certificates exclude 113 as exact remainders of a maximal triangle-free graph with a degree-six center; 15 remain unresolved.[^4] Here *maximal* means that adding any missing edge would create a triangle. The certificates do not exclude nonmaximal extensions, and the sample does not exhaust the possible remainders.

The repository also retains a symmetry census and bounded searches that stopped without a decision. Their reports distinguish a proved exclusion from a resource limit.

## What came out of the attempt

The deliverables are a universal minimum-degree restriction for the hypothetical 40-vertex witness, several precisely delimited exclusions, and portable proof files and checkers. The method combines a known structural classification, finite encoding and independent replay.

None of these results changes the Ramsey bound, and no publication-priority claim is made. They narrow some routes without closing the problem. The [small-grid report](/discoveries/points-without-a-common-sphere) shows the parallel issue for geometry: existence examples and complete exclusion proofs answer different halves of an extremal question.
