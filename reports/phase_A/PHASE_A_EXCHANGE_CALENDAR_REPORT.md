# TradeMindAI — Phase A Exchange Calendar Report

**Component**: [backend/services/data_quality_service.py](file:///D:/TradeMindAI/backend/services/data_quality_service.py)  
**Calendar Version**: `VERSIONED_NSE_TRADING_CALENDAR_V1` (v1.0.0)  
**Coverage Window**: 2015-01-01 through 2026-12-31

---

## 1. Official NSE Holiday Exclusions

The calendar tracks all official National Stock Exchange of India (NSE) trading holidays from 2015 to 2026, including:
- Republic Day (Jan 26)
- Mahashivratri
- Holi
- Good Friday
- Dr. Ambedkar Jayanti (Apr 14)
- Maharashtra Day (May 01)
- Independence Day (Aug 15)
- Mahatma Gandhi Jayanti (Oct 02)
- Diwali / Laxmi Pujan
- Gurunanak Jayanti
- Christmas (Dec 25)

### Impact on Quality Evaluation
Excluding official exchange holidays from expected trading days ensures that valid exchange closures are not incorrectly flagged as missing trading sessions.

---

## 2. Special Trading Sessions (Muhurat Trading)

The calendar registers special trading sessions with custom market hours:
- `2025-10-21 18:15:00`: Muhurat Trading (Diwali 2025) — 13 expected 5m slots (18:15 to 19:15 IST).
- `2026-11-08 18:15:00`: Muhurat Trading (Diwali 2026) — 13 expected 5m slots (18:15 to 19:15 IST).

---

## 3. Freshness Validator

Function `validate_freshness(latest_date_str, current_date_str)` evaluates market freshness:
- `FRESH`: `latest_date` within `max_days_behind` (default 7 calendar days) of `current_date`.
- `STALE`: `latest_date` > 7 days behind `current_date`.
- `FUTURE_DATED`: `latest_date > current_date`.
- `UNAVAILABLE`: missing `latest_date`.

---

## 4. Test Verification Summary

- `test_exchange_holidays_and_weekends_excluded_from_missing_sessions`: **PASSED**
- `test_intraday_scenario_6_holiday_excluded_from_expected_5m`: **PASSED**
- `test_phase_a_freshness_evaluation`: **PASSED**
- `test_future_dated_and_stale_freshness`: **PASSED**
