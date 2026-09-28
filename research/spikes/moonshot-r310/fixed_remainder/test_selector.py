"""Selector projection, independent census agreement, and dual proof controls."""

import ctypes
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from catalogue import ramsey_catalogue
import proof as original_proof
from selector import (PROFILE, catalogue_columns, check_cover, encode_selection,
                      missed_bitsets, validate_selection, write_instance)
import selector_proof
from selector_run import control_inventory, run_attempt
from shared import Budget, SearchLimit, native

LIBRARY, SOLVER, TRIM = (os.environ.get(name) for name in ("CADICAL_LIBRARY", "CADICAL_BINARY", "LRAT_TRIM"))
INDEPENDENT_CENSUS = os.environ.get("SELECTOR_INDEPENDENT_CENSUS")


@unittest.skipUnless(LIBRARY, "set CADICAL_LIBRARY for projected SAT controls")
class ProjectedSelectorControls(unittest.TestCase):
    def test_every_selector_assignment_for_375_small_formulas(self):
        columns, missed, formulas, assignments = list(range(8)), [0, 1, 2, 3, 1, 4, 6, 7], 0, 0
        for caps in itertools.product(range(4), repeat=3):
            exact_allowed = sum(1 << v for v, cap in enumerate(caps) if cap == 1)
            for exact in range(8):
                if exact & ~exact_allowed:
                    continue
                for choose in range(1, 4):
                    clauses = []
                    metadata = encode_selection(columns, caps, exact, missed, choose, clauses.append)
                    with native.Solver(LIBRARY, metadata["variables"], freeze=range(1, 9)) as solver:
                        assume = solver.api.ccadical_assume
                        assume.argtypes, assume.restype = [ctypes.c_void_p, ctypes.c_int], None
                        for clause in clauses:
                            solver.add(clause)
                        for mask in range(256):
                            selected = [index for index in range(8) if mask >> index & 1]
                            rows = [sum(bool(columns[index] & (1 << v)) for index in selected) for v in range(3)]
                            expected = (len(selected) == choose
                                        and all(rows[v] <= caps[v] for v in range(3))
                                        and all(rows[v] == 1 for v in range(3) if exact >> v & 1)
                                        and all(not (missed[a] & missed[b])
                                                for a, b in itertools.combinations(selected, 2)))
                            for variable in range(1, 9):
                                assume(solver.handle, variable if mask >> (variable - 1) & 1 else -variable)
                            status = solver.solve()
                            self.assertIn(status, (10, 20))
                            self.assertEqual(status == 10, expected, (caps, exact, choose, mask))
                            assignments += 1
                    formulas += 1
        self.assertEqual(formulas, 375)
        self.assertEqual(assignments, 96_000)


class SelectorInputControls(unittest.TestCase):
    def test_bitset_misses_equal_direct_set_intersections(self):
        columns, independent = list(range(32)), list(range(1, 32))
        misses = missed_bitsets(columns, independent)
        for left, right in itertools.combinations(range(len(columns)), 2):
            direct = any(not (columns[left] & mask) and not (columns[right] & mask) for mask in independent)
            self.assertEqual(bool(misses[left] & misses[right]), direct)

    def test_invalid_inputs_and_interrupted_write(self):
        for columns, caps, exact, missed, choose in (
                ([1, 1], [1], 1, [0, 0], 2), ([2], [1], 1, [0], 1),
                ([1], [2], 1, [0], 1), ([1], [1], 1, [-1], 1),
                ([1], [1], 1, [0], 7), ([1], [4], 0, [0], 1)):
            with self.assertRaises(ValueError):
                validate_selection(columns, caps, exact, missed, choose)
        with self.assertRaises(ValueError):
            control_inventory({"unexpected": 1})
        with self.assertRaises(ValueError):
            catalogue_columns([2, 1])
        inventory = control_inventory({"columns": [1, 2], "row_caps": [1, 1], "exact_rows": 3,
                                       "missed_eight_set_bitsets": [0, 0], "choose": 2})
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch("selector.MAX_CLAUSES", 1), self.assertRaises(SearchLimit):
                write_instance(output, inventory)
            self.assertFalse((output / "instance.cnf").exists())
            self.assertFalse((output / "instance.json").exists())
        with patch("selector.MAX_VARIABLES", 1), self.assertRaises(SearchLimit):
            encode_selection([1, 2], [1, 1], 3, [0, 0], 2, lambda _: None)

    def test_cover_status_is_not_a_graph_certificate(self):
        inventory = control_inventory({"columns": [1, 2], "row_caps": [1, 1], "exact_rows": 3,
                                       "missed_eight_set_bitsets": [0, 0], "choose": 2})
        self.assertTrue(check_cover(inventory, [0, 1]))
        for selected in ([0], [0, 0], [0, 2]):
            with self.assertRaises(ValueError):
                check_cover(inventory, selected)
        inventory["missed_eight_set_bitsets"] = [1, 1]
        with self.assertRaises(ValueError):
            check_cover(inventory, [0, 1])


