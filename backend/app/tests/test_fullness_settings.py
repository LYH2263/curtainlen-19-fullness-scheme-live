import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="curtainlen-test-")

import pytest
from fastapi.testclient import TestClient

from app import seed
from app.config import DB_PATH
from app.main import app
from app.repositories import settings_repo

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    seed.init_db()
    yield


def est(wid, fid=1):
    r = client.get(f"/api/estimate?window_id={wid}&fabric_id={fid}")
    assert r.status_code == 200
    return r.json()


def test_reject_non_positive_default():
    for bad in (0, -1.5, "abc", None):
        assert client.put("/api/settings", json={"default_fullness": bad}).status_code == 422
    assert client.put("/api/settings", json={}).status_code == 422
    assert client.get("/api/settings").json()["default_fullness"] == 2.0
    assert est(2)["fullness"] == 2.0


def test_larger_default_raises_finished_width_and_meters():
    base = est(2)  # 卧室窗 has no own fullness -> follows default
    assert base["fullness"] == 2.0
    assert base["fullness_source"] == "default"

    r = client.put("/api/settings", json={"default_fullness": 3.0})
    assert r.status_code == 200
    assert r.json()["default_fullness"] == 3.0

    new = est(2)
    assert new["fullness"] == 3.0
    assert new["finished_width"] == 6.6 > base["finished_width"] == 4.4
    assert new["meters"] == 8.75 > base["meters"] == 7.0
    # scheme page and bench read the same value
    assert client.get("/api/settings").json()["default_fullness"] == new["fullness"]


def test_window_override_wins():
    client.put("/api/settings", json={"default_fullness": 3.0})
    r = est(1)  # 客厅落地窗 has its own fullness 2.0 written
    assert r["fullness"] == 2.0
    assert r["fullness_source"] == "window"
    assert r["finished_width"] == 6.0
    assert r["meters"] == 14.25


def test_history_snapshot_keeps_written_version():
    saved = client.post("/api/estimate", json={"window_id": 2, "fabric_id": 1, "save": True}).json()
    assert saved["run_id"]
    client.put("/api/settings", json={"default_fullness": 3.0})

    old = client.get(f"/api/runs/{saved['run_id']}").json()
    assert old["result"]["fullness"] == 2.0
    assert old["result"]["meters"] == 7.0
    assert old["result"]["finished_width"] == 4.4

    listed = client.get("/api/runs").json()["items"][0]
    assert listed["result"]["fullness"] == 2.0
    assert listed["result"]["meters"] == 7.0

    assert est(2)["meters"] == 8.75  # new measurements use the new default


def test_run_not_found():
    assert client.get("/api/runs/9999").status_code == 404


def test_resolve_fullness_read_order():
    assert settings_repo.resolve_fullness(None) == 2.0
    assert settings_repo.resolve_fullness(0) == 2.0
    assert settings_repo.resolve_fullness(-3) == 2.0
    assert settings_repo.resolve_fullness(1.8) == 1.8
    settings_repo.set_default_fullness(2.6)
    assert settings_repo.resolve_fullness(None) == 2.6
    assert settings_repo.resolve_fullness(1.8) == 1.8
    for bad in (0, -1, "x", float("nan"), float("inf")):
        with pytest.raises(ValueError):
            settings_repo.set_default_fullness(bad)
