"""Independent Boolean-matrix reconstruction; imports no encoding producer."""

from itertools import combinations

from support import (INDEPENDENT_NODES, MAX_CNF_BYTES, MAX_CUTS, checker, digest,
                     read_json, require)


def matrix(raw):
    require(type(raw) is list and 1 <= len(raw) <= 40, "raw graph order")
    n = len(raw)
    require(all(type(row) is int and 0 <= row < 2**n for row in raw), "raw graph masks")
    rows = [[bool(raw[u] & 2**v) for v in range(n)] for u in range(n)]
    require(all(not rows[u][u] and all(rows[u][v] == rows[v][u] for v in range(n)) for u in range(n)),
            "raw graph symmetry or diagonal")
    return rows


def independent(rows, vertices):
    return all(not rows[u][v] for u, v in combinations(vertices, 2))


def parameter_check(raw, m, r, minimum):
    rows = matrix(raw)
    require(len(rows) <= 33 and all(type(x) is int for x in (m, r, minimum))
            and 1 <= m <= 6 and 2 <= r <= 9 and 0 <= minimum <= m <= r, "parameters")
    require(all(sum(row) <= r - 1 for row in rows), "H maximum degree")
    require(not any(rows[u][v] and rows[v][w] and rows[u][w]
                    for u, v, w in combinations(range(len(rows)), 3)), "H triangle")
    return rows


def checked_subset(raw, cut, m, r):
    rows = matrix(raw)
    require(type(cut) is dict and set(cut) == {"subset", "witness", "columns", "candidate"}, "cut schema")
    subset = cut["subset"]
    require(type(subset) is int and 0 < subset < 2**len(raw), "subset encoding")
    vertices = [v for v in range(len(raw)) if subset & 2**v]
    require(max(1, r + 1 - m) <= len(vertices) <= r - 1 and independent(rows, vertices), "invalid independent T")
    columns = cut["columns"]
    require(type(columns) is list and len(columns) == m
            and all(type(s) is int and 0 <= s < 2**len(raw) for s in columns), "witness columns")
    full = matrix(cut["candidate"])
    require(len(full) == len(raw) + m + 1, "witness graph order")
    for u in range(len(full)):
        for v in range(len(full)):
            if u == 0 or v == 0:
                other = max(u, v)
                expected = 1 <= other <= m
            elif u <= m and v <= m:
                expected = False
            elif u > m and v > m:
                expected = rows[u - m - 1][v - m - 1]
            else:
                a, h = min(u, v) - 1, max(u, v) - m - 1
                expected = bool(columns[a] & 2**h)
            require(full[u][v] == expected, "witness graph differs from its H/columns")
    witness = cut["witness"]
    require(type(witness) is int and 0 < witness < 2**len(full), "witness encoding")
    chosen = [v for v in range(len(full)) if witness & 2**v]
    require(len(chosen) == r + 1 and 0 not in chosen and independent(full, chosen)
            and [v - m - 1 for v in chosen if v > m] == vertices, "invalid rejecting witness")
    return vertices


class Reconstruction:
    def __init__(self, variables):
        self.variables, self.clauses, self.wires = variables, [], []

    def add(self, *literals):
        if True in [x for x in literals if type(x) is bool]:
            return
        row = tuple(x for x in literals if type(x) is not bool)
        require(all(type(x) is int and 1 <= abs(x) <= self.variables for x in row), "reconstructed literal")
        self.clauses.append(row)

    def wire(self, kind, *inputs):
        self.variables += 1
        self.wires.append((self.variables, kind, inputs))
        return self.variables

    @staticmethod
    def neg(value):
        return not value if type(value) is bool else -value

    def count(self, literals, lower, upper):
        lo, hi = max(0, lower), min(len(literals), upper)
        if lo > hi:
            self.add()
            return
        # Independently indexed prefix thresholds, with an explicit logical
        # wire for the exhaustive controls' auxiliary-assignment oracle.
        table = {(0, 0): True}
        for i, x in enumerate(literals, 1):
            table[i, 0] = True
            for j in range(1, min(i, hi + 1) + 1):
                a, b = table.get((i - 1, j), False), table.get((i - 1, j - 1), False)
                q = self.wire("or_and", a, x, b)
                table[i, j] = q
                self.add(self.neg(a), q)
                self.add(-x, self.neg(b), q)
                self.add(-q, a, x)
                self.add(-q, a, b)
        self.add(table.get((len(literals), lo), False))
        self.add(self.neg(table.get((len(literals), hi + 1), False)))

    def complete(self, inputs):
        values = dict(inputs)

        def value(x):
            return x if type(x) is bool else values[abs(x)] == (x > 0)

        for identifier, kind, arguments in self.wires:
            args = [value(x) for x in arguments]
            if kind == "or_and":
                output = args[0] or (args[1] and args[2])
            elif kind == "and":
                output = args[0] and args[1]
            else:
                require(kind == "prefix", "unknown wire")
                output = args[0] and args[1] == args[2]
            values[identifier] = output
        return values

    def bytes(self):
        raw = ("p cnf %d %d\n" % (self.variables, len(self.clauses)) +
               "".join(" ".join(str(x) for x in row) + " 0\n" for row in self.clauses)).encode("ascii")
        require(len(raw) <= MAX_CNF_BYTES, "reconstructed CNF limit")
        return raw


