import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "users.db"
)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            rappel_actif INTEGER DEFAULT 1,
            ville TEXT,
            latitude REAL,
            longitude REAL,
            langue TEXT DEFAULT 'fr'
        )
    """)
    for col, typ, default in [
        ("ville", "TEXT", None),
        ("latitude", "REAL", None),
        ("longitude", "REAL", None),
        ("langue", "TEXT", "'fr'"),
    ]:
        try:
            if default:
                c.execute(f"ALTER TABLE users ADD COLUMN {col} {typ} DEFAULT {default}")
            else:
                c.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def register_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
    """, (user_id, username or ""))
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT rappel_actif FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def set_rappel(user_id: int, actif: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET rappel_actif = ? WHERE user_id = ?", (actif, user_id))
    conn.commit()
    conn.close()


def get_users_with_rappel():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE rappel_actif = 1")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def set_ville(user_id: int, ville: str, lat: float, lon: float):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET ville = ?, latitude = ?, longitude = ? WHERE user_id = ?",
        (ville, lat, lon, user_id)
    )
    conn.commit()
    conn.close()


def get_ville(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT ville, latitude, longitude FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = c.fetchone()
    conn.close()
    return row


def set_langue(user_id: int, langue: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET langue = ? WHERE user_id = ?", (langue, user_id))
    conn.commit()
    conn.close()


def get_langue(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT langue FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] else "fr"