from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

class Nifty200UniverseService:
    @staticmethod
    def get_current_nifty200_universe(db: Session) -> List[Dict[str, Any]]:
        """
        Retrieves the active NIFTY-200 universe dynamically from the canonical security_master table.
        Fails closed (raises RuntimeError/ValueError) if table is missing, empty, or query fails.
        """
        try:
            result = db.execute(text("""
                SELECT symbol, company_name, exchange, sector, industry, provider_symbol, active
                FROM security_master
                WHERE index_name = 'NIFTY 200' AND index_member = 1 AND active = 1;
            """)).fetchall()

            if not result:
                raise ValueError("Security master query returned zero active NIFTY-200 members. Failing closed.")

            constituents = []
            for row in result:
                p_sym = row[5]
                if not p_sym:
                    raise ValueError(f"Constituent {row[0]} has no provider_symbol configured. Failing closed.")
                constituents.append({
                    "symbol": row[0],
                    "company_name": row[1],
                    "exchange": row[2],
                    "sector": row[3],
                    "industry": row[4],
                    "provider_symbol": p_sym,
                    "active": bool(row[6])
                })
            return constituents
        except (OperationalError, ProgrammingError) as e:
            raise RuntimeError(f"Security master table missing or inaccessible: {e}")
        except Exception as e:
            raise RuntimeError(f"Critical error resolving NIFTY-200 universe: {e}")
