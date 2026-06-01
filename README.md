# Spotify Tracker

Spotify Tracker is a private listening analytics web app built with Python, Flask, SQLite, Spotipy, and Chart.js. It connects to a user's Spotify account, syncs recently played tracks, and turns listening history into a clean dashboard with album covers, artist portraits, charts, and a detailed playback history.

Designed and developed by Iliass Khalki.

## Project Preview

Spotify Tracker is built as a portfolio-ready full stack project. The app focuses on a polished user experience rather than a plain data table:

- Modern landing page with Spotify OAuth login
- Personal dashboard after login
- Album artwork for tracks
- Artist portrait cards for top artists
- Recent listening history with readable timestamps
- Charts for top tracks, top artists, daily plays, and listening hours
- Auto-sync polling so the dashboard can refresh while the user is logged in
- Server-side token handling and CSRF protection for sync requests

## Tech Stack

- Python
- Flask
- SQLite
- Spotipy
- Spotify Web API
- Jinja templates
- Chart.js
- HTML and CSS

## How It Works

1. The user opens the landing page.
2. The user logs in with Spotify OAuth.
3. Spotify redirects back to `/callback`.
4. The app stores the Spotify token server-side for the current app process.
5. The dashboard loads saved listening data from SQLite.
6. The dashboard calls `/api/sync` in the background.
7. The sync endpoint fetches recently played tracks from Spotify, stores album art and artist images, then updates the dashboard.

The app does not need a global Spotify API key for everyone. Each user authorizes their own Spotify account through OAuth, and the app uses that user's token to read their listening history.

## Features

- Spotify OAuth login
- Per-user listening history
- Recently played track sync
- Album cover storage
- Primary artist image backfill
- Dashboard auto-sync polling
- Human-readable timestamps
- Top track and top artist analytics
- Daily and hourly listening charts
- Secure session cookie settings
- CSRF-protected sync endpoint
- Local SQLite database for development

## Project Structure

```text
SpotifyTracker/
|-- app/
|   |-- auth/
|   |   `-- spotify_auth.py       # Spotify OAuth setup
|   |-- database/
|   |   |-- db.py                 # SQLite schema and write helpers
|   |   `-- queries.py            # Dashboard/history read queries
|   |-- spotify/
|   |   |-- auth.py               # Legacy Spotify auth helpers
|   |   `-- client.py             # Legacy Spotify client helpers
|   `-- web/
|       |-- app.py                # Flask routes, sync API, security headers
|       `-- templates/
|           |-- landing.html      # Public landing page
|           |-- index.html        # Logged-in dashboard
|           `-- history.html      # Listening history page
|-- data/                         # Local SQLite database, ignored by Git
|-- .env.example                  # Safe environment template
|-- .gitignore                    # Keeps secrets/runtime files out of Git
|-- requirements.txt              # Python dependencies
|-- wsgi.py                       # WSGI entry point
|-- LICENSE
`-- README.md
```

## Local Setup

Clone the repository:

```bash
git clone https://github.com/IliassKhalki/SpotifyTracker.git
cd SpotifyTracker
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Fill in `.env`:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5050/callback
FLASK_SECRET_KEY=change_this_to_a_long_random_secret
PORT=5050
```

## Spotify Developer Setup

1. Go to the Spotify Developer Dashboard.
2. Create an app.
3. Copy the Client ID into `SPOTIPY_CLIENT_ID`.
4. Copy the Client Secret into `SPOTIPY_CLIENT_SECRET`.
5. Add this redirect URI:

```text
http://127.0.0.1:5050/callback
```

Use one redirect URL while developing. This project is configured around port `5050`.

## Run The App

Start the Flask app:

```bash
python -m app.web.app
```

Open:

```text
http://127.0.0.1:5050/
```

After logging in with Spotify, the app redirects back to:

```text
http://127.0.0.1:5050/callback
```

Then it sends you to the dashboard.

## Useful Commands

Compile-check the Python code:

```bash
python -m compileall app\auth app\database app\web
```

Run the app:

```bash
python -m app.web.app
```

Check Git status before pushing:

```bash
git status
```

Push to GitHub:

```bash
git push
```

## Security And Privacy

This project is designed to avoid pushing private data to GitHub.

Ignored locally:

- `.env`
- `.cache`
- `.vscode/`
- `data/`
- `*.db`
- Flask logs
- Python cache files
- Virtual environments

Security choices in the app:

- Spotify tokens are stored server-side in memory for the current process.
- Tokens are not written to `.cache`.
- Browser sessions store only a random token key, not the Spotify access token.
- Session cookies use `HttpOnly` and `SameSite=Lax`.
- `/api/sync` requires a CSRF token.
- Basic security headers are added to every response.
- Spotify API calls use request timeouts.

For production, move token storage from in-memory Python state to a durable server-side store such as Redis or a database-backed session table.

## Database

The app creates a local SQLite database automatically:

```text
data/spotify_tracker.db
```

That file is ignored by Git because it contains personal listening history.

Main stored data:

- Spotify user ID
- Display name
- Track ID
- Song name
- Artist name
- Primary artist ID
- Album name
- Album image URL
- Artist image URL
- Played-at timestamp

## License

This project is licensed under the MIT License.

## Author

Made, designed and developed by Iliass Khalki.
