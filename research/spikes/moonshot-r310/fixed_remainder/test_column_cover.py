"""Exhaustive and adversarial controls for the separate column-cover reduction."""

import copy
import itertools
import random
import unittest

from column_cover import (maximal_independent_sets, replay_cover, search_cover,
                          validate_cover_problem)
from shared import SearchLimit


def abstract_problem(columns, caps, required, slots, compatible=None, private_cap=None,
                     cover_all=True):
    if compatible is None:
        compatible = [((1 << len(columns)) - 1) ^ (1 << i) for i in range(len(columns))]
    return {"columns": columns, "row_caps": caps, "required_mask": required,
            "slots": slots, "compatible": compatible, "private_cap": private_cap,
            "cover_all": cover_all}


def brute_cover(problem):
    columns, caps = problem["columns"], problem["row_caps"]
    for selected in itertools.combinations(range(len(columns)), problem["slots"]):
        if any(not (problem["compatible"][i] >> j & 1)
               for i, j in itertools.combinations(selected, 2)):
            continue
        usage = [sum(bool(columns[i] >> v & 1) for i in selected) for v in range(len(caps))]
        if any(value > cap for value, cap in zip(usage, caps)):
            continue
        if any(problem["required_mask"] >> v & 1 and usage[v] != 1 for v in range(len(caps))):
            continue
        if problem["cover_all"] and 0 in usage:
            continue
        if problem["private_cap"] is not None and any(
                sum(bool(columns[i] >> v & 1) and usage[v] == 1 for v in range(len(caps)))
                > problem["private_cap"] for i in selected):
            continue
        return selected
    return None


class MaximalSetControls(unittest.TestCase):
    def test_all_simple_graphs_through_five_vertices(self):
        checked = 0
        for n in range(1, 6):
            pairs = list(itertools.combinations(range(n), 2))
            for edge_mask in range(1 << len(pairs)):
                adjacency = [0] * n
                for k, (u, v) in enumerate(pairs):
                    if edge_mask >> k & 1:
                        adjacency[u] |= 1 << v
                        adjacency[v] |= 1 << u
                independent = [mask for mask in range(1 << n)
                               if all(not (mask >> u & 1 and mask >> v & 1)
                                      for k, (u, v) in enumerate(pairs) if edge_mask >> k & 1)]
                expected = [mask for mask in independent
                            if not any(mask != other and mask & other == mask for other in independent)]
                actual, _ = maximal_independent_sets(adjacency)
                self.assertEqual(actual, expected)
                checked += 1
        self.assertEqual(checked, 1099)

    def test_node_limit_is_incomplete_not_negative(self):
        with self.assertRaises(SearchLimit):
            maximal_independent_sets([0, 0], node_limit=1)


class CoverControls(unittest.TestCase):
    def test_pivot_can_require_a_lower_index_after_a_higher_one(self):
        problem = abstract_problem([0b110, 0b001], [1, 1, 1], 0b111, 2)
        result = search_cover(problem)
        self.assertEqual(result["status"], "necessary_cover_found")
        self.assertEqual(result["found_columns"], [1, 0])

    def test_zero_required_columns_are_completed_even_when_more_than_one(self):
        problem = abstract_problem([0b010, 0b100, 0b001], [1, 1, 1], 0b001, 3)
        result = search_cover(problem)
        self.assertEqual(result["status"], "necessary_cover_found")
        self.assertEqual(result["found_columns"], [2, 0, 1])

    def test_exhaustive_column_families_and_all_small_slot_counts(self):
        checked = 0
        for family in range(1, 1 << 7):
            columns = [mask for mask in range(1, 8) if family >> (mask - 1) & 1]
            for slots in range(1, 4):
                for caps, required in [([1, 1, 1], 7), ([1, 2, 3], 1), ([2, 2, 2], 0)]:
                    problem = abstract_problem(columns, caps, required, slots)
                    result, expected = search_cover(problem), brute_cover(problem)
                    self.assertEqual(result["status"] == "necessary_cover_found", expected is not None)
                    if expected is None:
                        self.assertTrue(replay_cover(problem, result)["replayed"])
                    checked += 1
        self.assertEqual(checked, 1143)

    def test_pair_constraints_private_caps_and_optional_coverage(self):
        rng = random.Random(20260928)
        for _ in range(200):
            columns = sorted(rng.sample(range(1, 32), rng.randint(1, 9)))
            caps = [rng.randint(1, 3) for _ in range(5)]
            required = sum(1 << v for v, cap in enumerate(caps) if cap == 1 and rng.choice([False, True]))
            compatible = [0] * len(columns)
            for i, j in itertools.combinations(range(len(columns)), 2):
                if rng.random() < 0.7:
                    compatible[i] |= 1 << j
                    compatible[j] |= 1 << i
            problem = abstract_problem(columns, caps, required, rng.randint(1, 5), compatible,
                                       rng.choice([None, 0, 1, 2]), rng.choice([False, True]))
            expected, result = brute_cover(problem), search_cover(problem)
            self.assertEqual(result["status"] == "necessary_cover_found", expected is not None)
            if expected is None:
                self.assertTrue(replay_cover(problem, result)["replayed"])

    def test_negative_replay_rejects_missing_branch_and_false_candidate(self):
        problem = abstract_problem([0b011, 0b101], [1, 1, 1], 0b001, 2)
        result = search_cover(problem)
        self.assertEqual(result["status"], "no_necessary_cover")
        self.assertTrue(replay_cover(problem, result)["replayed"])
        missing = copy.deepcopy(result)
        missing["tree"][0]["options"].pop()
        missing["tree"][0]["children"].pop()
        with self.assertRaises(ValueError):
            replay_cover(problem, missing)
        false_candidate = copy.deepcopy(result)
        false_candidate["tree"][1]["candidates_hex"] = "0x2"
        with self.assertRaises(ValueError):
            replay_cover(problem, false_candidate)
        omitted_candidate = copy.deepcopy(result)
        omitted_candidate["tree"][0]["candidates_hex"] = "0x1"
        with self.assertRaises(ValueError):
            replay_cover(problem, omitted_candidate)
        false_leaf = copy.deepcopy(result)
        false_leaf["tree"][0]["status"] = "too_few_columns"
        with self.assertRaises(ValueError):
            replay_cover(problem, false_leaf)
        cyclic = copy.deepcopy(result)
        cyclic["tree"][0]["children"][0] = 0
        with self.assertRaises(ValueError):
            replay_cover(problem, cyclic)
        unreachable = copy.deepcopy(result)
        unreachable["tree"].append(copy.deepcopy(result["tree"][1]))
        unreachable["search_nodes"] += 1
        with self.assertRaises(ValueError):
            replay_cover(problem, unreachable)

    def test_limits_and_invalid_compatibility_fail_closed(self):
        problem = abstract_problem([0b011, 0b101], [1, 1, 1], 0b001, 2)
        with self.assertRaises(SearchLimit):
            search_cover(problem, node_limit=1)
        bad = copy.deepcopy(problem)
        bad["compatible"][0] |= 1
        with self.assertRaises(ValueError):
            validate_cover_problem(bad)
        bad = copy.deepcopy(problem)
        bad["compatible"][0] = 0
        with self.assertRaises(ValueError):
            validate_cover_problem(bad)


if __name__ == "__main__":
    unittest.main()
