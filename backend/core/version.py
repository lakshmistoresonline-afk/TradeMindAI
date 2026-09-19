import datetime
from datetime import timezone
from backend.core.config import settings


# Canonical Version Identity (Phase 3 Final Hardening)
APP_VERSION = "2.2.0-STABLE-TRUTH"
RELEASE_ID = "TRADEMIND_FINAL_LOCK_20260919"
GIT_SHA = settings.GIT_SHA
BUILD_TIMESTAMP = "2026-09-19T13:00:00Z"
ENVIRONMENT = settings.ENVIRONMENT


def get_version_metadata():
    return {
        "version": APP_VERSION,
        "release": RELEASE_ID,
        "git_sha": GIT_SHA,
        "build_timestamp": BUILD_TIMESTAMP,
        "environment": ENVIRONMENT,
        "server_time": datetime.datetime.now(timezone.utc).isoformat()
    }

