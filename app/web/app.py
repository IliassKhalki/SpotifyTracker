import os
import secrets
from datetime import datetime, timezone

import spotipy
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for

from app.auth.spotify_auth import get_spotify_oauth
from app.database.db import (
    create_tables,
    get_missing_artist_image_ids,
    insert_track,
    update_artist_image_url,
    upsert_user,
)
from app.database.queries import (
    get_daily_plays,
    get_hourly_pattern,
    get_recent_history,
    get_summary_stats,
    get_top_artists,
    get_top_tracks,
)


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_urlsafe(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "").lower() in {"1", "true", "yes"},
)
create_tables()

TOKEN_STORE = {}
SPOTIFY_TIMEOUT = 6


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';",
    )
    return response


def _token_key():
    key = session.get("token_key")

    if not key:
        key = secrets.token_urlsafe(32)
        session["token_key"] = key

    return key


def _csrf_token():
    token = session.get("csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token

    return token


def _check_csrf():
    expected = session.get("csrf_token")
    supplied = request.headers.get("X-CSRF-Token")

    if not expected or not supplied or not secrets.compare_digest(supplied, expected):
        abort(403)


def _spotify_client():
    token_info = TOKEN_STORE.get(session.get("token_key"))

    if not token_info:
        return None

    sp_oauth = get_spotify_oauth()
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        TOKEN_STORE[_token_key()] = token_info

    return spotipy.Spotify(
        auth=token_info["access_token"],
        requests_timeout=SPOTIFY_TIMEOUT,
        retries=1,
        status_retries=1,
    )


def _image_url(profile):
    images = profile.get("images") or []
    return images[0]["url"] if images else None


def _first_image(payload):
    images = payload.get("images") or []
    return images[0]["url"] if images else None


@app.template_filter("listened_at")
def listened_at(value):
    if not value:
        return ""

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value.split(".")[0].replace("T", " ")

    return parsed.strftime("%b %d, %Y at %H:%M")


def _artist_images_for(spotify, artist_ids):
    artist_ids = list(dict.fromkeys(artist_id for artist_id in artist_ids if artist_id))[:50]

    if not artist_ids:
        return {}

    images = {}

    try:
        response = spotify.artists(artist_ids)
    except spotipy.SpotifyException:
        response = {"artists": []}

    for artist in response.get("artists", []):
        if artist:
            images[artist["id"]] = _first_image(artist)

    for artist_id in artist_ids:
        if images.get(artist_id):
            continue

        try:
            images[artist_id] = _first_image(spotify.artist(artist_id))
        except spotipy.SpotifyException:
            images[artist_id] = None

    return images


def _current_user():
    user = session.get("user")
    if user:
        user.pop("email", None)
        return user

    spotify = _spotify_client()
    if not spotify:
        return None

    try:
        profile = spotify.current_user()
    except spotipy.SpotifyException:
        return None

    user = {
        "id": profile["id"],
        "display_name": profile.get("display_name") or profile["id"],
        "image_url": _image_url(profile),
    }
    session["user"] = user
    upsert_user(
        user_id=user["id"],
        display_name=user["display_name"],
        email=None,
        image_url=user["image_url"],
    )
    return user


def _sync_recent_tracks(limit=50):
    user = _current_user()
    spotify = _spotify_client()

    if not user or not spotify:
        return 0

    try:
        results = spotify.current_user_recently_played(limit=limit)
    except spotipy.SpotifyException:
        return 0

    items = results.get("items", [])
    synced = 0
    backfill_artist_ids = get_missing_artist_image_ids(limit=25, user_id=user["id"])
    artist_images = _artist_images_for(
        spotify,
        backfill_artist_ids + [
            (item.get("track", {}).get("artists") or [{}])[0].get("id")
            for item in items
        ],
    )
    for artist_id in backfill_artist_ids:
        synced += update_artist_image_url(artist_id, artist_images.get(artist_id), user_id=user["id"])

    for item in items:
        track = item["track"]
        track_artists = track.get("artists", [])
        primary_artist = track_artists[0] if track_artists else {}
        primary_artist_id = primary_artist.get("id")
        primary_artist_name = primary_artist.get("name")
        artists = ", ".join(artist["name"] for artist in track_artists)
        album = track.get("album") or {}

        inserted = insert_track(
            track_id=track["id"],
            song_name=track["name"],
            artist_name=artists,
            played_at=item["played_at"],
            user_id=user["id"],
            primary_artist_name=primary_artist_name,
            artist_id=primary_artist_id,
            album_name=album.get("name"),
            album_image_url=_first_image(album),
            artist_image_url=artist_images.get(primary_artist_id),
        )
        if inserted:
            synced += 1

    session["last_sync_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return synced


def _require_login():
    if session.get("token_key") not in TOKEN_STORE:
        return redirect(url_for("login"))
    return None


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "spotify_client_id_configured": bool(os.getenv("SPOTIPY_CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID")),
        "spotify_client_secret_configured": bool(os.getenv("SPOTIPY_CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET")),
        "spotify_redirect_uri": os.getenv("SPOTIPY_REDIRECT_URI") or os.getenv("SPOTIFY_REDIRECT_URI"),
        "vercel": bool(os.getenv("VERCEL")),
    })


