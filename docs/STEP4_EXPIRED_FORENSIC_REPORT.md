# TradeMind AI - Step 4 EXPIRED Forensic Report

## Executive Summary
Forensic analysis of the 322 `EXPIRED` trades confirms a critical failure in the `OutcomeEngine` trigger and stop-enforcement logic. These trades were allowed to bypass the 3% stop loss because they never formally "triggered" an entry, despite price moving significantly past the entry and stop levels.

## Critical Findings

### 1. Trigger Logic Failure (Good-Gap Bug)
The `OutcomeEngine` fails to trigger a trade if the price gaps to a *better* price than the entry limit.
- **Example**: `ADANIENT` (2023-02-28) Short entry at 1361.37. The next bar gapped to 1421 (higher). For a Short, 1421 is a better entry price. However, the engine only triggers if price is between Low and High or gaps *down* for a short.
- **Impact**: The trade remained in `WAITING_FOR_ENTRY` status indefinitely.

### 2. Stop Enforcement Bypass
Because the trades never "entered" (due to the bug above), the `OutcomeEngine` never active-monitored the stop loss.
- **Impact**: Price was allowed to move against the intended position for the full 200-bar holding period.
- **Result**: `ADANIPOWER` showed a raw loss of **-245%** at expiration, as the stop was never hit.

### 3. Data Integrity & Drawdown
The reported Max Drawdown of **-102.6%** is only possible if these extreme losses are accounted for in the equity curve. The current JSON masks these as `0.0%` profit, which is a reporting error that obscures catastrophic risk.

## Corporate Action Audit
- **Gaps > 20%**: Only 4 instances found (IRFC, ITC). 
- **Conclusion**: The majority of extreme losses are NOT due to corporate actions but are realized price movements against un-stopped positions.

## Conclusion
The Step 4 Baseline is **NOT VERIFIED**. The current results are mathematically invalid due to the engine's failure to enforce stops on gapped entries.

> [!CAUTION]
> **Risk Warning**: The strategy currently permits unlimited losses on gapped entries. This must be remediated in the `OutcomeEngine` before any production deployment or further optimization.
