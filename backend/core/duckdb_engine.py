import duckdb
import os
import pandas as pd
from typing import List, Dict, Any

class DuckDBEngine:
    def __init__(self, db_path: str = None):
        # Determine base directory reliably
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(base_dir, "data", "analytical.duckdb")

        # Standardized path for analytical features
        self.feature_storage = os.path.join(base_dir, "data", "features")
        if not os.path.exists(self.feature_storage):
            os.makedirs(self.feature_storage)

    def get_connection(self):
        return duckdb.connect(self.db_path)

    def ingest_features(self, symbol: str, df: pd.DataFrame):
        """
        Stores feature vectors as Parquet for high-speed analytical queries.
        """
        file_path = os.path.join(self.feature_storage, f"{symbol}.parquet")

        # Append logic: Read existing, concat, write new
        if os.path.exists(file_path):
            existing_df = pd.read_parquet(file_path)
            # Ensure unique dates
            combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['date'])
            combined_df.to_parquet(file_path, index=False)
        else:
            df.to_parquet(file_path, index=False)

    def query_features(self, query: str) -> pd.DataFrame:
        """
        Runs analytical queries across Parquet datasets using DuckDB.
        Example: SELECT * FROM 'backend/data/features/*.parquet' WHERE momentum_rsi > 0.8
        """
        con = self.get_connection()
        try:
            return con.execute(query).df()
        finally:
            con.close()

    def create_ml_dataset(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Vision 2.0: Dynamic Dataset Creation for ML Training.
        """
        file_path = os.path.join(self.feature_storage, f"{symbol}.parquet")
        if not os.path.exists(file_path):
            return pd.DataFrame()

        con = self.get_connection()
        query = f"SELECT * FROM '{file_path}' WHERE date >= '{start_date}' AND date <= '{end_date}'"
        return con.execute(query).df()

analytical_engine = DuckDBEngine()
