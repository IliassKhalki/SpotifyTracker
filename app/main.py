import time
from app.database.db import create_tables, insert_track
from app.database.queries import (
    get_summary_stats,
    get_top_tracks,
    get_top_artists
)
from app.spotify.client import get_recent_tracks


def fetch_and_store():
    results = get_recent_tracks()

    for item in results["items"]:
        track = item["track"]

        insert_track(
            track["id"],
            track["name"],
            track["artists"][0]["name"],
            item["played_at"]
        )


def show_dashboard():

    total, songs, artists = get_summary_stats()

    print("\n=== SUMMARY ===")
    print(total, songs, artists)

    print("\n=== TOP TRACKS ===")
    for t in get_top_tracks(5):
        print(t)

    print("\n=== TOP ARTISTS ===")
    for a in get_top_artists(5):
        print(a)


def main():

    create_tables()

    while True:

        print("\nFetching Spotify data...")
        fetch_and_store()

        print("\nUpdating stats...")
        show_dashboard()

        print("\nWaiting 30 seconds...\n")
        time.sleep(30)


if __name__ == "__main__":
    main()