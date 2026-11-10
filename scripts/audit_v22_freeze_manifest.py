import json
import hashlib
import os

def audit_freeze_manifest():
    with open("docs/V22_FREEZE_MANIFEST.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("=== V2.2 FREEZE MANIFEST FORENSIC AUDIT ===")
    for item in manifest["files"]:
        name = item["name"]
        path = item["path"]
        manifest_hash = item["hash"]

        with open(path, "rb") as f_in:
            actual_hash = hashlib.sha256(f_in.read()).hexdigest().upper()

        match = (manifest_hash == actual_hash)
        print(f"File: {name} ({path})")
        print(f"  Manifest SHA-256: {manifest_hash}")
        print(f"  Actual SHA-256:   {actual_hash}")
        print(f"  Match: {match}\n")

if __name__ == "__main__":
    audit_freeze_manifest()
