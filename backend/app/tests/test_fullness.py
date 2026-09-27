import pytest
from fastapi import HTTPException

from app import seed
from app.repositories import history, settings_repo
from app.repositories import windows as windows_repo
from app.services import estimate_service


@pytest.fixture()
def db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "t.db")
    seed.init_db()
    return tmp_path / "t.db"


def _window_id(name):
    return next(w["id"] for w in windows_repo.list_windows() if w["name"] == name)


def test_default_fullness_increase_raises_finished_width_and_meters(db):
    wid = _window_id("客厅落地窗")  # seeded without its own fullness
    before = estimate_service.run_estimate(wid, 1, False, "")
    settings_repo.set_default_fullness(3.0)
    after = estimate_service.run_estimate(wid, 1, False, "")
    assert after["fullness"] == 3.0
    assert after["fullness_source"] == "default"
    assert after["finished_width"] > before["finished_width"]
    assert after["meters"] > before["meters"]


def test_non_positive_default_fullness_rejected(db):
    for bad in (0, -1.5):
        with pytest.raises(ValueError):
            settings_repo.set_default_fullness(bad)
    assert settings_repo.get_default_fullness() == 2.0


def test_settings_router_rejects_non_positive(db):
    from app.routers.settings import DefaultFullnessBody, put_default_fullness

    with pytest.raises(HTTPException):
        put_default_fullness(DefaultFullnessBody(value=0))
    with pytest.raises(HTTPException):
        put_default_fullness(DefaultFullnessBody(value=-2))


def test_window_override_wins_over_default(db):
    wid = _window_id("客厅落地窗")
    windows_repo.set_fullness(wid, 1.5)
    settings_repo.set_default_fullness(3.0)
    r = estimate_service.run_estimate(wid, 1, False, "")
    assert r["fullness"] == 1.5
    assert r["fullness_source"] == "window"


def test_seeded_override_window_ignores_default_change(db):
    wid = _window_id("卧室窗")  # seeded with explicit 2.5
    settings_repo.set_default_fullness(3.0)
    r = estimate_service.run_estimate(wid, 1, False, "")
    assert r["fullness"] == 2.5
    assert r["fullness_source"] == "window"


def test_clearing_override_falls_back_to_default(db):
    wid = _window_id("客厅落地窗")
    windows_repo.set_fullness(wid, 1.5)
    windows_repo.set_fullness(wid, None)
    settings_repo.set_default_fullness(3.0)
    r = estimate_service.run_estimate(wid, 1, False, "")
    assert r["fullness"] == 3.0
    assert r["fullness_source"] == "default"


def test_history_keeps_fullness_and_meters_as_written(db):
    wid = _window_id("客厅落地窗")
    saved = estimate_service.run_estimate(wid, 1, True, "")
    settings_repo.set_default_fullness(3.5)
    run = history.get_run(saved["run_id"])
    assert run["result"]["fullness"] == saved["fullness"]
    assert run["result"]["meters"] == saved["meters"]


def test_resolve_order_matches_estimate_and_window_detail(db):
    from app.routers.windows import get_window

    wid = _window_id("客厅落地窗")
    settings_repo.set_default_fullness(2.8)
    detail = get_window(wid)
    est = estimate_service.run_estimate(wid, 1, False, "")
    assert detail["effective_fullness"] == est["fullness"] == 2.8
    assert detail["fullness_source"] == est["fullness_source"] == "default"


def test_existing_db_migrated_to_follow_default(tmp_path, monkeypatch):
    # simulate a DB created by the old seed (every window pinned to 2.0)
    import sqlite3

    db_path = tmp_path / "old.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)
    conn = sqlite3.connect(db_path)
    conn.executescript("""
    CREATE TABLE windows(id INTEGER PRIMARY KEY,name TEXT,width REAL,height REAL,fullness REAL,data_quality TEXT,note TEXT);
    CREATE TABLE fabrics(id INTEGER PRIMARY KEY,name TEXT,fabric_width REAL,hem_top REAL,hem_bottom REAL,data_quality TEXT,note TEXT);
    CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,window_id INT,fabric_id INT,result_json TEXT,note TEXT,created_at TEXT);
    INSERT INTO windows VALUES (1,'旧窗',3.0,2.6,2.0,'clean','');
    INSERT INTO fabrics VALUES (1,'遮光1.4m',1.4,0.10,0.15,'clean','');
    INSERT INTO settings VALUES ('default_fullness','2.0');
    """)
    conn.commit()
    conn.close()

    seed.init_db()
    assert windows_repo.get_window(1)["fullness"] is None
    settings_repo.set_default_fullness(3.0)
    r = estimate_service.run_estimate(1, 1, False, "")
    assert r["fullness"] == 3.0
    # migration runs only once
    windows_repo.set_fullness(1, 1.8)
    seed.init_db()
    assert windows_repo.get_window(1)["fullness"] == 1.8
