import datetime
import os

# Canonical Version Identity (Phase 2 Hardening)
APP_VERSION = "2.1.0-PRODUCTION-HARDENED"
RELEASE_ID = "COMMERCIAL_RELEASE_20260919"
GIT_SHA = os.getenv("RENDER_GIT_COMMIT", "LOCAL_HEAD")
BUILD_TIMESTAMP = "2026-09-19T12:00:00Z"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def get_version_metadata():
    return {
        "version": APP_VERSION,
        "release": RELEASE_ID,
        "git_sha": GIT_SHA,
        "build_timestamp": BUILD_TIMESTAMP,
        "environment": ENVIRONMENT,
        "server_time": datetime.datetime.utcnow().isoformat()
    }
