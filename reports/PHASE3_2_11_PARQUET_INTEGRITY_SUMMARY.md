# Phase 3.2.11 Parquet Integrity Summary Report

**Date**: 2026-11-03  
**Total Parquet Files Audited**: 1,201 files across `backend/data/`  
**Inventory Source**: [reports/PHASE3_2_11_PARQUET_COMPLETE_INVENTORY.csv](file:///D:/TradeMindAI/reports/PHASE3_2_11_PARQUET_COMPLETE_INVENTORY.csv)

## Complete Inventory Breakdown

- **`CONFIRMED_VALID`**: `1,006` files (0 NULLs in primary keys or OHLCV columns, 0 duplicate keys, 0 geometry violations).
- **`READABLE_WITH_OHLCV_NULLS`**: `195` 5m intraday files (contain volume gap NULLs from Yahoo Finance provider quotes).
- **`UNREADABLE`**: `0` files (100% of all 1,201 Parquet files are readable).
- **`BACKUP_SNAPSHOT` files**: `201` files in `backend/data/backup_snapshot_r4640/features/`.
- **`LIVE_FEATURE` files**: `1,000` files in `backend/data/features/`.
