import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = (
    Path("/tmp") / "spotify_tracker.db"
    if os.getenv("VERCEL")
    else BASE_DIR / "data" / "spotify_tracker.db"
)


def create_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH, timeout=10)


def create_tables():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spotify_users (
        id TEXT PRIMARY KEY,
        display_name TEXT,
        email TEXT,
        image_url TEXT,
        last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recent_tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        track_id TEXT NOT NULL,
        song_name TEXT NOT NULL,
        artist_name TEXT NOT NULL,
        primary_artist_name TEXT,
        artist_id TEXT,
        album_name TEXT,
        album_image_url TEXT,
        artist_image_url TEXT,
        played_at TEXT NOT NULL,
        UNIQUE(user_id, track_id, played_at)
    )
    """)

    for column, definition in {
        "user_id": "TEXT",
        "primary_artist_name": "TEXT",
        "artist_id": "TEXT",
        "album_name": "TEXT",
        "album_image_url": "TEXT",
        "artist_image_url": "TEXT",
    }.items():
        _ensure_column(cursor, "recent_tracks", column, definition)

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_recent_tracks_user_event
    ON recent_tracks(user_id, track_id, played_at)
    """)

    connection.commit()
    connection.close()


def _ensure_column(cursor, table, column, definition):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}

    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def upsert_user(user_id, display_name=None, email=None, image_url=None):
    connection = create_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO spotify_users (id, display_name, email, image_url, last_seen_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            display_name = excluded.display_name,
            email = excluded.email,
            image_url = excluded.image_url,
            last_seen_at = CURRENT_TIMESTAMP
        """, (user_id, display_name, email, image_url))
        connection.commit()
    finally:
        connection.close()


def update_artist_image_url(artist_id, artist_image_url, user_id=None):
    if not artist_id or not artist_image_url:
        return 0

    connection = create_connection()

    try:
        cursor = connection.cursor()

        if user_id:
            cursor.execute("""
            UPDATE recent_tracks
            SET artist_image_url = ?
            WHERE artist_id = ?
              AND user_id = ?
              AND (artist_image_url IS NULL OR artist_image_url = '')
            """, (artist_image_url, artist_id, user_id))
        else:
            cursor.execute("""
            UPDATE recent_tracks
            SET artist_image_url = ?
            WHERE artist_id = ?
              AND (artist_image_url IS NULL OR artist_image_url = '')
            """, (artist_image_url, artist_id))

        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()


def get_missing_artist_image_ids(limit=50, user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("""
        SELECT DISTINCT artist_id
        FROM recent_tracks
        WHERE user_id = ?
          AND artist_id IS NOT NULL
          AND artist_id != ''
          AND (artist_image_url IS NULL OR artist_image_url = '')
        LIMIT ?
        """, (user_id, limit))
    else:
        cursor.execute("""
        SELECT DISTINCT artist_id
        FROM recent_tracks
        WHERE artist_id IS NOT NULL
          AND artist_id != ''
          AND (artist_image_url IS NULL OR artist_image_url = '')
        LIMIT ?
        """, (limit,))

    rows = [row[0] for row in cursor.fetchall()]
    connection.close()
    return rows


def insert_track(
    track_id,
    song_name,
    artist_name,
    played_at,
    user_id=None,
    primary_artist_name=None,
    artist_id=None,
    album_name=None,
    album_image_url=None,
    artist_image_url=None,
):
    connection = create_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO recent_tracks (
            user_id,
            track_id,
            song_name,
            artist_name,
            primary_artist_name,
            artist_id,
            album_name,
            album_image_url,
            artist_image_url,
            played_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            track_id,
            song_name,
            artist_name,
            primary_artist_name,
            artist_id,
            album_name,
            album_image_url,
            artist_image_url,
            played_at,
        ))
        inserted = cursor.rowcount > 0

        cursor.execute("""
        UPDATE recent_tracks
        SET
            song_name = ?,
            artist_name = ?,
            primary_artist_name = COALESCE(?, primary_artist_name),
            artist_id = COALESCE(?, artist_id),
            album_name = COALESCE(?, album_name),
            album_image_url = COALESCE(?, album_image_url),
            artist_image_url = COALESCE(?, artist_image_url)
        WHERE (user_id = ? OR (user_id IS NULL AND ? IS NULL))
          AND track_id = ?
          AND played_at = ?
        """, (
            song_name,
            artist_name,
            primary_artist_name,
            artist_id,
            album_name,
            album_image_url,
            artist_image_url,
            user_id,
            user_id,
            track_id,
            played_at,
        ))

        connection.commit()
        return inserted
    finally:
        connection.close()


def get_recent_history(limit=50, user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("""
            SELECT song_name, artist_name, played_at, album_image_url, artist_image_url, album_name
            FROM recent_tracks
            WHERE user_id = ?
            ORDER BY played_at DESC
            LIMIT ?
        """, (user_id, limit))
    else:
        cursor.execute("""
            SELECT song_name, artist_name, played_at, album_image_url, artist_image_url, album_name
            FROM recent_tracks
            ORDER BY played_at DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    connection.close()
    return rows


def get_top_tracks(limit=10, user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("""
            SELECT song_name, artist_name, COUNT(*) AS play_count, MAX(album_image_url), MAX(album_name)
            FROM recent_tracks
            WHERE user_id = ?
            GROUP BY track_id, song_name, artist_name
            ORDER BY play_count DESC
            LIMIT ?
        """, (user_id, limit))
    else:
        cursor.execute("""
            SELECT song_name, artist_name, COUNT(*) AS play_count, MAX(album_image_url), MAX(album_name)
            FROM recent_tracks
            GROUP BY track_id, song_name, artist_name
            ORDER BY play_count DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    connection.close()
    return rows


def get_top_artists(limit=10, user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("""
            SELECT COALESCE(primary_artist_name, artist_name) AS artist, COUNT(*) AS play_count, MAX(artist_image_url)
            FROM recent_tracks
            WHERE user_id = ?
            GROUP BY COALESCE(artist_id, primary_artist_name, artist_name), artist
            ORDER BY play_count DESC
            LIMIT ?
        """, (user_id, limit))
    else:
        cursor.execute("""
            SELECT COALESCE(primary_artist_name, artist_name) AS artist, COUNT(*) AS play_count, MAX(artist_image_url)
            FROM recent_tracks
            GROUP BY COALESCE(artist_id, primary_artist_name, artist_name), artist
            ORDER BY play_count DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    connection.close()
    return rows


def get_summary_stats(user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("SELECT COUNT(*) FROM recent_tracks WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT track_id) FROM recent_tracks WHERE user_id = ?", (user_id,))
        songs = cursor.fetchone()[0]
        cursor.execute("""
            SELECT COUNT(DISTINCT COALESCE(artist_id, primary_artist_name, artist_name))
            FROM recent_tracks
            WHERE user_id = ?
        """, (user_id,))
        artists = cursor.fetchone()[0]
    else:
        cursor.execute("SELECT COUNT(*) FROM recent_tracks")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT track_id) FROM recent_tracks")
        songs = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT COALESCE(artist_id, primary_artist_name, artist_name)) FROM recent_tracks")
        artists = cursor.fetchone()[0]

    connection.close()
    return total, songs, artists
