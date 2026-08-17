import sys
import os
import unittest
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from backend.services.calibration_service import CalibrationService
from backend.services.risk_engine import RiskEngine
from backend.core.config import settings

class TestShortLogic(unittest.TestCase):
    def test_direction_probability(self):
        # Case 1: LONG
        prob_up = 0.7
        p_long = CalibrationService.get_direction_probability(prob_up, "LONG")
        self.assertEqual(p_long, 0.7)

        # Case 2: SHORT
        p_short = CalibrationService.get_direction_probability(prob_up, "SHORT")
        self.assertAlmostEqual(p_short, 0.3)

        # Case 3: Complement
        self.assertAlmostEqual(p_long + p_short, 1.0)

    def test_risk_reward_normalization(self):
        atr = 2.0
        price = 100.0

        # LONG
        params_long = RiskEngine.calculate_trade_parameters("TEST", price, "LONG", atr)
        risk_long = abs(params_long['entry'] - params_long['stop_loss'])
        reward_long = abs(params_long['target'] - params_long['entry'])

        self.assertTrue(risk_long > 0)
        self.assertTrue(reward_long > 0)
        self.assertAlmostEqual(reward_long / risk_long, settings.DEFAULT_RISK_REWARD)

        # SHORT
        params_short = RiskEngine.calculate_trade_parameters("TEST", price, "SHORT", atr)
        risk_short = abs(params_short['entry'] - params_short['stop_loss'])
        reward_short = abs(params_short['target'] - params_short['entry'])

        self.assertTrue(risk_short > 0)
        self.assertTrue(reward_short > 0)
        self.assertAlmostEqual(reward_short / risk_short, settings.DEFAULT_RISK_REWARD)

    def test_expected_value_logic(self):
        # Scenario: P(UP) = 0.7, Direction = LONG
        # Risk = 10, Reward = 25 (2.5 RR)
        prob_up = 0.7
        p_long = CalibrationService.get_direction_probability(prob_up, "LONG")
        ev_long = CalibrationService.calculate_expected_value(p_long, 25, 10)

        # EV = 0.7 * 25 - 0.3 * 10 - costs
        # EV = 17.5 - 3 = 14.5 (minus ~0.03 costs)
        self.assertTrue(ev_long > 14.0)

        # Scenario: P(UP) = 0.7, Direction = SHORT
        p_short = CalibrationService.get_direction_probability(prob_up, "SHORT")
        ev_short = CalibrationService.calculate_expected_value(p_short, 25, 10)

        # EV = 0.3 * 25 - 0.7 * 10 - costs
        # EV = 7.5 - 7 = 0.5 (minus costs)
        self.assertTrue(ev_short < 1.0)

        # Scenario: P(UP) = 0.3, Direction = SHORT
        prob_up_low = 0.3
        p_short_high = CalibrationService.get_direction_probability(prob_up_low, "SHORT")
        ev_short_high = CalibrationService.calculate_expected_value(p_short_high, 25, 10)
        # EV = 0.7 * 25 - 0.3 * 10 = 14.5
        self.assertTrue(ev_short_high > 14.0)

if __name__ == "__main__":
    unittest.main()
