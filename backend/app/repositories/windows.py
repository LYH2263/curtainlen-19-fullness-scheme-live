from app.db import connect

def list_windows():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM windows ORDER BY id").fetchall()]
    finally:
        c.close()

def get_window(wid: int):
    c = connect()
    try:
        r = c.execute("SELECT * FROM windows WHERE id=?", (wid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def set_fullness(wid: int, value):
    c = connect()
    try:
        cur = c.execute("UPDATE windows SET fullness=? WHERE id=?", (value, wid))
        c.commit()
        return cur.rowcount > 0
    finally:
        c.close()
