import datetime
from datetime import timezone
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

class SignalQualityGate:
    """
    V2.3 Shadow Quality Gate.
    Implements evidence-driven gating and Meta-Labeling quality rules for institutional signals.
    """

    @staticmethod
    def evaluate_v23_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a signal against V2.3 criteria & Meta-Labeling viability filters.
        Returns {decision: PUBLISH|BLOCK|NO_SIGNAL, reasons: list, metadata: dict}
        """
        reasons = []

        # 1. Calibrated Probability Floor (Validated Forensic Hypothesis)
        prob = signal.calibrated_probability or (signal.conviction / 100.0)
        min_prob = getattr(settings, "V23_MIN_CALIBRATED_PROBABILITY", 0.65)
        if prob < min_prob:
            reasons.append(f"LOW_PROBABILITY: {prob:.2f} < {min_prob:.2f}")

        # 2. RSI Exhaustion Filter
        rsi_enabled = getattr(settings, "V23_RSI_EXHAUSTION_ENABLED", True)
        long_rsi_thresh = getattr(settings, "V23_RSI_LONG_THRESHOLD", 70.0)
        short_rsi_thresh = getattr(settings, "V23_RSI_SHORT_THRESHOLD", 30.0)

        rsi = features.get("rsi_14") or features.get("RSI") or features.get("momentum_rsi")
        if rsi and rsi_enabled:
            # Scale RSI to 0-100 if provided as 0-1
            if rsi <= 1.0:
                rsi = rsi * 100.0

            if signal.direction == "LONG" and rsi > long_rsi_thresh:
                reasons.append(f"RSI_EXHAUSTION_LONG: {rsi:.1f} > {long_rsi_thresh:.1f}")
            elif signal.direction == "SHORT" and rsi < short_rsi_thresh:
                reasons.append(f"RSI_EXHAUSTION_SHORT: {rsi:.1f} < {short_rsi_thresh:.1f}")

        # 3. Expected Value Gate
        ev = signal.expected_value or 0.0
        if ev <= 0:
            reasons.append(f"NEGATIVE_EXPECTED_VALUE: {ev:.2f}")

        # 4. Risk/Reward Gate
        rr = signal.risk_reward_ratio or 0.0
        if rr < 1.5:
            reasons.append(f"INSUFFICIENT_RR: {rr:.2f}")

        # 5. Meta-Labeling Overextension & Volatility Checks
        dist_ema200 = features.get("dist_ema_200")
        if dist_ema200 is not None:
            if signal.direction == "LONG" and dist_ema200 > 0.20:
                reasons.append(f"OVEREXTENDED_LONG: {dist_ema200*100:.1f}% above EMA200")
            elif signal.direction == "SHORT" and dist_ema200 < -0.20:
                reasons.append(f"OVEREXTENDED_SHORT: {abs(dist_ema200)*100:.1f}% below EMA200")

        vol_z = features.get("market_volatility_z")
        if vol_z is not None and abs(vol_z) > 3.0:
            reasons.append(f"EXTREME_VOLATILITY_Z: {vol_z:.2f}")

        # 6. Sector Relative Strength Check
        sector_bias = features.get("sector_bias")
        if sector_bias == "WEAK" and signal.direction == "LONG":
            reasons.append("SECTOR_CONFLICT_WEAK_RELATIVE_STRENGTH")

        # 7. Smart Money Concepts (SMC) Structure Alignment
        smc_bear_ob = features.get("smc_bearish_ob", 0.0)
        smc_bull_ob = features.get("smc_bullish_ob", 0.0)
        if signal.direction == "LONG" and smc_bear_ob > 0.5 and not smc_bull_ob:
            reasons.append("SMC_CONFLICT_BEARISH_ORDER_BLOCK")
        elif signal.direction == "SHORT" and smc_bull_ob > 0.5 and not smc_bear_ob:
            reasons.append("SMC_CONFLICT_BULLISH_ORDER_BLOCK")

        # 8. Signal Age Decay Check (Edge drops significantly past 24h)
        if signal.timestamp and hasattr(signal, "candidate_timestamp") and signal.candidate_timestamp:
            try:
                sig_ts = signal.timestamp
                cand_ts = signal.candidate_timestamp
                if sig_ts and cand_ts:
                    age_hours = abs((cand_ts - sig_ts).total_seconds()) / 3600.0
                    if age_hours > 24.0:
                        reasons.append(f"SIGNAL_AGE_DECAY: {age_hours:.1f}h exceeds 24h alpha window")
            except Exception:
                pass

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

        # 12. Earnings Announcement Blackout Window Filter (Prevents Binary Earnings Gap Risk)
        days_to_earnings = features.get("days_to_earnings")
        if days_to_earnings is not None and days_to_earnings <= 3.0:
            reasons.append(f"EARNINGS_BLACKOUT_WINDOW: Announcement scheduled in {days_to_earnings:.0f} days")

        # 13. Institutional Net FII/DII Flow Pressure Filter
        fii_flow = features.get("fii_net_bias")
        if fii_flow is not None and signal.direction == "LONG" and fii_flow < -0.50:
            reasons.append(f"INSTITUTIONAL_FLOW_CONFLICT: Net FII outflow bias {fii_flow:.2f}")

        # 14. Index Options PCR Macro Support Filter
        index_pcr = features.get("nifty_index_pcr")
        if index_pcr is not None and signal.direction == "LONG" and index_pcr < 0.70:
            reasons.append(f"INDEX_PCR_BEARISH_DIVERGENCE: NIFTY Index PCR {index_pcr:.2f} < 0.70")

        # 15. Promoter Shareholding Change Filter
        promoter_change = features.get("promoter_net_change_pct")
        if promoter_change is not None and signal.direction == "LONG" and promoter_change < -2.0:
            reasons.append(f"PROMOTER_SELLING_DIVERGENCE: Net promoter stake reduction {promoter_change:.1f}%")

        decision = "PUBLISH" if not reasons else "BLOCK"

        return {
            "decision": decision,
            "reasons": reasons,
            "metadata": {
                "gate_version": "v2.3.6",
                "prob_threshold": min_prob,
                "rsi_enabled": rsi_enabled,
                "rsi_value": rsi,
                "dist_ema200": dist_ema200,
                "volatility_z": vol_z,
                "sector_bias": sector_bias,
                "smc_bull_ob": smc_bull_ob,
                "smc_bear_ob": smc_bear_ob,
                "dist_vp_poc": dist_poc,
                "cs_spread": cs_spread,
                "order_flow_imbalance": ofi,
                "days_to_earnings": days_to_earnings,
                "fii_net_bias": fii_flow,
                "index_pcr": index_pcr,
                "promoter_change": promoter_change
            }
        }