@app.route("/")
def home():
    if session.get("token_key") not in TOKEN_STORE:
        return render_template("landing.html")

    user = _current_user()
    if not user:
        return redirect(url_for("logout"))

    total, songs, artists = get_summary_stats(user["id"])
    top_tracks = get_top_tracks(8, user["id"])
    top_artists = get_top_artists(8, user["id"])
    daily = get_daily_plays(user["id"]) or []
    hourly = get_hourly_pattern(user["id"]) or []
    recent = get_recent_history(8, user["id"])

    track_labels = [f"{row[0]} - {row[1]}" for row in top_tracks]
    track_values = [row[2] for row in top_tracks]

    return render_template(
        "index.html",
        logged_in=True,
        user=user,
        total=total,
        songs=songs,
        artists=artists,
        top_tracks=top_tracks,
        top_artists=top_artists,
        recent=recent,
        hero_track=recent[0] if recent else None,
        track_labels=track_labels,
        track_values=track_values,
        daily_labels=[row[0] for row in daily],
        daily_values=[row[1] for row in daily],
        hourly_labels=[f"{row[0]}:00" for row in hourly],
        hourly_values=[row[1] for row in hourly],
        last_sync_at=session.get("last_sync_at"),
        csrf_token=_csrf_token(),
    )


@app.route("/login")
def login():
    sp_oauth = get_spotify_oauth()
    return redirect(sp_oauth.get_authorize_url())


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return redirect(url_for("home"))

    sp_oauth = get_spotify_oauth()
    session.clear()
    try:
        TOKEN_STORE[_token_key()] = sp_oauth.get_access_token(code, as_dict=True)
    except Exception:
        session.clear()
        return redirect(url_for("home"))

    return redirect(url_for("home"))


@app.post("/api/sync")
def sync_now():
    _check_csrf()

    login_redirect = _require_login()
    if login_redirect:
        return jsonify({"ok": False, "error": "not_authenticated"}), 401

    user = _current_user()
    if not user:
        return jsonify({"ok": False, "error": "spotify_profile_unavailable"}), 401

    synced = _sync_recent_tracks()
    total, songs, artists = get_summary_stats(user["id"])
    recent = get_recent_history(8, user["id"])
    top_tracks = get_top_tracks(8, user["id"])
    top_artists = get_top_artists(8, user["id"])
    daily = get_daily_plays(user["id"]) or []
    hourly = get_hourly_pattern(user["id"]) or []

    return jsonify({
        "ok": True,
        "synced": synced,
        "last_sync_at": session.get("last_sync_at"),
        "stats": {
            "total": total,
            "songs": songs,
            "artists": artists,
        },
        "recent": [
            {
                "song": row[0],
                "artist": row[1],
                "played_at": row[2],
                "album_image_url": row[3],
                "artist_image_url": row[4],
                "album_name": row[5],
            }
            for row in recent
        ],
        "top_tracks": [
            {
                "song": row[0],
                "artist": row[1],
                "plays": row[2],
                "album_image_url": row[3],
                "album_name": row[4],
            }
            for row in top_tracks
        ],
        "top_artists": [
            {
                "artist": row[0],
                "plays": row[1],
                "artist_image_url": row[2],
            }
            for row in top_artists
        ],
        "daily": [{"label": row[0], "value": row[1]} for row in daily],
        "hourly": [{"label": f"{row[0]}:00", "value": row[1]} for row in hourly],
    })


@app.route("/logout")
def logout():
    TOKEN_STORE.pop(session.get("token_key"), None)
    session.clear()
    return redirect(url_for("home"))


@app.route("/history")
def history():
    login_redirect = _require_login()
    if login_redirect:
        return login_redirect

    user = _current_user()
    if not user:
        return redirect(url_for("logout"))

    data = get_recent_history(75, user["id"])

    return render_template(
        "history.html",
        data=data,
        logged_in=True,
        user=user,
        last_sync_at=session.get("last_sync_at"),
    )


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG") == "1",
        port=int(os.getenv("PORT", "5050")),
        use_reloader=False,
    )
