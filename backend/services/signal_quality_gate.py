import datetime
from datetime import timezone
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

class SignalQualityGate:
    """
    V2.4 Enhanced Shadow Quality Gate.
    Implements evidence-driven gating, Dynamic VIX-Scaled Probability Floors,
    SMC Liquidity Sweeps, Anchored VWAP confirmation, and Meta-Labeling quality rules.
    """

    @staticmethod
    def get_dynamic_vix_floor(vix_value: Optional[float]) -> float:
        """
        Calculates dynamic probability floor conditioned on market volatility (India VIX).
        - Low VIX (< 13.0): Floor = 0.62
        - Normal VIX (13.0 - 17.0): Floor = 0.68
        - High VIX (> 17.0): Floor = 0.78
        """
        if vix_value is None or vix_value <= 0:
            return 0.68
        if vix_value < 13.0:
            return 0.62
        if vix_value <= 17.0:
            return 0.68
        return 0.78

    @staticmethod
    def evaluate_v23_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a signal against V2.4 criteria & Meta-Labeling viability filters.
        Returns {decision: PUBLISH|BLOCK|NO_SIGNAL, reasons: list, metadata: dict}
        """
        reasons = []

        # 1. Dynamic VIX-Scaled Calibrated Probability Floor (Strategy V2.4)
        prob = signal.calibrated_probability or (signal.conviction / 100.0)
        vix_val = features.get("vix_value") or features.get("india_vix") or 15.0
        min_prob = SignalQualityGate.get_dynamic_vix_floor(vix_val)

        if prob < min_prob:
            reasons.append(f"LOW_PROBABILITY_VIX_SCALED: {prob:.2f} < {min_prob:.2f} (VIX: {vix_val:.1f})")

        # 2. RSI Exhaustion Filter
        rsi_enabled = getattr(settings, "V23_RSI_EXHAUSTION_ENABLED", True)
        long_rsi_thresh = getattr(settings, "V23_RSI_LONG_THRESHOLD", 70.0)
        short_rsi_thresh = getattr(settings, "V23_RSI_SHORT_THRESHOLD", 30.0)

        rsi = features.get("rsi_14") or features.get("RSI") or features.get("momentum_rsi")
        if rsi and rsi_enabled:
            if rsi <= 1.0:
                rsi = rsi * 100.0

            if signal.direction == "LONG" and rsi > long_rsi_thresh:
                reasons.append(f"RSI_EXHAUSTION_LONG: {rsi:.1f} > {long_rsi_thresh:.1f}")
            elif signal.direction == "SHORT" and rsi < short_rsi_thresh:
                reasons.append(f"RSI_EXHAUSTION_SHORT: {rsi:.1f} < {short_rsi_thresh:.1f}")

        # 3. Anchored VWAP (AVWAP) Institutional Support Gate (Strategy V2.4)
        avwap = features.get("anchored_vwap") or features.get("vwap")
        if avwap and signal.entry_price:
            if signal.direction == "LONG" and signal.entry_price < avwap * 0.995:
                reasons.append(f"ANCHORED_VWAP_BELOW: Entry ₹{signal.entry_price:.1f} < AVWAP ₹{avwap:.1f}")

        # 4. Expected Value Gate
        ev = signal.expected_value or 0.0
        if ev <= 0:
            reasons.append(f"NEGATIVE_EXPECTED_VALUE: {ev:.2f}")

        # 5. Risk/Reward Gate
        rr = signal.risk_reward_ratio or 0.0
        if rr < 1.5:
            reasons.append(f"INSUFFICIENT_RR: {rr:.2f}")

        # 6. Meta-Labeling Overextension & Volatility Checks
        dist_ema200 = features.get("dist_ema_200")
        if dist_ema200 is not None:
            if signal.direction == "LONG" and dist_ema200 > 0.20:
                reasons.append(f"OVEREXTENDED_LONG: {dist_ema200*100:.1f}% above EMA200")
            elif signal.direction == "SHORT" and dist_ema200 < -0.20:
                reasons.append(f"OVEREXTENDED_SHORT: {abs(dist_ema200)*100:.1f}% below EMA200")

        vol_z = features.get("market_volatility_z")
        if vol_z is not None and abs(vol_z) > 3.0:
            reasons.append(f"EXTREME_VOLATILITY_Z: {vol_z:.2f}")

        # 7. Sector Relative Strength Check
        sector_bias = features.get("sector_bias")
        if sector_bias == "WEAK" and signal.direction == "LONG":
            reasons.append("SECTOR_CONFLICT_WEAK_RELATIVE_STRENGTH")

        # 8. Smart Money Concepts (SMC) Structure & Liquidity Sweep Gate
        smc_bear_ob = features.get("smc_bearish_ob", 0.0)
        smc_bull_ob = features.get("smc_bullish_ob", 0.0)
        if signal.direction == "LONG" and smc_bear_ob > 0.5 and not smc_bull_ob:
            reasons.append("SMC_CONFLICT_BEARISH_ORDER_BLOCK")
        elif signal.direction == "SHORT" and smc_bull_ob > 0.5 and not smc_bear_ob:
            reasons.append("SMC_CONFLICT_BULLISH_ORDER_BLOCK")

        # 9. Volume Profile Point of Control (POC) Anchor Filter
        dist_poc = features.get("dist_vp_poc")
        if dist_poc is not None and abs(dist_poc) > 0.08:
            reasons.append(f"VOLUME_PROFILE_DISCONNECT: {dist_poc*100:.1f}% away from 20d POC")

        # 10. Bid-Ask Spread Impact Filter
        cs_spread = features.get("corwin_schultz_spread")
        if cs_spread is not None and signal.entry_price and ev > 0:
            est_impact = (signal.entry_price * cs_spread * 2.0)
            if est_impact > (ev * 0.15):
                reasons.append(f"SPREAD_IMPACT_EXCESSIVE: Spread impact ₹{est_impact:.2f} exceeds 15% of EV")

        # 11. Order Flow Imbalance (OFI) Filter
        ofi = features.get("order_flow_imbalance")
        if ofi is not None:
            if signal.direction == "LONG" and ofi < -0.30:
                reasons.append(f"ORDER_FLOW_IMBALANCE_BEARISH: OFI {ofi:.2f} < -0.30")
            elif signal.direction == "SHORT" and ofi > 0.30:
                reasons.append(f"ORDER_FLOW_IMBALANCE_BULLISH: OFI {ofi:.2f} > 0.30")

        # 12. Earnings Announcement Blackout Window Filter
        days_to_earnings = features.get("days_to_earnings")
        if days_to_earnings is not None and days_to_earnings <= 3.0:
            reasons.append(f"EARNINGS_BLACKOUT_WINDOW: Announcement scheduled in {days_to_earnings:.0f} days")

        decision = "PUBLISH" if not reasons else "BLOCK"

        return {
            "decision": decision,
            "reasons": reasons,
            "metadata": {
                "gate_version": "v2.4.0-ENHANCED",
                "vix_value": vix_val,
                "prob_threshold": min_prob,
                "rsi_value": rsi,
                "anchored_vwap": avwap,
                "volatility_z": vol_z,
                "sector_bias": sector_bias
            }
        }
