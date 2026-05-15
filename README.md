# 🎧 Spotify Listening Tracker

A personal analytics dashboard that tracks your Spotify listening habits using the Spotify Web API. Think of it as a continuous, self-hosted Spotify Wrapped — updated in real time instead of once a year.

Built with **Python**, **Flask**, and **SQLite**.

---

## Features

- 🔐 Spotify OAuth authentication
- 🎵 Automatic fetching of recently played tracks
- 📊 Play count tracking per song and artist
- 📅 Daily listening activity analytics
- 🕒 Hourly listening pattern insights
- 📈 Interactive charts dashboard powered by Chart.js
- 📜 Full listening history page
- 💾 Local SQLite database — no external DB required

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Spotify Integration | Spotipy (Spotify Web API) |
| Database | SQLite |
| Frontend | HTML, CSS, Jinja2, Chart.js |

---

## Project Structure

```
SpotifyTracker/
├── app/
│   ├── web/          # Flask frontend (routes, templates)
│   ├── database/     # SQLite logic & queries
│   ├── spotify/      # Spotify API client
│   └── main.py       # Data collector (run this to track)
├── data/             # Local database — ignored in git
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/IliassKhalki/SpotifyTracker.git
cd SpotifyTracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Spotify API credentials

Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard), create an app, and set the redirect URI to `http://127.0.0.1:8888/callback`.

Then create a `.env` file in the project root:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### 4. Start the tracker

This runs in the background and periodically fetches your recently played tracks:

```bash
python -m app.main
```

### 5. Launch the dashboard

```bash
python -m app.web.app
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## Security Notes

- The `.env` file and `.cache` (Spotipy token) are both excluded from version control via `.gitignore` — never commit them.
- The `data/` folder (your SQLite database) is also gitignored since it contains personal listening history.

---

## Project Goal

This project was built to analyze personal Spotify listening habits and visualize music behavior over time — a lightweight, self-hosted alternative to Spotify Wrapped with continuous tracking.