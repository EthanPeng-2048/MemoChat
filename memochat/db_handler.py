import logging
import sqlite3
from typing import Optional

from .config import DB_PATH, ALLOWED_CATEGORIES

logger = logging.getLogger(__name__)


def init_db() -> None:
    conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, key)
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized with WAL mode")


def query(category: str, key: str) -> Optional[str]:
    if category not in ALLOWED_CATEGORIES:
        logger.warning(f"Invalid category: {category}")
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT value FROM memory WHERE category = ? AND key = ?",
        (category, key)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        logger.debug(f"Memory hit: category={category}, key={key}")
        return result[0]
    else:
        logger.debug(f"Memory miss: category={category}, key={key}")
        return None


def upsert(category: str, key: str, value: str) -> bool:
    if category not in ALLOWED_CATEGORIES:
        logger.warning(f"Invalid category: {category}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO memory (category, key, value)
        VALUES (?, ?, ?)
        ON CONFLICT(category, key) DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
        """,
        (category, key, value)
    )
    conn.commit()
    conn.close()
    
    logger.info(f"Memory upserted: category={category}, key={key}")
    return True


def delete(category: str, key: str) -> bool:
    if category not in ALLOWED_CATEGORIES:
        logger.warning(f"Invalid category: {category}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM memory WHERE category = ? AND key = ?",
        (category, key)
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if rows_affected > 0:
        logger.info(f"Memory deleted: category={category}, key={key}")
        return True
    else:
        logger.warning(f"Memory not found for deletion: category={category}, key={key}")
        return False


def get_all_memory() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT category, key, value FROM memory ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_memory_by_category(category: str) -> list[dict]:
    if category not in ALLOWED_CATEGORIES:
        logger.warning(f"Invalid category: {category}")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, key, value FROM memory WHERE category = ? ORDER BY updated_at DESC",
        (category,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
