from app.db import connect

def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS windows(id INTEGER PRIMARY KEY,name TEXT,width REAL,height REAL,fullness REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS fabrics(id INTEGER PRIMARY KEY,name TEXT,fabric_width REAL,hem_top REAL,hem_bottom REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,window_id INT,fabric_id INT,result_json TEXT,note TEXT,created_at TEXT);
    """)
    fresh = c.execute("SELECT COUNT(*) c FROM windows").fetchone()["c"] == 0
    if fresh:
        c.executemany("INSERT INTO windows(name,width,height,fullness,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("客厅落地窗",3.0,2.6,None,"clean",""),
            ("卧室窗",2.2,1.5,2.5,"clean",""),
            ("脏数据-零宽",0.0,2.0,None,"dirty","宽度为0"),
        ])
        c.executemany("INSERT INTO fabrics(name,fabric_width,hem_top,hem_bottom,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("遮光1.4m",1.4,0.10,0.15,"clean",""),
            ("纱帘2.8m",2.8,0.08,0.12,"clean",""),
            ("脏数据-零门幅",0.0,0.1,0.1,"dirty",""),
        ])
        c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('default_fullness','2.0')")
        c.commit()
    elif not c.execute("SELECT 1 FROM settings WHERE key='window_fullness_override_v1'").fetchone():
        # one-time migration: seeded fixed fullness used to shadow the default for
        # every window; NULL means "follow the default" from now on
        c.execute("UPDATE windows SET fullness=NULL")
        c.execute("INSERT INTO settings(key,value) VALUES ('window_fullness_override_v1','1')")
        c.commit()
    c.close()
