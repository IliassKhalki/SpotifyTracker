import sqlite3

DATABASE_PATH = "data/spotify_tracker.db"

def create_connection():
    """
    Create a connection to the SQLite database.
    """

    connection = sqlite3.connect(DATABASE_PATH, timeout=10)

    return connection


def create_tables():
    """
    Create database tables if they do not exist.
    """

    connection = create_connection()

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recent_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spotify_track_id TEXT,
    song_name TEXT,
    artist_name TEXT,
    played_at TEXT UNIQUE
)
""")

    connection.commit()

    connection.close()



def insert_track(spotify_track_id, song_name, artist_name, played_at):
    """
    Insert a track into the database.
    """

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        INSERT OR IGNORE INTO recent_tracks (
            spotify_track_id,
            song_name,
            artist_name,
            played_at
        )
        VALUES (?, ?, ?, ?)
        """, (
            spotify_track_id,
            song_name,
            artist_name,
            played_at
        ))

        connection.commit()

    finally:
        connection.close()