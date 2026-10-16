"""
================================================================================
TradeMindAI: Authoritative Performance Metrics Exporter (v2.3-PROD)
================================================================================
Calculates performance metrics strictly from genuine persisted resolved signals
in web/public/signals_history.json using ResearchMetricsService.
Fails visibly if history is unavailable. Never uses hardcoded fake performance figures.
"""

import json
import os
import datetime
from backend.services.research_metrics_service import ResearchMetricsService

def export_performance():
    print("[Export Performance] Reading authoritative signals history...")
    history_path = os.path.abspath('web/public/signals_history.json')
    if not os.path.exists(history_path):
        print(f"[!] Error: {history_path} not found. Run export_history_json.py first.")
        raise FileNotFoundError(f"{history_path} not found.")

    with open(history_path, 'r') as f:
        data = json.load(f)

    records = data.get('records', [])
    metrics = ResearchMetricsService.calculate_performance_metrics(records)

    horizons = {}
    for h_name in ["SWING", "LONG", "SHORT"]:
        sub = [r for r in records if str(r.get('signal_type', '')).upper() == h_name or str(r.get('timeframe', '')).upper() == h_name]
        sub_metrics = ResearchMetricsService.calculate_performance_metrics(sub)
        horizons[h_name] = {
            "sample_size": sub_metrics.get("sample_size", 0),
            "eligible_directional_outcomes": sub_metrics.get("eligible_directional_outcomes", 0),
            "win_rate": sub_metrics.get("win_rate"),
            "profit_factor": sub_metrics.get("profit_factor"),
            "net_pnl": sub_metrics.get("net_pnl"),
            "brier_score": sub_metrics.get("brier_score"),
            "status": sub_metrics.get("status")
        }

    perf_payload = {
        "verified_benchmark": {
            "n": metrics.get("sample_size", 0),
            "eligible_directional_outcomes": metrics.get("eligible_directional_outcomes", 0),
            "win_rate": metrics.get("win_rate"),
            "profit_factor": metrics.get("profit_factor"),
            "net_pnl": metrics.get("net_pnl"),
            "status": metrics.get("status")
        },
        "horizons": horizons,
        "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "AUTHORITATIVE_LEDGER_DERIVED"
    }

    perf_path = os.path.abspath('web/public/performance.json')
    os.makedirs('web/public', exist_ok=True)
    with open(perf_path, 'w') as f:
        json.dump(perf_payload, f, indent=2)

    print(f"Successfully exported authentic performance metrics to {perf_path}")

if __name__ == "__main__":
    export_performance()
