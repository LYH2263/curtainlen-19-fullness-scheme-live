import json
from datetime import datetime, timezone
from app.db import connect

def insert_run(window_id, fabric_id, result, note=""):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(window_id,fabric_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (window_id, fabric_id, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _with_result(row):
    d = dict(row)
    d["result"] = json.loads(d.pop("result_json"))
    return d

def get_run(rid: int):
    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, w.name window_name, f.name fabric_name FROM calc_runs r
            LEFT JOIN windows w ON w.id=r.window_id LEFT JOIN fabrics f ON f.id=r.fabric_id
            WHERE r.id=?""", (rid,)).fetchone()
        return _with_result(row) if row else None
    finally:
        c.close()

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, w.name window_name, f.name fabric_name FROM calc_runs r
            LEFT JOIN windows w ON w.id=r.window_id LEFT JOIN fabrics f ON f.id=r.fabric_id
            ORDER BY r.id DESC LIMIT ?""", (limit,)).fetchall()
        return [_with_result(row) for row in rows]
    finally:
        c.close()
