from app.database.db import create_connection


def get_top_tracks(limit=10, user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    params = (limit,)
    where = ""

    if user_id:
        where = "WHERE user_id = ?"
        params = (user_id, limit)

    cursor.execute(f"""
    SELECT
        song_name,
        artist_name,
        COUNT(*) AS play_count,
        MAX(album_image_url) AS album_image_url,
        MAX(album_name) AS album_name
    FROM recent_tracks
    {where}
    GROUP BY track_id, song_name, artist_name
    ORDER BY play_count DESC
    LIMIT ?
    """, params)

    results = cursor.fetchall()
    connection.close()
    return results


def get_top_artists(limit=10, user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    params = (limit,)
    where = ""

    if user_id:
        where = "WHERE user_id = ?"
        params = (user_id, limit)

    cursor.execute(f"""
    SELECT
        COALESCE(primary_artist_name, artist_name) AS artist,
        COUNT(*) AS play_count,
        MAX(artist_image_url) AS artist_image_url
    FROM recent_tracks
    {where}
    GROUP BY COALESCE(artist_id, primary_artist_name, artist_name), artist
    ORDER BY play_count DESC
    LIMIT ?
    """, params)

    results = cursor.fetchall()
    connection.close()
    return results


def get_summary_stats(user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("SELECT COUNT(*) FROM recent_tracks WHERE user_id = ?", (user_id,))
        total_plays = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT track_id) FROM recent_tracks WHERE user_id = ?", (user_id,))
        unique_songs = cursor.fetchone()[0]

        cursor.execute("""
        SELECT COUNT(DISTINCT COALESCE(artist_id, primary_artist_name, artist_name))
        FROM recent_tracks
        WHERE user_id = ?
        """, (user_id,))
        unique_artists = cursor.fetchone()[0]
    else:
        cursor.execute("SELECT COUNT(*) FROM recent_tracks")
        total_plays = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT track_id) FROM recent_tracks")
        unique_songs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT COALESCE(artist_id, primary_artist_name, artist_name)) FROM recent_tracks")
        unique_artists = cursor.fetchone()[0]

    connection.close()
    return total_plays, unique_songs, unique_artists


def get_daily_plays(user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("""
        SELECT play_date, play_count
        FROM (
            SELECT date(played_at) AS play_date, COUNT(*) AS play_count
            FROM recent_tracks
            WHERE user_id = ?
            GROUP BY date(played_at)
            ORDER BY date(played_at) DESC
            LIMIT 14
        )
        ORDER BY play_date ASC
        """, (user_id,))
    else:
        cursor.execute("""
        SELECT play_date, play_count
        FROM (
            SELECT date(played_at) AS play_date, COUNT(*) AS play_count
            FROM recent_tracks
            GROUP BY date(played_at)
            ORDER BY date(played_at) DESC
            LIMIT 14
        )
        ORDER BY play_date ASC
        """)

    result = cursor.fetchall()
    connection.close()
    return result


def get_hourly_pattern(user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("""
        SELECT strftime('%H', played_at), COUNT(*)
        FROM recent_tracks
        WHERE user_id = ?
        GROUP BY strftime('%H', played_at)
        ORDER BY strftime('%H', played_at)
        """, (user_id,))
    else:
        cursor.execute("""
        SELECT strftime('%H', played_at), COUNT(*)
        FROM recent_tracks
        GROUP BY strftime('%H', played_at)
        ORDER BY strftime('%H', played_at)
        """)

    result = cursor.fetchall()
    connection.close()
    return result


def get_best_day(user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("""
        SELECT date(played_at), COUNT(*) AS c
        FROM recent_tracks
        WHERE user_id = ?
        GROUP BY date(played_at)
        ORDER BY c DESC
        LIMIT 1
        """, (user_id,))
    else:
        cursor.execute("""
        SELECT date(played_at), COUNT(*) AS c
        FROM recent_tracks
        GROUP BY date(played_at)
        ORDER BY c DESC
        LIMIT 1
        """)

    result = cursor.fetchone()
    connection.close()
    return result


def get_recent_history(limit=20, user_id=None):
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

    data = cursor.fetchall()
    connection.close()
    return data
