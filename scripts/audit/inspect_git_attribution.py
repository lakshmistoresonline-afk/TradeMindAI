"""
================================================================================
TradeMindAI: Bounded Read-Only Git Attribution Audit (Task 2)
================================================================================
Executes path-scoped git status and diff commands with strict timeouts.
Categorizes working-tree changes across frontend, data, and config.
================================================================================
"""

import subprocess
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent

target_paths = [
    "web/package.json",
    "web/package-lock.json",
    "web/src/pages/EquitySignals.tsx",
    "web/src/utils/nseDateUtils.ts",
    "web/public/signals_history.json",
    "backend/data/features/",
    "reports/"
]

def audit_git_attribution():
    print("=== [TASK 2] Path-Scoped Git Attribution Audit ===")

    for target in target_paths:
        print(f"\n[*] Inspecting Path: {target}")
        try:
            # 1. Status check
            res_status = subprocess.run(
                ["git", "status", "--short", "--", target],
                capture_output=True, text=True, cwd=str(root_dir), timeout=5
            )
            status_output = res_status.stdout.strip()
            print(f"    - Git Status: {status_output if status_output else 'No changes'}")

            # 2. Diff summary check
            res_diff = subprocess.run(
                ["git", "diff", "--stat", "HEAD", "--", target],
                capture_output=True, text=True, cwd=str(root_dir), timeout=5
            )
            diff_output = res_diff.stdout.strip()
            print(f"    - Git Diff Stat vs HEAD:\n{diff_output if diff_output else '    (No diff)'}")

        except subprocess.TimeoutExpired:
            print(f"    - Result: TIMED OUT (Classified as NOT VERIFIED)")
        except Exception as ex:
            print(f"    - Result: ERROR ({ex})")

if __name__ == "__main__":
    audit_git_attribution()
