import math
import unittest

from tools.game_simulator import SimulationConfig, run_simulation


class SimulationSmokeTest(unittest.TestCase):
    def test_small_simulation_runs(self) -> None:
        config = SimulationConfig(
            num_players=3,
            games=5,
            max_turns=20,
            strategies=["builder", "balanced", "saboteur"],
            seed=42,
        )
        result = run_simulation(config)
        self.assertEqual(result.total_games, 5)
        self.assertEqual(sum(result.wins.values()), 5)
        self.assertGreater(result.avg_turns, 0)
        self.assertFalse(math.isnan(result.attack_rate))
        self.assertGreaterEqual(result.mean_slo, 0)
        self.assertGreaterEqual(result.mean_resilience, 0)


if __name__ == "__main__":
    unittest.main()
