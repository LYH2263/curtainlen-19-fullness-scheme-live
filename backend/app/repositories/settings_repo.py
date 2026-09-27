import math
from app.db import connect

DEFAULT_FULLNESS_KEY = "default_fullness"
FALLBACK_FULLNESS = 2.0


def get_all():
    c = connect()
    try:
        return {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
    finally:
        c.close()


def get_default_fullness() -> float:
    raw = get_all().get(DEFAULT_FULLNESS_KEY)
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return FALLBACK_FULLNESS
    if not math.isfinite(v) or v <= 0:
        return FALLBACK_FULLNESS
    return v


def has_window_override(window_fullness) -> bool:
    if window_fullness is None:
        return False
    try:
        v = float(window_fullness)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v) and v > 0


def resolve_fullness(window_fullness) -> float:
    """Single read order shared by bench, scheme page and settings:
    window's own fullness (>0) wins, otherwise the saved default."""
    if has_window_override(window_fullness):
        return float(window_fullness)
    return get_default_fullness()


def set_default_fullness(value) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValueError("default_fullness must be a number")
    if not math.isfinite(v) or v <= 0:
        raise ValueError("default_fullness must be positive")
    set_value(DEFAULT_FULLNESS_KEY, repr(v))
    return v


def set_value(key: str, value: str):
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        c.commit()
    finally:
        c.close()


def get_public() -> dict:
    """Settings as exposed to pages: default_fullness as the exact float the
    estimate path resolves, so displayed and applied values cannot drift."""
    raw = get_all()
    raw[DEFAULT_FULLNESS_KEY] = get_default_fullness()
    return raw
