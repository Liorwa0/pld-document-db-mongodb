#!/usr/bin/env python3
"""Convert Spotify tracks CSV rows into MongoDB-ready nested documents."""
import csv
import json
from pathlib import Path
from typing import Iterable

INPUT_FILE = Path("data/dataset.csv")
OUTPUT_FILE = Path("data/tracks.json")

AUDIO_FEATURES = [
    "danceability", "energy", "key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
    "time_signature",
]


def build_document(row: dict[str, str]) -> dict:
    """Turn one flat CSV row into a nested document."""
    artists = row["artists"].split(";") if row.get("artists") else []
    return {
        "_id": row["track_id"],
        "name": row["track_name"],
        "album": row["album_name"],
        "artists": artists,
        "genres": [row["track_genre"]],
        "popularity": int(row["popularity"]),
        "duration_ms": int(row["duration_ms"]),
        "explicit": row["explicit"].strip().lower() == "true",
        "audio_features": {
            feature: float(row[feature]) for feature in AUDIO_FEATURES
        },
    }


def transform_rows(rows: Iterable[dict[str, str]]) -> list[dict]:
    """Merge repeated track rows while retaining each distinct genre."""
    tracks: dict[str, dict] = {}
    for row in rows:
        track_id = row["track_id"]
        if not track_id:
            continue
        if track_id in tracks:
            genre = row["track_genre"]
            if genre and genre not in tracks[track_id]["genres"]:
                tracks[track_id]["genres"].append(genre)
        else:
            tracks[track_id] = build_document(row)
    return list(tracks.values())


def main() -> None:
    """Read the CSV and write normalized JSON."""
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")
    with INPUT_FILE.open(encoding="utf-8", newline="") as file:
        documents = transform_rows(csv.DictReader(file))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = OUTPUT_FILE.with_suffix(".json.tmp")
    temporary_output.write_text(
        json.dumps(documents, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_output.replace(OUTPUT_FILE)
    print(f"Unique tracks written: {len(documents)}")


if __name__ == "__main__":
    main()
