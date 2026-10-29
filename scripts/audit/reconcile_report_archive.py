"""
================================================================================
TradeMindAI: Report Archive Content Verification Script
================================================================================
Compares deleted report files retrieved read-only from Git HEAD against
archived files in backend/data/backup_snapshot_r4640/old_reports/.
Computes exact path matches, size matches, and byte-for-byte SHA-256 matches.
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

def compute_file_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def reconcile_report_archive():
    print("=== [TASK 2] Byte-For-Byte Report Archive Content Verification ===")

    # 1. Inspect archive_dir contents
    archived_files = {}
    if archive_dir.exists():
        for r, _, files in os.walk(archive_dir):
            for f in files:
                full_p = Path(r) / f
                rel_p = full_p.relative_to(archive_dir).as_posix()
                archived_files[rel_p] = full_p

    print(f"[*] Found {len(archived_files)} total files in archive directory '{archive_dir}'")

    # 2. Get list of tracked deleted files under reports/ from git ls-files
    deleted_tracked = []
    try:
        res = subprocess.run(["git", "ls-files", "-d", "reports/"], capture_output=True, text=True, cwd=str(root_dir), timeout=10)
        if res.returncode == 0:
            deleted_tracked = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
    except Exception as ex:
        print(f"[-] Error querying git ls-files: {ex}")

    print(f"[*] Found {len(deleted_tracked)} deleted tracked files under 'reports/'")

    matched_paths = 0
    matched_sizes = 0
    matched_content_sha256 = 0
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

        # Retrieve Git HEAD file content read-only
        try:
            res_git = subprocess.run(["git", "cat-file", "-p", f"HEAD:{git_path}"], capture_output=True, cwd=str(root_dir), timeout=5)
            if res_git.returncode != 0:
                unverifiable.append(rel_in_reports)
                continue

            git_content = res_git.stdout
            git_size = len(git_content)
            git_sha = compute_bytes_sha256(git_content)

            archive_size = archived_path.stat().st_size
            archive_sha = compute_file_sha256(archived_path)

            if git_size == archive_size:
                matched_sizes += 1

            if git_sha == archive_sha:
                matched_content_sha256 += 1
            else:
                mismatched_content.append({
                    "path": rel_in_reports,
                    "git_size": git_size,
                    "archive_size": archive_size,
                    "git_sha": git_sha[:12],
                    "archive_sha": archive_sha[:12]
                })
        except Exception as ex:
            unverifiable.append(rel_in_reports)

    print(f"\n[+] Archive Content Verification Results:")
    print(f"    - Total Deleted Tracked Reports: {len(deleted_tracked)}")
    print(f"    - Exact Path Counterpart Matches: {matched_paths}")
    print(f"    - File Size Matches: {matched_sizes}")
    print(f"    - Byte-for-Byte SHA-256 Content Matches: {matched_content_sha256}")
    print(f"    - Mismatched Content Count: {len(mismatched_content)}")
    print(f"    - Missing Counterparts: {len(missing_counterparts)}")
    print(f"    - Unverifiable Git Objects: {len(unverifiable)}")

    if mismatched_content:
        print(f"\n[-] Representative Content Mismatches:")
        for m in mismatched_content[:5]:
            print(f"    - {m['path']}: Git Size={m['git_size']}, Archive Size={m['archive_size']}, Git SHA={m['git_sha']}, Archive SHA={m['archive_sha']}")

    # Unmanifested Archive Files Accounting
    unmanifested_archive_count = len(archived_files) - matched_paths
    print(f"\n[*] Additional Archive Files (Outside 772 Tracked Paths): {unmanifested_archive_count} files")

if __name__ == "__main__":
    reconcile_report_archive()