@unittest.skipUnless(INDEPENDENT_CENSUS, "set SELECTOR_INDEPENDENT_CENSUS for external census comparison")
class IndependentCensusControls(unittest.TestCase):
    def test_all_seven_inventories_match_independent_bron_kerbosch(self):
        evidence = json.loads(Path(INDEPENDENT_CENSUS).read_text())
        records = {tuple(record["deleted_local_pair"]): record for record in evidence["cases"]}
        catalogue = ramsey_catalogue()
        self.assertEqual(len(records), 7)
        for case in catalogue["cases"]:
            inventory = catalogue_columns(case["adjacency"], budget=Budget(10))
            record = records[tuple(case["representative_pair"])]
            self.assertEqual(inventory["base_adjacency_sha256"], record["base_adjacency_sha256"])
            self.assertEqual(len(inventory["columns"]), record["eligible_columns"])
            for key in ("eligible_column_inventory_sha256", "maximal_set_inventory_sha256"):
                self.assertEqual(inventory[key], record[key])
            self.assertEqual({size: inventory["maximal_set_counts"][size] for size in ("7", "8")},
                             record["maximal_set_counts"])


class SelectorProofControls(unittest.TestCase):
    def test_selector_deletion_line_boundary_and_original_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            cnf, proof = Path(directory) / "x.cnf", Path(directory) / "x.lrat"
            cnf.write_text("p cnf 1 3\n1 0\n-1 0\n1 0\n")
            limit = selector_proof.MAX_DELETION_LINE_BYTES
            deletion = "3 d 3 0"
            exact = deletion + " " * (limit - len(deletion) - 1) + "\n"
            proof.write_text(exact + "4 0 1 2 0\n")
            result = selector_proof.verify(cnf, proof, profile=PROFILE)
            self.assertTrue(result["verified_unsatisfiable"])
            self.assertEqual(result["maximum_line_bytes"], 2 * 1024**2)
            self.assertEqual(result["deletions"], 1)
            with self.assertRaisesRegex(ValueError, "oversized artifact line"):
                original_proof.verify(cnf, proof)
            proof.write_text(" " + exact + "4 0 1 2 0\n")
            with self.assertRaisesRegex(ValueError, "deletion record exceeds line limit"):
                selector_proof.verify(cnf, proof, profile=PROFILE)
            # The larger lexical allowance does not relax deletion semantics.
            proof.write_text(exact.replace("3 d 3 0", "3 d 3 1") + "4 0 1 2 0\n")
            with self.assertRaisesRegex(ValueError, "invalid selector LRAT deletion"):
                selector_proof.verify(cnf, proof, profile=PROFILE)

    def test_ordinary_line_and_total_proof_limits_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            cnf, proof = Path(directory) / "x.cnf", Path(directory) / "x.lrat"
            cnf.write_text("p cnf 1 2\n1 0\n-1 0\n")
            addition = "3 0 1 2 0"
            limit = selector_proof.MAX_ORDINARY_PROOF_LINE_BYTES
            exact = addition + " " * (limit - len(addition) - 1) + "\n"
            proof.write_text(exact)
            self.assertTrue(selector_proof.verify(cnf, proof, profile=PROFILE)["verified_unsatisfiable"])
            self.assertTrue(original_proof.verify(cnf, proof)["verified_unsatisfiable"])
            for prefix in (addition, "c d"):
                proof.write_text(prefix + " " * (limit - len(prefix)) + "\n")
                with self.assertRaisesRegex(ValueError, "non-deletion record"):
                    selector_proof.verify(cnf, proof, profile=PROFILE)
            with proof.open("wb") as stream:
                stream.truncate(selector_proof.MAX_PROOF_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "proof exceeds byte limit"):
                selector_proof.verify(cnf, proof, profile=PROFILE)

    def test_profile_is_explicit_and_original_bounds_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            cnf, proof = Path(directory) / "x.cnf", Path(directory) / "x.lrat"
            cnf.write_text("p cnf 10001 2\n10001 0\n-10001 0\n")
            proof.write_text("3 0 1 2 0\n")
            self.assertTrue(selector_proof.verify(cnf, proof, profile=PROFILE)["verified_unsatisfiable"])
            with self.assertRaises(ValueError):
                original_proof.verify(cnf, proof)
            with self.assertRaises(ValueError):
                selector_proof.verify(cnf, proof, profile="unreviewed-profile")
            with self.assertRaises(TypeError):
                selector_proof.verify(cnf, proof)
            for invalid in ("p cnf 60001 2\n1 0\n-1 0\n", "p cnf 1 1500001\n",
                            "p cnf 1 1\n2 0\n", "p cnf 1 2\n1 0\n", "p cnf 1 1\n1\n"):
                cnf.write_text(invalid)
                with self.assertRaises(ValueError):
                    selector_proof.verify(cnf, proof, profile=PROFILE)
            with cnf.open("wb") as destination:
                destination.truncate(32 * 1024**2 + 1)
            with self.assertRaises(ValueError):
                selector_proof.verify(cnf, proof, profile=PROFILE)

    def test_corrupt_proof_does_not_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            cnf, proof = Path(directory) / "x.cnf", Path(directory) / "x.lrat"
            cnf.write_text("p cnf 1 2\n1 0\n-1 0\n")
            for invalid in ("3 0 1 0\n", "3 0 -1 2 0\n", "3 0 3 0\n", "3 2 0 1 2 0\n", ""):
                proof.write_text(invalid)
                with self.assertRaises(ValueError):
                    selector_proof.verify(cnf, proof, profile=PROFILE)


