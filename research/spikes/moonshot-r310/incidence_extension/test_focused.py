"""Finite truth oracles, counter boundaries, symmetry and adversarial artifacts."""

import copy
from itertools import combinations, permutations, product
from pathlib import Path
import tempfile
import unittest

import audit
import encode
import proof
from support import Budget, Formula, SearchLimit, cardinality, decode, require

BUDGET = None


def budget():
    return BUDGET if BUDGET is not None else Budget(30)


def graph(n, edges):
    rows = [0] * n
    for u, v in edges:
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    return rows


def satisfies(formula, values):
    return all(any(values[abs(lit)] == (lit > 0) for lit in row) for row in formula.clauses)


def values(masks, n):
    return {a * n + v + 1: bool(mask & 1 << v) for a, mask in enumerate(masks) for v in range(n)}


class Controls(unittest.TestCase):
    def test_all_small_structures_against_direct_graph_conditions(self):
        checked, inputs = 0, 0
        for n in range(1, 4):
            edges = list(combinations(range(n), 2))
            for selected in product((False, True), repeat=len(edges)):
                raw = graph(n, [e for e, selected_edge in zip(edges, selected) if selected_edge])
                if any(raw[u] & 1 << v and raw[v] & 1 << w and raw[u] & 1 << w
                       for u, v, w in combinations(range(n), 3)):
                    continue
                for m in (2, 3):
                    r = max(m, n + 1)
                    options = {"m": m, "r": r, "minimum": 1}
                    produced, _ = encode.build(raw, [], **options)
                    rebuilt = audit.reconstruct(raw, [], **options)
                    self.assertEqual(encode.dimacs(produced), rebuilt.bytes())
                    for masks in product(range(1 << n), repeat=m):
                        completed = rebuilt.complete(values(masks, n))
                        self.assertEqual(satisfies(produced, completed),
                                         audit.structural_truth(raw, masks, r=r, minimum=1))
                        checked += 1
                    inputs += 1
                    budget().check()
        self.assertEqual((inputs, checked), (20, 4204))

    def test_counter_truth_and_unique_auxiliary_semantics(self):
        for n in range(6):
            for lower in range(n + 1):
                for upper in range(lower, n + 1):
                    f, g = Formula(n), audit.Reconstruction(n)
                    literals = list(range(1, n + 1))
                    cardinality(f, literals, lower, upper)
                    g.count(literals, lower, upper)
                    self.assertEqual((f.variables, f.clauses), (g.variables, g.clauses))
                    for assignment in product((False, True), repeat=n):
                        completed = g.complete(dict(zip(literals, assignment)))
                        expected = lower <= sum(assignment) <= upper
                        self.assertEqual(satisfies(f, completed), expected)
                        if expected:
                            for variable, _, _ in g.wires:
                                bad = dict(completed)
                                bad[variable] = not bad[variable]
                                self.assertFalse(satisfies(f, bad))
            budget().check()
        # The production degree-five row has upper capacity four, not three.
        f = Formula(6)
        encode.interval(f, list(range(1, 7)), 1, 4)
        g = audit.Reconstruction(6)
        g.count(list(range(1, 7)), 1, 4)
        for count in (0, 1, 4, 5, 6):
            self.assertEqual(satisfies(f, g.complete({i: i <= count for i in range(1, 7)})), 1 <= count <= 4)

    def test_lexicographic_symmetry_is_complete_including_ties(self):
        n, m = 2, 3
        raw = [0, 0]
        for masks in product(range(1 << n), repeat=m):
            f = Formula(m * n)
            encode.column_order(f, [[a * n + v + 1 for v in range(n)] for a in range(m)])
            # A tiny exhaustive auxiliary oracle does not use either prefix
            # implementation to decide the projected lexicographic relation.
            relation = False
            base = values(masks, n)
            for assignment in product((False, True), repeat=f.variables - m * n):
                model = dict(base)
                model.update(zip(range(m * n + 1, f.variables + 1), assignment))
                relation |= satisfies(f, model)
            vectors = [tuple(bool(mask & 1 << v) for v in range(n)) for mask in masks]
            self.assertEqual(relation, vectors == sorted(vectors))
            self.assertTrue(any([vectors[i] for i in p] == sorted(vectors) for p in permutations(range(m))))
        self.assertFalse(audit.structural_truth(raw, [0, 0, 0], r=3, minimum=1))

    def test_full_independent_subset_cut_and_rejecting_witness(self):
        raw = graph(6, [(v, (v + 1) % 6) for v in range(6)])
        masks = [36, 18, 9, 9]
        candidate = encode.graph(raw, masks)
        witness = (1 << 2) | (1 << 3) | (1 << 4) | (1 << 7) | (1 << 10)
        cut = {"subset": 36, "witness": witness, "columns": masks, "candidate": candidate}
        options = {"m": 4, "r": 4, "minimum": 1}
        before, _ = encode.build(raw, [], **options)
        g = audit.reconstruct(raw, [], **options)
        self.assertTrue(satisfies(before, g.complete(values(masks, 6))))
        after, _ = encode.build(raw, [cut], **options)
        checked = audit.reconstruct(raw, [cut], **options)
        self.assertEqual(encode.dimacs(after), checked.bytes())
        self.assertFalse(satisfies(after, checked.complete(values(masks, 6))))
        clauses = after.clauses[len(before.clauses):]
        self.assertEqual(len(clauses), 4)
        # Exhaust all 2^8 incidence patterns on T. A cut is exactly the
        # condition that at most two of four columns completely miss T.
        for bits in product((False, True), repeat=8):
            model = {1 + a * 6 + v: bits[2 * a + j] for a in range(4) for j, v in enumerate((2, 5))}
            passed = all(any(model[lit] for lit in clause) for clause in clauses)
            self.assertEqual(passed, sum(not bits[2 * a] and not bits[2 * a + 1] for a in range(4)) <= 2)
        for field, value in (("subset", 3), ("witness", witness ^ 1), ("candidate", [0] * 11),
                             ("columns", [0] * 4)):
            bad = copy.deepcopy(cut)
            bad[field] = value
            for verifier in (lambda: encode.validate_cut(raw, bad, 4, 4), lambda: audit.checked_subset(raw, bad, 4, 4)):
                with self.assertRaises(ValueError):
                    verifier()
        with self.assertRaises(ValueError):
            encode.build(raw, [cut, cut], **options)

    def test_row_minimum_sizes_and_demand_maximality(self):
        # Five/six attachments and a degree-five H row are not silently lost.
        raw = graph(6, [(0, v) for v in range(1, 6)])
        f, metadata = encode.build(raw, [])
        g = audit.reconstruct(raw, [])
        self.assertEqual(encode.dimacs(f), g.bytes())
        self.assertEqual(metadata["incidence_variables"], 36)
        for size in (4, 5, 6, 8, 9):
            counter, replay = Formula(9), audit.Reconstruction(9)
            encode.interval(counter, list(range(1, 10)), 5, 8)
            replay.count(list(range(1, 10)), 5, 8)
            self.assertEqual(satisfies(counter, replay.complete({i: i <= size for i in range(1, 10)})), 5 <= size <= 8)
        impossible, _ = encode.build([0], [], m=2, r=3, minimum=2)
        # Empty/short intervals are represented by an actual empty clause.
        counter = Formula(2)
        encode.interval(counter, [1, 2], 3, 4)
        self.assertIn((), counter.clauses)
        self.assertGreater(len(impossible.clauses), 0)
        cycle = graph(6, [(v, (v + 1) % 6) for v in range(6)])
        # Alternating maximal columns cover all H, but cover no opposite pair.
        self.assertFalse(audit.structural_truth(cycle, [21, 42, 42], r=4, minimum=1, ordered=False))

    def test_cnf_models_rup_and_tampered_proofs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cnf, trace, model = (root / name for name in ("i.cnf", "p.lrat", "model.log"))
            cnf.write_text("p cnf 1 2\n1 0\n-1 0\n")
            trace.write_text("3 0 1 2 0\n")
            self.assertTrue(proof.verify(cnf, trace, budget())["python_rup_verified"])
            for raw in ("", "3 0 1 0\n", "3 0 -1 2 0\n", "2 0 1 2 0\n"):
                trace.write_text(raw)
                with self.assertRaises(ValueError):
                    proof.verify(cnf, trace, budget())
            cnf.write_text("p cnf 2 1\n1 2 0\n")
            model.write_text("s SATISFIABLE\nv 1 -2 0\n")
            self.assertEqual(proof.check_model(cnf, model, budget()), {1: True, 2: False})
            for raw in ("v -1 -2 0\n", "v 1 0\n", "v 1 -1 2 0\n", "v 1 3 0\n"):
                model.write_text(raw)
                with self.assertRaises(ValueError):
                    proof.check_model(cnf, model, budget())

    def test_fail_closed_budgets_schemas_and_final_acceptance(self):
        import run
        expired = Budget(1)
        expired.start -= 2
        with self.assertRaises(SearchLimit):
            expired.check()
        expired = Budget(1)
        expired.wall_start -= 30
        with self.assertRaises(SearchLimit):
            expired.check()
        for raw in ('{"a":1,"a":2}', '{"a":NaN}'):
            with self.assertRaises(ValueError):
                decode(raw)
        accepted = {"independent_encoding_verified": True, "independent_cuts_verified": True,
                    "H_triangle_free_and_alpha_at_most_eight_verified": True, "python_rup_verified": True,
                    "cnf_sha256": "c", "proof_sha256": "p",
                    "proof_replay": {"python_rup_verified": True, "cnf_sha256": "c", "proof_sha256": "p"}}
        self.assertTrue(run.negative_checked(accepted, 20, ["s VERIFIED"], "c", "p", "c"))
        for key in ("independent_encoding_verified", "independent_cuts_verified", "python_rup_verified"):
            bad = dict(accepted)
            bad[key] = False
            self.assertFalse(run.negative_checked(bad, 20, ["s VERIFIED"], "c", "p", "c"))
        self.assertFalse(run.negative_checked(accepted, 10, ["s VERIFIED"], "c", "p", "c"))
        self.assertFalse(run.negative_checked(accepted, 20, [], "c", "p", "c"))
        self.assertFalse(run.negative_checked(accepted, 20, ["s VERIFIED"], "changed", "p", "c"))
        self.assertFalse(run.negative_checked(accepted, 20, ["s VERIFIED"], "c", "changed", "c"))
        mismatched = copy.deepcopy(accepted)
        mismatched["proof_replay"]["cnf_sha256"] = "different_replay"
        self.assertFalse(run.negative_checked(mismatched, 20, ["s VERIFIED"], "different_replay", "p", "c"))
        both_changed = copy.deepcopy(accepted)
        both_changed["cnf_sha256"] = both_changed["proof_replay"]["cnf_sha256"] = "changed"
        self.assertFalse(run.negative_checked(both_changed, 20, ["s VERIFIED"], "changed", "p", "c"))
        review = {"schema_version": 1, "profile": run.PROFILE, "source_sha256": {"a": "b"},
                  "manifest_sha256": "m", "approved_for_pilot": True, "reviewer": "control"}
        run.review_ok(review, {"a": "b"}, "m")
        for field, value in (("approved_for_pilot", False), ("source_sha256", {}), ("manifest_sha256", "changed")):
            bad = dict(review)
            bad[field] = value
            with self.assertRaises(ValueError):
                run.review_ok(bad, {"a": "b"}, "m")


if __name__ == "__main__":
    BUDGET = Budget(30)
    unittest.main()
