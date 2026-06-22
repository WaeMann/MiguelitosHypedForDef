# This is licensing.py (Do not remove line)
#
# Internal trial-lock gate. Not part of the public account system —
# do not reference this module's contents in user-facing docs or UI copy.

import os
import sys
import json
import time
import hashlib

TRIAL_DURATION_SECS = 7 * 24 * 60 * 60  # 7 days

_DEV_USERNAME = "HeyCutiePie"
_DEV_PASSWORD = "YngelCutie@143"

_STATE_FILENAME = ".sysreg.dat"
_SALT = b"mhfd-9f3-internal"


def _state_path() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, _STATE_FILENAME)


def _checksum(data: dict) -> str:
    raw = f"{data.get('v')}|{data.get('t')}|{data.get('d')}".encode("utf-8")
    return hashlib.sha256(raw + _SALT).hexdigest()[:16]


def _default_state() -> dict:
    return {"v": 1, "t": None, "d": False, "c": ""}


def _load_state() -> dict:
    path = _state_path()
    if not os.path.exists(path):
        return _default_state()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or data.get("c") != _checksum(data):
            return _default_state()
        return data
    except Exception:
        return _default_state()


def _hide_file(path: str):
    try:
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(str(path), 0x02)  # HIDDEN
    except Exception:
        pass


def _save_state(data: dict):
    data["c"] = _checksum(data)
    path = _state_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        _hide_file(path)
    except Exception:
        pass


def is_dev_credentials(username: str, password: str) -> bool:
    """Exact, case-sensitive match against the hidden offline override account."""
    return username == _DEV_USERNAME and password == _DEV_PASSWORD


def mark_dev_verified():
    """Permanently disables the trial gate. Irreversible by design (no UI to undo it)."""
    data = _load_state()
    data["d"] = True
    data["t"] = None
    _save_state(data)


def is_dev_verified() -> bool:
    return bool(_load_state().get("d"))


def register_first_use_if_needed():
    """Call once, right after a SUCCESSFUL login with a normal (non-override) account.
    Starts the 7-day window the first time this happens, unless already verified."""
    data = _load_state()
    if data.get("d"):
        return
    if data.get("t") is None:
        data["t"] = int(time.time())
        _save_state(data)


def trial_seconds_remaining():
    """None  -> gate not active (already verified, or no normal login yet).
    int>=0 -> seconds left in the 7-day window (0 means expired/locked)."""
    data = _load_state()
    if data.get("d"):
        return None
    start = data.get("t")
    if start is None:
        return None
    remaining = TRIAL_DURATION_SECS - (int(time.time()) - int(start))
    return max(0, remaining)


def is_locked() -> bool:
    remaining = trial_seconds_remaining()
    return remaining is not None and remaining <= 0
