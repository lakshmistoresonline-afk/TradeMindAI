"""
================================================================================
TradeMindAI: CRLF-Normalized Report Archive Content Verification Script
================================================================================
Compares deleted report files retrieved read-only from Git HEAD against
archived files in backend/data/backup_snapshot_r4640/old_reports/, applying
standard line ending normalization (CRLF -> LF) to account for Windows checkout.
================================================================================
"""

import os
import hashlib
import subprocess
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
archive_dir = root_dir / "backend" / "data" / "backup_snapshot_r4640" / "old_reports"

def compute_bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def reconcile_crlf_archive():
    print("=== [TASK 1 & 2] CRLF-Normalized Archive Content Verification ===")

    archived_files = {}
    if archive_dir.exists():
        for r, _, files in os.walk(archive_dir):
            for f in files:
                full_p = Path(r) / f
                rel_p = full_p.relative_to(archive_dir).as_posix()
                archived_files[rel_p] = full_p

    print(f"[*] Found {len(archived_files)} total files in archive directory '{archive_dir}'")

    deleted_tracked = []
    try:
        res = subprocess.run(["git", "ls-files", "-d", "reports/"], capture_output=True, text=True, cwd=str(root_dir), timeout=10)
        if res.returncode == 0:
            deleted_tracked = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
    except Exception as ex:
        print(f"[-] Error querying git ls-files: {ex}")

    print(f"[*] Found {len(deleted_tracked)} deleted tracked files under 'reports/'")

    matched_paths = 0
    raw_sha256_matches = 0
    lf_normalized_sha256_matches = 0
    mismatched_content = []
    missing_counterparts = []
    unverifiable = []

    for git_path in deleted_tracked:
        rel_in_reports = Path(git_path).relative_to("reports").as_posix()

        if rel_in_reports not in archived_files:
            missing_counterparts.append(rel_in_reports)
            continue

        matched_paths += 1
        archived_path = archived_files[rel_in_reports]

        try:
            res_git = subprocess.run(["git", "cat-file", "-p", f"HEAD:{git_path}"], capture_output=True, cwd=str(root_dir), timeout=5)
            if res_git.returncode != 0:
                unverifiable.append(rel_in_reports)
                continue

            git_content = res_git.stdout
            git_sha = compute_bytes_sha256(git_content)

            file_content = archived_path.read_bytes()
            raw_file_sha = compute_bytes_sha256(file_content)

            # Normalize CRLF -> LF for line-ending-invariant content comparison
            norm_file_content = file_content.replace(b"\r\n", b"\n")
            norm_file_sha = compute_bytes_sha256(norm_file_content)

            if git_sha == raw_file_sha:
                raw_sha256_matches += 1

            if git_sha == norm_file_sha:
                lf_normalized_sha256_matches += 1
            else:
                mismatched_content.append({
                    "path": rel_in_reports,
                    "git_sha": git_sha[:12],
                    "norm_file_sha": norm_file_sha[:12]
                })
        except Exception as ex:
            unverifiable.append(rel_in_reports)

    print(f"\n[+] Archive Content Verification Results:")
    print(f"    - Total Deleted Tracked Reports: {len(deleted_tracked)}")
    print(f"    - Exact Path Counterpart Matches: {matched_paths}")
    print(f"    - Raw Byte-for-Byte SHA-256 Matches: {raw_sha256_matches}")
    print(f"    - LF-Normalized SHA-256 Content Matches: {lf_normalized_sha256_matches}")
    print(f"    - Mismatched Content Count (after LF normalization): {len(mismatched_content)}")
    print(f"    - Missing Counterparts: {len(missing_counterparts)}")
    print(f"    - Unverifiable Git Objects: {len(unverifiable)}")

    if mismatched_content:
        print(f"\n[-] Remaining Genuine Mismatches (after LF normalization): {len(mismatched_content)}")
        for m in mismatched_content[:5]:
            print(f"    - {m['path']}: Git SHA={m['git_sha']}, Norm File SHA={m['norm_file_sha']}")

if __name__ == "__main__":
    reconcile_crlf_archive()
