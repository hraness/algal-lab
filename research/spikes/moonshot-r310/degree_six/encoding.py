"""Exact structural CNF for an incremental Ramsey-graph search."""

import itertools

PROFILES = ("baseline", "degree-six-structure-v1")


class Formula:
    def __init__(self, variables=0):
        self.variables = variables
        self.clauses = []

    def fresh(self):
        self.variables += 1
        return self.variables

    def add(self, *literals):
        # Boolean constants simplify boundary cells of the unary counter.
        if any(type(literal) is bool and literal for literal in literals):
            return
        clause = tuple(literal for literal in literals if type(literal) is not bool)
        if any(type(literal) is not int or not 1 <= abs(literal) <= self.variables
               for literal in clause):
            raise ValueError("invalid CNF literal")
        self.clauses.append(clause)


def neg(literal):
    return not literal if type(literal) is bool else -literal


def cardinality(formula, inputs, lower, upper):
    """Exactly constrain lower <= sum(inputs) <= upper.

    Cell (i,j) means at least j of the first i inputs are true. Only cells
    through upper+1 are needed. Every cell is encoded by full equivalence,
    so both the lower and upper bound are sound.
    """
    if not 0 <= lower <= upper <= len(inputs):
        raise ValueError("invalid cardinality interval")
    previous = {0: True}
    for position, literal in enumerate(inputs, 1):
        current = {0: True}
        for threshold in range(1, min(position, upper + 1) + 1):
            a = previous.get(threshold, False)
            b = previous.get(threshold - 1, False)
            y = formula.fresh()
            # y <=> a OR (literal AND b).
            formula.add(neg(a), y)
            formula.add(-literal, neg(b), y)
            formula.add(-y, a, literal)
            formula.add(-y, a, b)
            current[threshold] = y
        previous = current
    formula.add(previous.get(lower, False))
    formula.add(neg(previous.get(upper + 1, False)))
    return previous


def nondecreasing_signatures(formula, signatures):
    """Order positive-literal bit vectors lexicographically, first bit highest.

    Forbid 1 > 0 at the first differing position, for every possible shared
    prefix. Six-bit signatures need 63 clauses per adjacent pair, no variables.
    """
    for left, right in zip(signatures, signatures[1:]):
        if len(left) != len(right):
            raise ValueError("signature widths differ")
        for position in range(len(left)):
            for prefix in itertools.product((False, True), repeat=position):
                guards = [(-row[i] if bit else row[i])
                          for i, bit in enumerate(prefix) for row in (left, right)]
                formula.add(*guards, -left[position], right[position])


def private_neighbor_cap(formula, signatures, limit):
    """Cap each singleton signature; requires nondecreasing_signatures first.

    Equal signatures are contiguous in an ordered sequence. Forbid limit+1
    consecutive copies of each one-bit signature.
    """
    if type(limit) is not int or limit < 0:
        raise ValueError("invalid private-neighbor limit")
    if not signatures:
        return
    width = len(signatures[0])
    if any(len(row) != width for row in signatures):
        raise ValueError("signature widths differ")
    for start in range(len(signatures) - limit):
        for singleton in range(width):
            formula.add(*(neg(literal) if bit == singleton else literal
                          for row in signatures[start:start + limit + 1]
                          for bit, literal in enumerate(row)))


def anti_neighborhood_edge_bound(formula, thresholds, order, centre, minimum, maximum, lower):
    """Reuse degree thresholds to impose e(G-N[0]) >= lower exactly.

    Every degree is minimum plus the sum of its higher threshold bits, and
    N(0) is independent. These are required preconditions of this helper.
    """
    bits_a = [thresholds[v][d] for v in range(1, centre + 1)
              for d in range(minimum + 1, maximum + 1)]
    bits_h = [thresholds[v][d] for v in range(centre + 1, order)
              for d in range(minimum + 1, maximum + 1)]
    inputs = [-bit for bit in bits_h] + bits_a
    bound = (order - centre - 1) * maximum - centre * (minimum - 1) - 2 * lower
    if bound < 0:
        formula.add()
    elif bound < len(inputs):
        cardinality(formula, inputs, 0, bound)
    return bits_a


