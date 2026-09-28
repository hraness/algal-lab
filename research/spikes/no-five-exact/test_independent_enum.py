"""Bounded regressions for the independent exact enumerator.

The Python determinant uses Leibniz expansion, independent of the C Bareiss
oracle. Binary output belongs in the temporary directory, not the repository.
"""
from itertools import combinations, permutations
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


def determinant(matrix):
    size = len(matrix)
    answer = 0
    for order in permutations(range(size)):
        sign = (-1) ** sum(order[i] > order[j] for i in range(size) for j in range(i + 1, size))
        term = sign
        for row, column in enumerate(order):
            term *= matrix[row][column]
        answer += term
    return answer


def canonical_mask(indices, n):
    images = []
    for swap in (False, True):
        for turns in range(4):
            mask = 0
            for index in indices:
                x, y = index % n, index // n
                if swap:
                    x, y = y, x
                for _ in range(turns):
                    x, y = y, n - 1 - x
                mask |= 1 << (x + n * y)
            images.append(mask)
    return min(images)


class IndependentEnumeratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="algal-independent-enum-")
        cls.binary = Path(cls.temporary.name) / "independent-enum"
        subprocess.run(
            [compiler, "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
             str(ROOT / "independent_enum.c"), "-o", str(cls.binary)],
            check=True, capture_output=True, text=True, timeout=30,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def run_case(self, n, target, *options):
        result = subprocess.run(
            [str(self.binary), "--n", str(n), "--target", str(target),
             "--seconds", "5", *options],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        expected_code = {"found": 0, "exhausted": 1, "unknown": 124, "inspected": 0}[data["status"]]
        self.assertEqual(result.returncode, expected_code, result.stderr)
        self.assertLessEqual(data["cache_bytes"], 56 * 1024 * 1024)
        return data

    def assert_witness(self, data):
        points = data["points"]
        self.assertEqual(data["status"], "found")
        self.assertEqual(len(points), data["target"])
        self.assertEqual(len(set(map(tuple, points))), len(points))
        self.assertTrue(all(0 <= v < data["n"] for point in points for v in point))
        for five in combinations(points, 5):
            matrix = [[x, y, z, x*x + y*y + z*z, 1] for x, y, z in five]
            self.assertNotEqual(determinant(matrix), 0, five)

    def test_combination_and_locus_selftests_across_grid_sizes(self):
        for n in range(1, 7):
            with self.subTest(n=n):
                data = self.run_case(n, 5, "--selftest")
                self.assertEqual(data["status"], "inspected")
                self.assertEqual(data["oracle_checks"], 0 if n == 1 else 200*n**3)

    def test_initial_orbits_include_every_small_layer_type(self):
        counts, canonical = [0] * 5, [set() for _ in range(5)]
        n = 3
        for size in range(5):
            for indices in combinations(range(n*n), size):
                if size == 4:
                    rows = [[i % n, i // n, (i % n)**2 + (i // n)**2, 1] for i in indices]
                    if determinant(rows) == 0:
                        continue
                counts[size] += 1
                canonical[size].add(canonical_mask(indices, n))
        reduced = self.run_case(n, 9, "--inspect")
        full = self.run_case(n, 9, "--inspect", "--no-symmetry")
        self.assertEqual(reduced["orbit_sizes"], list(map(len, canonical)))
        self.assertEqual(full["orbit_sizes"], counts)
        self.assertEqual(reduced["orbit_sizes"][:2], [1, 3])

    def test_positive_and_negative_tiny_controls(self):
        for n, maximum in ((1, 1), (2, 4), (3, 8)):
            with self.subTest(n=n):
                self.assert_witness(self.run_case(n, maximum))
                excluded = self.run_case(n, maximum + 1)
                self.assertEqual(excluded["status"], "exhausted")
                self.assertTrue(excluded["complete"])
                self.assertEqual(excluded["orbits_completed"], excluded["orbits_total"])

    def test_full_single_slot_cache_terminates_without_changing_result(self):
        data = self.run_case(3, 9, "--cache-bits", "0")
        self.assertEqual(data["status"], "exhausted")
        self.assertEqual(data["cache_entries"], 1)
        self.assertGreater(data["cache_replacements"], 0)
        self.assertEqual(data["nodes"], self.run_case(3, 9)["nodes"])

    def test_symmetry_free_control_agrees(self):
        self.assert_witness(self.run_case(3, 8, "--no-symmetry"))
        excluded = self.run_case(3, 9, "--no-symmetry")
        self.assertEqual(excluded["status"], "exhausted")
        self.assertEqual(excluded["orbits_completed"], excluded["orbits_total"])

    def test_interrupted_search_never_claims_exclusion(self):
        node_limited = self.run_case(3, 9, "--max-nodes", "1")
        self.assertEqual(node_limited["status"], "unknown")
        self.assertFalse(node_limited["complete"])
        self.assertEqual(node_limited["nodes"], 1)
        timed = self.run_case(6, 19, "--seconds", "0.01")
        self.assertEqual(timed["status"], "unknown")
        self.assertFalse(timed["complete"])
        self.assertLess(timed["seconds"], 2)

    def test_invalid_inputs_fail_closed(self):
        for args in (("--n", "0"), ("--n", "7"), ("--cache-bits", "21"),
                     ("--target", "999"), ("--seconds", "nan"),
                     ("--seconds", "601"), ("--target", "-1"), ("--unknown", "1")):
            with self.subTest(args=args):
                result = subprocess.run([str(self.binary), *args], capture_output=True, timeout=3)
                self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