def reconstruct(raw, cuts, *, m=6, r=9, minimum=6, ordered=True):
    rows = parameter_check(raw, m, r, minimum)
    require(type(ordered) is bool and type(cuts) is list and len(cuts) <= MAX_CUTS, "reconstruction options")
    n = len(raw)
    f = Reconstruction(n * m)
    x = lambda a, v: 1 + a * n + v
    for a in range(m):
        for u in range(n):
            for v in range(u + 1, n):
                if rows[u][v]:
                    f.add(-x(a, u), -x(a, v))
    for v in range(n):
        f.count([x(a, v) for a in range(m)], max(1, minimum - sum(rows[v])), r - sum(rows[v]))
    for a in range(m):
        f.count([x(a, v) for v in range(n)], max(0, minimum - 1), r - 1)
    for a in range(m):
        for v in range(n):
            f.add(x(a, v), *(x(a, w) for w in range(n) if rows[v][w]))
    for u in range(n):
        for v in range(u + 1, n):
            if rows[u][v] or any(rows[u][w] and rows[v][w] for w in range(n)):
                continue
            blockers = []
            for a in range(m):
                q = f.wire("and", x(a, u), x(a, v))
                f.add(-q, x(a, u))
                f.add(-q, x(a, v))
                f.add(-x(a, u), -x(a, v), q)
                blockers.append(q)
            f.add(*blockers)
    if ordered:
        for a in range(m - 1):
            prefix = True
            for v in range(n):
                left, right = x(a, v), x(a + 1, v)
                f.add(f.neg(prefix), -left, right)
                if v == n - 1:
                    continue
                q = f.wire("prefix", prefix, left, right)
                f.add(-q, prefix)
                f.add(-q, -left, right)
                f.add(-q, left, -right)
                f.add(f.neg(prefix), left, right, q)
                f.add(f.neg(prefix), -left, -right, q)
                prefix = q
    seen = set()
    for cut in cuts:
        vertices = checked_subset(raw, cut, m, r)
        require(tuple(vertices) not in seen, "duplicate T")
        seen.add(tuple(vertices))
        for attachments in combinations(range(m), r + 1 - len(vertices)):
            f.add(*(x(a, v) for a in attachments for v in vertices))
    return f


def structural_truth(raw, columns, *, r=9, minimum=6, ordered=True):
    rows, n, m = matrix(raw), len(raw), len(columns)
    sets = [{v for v in range(n) if mask & 2**v} for mask in columns]
    if not minimum <= m <= r:
        return False
    if any(not independent(rows, sorted(s)) or not max(0, minimum - 1) <= len(s) <= r - 1 for s in sets):
        return False
    if any(not max(1, minimum - sum(rows[v])) <= sum(v in s for s in sets) <= r - sum(rows[v]) for v in range(n)):
        return False
    if any(v not in s and not any(rows[v][w] for w in s) for s in sets for v in range(n)):
        return False
    if any(not rows[u][v] and not any(rows[u][w] and rows[v][w] for w in range(n))
           and not any(u in s and v in s for s in sets) for u, v in combinations(range(n), 2)):
        return False
    vectors = [tuple(v in s for v in range(n)) for s in sets]
    return not ordered or vectors == sorted(vectors)


def check_graph(raw, columns, candidate, budget):
    require(structural_truth(raw, columns), "candidate structural conditions")
    rows = matrix(candidate)
    require(len(rows) == 40 and rows[0] == [False] + [True] * 6 + [False] * 33, "candidate centre")
    for u in range(40):
        for v in range(40):
            if u > 6 and v > 6:
                require(rows[u][v] == bool(raw[u - 7] & 2**(v - 7)), "candidate H changed")
            elif 1 <= u <= 6 and v > 6:
                require(rows[u][v] == bool(columns[u - 1] & 2**(v - 7)), "candidate incidences changed")
            elif 1 <= u <= 6 and 1 <= v <= 6:
                require(not rows[u][v], "attachment edge")
    require(all(6 <= sum(row) <= 9 for row in rows), "candidate degrees")
    require(not any(rows[u][v] and rows[v][w] and rows[u][w] for u, v, w in combinations(range(40), 3)), "candidate triangle")
    require(all(rows[u][v] or any(rows[u][w] and rows[v][w] for w in range(40))
                for u, v in combinations(range(40), 2)), "candidate not maximal")
    budget.check()
    witness = checker.independent_set(candidate, 10, node_limit=INDEPENDENT_NODES, deadline=budget.deadline)
    budget.check()
    return witness


def audit(directory, raw, budget):
    metadata, cuts = read_json(directory / "instance.json"), read_json(directory / "cuts.json")
    require(digest(directory / "cuts.json") == metadata["cuts_sha256"], "cuts changed")
    rebuilt = reconstruct(raw, cuts)
    budget.check()
    require((directory / "instance.cnf").stat().st_size <= MAX_CNF_BYTES, "CNF byte bound")
    require(rebuilt.bytes() == (directory / "instance.cnf").read_bytes()
            and digest(directory / "instance.cnf") == metadata["cnf_sha256"], "CNF independent reconstruction failed")
    require(checker.independent_set(raw, 9, node_limit=INDEPENDENT_NODES, deadline=budget.deadline) is None,
            "raw H contains an independent nine-set")
    budget.check()
    return {"independent_encoding_verified": True, "independent_cuts_verified": True,
            "H_triangle_free_and_alpha_at_most_eight_verified": True,
            "cuts_checked": len(cuts), "cnf_sha256": digest(directory / "instance.cnf"),
            "cuts_sha256": digest(directory / "cuts.json"), "variables": rebuilt.variables,
            "clauses": len(rebuilt.clauses)}
