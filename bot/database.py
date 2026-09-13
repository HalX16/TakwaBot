import sqlite3
import os

# Sur Railway, le volume persistant est monté sur /data
# En local (Windows), on utilise le dossier data/ du projet
if os.path.exists("/data"):
    DB_PATH = "/data/users.db"
else:
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
            langue TEXT DEFAULT 'fr',
            pub_matin INTEGER DEFAULT 1,
            pub_midi INTEGER DEFAULT 1,
            pub_soir INTEGER DEFAULT 1,
            pub_nuit INTEGER DEFAULT 1
        )
    """)
    # Migration : ajoute les colonnes si elles n'existent pas
    for col, typ, default in [
        ("ville", "TEXT", None),
        ("latitude", "REAL", None),
        ("longitude", "REAL", None),
        ("langue", "TEXT", "'fr'"),
        ("pub_matin", "INTEGER", "1"),
        ("pub_midi", "INTEGER", "1"),
        ("pub_soir", "INTEGER", "1"),
        ("pub_nuit", "INTEGER", "1"),
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


# ============================================================
#   Notifications multiples
# ============================================================

def set_pub(user_id: int, creneau: str, actif: int):
    """creneau : 'matin', 'midi', 'soir', 'nuit'"""
    if creneau not in ("matin", "midi", "soir", "nuit"):
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"UPDATE users SET pub_{creneau} = ? WHERE user_id = ?", (actif, user_id))
    conn.commit()
    conn.close()


def get_pub(user_id: int):
    """Retourne (matin, midi, soir, nuit) → tuple de 4 entiers (0 ou 1)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT pub_matin, pub_midi, pub_soir, pub_nuit FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = c.fetchone()
    conn.close()
    return row if row else (1, 1, 1, 1)


def get_users_with_pub(creneau: str):
    """Retourne la liste des user_id ayant ce créneau activé."""
    if creneau not in ("matin", "midi", "soir", "nuit"):
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT user_id FROM users WHERE pub_{creneau} = 1")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]