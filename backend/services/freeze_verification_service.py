import hashlib
import json
import os
from typing import Dict, Any, List

class V22FreezeVerificationService:
    @staticmethod
    def calculate_hash(file_path: str) -> str:
        """
        Calculates SHA256 hash of file content.
        Normalizes line endings to \n to ensure cross-platform consistency.
        """
        with open(file_path, "rb") as f:
            content = f.read()

        # Normalize line endings: CRLF -> LF
        normalized_content = content.replace(b"\r\n", b"\n")

        return hashlib.sha256(normalized_content).hexdigest().upper()

    @staticmethod
    def verify_freeze() -> Dict[str, Any]:
        manifest_path = os.path.join("docs", "V22_FREEZE_MANIFEST.json")
        if not os.path.exists(manifest_path):
            return {"status": "FAIL", "reason": "MANIFEST_MISSING"}

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        results = []
        all_passed = True

        for file_entry in manifest.get("files", []):
            file_path = file_entry["path"]
            expected_hash = file_entry["hash"].upper()

            # Adjust path if running from root
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                results.append({"file": file_path, "status": "FILE_NOT_FOUND"})
                all_passed = False
                continue

            actual_hash = V22FreezeVerificationService.calculate_hash(abs_path)
            passed = actual_hash == expected_hash

            results.append({
                "file": file_path,
                "expected": expected_hash,
                "actual": actual_hash,
                "status": "PASS" if passed else "FAIL"
            })

            if not passed:
                all_passed = False

        return {
            "status": "PASS" if all_passed else "V22_FREEZE_VIOLATION",
            "results": results
        }
