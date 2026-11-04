import os
import pytest
from unittest.mock import MagicMock, patch
from backend.scripts.local_pulse_worker import PulseDistributedLock

def test_pulse_lock_verify_ownership_bytes():
    lock = PulseDistributedLock.__new__(PulseDistributedLock)
    lock.key = "lock:pulse"
    lock.token = "test-token-123"
    lock.redis_client = MagicMock()
    lock.redis_client.get.return_value = b"test-token-123"

    assert lock.verify_ownership() is True

def test_pulse_lock_verify_ownership_string():
    lock = PulseDistributedLock.__new__(PulseDistributedLock)
    lock.key = "lock:pulse"
    lock.token = "test-token-123"
    lock.redis_client = MagicMock()
    lock.redis_client.get.return_value = "test-token-123"

    assert lock.verify_ownership() is True

def test_pulse_lock_verify_ownership_missing():
    lock = PulseDistributedLock.__new__(PulseDistributedLock)
    lock.key = "lock:pulse"
    lock.token = "test-token-123"
    lock.redis_client = MagicMock()
    lock.redis_client.get.return_value = None

    assert lock.verify_ownership() is False

def test_pulse_lock_verify_ownership_mismatch():
    lock = PulseDistributedLock.__new__(PulseDistributedLock)
    lock.key = "lock:pulse"
    lock.token = "test-token-123"
    lock.redis_client = MagicMock()
    lock.redis_client.get.return_value = b"different-token-999"

    assert lock.verify_ownership() is False

def test_pulse_lock_verify_ownership_communication_failure():
    lock = PulseDistributedLock.__new__(PulseDistributedLock)
    lock.key = "lock:pulse"
    lock.token = "test-token-123"
    lock.redis_client = MagicMock()
    lock.redis_client.get.side_effect = Exception("Connection refused")

    with pytest.raises(RuntimeError, match="Redis communication failure"):
        lock.verify_ownership()

def test_pulse_lock_fails_closed_when_redis_unavailable(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "invalid_host_12345")
    with pytest.raises(RuntimeError, match="Redis instance required"):
        PulseDistributedLock()
