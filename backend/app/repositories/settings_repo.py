from app.db import connect

DEFAULT_FULLNESS_KEY = "default_fullness"
DEFAULT_FULLNESS_FALLBACK = 2.0


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
        return DEFAULT_FULLNESS_FALLBACK
    return v if v > 0 else DEFAULT_FULLNESS_FALLBACK


def set_default_fullness(value) -> float:
    v = float(value)
    if v <= 0:
        raise ValueError("default fullness must be positive")
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (DEFAULT_FULLNESS_KEY, str(v)),
        )
        c.commit()
    finally:
        c.close()
    return v


def resolve_fullness(window: dict):
    """Single read order shared by bench, scheme page and window detail:
    a positive per-window fullness wins, otherwise the default fullness."""
    wv = (window or {}).get("fullness")
    if wv is not None:
        try:
            fv = float(wv)
        except (TypeError, ValueError):
            fv = 0.0
        if fv > 0:
            return fv, "window"
    return get_default_fullness(), "default"
