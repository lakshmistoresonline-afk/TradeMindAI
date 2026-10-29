"""
================================================================================
TradeMindAI: Report Cleanup Script
================================================================================
Cleans up old, stale report files and audit sets in reports/ while preserving
reports/CLEAN_RESET_REPORT.md and creating a backup manifest in
backend/data/backup_snapshot_r4640/old_reports_backup/.
================================================================================
"""

import os
import shutil
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
reports_dir = root_dir / "reports"
backup_reports_dir = root_dir / "backend" / "data" / "backup_snapshot_r4640" / "old_reports"
backup_reports_dir.mkdir(parents=True, exist_ok=True)

# Preserve CLEAN_RESET_REPORT.md
PRESERVED_REPORTS = {"CLEAN_RESET_REPORT.md"}

def clean_reports():
    print("=== [CLEANUP] Cleaning Old Report Files ===")

    removed_files = 0
    removed_dirs = 0

    for item in list(reports_dir.iterdir()):
        if item.name in PRESERVED_REPORTS:
            print(f"    [PRESERVED] {item.name}")
            continue

        backup_dst = backup_reports_dir / item.name

        if item.is_file():
            shutil.copy2(item, backup_dst)
            item.unlink()
            removed_files += 1
        elif item.is_dir():
            shutil.copytree(item, backup_dst, dirs_exist_ok=True)
            shutil.rmtree(item)
            removed_dirs += 1

    print(f"=== [CLEANUP] Report Cleanup Complete: {removed_files} files and {removed_dirs} directories cleaned and archived ===")

if __name__ == "__main__":
    clean_reports()
