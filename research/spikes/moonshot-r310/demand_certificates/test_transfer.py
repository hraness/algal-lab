"""Focused exact and adversarial controls for the frozen transfer rule."""

import itertools
import time
import unittest
from unittest.mock import patch

import transfer
import verify
import verify_sample as sampled


def oracle(adjacency, pairs, weights):
    """Separate small-graph brute-force oracle over *all* vertex subsets."""
    n = len(adjacency)
    return max((sum(w for (u, v), w in zip(pairs, weights)
                    if mask & (1 << u) and mask & (1 << v))
                for mask in range(1 << n)
                if all(not (adjacency[v] & mask) for v in range(n) if mask & (1 << v))), default=0)


def six_cycle():
    return [(1 << ((v - 1) % 6)) | (1 << ((v + 1) % 6)) for v in range(6)]


class TransferControls(unittest.TestCase):
    def test_frozen_fixture_and_nonadaptive_proposals(self):
        bundle, baseline = transfer.fixture()
        self.assertEqual((baseline["sample_size"], baseline["certified_exclusions"]), (128, 113))
        trials = list(transfer.proposals(bundle))
        self.assertEqual(len(trials), 120)
        self.assertEqual([target["index"] for target, _, _, _ in trials],
                         [index for index in transfer.TARGETS for _ in range(8)])
        self.assertEqual(set(source["sample_index"] for _, source, _, _ in trials)
                         & set(transfer.TARGETS), set())
        for target, source, distance, kept in trials:
            adjacency = target["adjacency"]
            old = dict((tuple(pair), weight) for pair, weight in zip(source["demands"], source["weights"]))
            self.assertGreaterEqual(distance, 0)
            self.assertEqual(len(kept), len(set(tuple(pair) for pair, _ in kept)))
            for pair, weight in kept:
                self.assertEqual(weight, old[tuple(pair)])
                self.assertFalse(adjacency[pair[0]] & (1 << pair[1]))
                self.assertFalse(adjacency[pair[0]] & adjacency[pair[1]])
        with patch.object(transfer, "SAMPLE_SHA256", "0" * 64):
            with self.assertRaises(verify.InvalidCertificate):
                transfer.fixture()

    def test_direct_checker_matches_exhaustive_small_graphs(self):
        checks = 0
        for n in range(1, 5):
            edges = list(itertools.combinations(range(n), 2))
            for bits in range(1 << len(edges)):
                adjacency = [0] * n
                for i, (u, v) in enumerate(edges):
                    if bits & (1 << i):
                        adjacency[u] |= 1 << v
                        adjacency[v] |= 1 << u
                demands = [[u, v] for u, v in edges
                           if not (adjacency[u] & (1 << v)) and not adjacency[u] & adjacency[v]]
                for weights in ([1] * len(demands), [1 + i % 3 for i in range(len(demands))]):
                    got, nodes = transfer.direct_maximum(adjacency, demands, weights,
                                                         {"start": time.process_time(), "nodes": 0})
                    self.assertEqual(got, oracle(adjacency, demands, weights))
                    self.assertGreater(nodes, 0)
                    checks += 1
        self.assertEqual(checks, 150)

    def test_six_cycle_and_adversarial_target_reject_false_transfer(self):
        adjacency = six_cycle()
        pairs, weights = [[0, 3], [1, 4], [2, 5]], [2, 1, 1]
        accepted = sampled.verify_claim(adjacency, pairs, weights, 2, 1, sampled.Budget())
        self.assertTrue(accepted["maximal_extension_excluded"])
        self.assertEqual(transfer.direct_maximum(adjacency, pairs, weights,
                                                {"start": time.process_time(), "nodes": 0})[0], 2)
        # Keeping a valid source demand set is not enough: an edgeless target
        # has larger independent sets, so the old capacity must be rejected.
        empty = [0] * 6
        self.assertEqual(oracle(empty, pairs, weights), 4)
        with self.assertRaisesRegex(verify.InvalidCertificate, "capacity is false"):
            sampled.verify_claim(empty, pairs, weights, 2, 1, sampled.Budget())
        # Deleting two edges keeps these demands valid but makes M=2 false.
        changed = adjacency.copy()
        for u, v in ((0, 1), (3, 4)):
            changed[u] &= ~(1 << v)
            changed[v] &= ~(1 << u)
        self.assertEqual(oracle(changed, pairs, weights), 3)
        self.assertEqual(transfer.direct_maximum(changed, pairs, weights,
                                                {"start": time.process_time(), "nodes": 0})[0], 3)
        with self.assertRaisesRegex(verify.InvalidCertificate, "capacity is false"):
            sampled.verify_claim(changed, pairs, weights, 2, 1, sampled.Budget())
        with self.assertRaisesRegex(verify.InvalidCertificate, "strict weighted"):
            sampled.verify_claim(adjacency, pairs, weights, 2, 2, sampled.Budget())
        with self.assertRaises(verify.VerificationLimit):
            sampled.verify_claim(adjacency, pairs, weights, 2, 1,
                                 sampled.Budget(combinations=1))
        with self.assertRaises(transfer.OracleLimit):
            transfer.direct_maximum(adjacency, pairs, weights,
                                    {"start": time.process_time() - 6, "nodes": 0})


if __name__ == "__main__":
    unittest.main()
