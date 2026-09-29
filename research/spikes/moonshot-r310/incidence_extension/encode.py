"""A labelled centre, six attachment columns, and witnessed independent-set cuts."""

from itertools import combinations

from support import (Formula, MAX_CLAUSES, MAX_CNF_BYTES, MAX_CUTS, MAX_VARIABLES,
                     cardinality, checker, digest, require, write_json)


def parameters(adj, m=6, r=9, minimum=6):
    require(type(adj) is list and 1 <= len(adj) <= 33, "remainder order")
    checker.validate_adjacency(adj)
    require(checker.triangle(adj) is None, "remainder triangle")
    require(all(type(x) is int for x in (m, r, minimum)) and 1 <= m <= 6
            and 2 <= r <= 9 and 0 <= minimum <= m <= r
            and max(row.bit_count() for row in adj) <= r - 1, "structural parameters")


def variable(a, v, n):
    return 1 + a * n + v


def interval(formula, inputs, lower, upper):
    lower, upper = max(0, lower), min(len(inputs), upper)
    if lower > upper:
        formula.add()
    else:
        cardinality(formula, inputs, lower, upper)


def column_order(formula, columns):
    for left, right in zip(columns, columns[1:]):
        prefix = True
        for v, (l, r) in enumerate(zip(left, right)):
            not_prefix = not prefix if type(prefix) is bool else -prefix
            formula.add(not_prefix, -l, r)
            if v + 1 == len(left):
                break
            q = formula.fresh()
            formula.add(-q, prefix)
            formula.add(-q, -l, r)
            formula.add(-q, l, -r)
            formula.add(not_prefix, l, r, q)
            formula.add(not_prefix, -l, -r, q)
            prefix = q


def graph(adj, masks):
    n, m = len(adj), len(masks)
    offset = m + 1
    require(all(type(mask) is int and 0 <= mask < 1 << n for mask in masks), "column masks")
    result = [sum(1 << a for a in range(1, m + 1))] + [1] * m + [row << offset for row in adj]
    for a, mask in enumerate(masks, 1):
        result[a] |= mask << offset
        for v in range(n):
            if mask >> v & 1:
                result[offset + v] |= 1 << a
    return result


def validate_cut(adj, cut, m=6, r=9):
    require(type(cut) is dict and set(cut) == {"subset", "witness", "columns", "candidate"}, "cut fields")
    subset, witness, masks = cut["subset"], cut["witness"], cut["columns"]
    require(type(subset) is int and 0 < subset < 1 << len(adj)
            and max(1, r + 1 - m) <= subset.bit_count() <= r - 1, "cut subset size")
    require(checker.verify_independent(adj, subset, subset.bit_count()), "cut subset not independent")
    require(type(masks) is list and len(masks) == m and cut["candidate"] == graph(adj, masks), "cut candidate")
    candidate = cut["candidate"]
    require(type(witness) is int and witness.bit_count() == r + 1 and witness & 1 == 0
            and witness >> (m + 1) == subset and checker.verify_independent(candidate, witness, r + 1),
            "cut lacks its rejecting independent-set witness")
    return subset


def build(adj, cuts, *, m=6, r=9, minimum=6, ordered=True):
    parameters(adj, m, r, minimum)
    require(type(ordered) is bool and type(cuts) is list and len(cuts) <= MAX_CUTS, "encoding options")
    n = len(adj)
    formula = Formula(m * n)
    columns = [[variable(a, v, n) for v in range(n)] for a in range(m)]
    counts = {}

    def done(name, before):
        counts[name] = len(formula.clauses) - before

    before = len(formula.clauses)
    for a in range(m):
        for u, v in combinations(range(n), 2):
            if adj[u] >> v & 1:
                formula.add(-columns[a][u], -columns[a][v])
    done("column_independence", before)
    before = len(formula.clauses)
    for v in range(n):
        degree = adj[v].bit_count()
        interval(formula, [columns[a][v] for a in range(m)], max(1, minimum - degree), r - degree)
    done("centre_coverage_and_H_degrees", before)
    before = len(formula.clauses)
    for column in columns:
        interval(formula, column, max(0, minimum - 1), r - 1)
    done("attachment_sizes", before)
    before = len(formula.clauses)
    for a in range(m):
        for v in range(n):
            formula.add(columns[a][v], *(columns[a][w] for w in range(n) if adj[v] >> w & 1))
    done("maximal_columns", before)
    before = len(formula.clauses)
    demands = []
    for u, v in combinations(range(n), 2):
        if adj[u] >> v & 1 or adj[u] & adj[v]:
            continue
        demands.append([u, v])
        blockers = []
        for a in range(m):
            q = formula.fresh()
            blockers.append(q)
            formula.add(-q, columns[a][u])
            formula.add(-q, columns[a][v])
            formula.add(-columns[a][u], -columns[a][v], q)
        formula.add(*blockers)
    done("demand_pair_blockers", before)
    before = len(formula.clauses)
    if ordered:
        column_order(formula, columns)
    done("attachment_label_symmetry", before)
    before = len(formula.clauses)
    seen = set()
    for cut in cuts:
        subset = validate_cut(adj, cut, m, r)
        require(subset not in seen, "duplicate cut")
        seen.add(subset)
        vertices = [v for v in range(n) if subset >> v & 1]
        for group in combinations(range(m), r + 1 - len(vertices)):
            formula.add(*(columns[a][v] for a in group for v in vertices))
    done("independent_set_cuts", before)
    require(formula.variables <= MAX_VARIABLES and len(formula.clauses) <= MAX_CLAUSES, "formula limit")
    return formula, {"variables": formula.variables, "clauses": len(formula.clauses),
                     "incidence_variables": m * n, "clause_counts": counts, "demands": demands}


def dimacs(formula):
    raw = (f"p cnf {formula.variables} {len(formula.clauses)}\n" +
           "".join(" ".join(map(str, clause)) + " 0\n" for clause in formula.clauses)).encode("ascii")
    require(len(raw) <= MAX_CNF_BYTES, "CNF byte limit")
    return raw


def write_instance(directory, adj, cuts, budget):
    budget.check()
    formula, metadata = build(adj, cuts)
    directory.mkdir(parents=True, exist_ok=False)
    with (directory / "instance.cnf").open("xb") as stream:
        stream.write(dimacs(formula))
    write_json(directory / "cuts.json", cuts)
    metadata.update(cnf_sha256=digest(directory / "instance.cnf"), cuts_sha256=digest(directory / "cuts.json"))
    write_json(directory / "instance.json", metadata)
    budget.check()
    return metadata
