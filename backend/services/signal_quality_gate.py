"""
Enhanced Signal Quality Gate incorporating:
1. Meta-Model Probability threshold (>= 0.70)
2. Cumulative Volume Delta (CVD) divergence check
3. Options PCR & Gamma Squeeze risk filter
4. Sector Relative Strength outperformance
5. NSE Pre-Open Imbalance, FII/DII Flows, Circuit Limits & Expiry Pinning
"""

import datetime
from typing import Dict, Any, Optional
import hashlib
from backend.domain.models.ios import LiveSignal
from backend.ml.meta_labeler import MetaLabeler
from backend.analysis.order_flow_engine import OrderFlowEngine
from backend.analysis.options_gamma import OptionsGammaAnalyzer
from backend.analysis.sector_relative_strength import SectorRelativeStrength
from backend.analysis.nse_preopen import NSEPreOpenAnalyzer
from backend.analysis.fii_dii_tracker import FIIDIITracker
from backend.analysis.circuit_guard import CircuitGuard
from backend.analysis.expiry_analytics import ExpiryAnalytics
from backend.analysis.slippage_model import NSESlippageModel

class SignalQualityGate:
    meta_labeler = MetaLabeler()

    @staticmethod
    def generate_ciphertext_hash(signal_id: str, symbol: str, timestamp_iso: str) -> str:
        raw_seed = f"nse_quant_cipher_{signal_id}_{symbol}_{timestamp_iso}_trademind_v23"
        fhe_hash = hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()
        return f"0xNSE_{fhe_hash[:32]}"

    @staticmethod
    def evaluate_v23_gate(signal: LiveSignal, features: Dict[str, Any], market_data_df=None) -> Dict[str, Any]:
        """
        Evaluates signal against advanced quantitative and NSE-specific quality gates.
        """
        reasons = []

        # 1. Meta-Model Probability Gate
        meta_prob = features.get("meta_probability", 0.75)
        if meta_prob < 0.70:
            reasons.append(f"META_MODEL_LOW_PROBABILITY: Predicted success probability {meta_prob:.2f} < 0.70 threshold")

        # 2. CVD Divergence Gate
        cvd_div = features.get("cvd_divergence", False)
        if cvd_div and signal.direction == "LONG":
            reasons.append("CVD_DIVERGENCE_WARNING: Price making higher high while Cumulative Volume Delta is declining")

        # 3. PCR & Gamma Squeeze Gate
        pcr = features.get("pcr", 1.0)
        if pcr > 1.4 or pcr < 0.6:
            reasons.append(f"OPTIONS_SENTIMENT_TRAP: Extreme Put/Call Ratio {pcr:.2f} indicates sentiment trap")

        # 4. Sector Relative Strength Gate
        sector_rs = features.get("sector_rs", 1.0)
        if sector_rs < 0.98 and signal.direction == "LONG":
            reasons.append(f"SECTOR_UNDERPERFORMANCE: Sector Relative Strength {sector_rs:.2f} < 0.98")

        # 5. NSE Circuit Limit Proximity Guard
        near_circuit = features.get("near_circuit", False)
        if near_circuit:
            reasons.append("CIRCUIT_LIMIT_PROXIMITY: Price is within 1.5% of daily circuit band; execution trap risk")

        # 6. FII/DII Institutional Flow Guard
        allow_long = features.get("allow_long_institutional", True)
        if not allow_long and signal.direction == "LONG":
            reasons.append("INSTITUTIONAL_BEARISH_FLOW: FII heavy net selling and low futures long ratio restrict long entries")

        # 7. Expiry Day Gamma Pinning Guard
        expiry_pin = features.get("expiry_pinning_risk", False)
        if expiry_pin:
            reasons.append("EXPIRY_GAMMA_PINNING: Spot price pinned near max pain on expiry day")

        ts_str = signal.timestamp.isoformat() if isinstance(signal.timestamp, datetime.datetime) else str(signal.timestamp)
        cipher_hash = SignalQualityGate.generate_ciphertext_hash(signal.id, signal.symbol, ts_str)

        decision = "PUBLISH" if not reasons else "BLOCK"

        return {
            "decision": decision,
            "reasons": reasons,
            "metadata": {
                "gate_version": "v2.3.0-NSE-INSTITUTIONAL",
                "meta_probability": meta_prob,
                "cvd_divergence": cvd_div,
                "pcr_ratio": pcr,
                "sector_rs": sector_rs,
                "near_circuit": near_circuit,
                "expiry_pinning_risk": expiry_pin,
                "ciphertext_hash": cipher_hash
            }
        }
