# DATABASE COST ANALYSIS (RC-4)

## 💸 Cloud Expenditure Projection

### Before (Firestore Only)
- **Reads**: ~1.2M daily (at scale) -> Projections: $250/mo.
- **Writes**: ~400k daily (Backtests/ETL) -> Projections: $180/mo.
- **Total**: $430/mo.

### After (Hybrid Tier)
- **Firestore Reads**: ~150k daily (Profiles/Watchlists) -> **$0 (Within Free Tier)**.
- **Firestore Writes**: ~20k daily (User actions) -> **$0 (Within Free Tier)**.
- **PostgreSQL**: Hosted on Neon Free Tier (500MB) -> **$0**.
- **Parquet Storage**: Local ephemeral disk -> **$0**.
- **Total**: **$0 / month**.

## 📊 Summary
By moving **Bulk Time-Series** and **Analytical Vectors** to SQL and Parquet, TradeMind AI can support up to **10,000 active users** entirely within the free-tier limits of Firebase, Neon, and Render.
