from typing import Dict, Any, Optional
import datetime

class MetricService:
    """
    Workstream 3: Canonical Metric Separation.
    Defines ownership and calculation methods for core quant metrics.
    """

    METRIC_DEFINITIONS = {
        "MODEL_PROBABILITY": "Raw sigmoid output from the ML model (Random Forest).",
        "CALIBRATED_PROBABILITY": "Platt-scaled probability representing estimated win frequency.",
        "EXPECTED_VALUE": "EV = (Prob_win * Target_Amt) - (Prob_loss * Stop_Amt) - Friction.",
        "RISK_REWARD": "Ratio of (Target - Entry) / (Entry - Stop).",
        "SIGNAL_SCORE": "Composite score used by V2.2 for ranking candidates.",
        "OPPORTUNITY_SCORE": "Heuristic discovery score separate from strategy execution."
    }

    @staticmethod
    def format_metric(name: str, value: Any, source: str) -> Dict[str, Any]:
        return {
            "name": name,
            "value": value if value is not None else "UNAVAILABLE",
            "definition": MetricService.METRIC_DEFINITIONS.get(name, "Unknown metric"),
            "source": source,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "status": "VALID" if value is not None else "UNAVAILABLE"
        }
