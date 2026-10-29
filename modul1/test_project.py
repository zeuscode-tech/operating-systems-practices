"""Детерминированные тесты основных алгоритмов проекта."""

from __future__ import annotations

import unittest
from pathlib import Path

from banker import evaluate_request, parse_requests, parse_state, safety_check
from wait_graph import build_graph, cycle_components, read_events, replay


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


class BankerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.safe_state = parse_state(DATA / "bank_state.txt")

    def test_first_state_is_safe(self) -> None:
        result = safety_check(self.safe_state)
        self.assertTrue(result.safe)
        self.assertEqual(result.sequence, ["P4", "P3", "P1", "P2", "P0"])

    def test_second_state_is_unsafe(self) -> None:
        result = safety_check(parse_state(DATA / "bank_state2.txt"))
        self.assertFalse(result.safe)
        self.assertEqual(result.sequence, ["P4"])
        self.assertEqual(result.unfinished, ["P0", "P1", "P2", "P3"])

    def test_requests_are_independent(self) -> None:
        statuses = [
            evaluate_request(self.safe_state, pid, request).status
            for pid, request in parse_requests(DATA / "requests.txt")
        ]
        self.assertEqual(statuses, ["GRANT", "REFUSE", "GRANT", "ERROR", "REFUSE"])
        self.assertEqual(self.safe_state.available, [4, 2, 1])


class WaitGraphTests(unittest.TestCase):
    def test_cycle_and_dependent_process(self) -> None:
        owners, waiting = replay(read_events(DATA / "waitlog.txt"))
        graph = build_graph(owners, waiting)
        self.assertEqual(cycle_components(graph), [["P3", "P4", "P5"]])
        self.assertEqual(graph["P7"], {"P5"})
        self.assertEqual(graph["P6"], {"P2"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
