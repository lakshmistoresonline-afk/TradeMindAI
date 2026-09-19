import datetime
from datetime import timezone
from backend.core.config import settings


# Canonical Version Identity (Phase 4 Final Production Completion)
APP_VERSION = "2.3.0-GOLD-RELEASE"
RELEASE_ID = "TRADEMIND_GOLD_LOCK_20260919"
GIT_SHA = settings.GIT_SHA
BUILD_TIMESTAMP = datetime.datetime.now(timezone.utc).isoformat()
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

