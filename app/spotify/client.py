from app.spotify.auth import create_spotify_client

def get_recent_tracks(limit=10):
    """
    Fetch recently played tracks from Spotify.
    """

    spotify = create_spotify_client()

    results = spotify.current_user_recently_played(limit=limit)

    return results