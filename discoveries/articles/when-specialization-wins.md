Suppose each member of a mathematical team has one unit of effort to distribute among several tasks. A member could divide that effort across tasks, or put it all into one. In the model studied here, **every globally optimal allocation chooses the second option** whenever both of the model’s weighting parameters are finite and positive.[^1]

That conclusion turns a continuous optimization problem, with infinitely many possible effort splits, into a finite problem of counting how many agents take each task. It is a theorem about a particular reward formula, rather than a general recommendation for organizing people or AI systems.

## The reward decides the question

The model comes from work by Michael Amir, Matteo Bettini and Amanda Prorok on cooperative multi-agent learning.[^3] It uses an exponential weighted average twice: first to combine the effort a task receives, then to combine the resulting task scores into a team reward.

For numbers $x_1,\ldots,x_n$, the weighted mean is

$$
B_t(x)=\frac{\sum_i x_i e^{t x_i}}{\sum_i e^{t x_i}}.
$$

When $t$ is positive, larger entries receive more weight. The same operation combines task scores using another parameter. The exact reward matters: changing the averaging rule can change the optimal team.

A *pure* allocation gives every agent a single task. It does not require every agent to choose a different task, or every agent to choose the same task. Which occupancy pattern wins still depends on the parameters.

## Excluding every fractional optimum

Checking many candidate allocations can suggest specialization, but it cannot eliminate all possible splits. The proof instead asks what a fractional optimum would have to look like.

Represent an allocation by a graph connecting each agent to the tasks receiving its effort. First- and second-derivative conditions severely restrict this graph. A proposed optimum has no cycles, no agent owns two private tasks, and pure and fractional agents cannot share a task.

These restrictions leave a path along which effort can be transferred. Along that path, the first derivative of reward vanishes while the second derivative is strictly positive. Such a point cannot be a local maximum. This excludes the remaining fractional configuration and proves purity.

The resulting integer-occupancy problem yields exact solutions in several small populations and parameter regimes. The paper also supplies exact counterexamples to the exactness conjecture stated in the original paper’s first arXiv version. Later versions are identified separately.[^3][^4]

## A companion question: when does spreading the inputs help?

A tempting shortcut is to assume that making an input vector more unequal always increases its positive-parameter exponential mean. A companion paper identifies exactly when that ordering is valid.[^2]

For vectors with $n\geq3$ entries in an interval $[a,b]$, the relevant majorization ordering holds precisely when

$$
|t|(b-a)\leq c_n,
\qquad (n-2)(c_n-2)e^{c_n}=4.
$$

For positive $t$ the mean is Schur-convex; for negative $t$ it is Schur-concave. These terms describe how the mean responds to a more unequal vector with the same total. At zero, the mean is the ordinary average.

The thresholds decrease toward two as the dimension grows. Thus the dimension-free condition $|t|(b-a)\leq2$ is sharp. Above the exact threshold, the paper constructs violations inside the box. It also derives separate thresholds when the entries are nonnegative and their total is fixed.

## What the two proofs make possible

The purity result removes fractional allocations from the positive-parameter search. The threshold result states when an ordering argument is safe to use on the scalar mean. Their proofs, exact identities and rational certificates are separate from numerical grid checks, which serve only as corroboration.

Neither theorem establishes a general benefit from agent diversity, and neither is presented as a literature-first discovery. The manuscripts retain their source-access and novelty limits. For a different model where members can fail, [the grouping result](/discoveries/grouping-components-that-last) explains why the definition of a working group changes the answer.
