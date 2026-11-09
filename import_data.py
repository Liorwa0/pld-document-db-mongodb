"""Load data/tracks.json into MongoDB.

By default, existing collection data is preserved and the import is refused.
Pass --replace only when you intentionally want to replace the collection.
"""
import argparse
import json
import sys
from pathlib import Path

from pymongo import MongoClient

from config import COLLECTION_NAME, DATA_FILE, DB_NAME, MONGO_URI

BATCH_SIZE = 5000


def load_tracks(path: str | Path) -> list[dict]:
    """Read and validate a JSON array of track documents."""
    with open(path, encoding="utf-8") as file:
        documents = json.load(file)
    if not isinstance(documents, list) or any(not isinstance(item, dict) for item in documents):
        raise ValueError("tracks.json must contain a JSON array of objects")
    if any("_id" not in item for item in documents):
        raise ValueError("Every track document must contain an _id")
    return documents


def import_tracks(collection, tracks: list[dict], replace: bool = False) -> int:
    """Insert tracks; never erase existing collection data without explicit opt-in."""
    existing = collection.count_documents({})
    if existing and not replace:
        raise RuntimeError(
            f"Collection already contains {existing} documents. "
            "Re-run with --replace only if you intend to replace them."
        )
    if replace:
        collection.drop()
    for start in range(0, len(tracks), BATCH_SIZE):
        collection.insert_many(tracks[start:start + BATCH_SIZE], ordered=False)
    return collection.count_documents({})


def main() -> None:
    parser = argparse.ArgumentParser(description="Import normalized Spotify track documents.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Drop existing collection contents before importing (destructive).",
    )
    args = parser.parse_args()

    if not Path(DATA_FILE).is_file():
        sys.exit(f"Data file not found: {DATA_FILE}. Run prepare_data.py first.")

    tracks = load_tracks(DATA_FILE)
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        collection = client[DB_NAME][COLLECTION_NAME]
        total = import_tracks(collection, tracks, replace=args.replace)
        print(f"Imported {total} documents into {DB_NAME}.{COLLECTION_NAME}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
