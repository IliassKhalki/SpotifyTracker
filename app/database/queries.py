from app.database.db import create_connection

def get_top_tracks(limit=10):
    """
    Returns most listened tracks based on stored play events.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT song_name, artist_name, COUNT(*) as play_count
    FROM recent_tracks
    GROUP BY song_name, artist_name
    ORDER BY play_count DESC
    LIMIT ?
    """, (limit,))

    results = cursor.fetchall()

    connection.close()

    return results

def get_top_artists(limit=10):
    """
    Returns most listened artists based on stored play events.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT artist_name, COUNT(*) as play_count
    FROM recent_tracks
    GROUP BY artist_name
    ORDER BY play_count DESC
    LIMIT ?
    """, (limit,))

    results = cursor.fetchall()

    connection.close()

    return results

def get_summary_stats():
    """
    Returns overall listening statistics.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM recent_tracks")
    total_plays = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT song_name) FROM recent_tracks")
    unique_songs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT artist_name) FROM recent_tracks")
    unique_artists = cursor.fetchone()[0]

    connection.close()

    return total_plays, unique_songs, unique_artists

def get_daily_plays():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT date(played_at), COUNT(*)
    FROM recent_tracks
    GROUP BY date(played_at)
    ORDER BY date(played_at) DESC
    LIMIT 7
    """)

    result = cursor.fetchall()
    connection.close()
    return result


def get_hourly_pattern():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT strftime('%H', played_at), COUNT(*)
    FROM recent_tracks
    GROUP BY strftime('%H', played_at)
    ORDER BY strftime('%H', played_at)
    """)

    result = cursor.fetchall()
    connection.close()
    return result

def get_best_day():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT date(played_at), COUNT(*) as c
    FROM recent_tracks
    GROUP BY date(played_at)
    ORDER BY c DESC
    LIMIT 1
    """)

    result = cursor.fetchone()
    connection.close()
    return result

def get_recent_history(limit=20):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT song_name, artist_name, played_at
    FROM recent_tracks
    ORDER BY played_at DESC
    LIMIT ?
    """, (limit,))

    data = cursor.fetchall()
    connection.close()

    return data