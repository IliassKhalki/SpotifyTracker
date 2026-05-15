from flask import Flask, render_template

from app.database.queries import (
    get_summary_stats,
    get_top_tracks,
    get_top_artists,
    get_daily_plays,
    get_hourly_pattern,
    get_recent_history
)

app = Flask(__name__)


@app.route("/")
def home():

    total, songs, artists = get_summary_stats()

    top_tracks = get_top_tracks(5)
    top_artists = get_top_artists(5)

    daily = get_daily_plays() or []
    hourly = get_hourly_pattern() or []

    # -----------------------------
    # FIX LONG CHART LABELS
    # -----------------------------
    track_labels = []

    for t in top_tracks:

        label = f"{t[0]} - {t[1]}"

        # truncate long labels
        if len(label) > 30:
            label = label[:30] + "..."

        track_labels.append(label)

    track_values = [t[2] for t in top_tracks]

    # -----------------------------
    # DAILY CHART DATA
    # -----------------------------
    daily_labels = [d[0] for d in daily]
    daily_values = [d[1] for d in daily]

    # -----------------------------
    # HOURLY CHART DATA
    # -----------------------------
    hourly_labels = [h[0] for h in hourly]
    hourly_values = [h[1] for h in hourly]

    return render_template(
        "index.html",

        total=total,
        songs=songs,
        artists=artists,

        top_tracks=top_tracks,
        top_artists=top_artists,

        track_labels=track_labels,
        track_values=track_values,

        daily_labels=daily_labels,
        daily_values=daily_values,

        hourly_labels=hourly_labels,
        hourly_values=hourly_values
    )


@app.route("/history")
def history():

    data = get_recent_history(50)

    return render_template(
        "history.html",
        data=data
    )


if __name__ == "__main__":
    app.run(debug=True)