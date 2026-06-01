import os
from pathlib import Path

from dotenv import load_dotenv
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=BASE_DIR / ".env")


def get_spotify_oauth():
    client_id = os.getenv("SPOTIPY_CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI") or os.getenv("SPOTIFY_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        raise RuntimeError(
            "Spotify credentials are missing. Add SPOTIPY_CLIENT_ID, "
            "SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI to .env."
        )

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=(
            "user-read-recently-played "
            "user-top-read "
            "user-read-private"
        ),
        cache_handler=MemoryCacheHandler(),
        requests_timeout=8,
        show_dialog=False,
    )
