from spotipy.oauth2 import SpotifyOAuth
import spotipy

from app.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI
)

def create_spotify_client():
    """
    Creates and returns an authenticated Spotify client.
    """

    scope = "user-read-recently-played"

    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=scope
    )

    spotify_client = spotipy.Spotify(auth_manager=auth_manager)

    return spotify_client