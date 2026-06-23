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
_DEV_PASSWORD = "YngelCutie@123"

_STATE_FILENAME = ".sysreg.dat"
_SALT = b"mhfd-9f3-internal"

# In-memory session cache. This is the real source of truth for "has the
# override been used this run" — disk persistence is best-effort on top of
# it. Without this, a silent write failure (read-only install folder, no
# admin rights on the client machine, AV locking the file, etc.) made the
# override look like it worked for a split second, then the next disk
# re-read brought the trial timer right back — which matches the bug being
# reported.
_session_dev_verified = False
_last_save_error = None  # kept only for local debugging, never shown in UI


def _fallback_dir() -> str:
    """A location that's writable even when the app's own install folder
    isn't (e.g. installed under Program Files without admin rights)."""
    if sys.platform.startswith("win"):
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        root = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(root, "MiguelitosHypedForDef")


def _candidate_paths():
    """Primary location first (next to the app), then a per-user fallback."""
    base = os.path.dirname(os.path.abspath(__file__))
    yield os.path.join(base, _STATE_FILENAME)
    yield os.path.join(_fallback_dir(), _STATE_FILENAME)


def _state_path() -> str:
    # Kept for compatibility with any external callers — first candidate.
    return next(_candidate_paths())


def _checksum(data: dict) -> str:
    raw = f"{data.get('v')}|{data.get('t')}|{data.get('d')}".encode("utf-8")
    return hashlib.sha256(raw + _SALT).hexdigest()[:16]


def _default_state() -> dict:
    return {"v": 1, "t": None, "d": False, "c": ""}


def _read_valid(path: str):
    """Parsed state dict if the file exists and its checksum matches,
    otherwise None. Never raises."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and data.get("c") == _checksum(data):
            return data
    except Exception:
        pass
    return None


def _load_state() -> dict:
    if _session_dev_verified:
        # Once verified this run, never let a disk read undo it in-memory.
        data = _default_state()
        data["d"] = True
        return data

    candidates = [d for d in (_read_valid(p) for p in _candidate_paths()) if d is not None]
    if not candidates:
        return _default_state()

    # The override is a one-way ratchet: if ANY known location says
    # verified, the whole thing is verified — even if a different location
    # (e.g. one that can no longer be written to) still has stale,
    # never-updated data sitting in it. Without this, a stale-but-valid
    # file at an earlier-checked path silently wins over a fresh, correct
    # write that landed at a later-checked path, which is exactly what was
    # happening here: the primary file was old and unwritable, so it kept
    # winning over the fallback file that actually had the unlock saved.
    if any(c.get("d") for c in candidates):
        data = _default_state()
        data["d"] = True
        return data

    return candidates[0]


def _hide_file(path: str):
    try:
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(str(path), 0x02)  # HIDDEN
    except Exception:
        pass


def _try_write(path: str, data: dict) -> bool:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        _hide_file(path)
        # Verify the write actually landed instead of trusting a silent
        # "success" — this is what was hiding the real failure before.
        return _read_valid(path) == data
    except Exception as err:
        global _last_save_error
        _last_save_error = err
        return False


def _save_state(data: dict) -> bool:
    data["c"] = _checksum(data)
    for path in _candidate_paths():
        if _try_write(path, data):
            return True
    # Every candidate location failed to persist. The in-memory cache (set
    # by mark_dev_verified) still guarantees correct behavior for the rest
    # of this run; only a restart before any successful save would lose
    # the unlock.
    return False


def is_dev_credentials(username: str, password: str) -> bool:
    """Exact, case-sensitive match against the hidden offline override account."""
    return username == _DEV_USERNAME and password == _DEV_PASSWORD


def mark_dev_verified():
    """Permanently disables the trial gate. Irreversible by design (no UI to undo it).

    Sets the in-memory flag first so the gate is guaranteed to be off for the
    rest of this run no matter what happens on disk, then attempts to persist
    that across restarts too."""
    global _session_dev_verified
    _session_dev_verified = True
    data = _load_state()
    data["d"] = True
    data["t"] = None
    _save_state(data)


def is_dev_verified() -> bool:
    return _session_dev_verified or bool(_load_state().get("d"))


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