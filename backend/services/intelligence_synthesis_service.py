import datetime
import json
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, IntelligenceSynthesisDB

class IntelligenceSynthesisService:
    """
    Workstream 10: AI Intelligence Synthesis.
    Aggregates all context into a single auditable snapshot.
    """

    @staticmethod
    def synthesize_signal_intelligence(
        symbol: str,
        prediction_id: str,
        market_regime: Any,
        sector_metrics: Dict[str, Any],
        stock_profile: Dict[str, Any],
        inst_bias: Dict[str, Any]
    ) -> Dict[str, Any]:

        synthesis = {
            "id": prediction_id,
            "symbol": symbol,
            "timestamp": datetime.datetime.utcnow(),
            "market_context": json.dumps(market_regime.model_dump() if hasattr(market_regime, 'model_dump') else str(market_regime)),
            "sector_context": json.dumps(sector_metrics),
            "technical_context": json.dumps(stock_profile.get("technical_structure", {})),
            "fundamental_context": json.dumps({"score": stock_profile.get("fundamental_score", 0.5)}),
            "institutional_context": json.dumps(inst_bias),
            "supporting_evidence": json.dumps([
                f"Trend Alignment: {stock_profile.get('trend_score')}",
                f"Market Regime: {market_regime.regime if hasattr(market_regime, 'regime') else 'SIDEWAYS'}"
            ]),
            "conflicting_evidence": json.dumps([]),
            "risk_factors": json.dumps([f"Volatility: {stock_profile.get('volatility_score')}"]),
            "final_interpretation": "Convergent signals across multiple timeframes and institutional data."
        }

        with SessionLocal() as session:
            db_syn = IntelligenceSynthesisDB(**synthesis)
            session.add(db_syn)
            session.commit()

        return synthesis
