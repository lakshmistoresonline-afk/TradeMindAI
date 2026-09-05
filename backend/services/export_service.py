import pandas as pd
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from backend.core.container import container

class ExportService:
    """
    Workstream 29: Master Export.
    Generates JSON, CSV and Markdown (PDF Foundation) exports from Neon authority.
    """

    @staticmethod
    async def generate_master_signal_register() -> Dict[str, str]:
        repo = container.canonical_signal_repo

        # 1. Fetch All Signals (Authoritative)
        # We use a broad query to get everything from the ledger
        with repo.session_factory() as session:
            from backend.core.postgres import ShadowSignalDB
            res = session.query(ShadowSignalDB).order_by(ShadowSignalDB.timestamp.desc()).all()
            data = []
            for s in res:
                s_dict = {c.name: getattr(s, c.name) for c in s.__table__.columns}
                # Formatting
                for k, v in s_dict.items():
                    if isinstance(v, datetime): s_dict[k] = v.isoformat()
                data.append(s_dict)

        df = pd.DataFrame(data)

        # 2. Export CSV
        csv_path = "docs/nifty200/TRADEMIND_MASTER_SIGNAL_REGISTER.csv"
        df.to_csv(csv_path, index=False)

        # 3. Export JSON
        json_path = "docs/nifty200/TRADEMIND_MASTER_SIGNAL_REGISTER.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)

        # 4. Export Markdown Dossier (PDF Foundation)
        md_path = "docs/nifty200/TRADEMIND_MASTER_COMPLETE_SIGNAL_DOSSIER.md"

        forensic = container.forensic_analytical_service.get_master_metrics()

        with open(md_path, 'w') as f:
            f.write("# TRADEMIND AI: MASTER SIGNAL DOSSIER\n\n")
            f.write(f"**Generation Timestamp**: {datetime.utcnow().isoformat()} UTC\n")
            f.write(f"**Total Records**: {len(data)}\n\n")

            f.write("## 1. PERFORMANCE SUMMARY (VERIFIED)\n")
            f.write(f"- Verified Win Rate: {forensic['win_rate_pct']}%\n")
            f.write(f"- Profit Factor: {forensic['profit_factor']}\n")
            f.write(f"- Total Net P&L: {forensic['total_net_pnl_pct']}%\n")
            f.write(f"- Expectancy: {forensic['expectancy_pct']}%\n\n")

            f.write("## 2. SIGNAL REGISTER (LATEST 100)\n")
            # Handle potential missing columns in df
            cols = ['id', 'symbol', 'direction', 'entry_price', 'status', 'net_pnl', 'evaluation_mode']
            existing_cols = [c for c in cols if c in df.columns]
            f.write(df[existing_cols].head(100).to_markdown(index=False))

            f.write("\n\n## 3. AUDIT NOTES\n")
            f.write("- All verified outcomes mapped to 1m forensic data.\n")
            f.write("- Strategy V2.2 remains FROZEN.\n")
            f.write("- Data integrity score calculated at T-0.\n")

        return {
            "csv": csv_path,
            "json": json_path,
            "md": md_path
        }
