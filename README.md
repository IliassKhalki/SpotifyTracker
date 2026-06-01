# Spotify Tracker

A private Spotify listening analytics app built with Python, Flask, SQLite, Spotipy, and Chart.js.

Spotify Tracker lets a logged-in Spotify user sync recently played tracks, view album artwork, see artist cards, and browse listening patterns over time.

## Features

- Spotify login with OAuth
- Recently played track sync
- Auto-sync polling from the dashboard
- Per-user listening history
- Album artwork and primary artist images
- Top tracks, top artists, daily plays, and hourly listening charts
- SQLite storage for local development

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5050/callback
FLASK_SECRET_KEY=replace_with_a_long_random_secret
```

In the Spotify Developer Dashboard, add the same redirect URI:

```text
http://127.0.0.1:5050/callback
```

Run the web app:

```bash
python -m app.web.app
```

Open:

```text
http://127.0.0.1:5050
```

## Security Notes

- Do not commit `.env`, `.cache`, database files, or log files.
- Set `FLASK_SECRET_KEY` in production. If it is missing, the app generates a temporary key at startup.
- Spotify tokens are stored server-side for the current app process, not inside the browser session cookie.
- Session cookies are HTTP-only and SameSite=Lax.
- The dashboard auto-sync endpoint uses a CSRF token.
- For a production multi-worker deployment, move the token store from memory to Redis, a database, or another server-side session store.