@unittest.skipUnless(SOLVER and TRIM, "set CADICAL_BINARY and LRAT_TRIM for dual proof controls")
class SelectorRunnerControls(unittest.TestCase):
    def test_tiny_sat_and_unsat_with_two_actual_checkers(self):
        for incompatible in (False, True):
            with self.subTest(incompatible=incompatible), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "attempt"
                control = {"columns": [1, 2], "row_caps": [1, 1], "exact_rows": 3,
                           "missed_eight_set_bitsets": [int(incompatible)] * 2, "choose": 2}
                result = run_attempt(output, SOLVER, TRIM, small_control=control,
                                     construction_seconds=5, solve_seconds=5, audit_seconds=5)
                self.assertEqual(result["status"], "selector_unsat_dual_verified" if incompatible
                                 else "necessary_cover_found", result)
                self.assertEqual(result["necessary_selector_formula_unsat"], incompatible)
                self.assertEqual(result["python_rup_verified"], incompatible)
                self.assertEqual(result["lrat_trim_verified"], incompatible)
                self.assertTrue(result["sat_is_only_a_cover"])
                self.assertFalse(result["ramsey_graph_found"])
                self.assertFalse(result["external_ramsey_bound_claim_made"])
                for stage in result["stages"].values():
                    self.assertTrue(stage["owned_child_collected"])
                    self.assertIsNone(stage["external_stop"])
                if incompatible:
                    self.assertEqual(result["stages"]["lrat-trim"]["returncode"], 20)
                self.assertTrue((output / "source" / "fixed_remainder" / "selector_proof.py").exists())
                with self.assertRaises(FileExistsError):
                    run_attempt(output, SOLVER, TRIM, small_control=control)


if __name__ == "__main__":
    unittest.main()
