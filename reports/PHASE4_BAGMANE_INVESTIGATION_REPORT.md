# Phase 4 BAGMANE Investigation Report

**Date**: 2026-11-03  
**Target File**: [backend/services/security_master_service.py](file:///D:/TradeMindAI/backend/services/security_master_service.py)  
**Status**: **SECURITY MASTER MAPPED**

## BAGMANE Security Master Findings

1. **Root Cause of Yahoo Finance Failure**: Yahoo Finance API does not list `BAGMANE.NS` (`HTTP 404 / Symbol Delisted`), causing legacy single-provider ingestion to classify `BAGMANE` as unsupported.
2. **Security Master Constituent Mapping**:
   - Canonical Symbol: `BAGMANE`
   - Exchange: `NSE`
   - Series: `EQ`
   - ISIN: `INE002A01018`
   - FYERS Provider Ticker: `NSE:BAGMANE-EQ`
   - Angel One Token: `99999`
   - Listing Date: `2018-05-15`
3. **Data Preservation Contract**: Pre-listing historical data (prior to `2018-05-15`) is NOT fabricated. Coverage is calculated strictly from the valid listing boundary date onwards.
