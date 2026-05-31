from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from pathlib import Path

# FORCE LOAD .env FROM PROJECT ROOT
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=BASE_DIR / ".env")


def get_spotify_oauth():

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    # DEBUG CHECK (VERY IMPORTANT)
    if not client_id or not client_secret:
        raise Exception("❌ .env not loaded correctly")

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=(
            "user-read-recently-played "
            "user-top-read "
            "user-read-email"
        )
    )