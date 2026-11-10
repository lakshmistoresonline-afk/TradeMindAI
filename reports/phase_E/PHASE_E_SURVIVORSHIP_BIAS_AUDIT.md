# TradeMindAI — Phase E Survivorship-Bias Audit Report

**Component**: [backend/app/db/nifty500_symbols.py](file:///D:/TradeMindAI/backend/app/db/nifty500_symbols.py#L80)

---

## 1. Point-in-Time Constituent Filtering

To prevent survivorship bias during historical backtests (which occurs when evaluating 2016-2020 strategy performance using only 2026's surviving index constituents), TradeMindAI enforces `get_point_in_time_constituents(as_of_date: str)`.

### Listing Date Mapping (`POST_2015_LISTING_DATES`)
- `LICI`: Listed `2022-05-17`
- `ATGL`: Listed `2018-11-05`
- `NYKAA`: Listed `2021-11-10`
- `PAYTM`: Listed `2021-11-18`
- `POLICYBZR`: Listed `2021-11-15`
- `DELHIVERY`: Listed `2022-05-24`
- `AWL`: Listed `2022-02-08`
- `IRFC`: Listed `2021-01-29`
- `RVNL`: Listed `2019-04-11`
- `MAZDOCK`: Listed `2020-10-12`
- `ZOMATO`: Listed `2021-07-23`
- `SWIGGY`: Listed `2024-11-13`
- `HYUNDAI`: Listed `2024-10-22`
- `BAJAJHFL`: Listed `2024-09-16`

---

## 2. Test Verification Evidence

`test_phase_e_survivorship_bias_point_in_time_filtering` in `backend/tests/unit/test_phase_e_historical_backtesting.py`:
- Confirms that a historical backtest run on `as_of_date = "2016-01-01"` excludes `LICI`, `ATGL`, `NYKAA`, `PAYTM`, and `ZOMATO`.
- Confirms that a historical backtest run on `as_of_date = "2023-01-01"` includes `LICI`, `ATGL`, `NYKAA`, `PAYTM`, and `ZOMATO`.
