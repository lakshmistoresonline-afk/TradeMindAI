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
        with open(md_path, 'w') as f:
            f.write("# TRADEMIND AI: MASTER SIGNAL DOSSIER\n\n")
            f.write(f"**Generation Timestamp**: {datetime.utcnow().isoformat()} UTC\n")
            f.write(f"**Total Records**: {len(data)}\n\n")

            f.write("## 1. PERFORMANCE SUMMARY\n")
            # Logic here to add summary table...

            f.write("\n## 2. SIGNAL REGISTER\n")
            f.write(df[['id', 'symbol', 'direction', 'entry_price', 'status', 'net_pnl']].head(100).to_markdown(index=False))

        return {
            "csv": csv_path,
            "json": json_path,
            "md": md_path
        }
