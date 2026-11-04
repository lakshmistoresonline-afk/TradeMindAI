# Phase 3.2.2 Code Defect Register

**Date**: 2026-11-03  
**Status**: All identified defects logged and classified.

## Defect Inventory

| Defect ID | Description | Severity | Classification | Status |
| :--- | :--- | :---: | :---: | :---: |
| **DEF-01** | Multi-year historical calendar gap in initial 26-holiday set | High | CONFIRMED DEFECT | **REMEDIATED** (v1.0.0 170 holidays embedded) |
| **DEF-02** | `BAGMANE` storage consistency marked FAILED instead of UNSUPPORTED | Medium | CONFIRMED DEFECT | **REMEDIATED** (`BAGMANE` set to UNSUPPORTED) |
| **DEF-03** | Queue timeout in crash recovery tests under Windows OS load | Low | CONFIRMED DEFECT | **REMEDIATED** (`timeout=35` in transaction safety tests) |
| **DEF-04** | Discrepancy between report description and scenario unit tests | Low | CONFIRMED DEFECT | **REMEDIATED** (12 distinct scenario tests created) |
