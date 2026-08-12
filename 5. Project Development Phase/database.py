import sqlite3
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = os.getenv("DATABASE_PATH", "brand_content.db")


def get_connection(db_path: str = DB_NAME) -> sqlite3.Connection:
    """Connects to SQLite database and enables foreign key constraints."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_NAME) -> None:
    """Creates the SQLite database tables according to the 6-entity ER diagram schema."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. USER_ACCOUNT Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER_ACCOUNT (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. BRAND_PROFILE Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BRAND_PROFILE (
            profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            brand_name TEXT NOT NULL,
            industry TEXT,
            target_audience TEXT,
            tone_voice TEXT,
            brand_guidelines TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT (user_id) ON DELETE CASCADE
        );
    """)

    # 3. SAMPLE_TEXT Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SAMPLE_TEXT (
            sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content_body TEXT NOT NULL,
            sample_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES BRAND_PROFILE (profile_id) ON DELETE CASCADE
        );
    """)

    # 4. CONTENT_REQUEST Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CONTENT_REQUEST (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            content_type TEXT NOT NULL,
            target_length TEXT,
            additional_instructions TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES BRAND_PROFILE (profile_id) ON DELETE CASCADE
        );
    """)

    # 5. GENERATED_CONTENT Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS GENERATED_CONTENT (
            content_id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            generated_text TEXT NOT NULL,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES CONTENT_REQUEST (request_id) ON DELETE CASCADE
        );
    """)

    # 6. CONTENT_REFINEMENT Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CONTENT_REFINEMENT (
            refinement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            refinement_prompt TEXT NOT NULL,
            refined_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES GENERATED_CONTENT (content_id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    logger.info("Database schema initialized successfully with all 6 entities and foreign key constraints.")


def get_or_create_default_user(username: str = "default_user", email: str = "user@example.com", db_path: str = DB_NAME) -> int:
    """Ensures a default user account exists and returns its user_id."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM USER_ACCOUNT WHERE username = ?;", (username,))
    row = cursor.fetchone()
    if row:
        user_id = row['user_id']
    else:
        cursor.execute(
            "INSERT INTO USER_ACCOUNT (username, email, password_hash) VALUES (?, ?, ?);",
            (username, email, "pbkdf2_hashed_placeholder")
        )
        conn.commit()
        user_id = cursor.lastrowid
    conn.close()
    return user_id


def create_brand_profile(
    user_id: int,
    brand_name: str,
    industry: str,
    target_audience: str,
    tone_voice: str,
    sample_title: str,
    sample_text: str,
    brand_guidelines: str = "",
    db_path: str = DB_NAME
) -> int:
    """Inserts a new BRAND_PROFILE and associated SAMPLE_TEXT into SQLite."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO BRAND_PROFILE (user_id, brand_name, industry, target_audience, tone_voice, brand_guidelines)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (user_id, brand_name, industry, target_audience, tone_voice, brand_guidelines))
    profile_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO SAMPLE_TEXT (profile_id, title, content_body, sample_type)
        VALUES (?, ?, ?, ?);
    """, (profile_id, sample_title or "Reference Sample", sample_text, "Brand Reference"))

    conn.commit()
    conn.close()
    return profile_id


def get_all_brand_profiles(db_path: str = DB_NAME) -> list:
    """Fetches all brand profiles from the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT profile_id, user_id, brand_name, industry, target_audience, tone_voice, brand_guidelines, created_at
        FROM BRAND_PROFILE
        ORDER BY created_at DESC;
    """)
    profiles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return profiles


def get_brand_profile_by_id(profile_id: int, db_path: str = DB_NAME) -> Optional[dict]:
    """Fetches a specific brand profile by profile_id."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT profile_id, user_id, brand_name, industry, target_audience, tone_voice, brand_guidelines, created_at
        FROM BRAND_PROFILE
        WHERE profile_id = ?;
    """, (profile_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_content_generation(
    profile_id: int,
    topic: str,
    content_type: str,
    generated_text: str,
    additional_instructions: str = "",
    model_used: str = "gemini-2.0-flash",
    db_path: str = DB_NAME
) -> int:
    """Inserts a CONTENT_REQUEST and corresponding GENERATED_CONTENT record into SQLite."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO CONTENT_REQUEST (profile_id, topic, content_type, additional_instructions, status)
        VALUES (?, ?, ?, ?, 'completed');
    """, (profile_id, topic, content_type, additional_instructions))
    request_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO GENERATED_CONTENT (request_id, generated_text, model_used)
        VALUES (?, ?, ?);
    """, (request_id, generated_text, model_used))
    content_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return content_id


def get_content_history(profile_id: Optional[int] = None, db_path: str = DB_NAME) -> list:
    """Retrieves content generation history joined with request details."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    if profile_id:
        query = """
            SELECT gc.content_id, cr.request_id, bp.brand_name, cr.topic, cr.content_type,
                   cr.additional_instructions, gc.generated_text, gc.model_used, gc.created_at
            FROM GENERATED_CONTENT gc
            JOIN CONTENT_REQUEST cr ON gc.request_id = cr.request_id
            JOIN BRAND_PROFILE bp ON cr.profile_id = bp.profile_id
            WHERE cr.profile_id = ?
            ORDER BY gc.created_at DESC;
        """
        cursor.execute(query, (profile_id,))
    else:
        query = """
            SELECT gc.content_id, cr.request_id, bp.brand_name, cr.topic, cr.content_type,
                   cr.additional_instructions, gc.generated_text, gc.model_used, gc.created_at
            FROM GENERATED_CONTENT gc
            JOIN CONTENT_REQUEST cr ON gc.request_id = cr.request_id
            JOIN BRAND_PROFILE bp ON cr.profile_id = bp.profile_id
            ORDER BY gc.created_at DESC;
        """
        cursor.execute(query)

    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history


def delete_brand_profile(profile_id: int, db_path: str = DB_NAME) -> bool:
    """Deletes a brand profile and cascades deletion to samples, requests, and outputs."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BRAND_PROFILE WHERE profile_id = ?;", (profile_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def verify_tables(db_path: str = DB_NAME) -> list:
    """Returns a list of all existing table names in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return tables


if __name__ == "__main__":
    init_db()
    existing_tables = verify_tables()
    print("Database tables initialized:", existing_tables)