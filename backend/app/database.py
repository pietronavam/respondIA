import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "respondIA.db")
CATALOG_PATH = os.getenv("CATALOG_PATH", "catalog.txt")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            customer  TEXT    NOT NULL,
            role      TEXT    NOT NULL,
            content   TEXT    NOT NULL,
            ts        DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS business (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_message(customer: str, user_msg: str, bot_msg: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (customer, role, content) VALUES (?, 'user', ?)",
        (customer, user_msg),
    )
    conn.execute(
        "INSERT INTO messages (customer, role, content) VALUES (?, 'assistant', ?)",
        (customer, bot_msg),
    )
    conn.commit()
    conn.close()


def get_history(customer: str, limit: int = 8) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE customer = ? ORDER BY ts DESC LIMIT ?",
        (customer, limit),
    ).fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def get_all_messages() -> list[tuple]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT customer, role, content, ts FROM messages ORDER BY ts DESC LIMIT 200"
    ).fetchall()
    conn.close()
    return rows


def get_catalog() -> str:
    if os.path.exists(CATALOG_PATH):
        return Path(CATALOG_PATH).read_text(encoding="utf-8")
    return ""


def save_catalog(text: str):
    Path(CATALOG_PATH).write_text(text, encoding="utf-8")


def get_business_setting(key: str, default: str = "") -> str:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT value FROM business WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row[0] if row else default


def save_business_setting(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO business (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()
    conn.close()
