"""Independent boundary and source-isolation controls for the stronger profile."""

import itertools
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from encoding import (Formula, anti_neighborhood_edge_bound, cardinality,
                      nondecreasing_signatures, private_neighbor_cap)
from native import Solver


LIBRARY = os.environ.get("CADICAL_LIBRARY")


class ProfileReviewControls(unittest.TestCase):
    def test_full_size_private_signature_boundaries(self):
        signatures = [[6 * row + bit + 1 for bit in range(6)] for row in range(33)]
        formula = Formula(198)
        nondecreasing_signatures(formula, signatures)
        private_neighbor_cap(formula, signatures, 4)
        base = sorted(list(itertools.chain.from_iterable([1 << bit] * 4 for bit in range(6)))
                      + [3] * 9)
        cases = [(base, True)]
        for bit in range(6):
            values = base.copy()
            values.remove(3)
            values.append(1 << bit)
            cases.append((sorted(values), False))
        # The first and last forbidden blocks exercise both window endpoints.
        self.assertEqual(cases[1][0][:5], [1] * 5)
        self.assertEqual(cases[-1][0][-5:], [32] * 5)
        for values, expected in cases:
            assignment = {literal: bool(value >> (5 - bit) & 1)
                          for row, value in zip(signatures, values)
                          for bit, literal in enumerate(row)}
            actual = all(any(assignment[abs(literal)] == (literal > 0) for literal in clause)
                         for clause in formula.clauses)
            self.assertEqual(actual, expected, values)

    @unittest.skipUnless(LIBRARY, "set CADICAL_LIBRARY for native controls")
    def test_full_size_signed_edge_bound_boundaries(self):
        # Inputs represent exact degree>=7, >=8, >=9 bits for all 39 vertices.
        thresholds = {v: {d: 3 * (v - 1) + d - 6 for d in (7, 8, 9)}
                      for v in range(1, 40)}
        formula = Formula(117)
        a_bits = anti_neighborhood_edge_bound(formula, thresholds, 40, 6, 6, 9, 118)
        cardinality(formula, [-bit for bit in a_bits], 0, 6)
        for total_a in (11, 12, 13, 17, 18):
            for difference in (67, 68, 69, 70):
                total_h = total_a + difference
                # These assignments are monotone within each vertex's three
                # bits, hence represent actual integer degrees in 6..9.
                values = [position < total_a for position in range(18)]
                values += [position < total_h for position in range(99)]
                expected = 30 + total_a >= 42 and 168 + total_h - total_a >= 236
                with Solver(LIBRARY, formula.variables) as solver:
                    for clause in formula.clauses:
                        solver.add(clause)
                    for variable, value in enumerate(values, 1):
                        solver.add((variable if value else -variable,))
                    self.assertEqual(solver.solve() == 10, expected, (total_a, total_h))

    def test_copied_checker_ignores_import_name_collisions(self):
        source = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(prefix="r310-profile-import-review-") as directory:
            root = Path(directory).resolve()
            driver = root / "degree_six"
            driver.mkdir()
            for name in ("encoding.py", "native.py", "search.py"):
                shutil.copy2(source / name, driver / name)
            checker = root / "vertex_transitive"
            checker.mkdir()
            shutil.copy2(source.parent / "vertex_transitive/checker.py", checker / "checker.py")
            script = """
import pathlib, sys, types
root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / 'degree_six'))
before = list(sys.path)
for name in ('checker', '_r310_degree_six_checker'):
    fake = types.ModuleType(name)
    fake.independent_set = lambda *_: None
    sys.modules[name] = fake
import search
assert sys.path == before
assert pathlib.Path(search._checker.__file__).resolve() == root / 'vertex_transitive/checker.py'
assert search.independent_set([0, 0, 0], 3) == 7
assert search._checker is sys.modules['_r310_degree_six_checker']
assert search._checker is not sys.modules['checker']
print('copied exact-path checker verified')
"""
            result = subprocess.run([sys.executable, "-I", "-c", script, str(root)],
                                    capture_output=True, text=True, timeout=5, cwd=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "copied exact-path checker verified")


if __name__ == "__main__":
    unittest.main()