def structural_formula(order=40, target=10, minimum=6, centre=6, *, coverage=True,
                       profile="baseline"):
    if (not all(type(value) is int for value in (order, target, minimum, centre))
            or not 3 <= order <= 40 or not 3 <= target <= min(10, order)
            or not 0 <= minimum <= centre <= min(target - 1, order - 1)
            or type(coverage) is not bool):
        raise ValueError("unsupported graph parameters")
    if profile not in PROFILES:
        raise ValueError("unknown structural profile")
    if profile != "baseline" and (order, target, minimum, centre, coverage) != (40, 10, 6, 6, True):
        raise ValueError("degree-six-structure-v1 requires (40,10,6,6) and coverage")
    edges = list(itertools.combinations(range(order), 2))
    variable = {edge: i + 1 for i, edge in enumerate(edges)}
    formula = Formula(len(edges))
    counts = {}

    def edge(u, v):
        return variable[tuple(sorted((u, v)))]

    for a, b, c in itertools.combinations(range(order), 3):
        formula.add(-edge(a, b), -edge(a, c), -edge(b, c))
    counts["triangles"] = len(formula.clauses)
    before = len(formula.clauses)
    for v in range(1, order):
        formula.add(edge(0, v) if v <= centre else -edge(0, v))
    counts["fixed_neighborhood"] = len(formula.clauses) - before
    before = len(formula.clauses)
    if coverage:
        for v in range(centre + 1, order):
            formula.add(*(edge(v, neighbor) for neighbor in range(1, centre + 1)))
    counts["neighborhood_coverage"] = len(formula.clauses) - before
    before = len(formula.clauses)
    thresholds = {}
    for v in range(order):
        thresholds[v] = cardinality(formula, [edge(v, w) for w in range(order) if v != w],
                                    minimum, min(target - 1, order - 1))
    counts["degrees"] = len(formula.clauses) - before
    strengthening = {}
    if profile == "degree-six-structure-v1":
        before = len(formula.clauses)
        bits_a = anti_neighborhood_edge_bound(formula, thresholds, 40, 6, 6, 9, 118)
        counts["anti_neighborhood_edge_bound"] = len(formula.clauses) - before
        signatures = [[edge(a, v) for a in range(1, 7)] for v in range(7, 40)]
        before = len(formula.clauses)
        nondecreasing_signatures(formula, signatures)
        counts["anti_neighborhood_signature_order"] = len(formula.clauses) - before
        before = len(formula.clauses)
        private_neighbor_cap(formula, signatures, 4)
        counts["private_neighbor_cap"] = len(formula.clauses) - before
        before = len(formula.clauses)
        cardinality(formula, [-bit for bit in bits_a], 0, 6)
        counts["neighborhood_cross_edge_bound"] = len(formula.clauses) - before
        strengthening = {
            "profile": profile, "anti_neighborhood_minimum_edges": 118,
            "neighborhood_cross_minimum_edges": 42, "private_neighbor_maximum": 4,
            "implied_global_minimum_edges": 166,
            "signature_order": "lexicographic ascending, vertex 1 most significant",
            "edge_bound_source": "Goedgebeur and Radziszowski, EJC 20(1), P30 (2013), Table 4, p. 11",
        }
    metadata = {
        "order": order, "independent_set_target": target,
        "minimum_degree": minimum, "maximum_degree": min(target - 1, order - 1),
        "centre_degree": centre, "centre_coverage_required": coverage,
        "edge_variables": len(edges), "variables": formula.variables,
        "clauses": len(formula.clauses), "clause_counts": counts,
        "symmetry_pruning": "fixed labelled neighborhood only",
        "independent_set_constraints_initially_complete": False,
    }
    if strengthening:
        metadata["strengthening"] = strengthening
        metadata["symmetry_pruning"] = "fixed labelled neighborhood; sorted outside-neighborhood signatures"
    return formula, variable, metadata


def independent_clause(vertex_mask, variable, target):
    if type(vertex_mask) is not int or vertex_mask < 0 or vertex_mask.bit_count() != target:
        raise ValueError("cut must describe exactly target vertices")
    vertices = [v for v in range(vertex_mask.bit_length()) if vertex_mask >> v & 1]
    return tuple(variable[pair] for pair in itertools.combinations(vertices, 2))
