import json
import hashlib
import os
import subprocess

def get_sha256_normalized(content_bytes: bytes) -> str:
    # Normalize CRLF to LF for deterministic cross-platform hash comparison
    normalized = content_bytes.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest().upper()

def get_git_head_blob_hash(rel_path):
    try:
        res = subprocess.run(["git", "show", f"HEAD:{rel_path}"], capture_output=True, check=True)
        return get_sha256_normalized(res.stdout)
    except Exception as e:
        return f"GIT_ERROR: {e}"

def audit_v22_freeze_task_a():
    with open("docs/V22_FREEZE_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("=== V2.2 FREEZE FORENSIC TRACE AUDIT (TASK A - NORMALIZED LINE ENDINGS) ===")
    for item in manifest["files"]:
        name = item["name"]
        path = item["path"]
        manifest_hash = item["hash"]

        with open(path, "rb") as f_in:
            actual_hash = get_sha256_normalized(f_in.read())

        git_head_hash = get_git_head_blob_hash(path)

        match_head = (git_head_hash == actual_hash)
        match_manifest = (manifest_hash == actual_hash)

        print(f"File: {name} ({path})")
        print(f"  Manifest Expected SHA-256: {manifest_hash}")
        print(f"  Git HEAD Blob SHA-256:     {git_head_hash}")
        print(f"  Current File SHA-256:     {actual_hash}")
        print(f"  Match with Git HEAD:      {match_head}")
        print(f"  Match with Manifest:      {match_manifest}\n")

if __name__ == "__main__":
    audit_v22_freeze_task_a()
