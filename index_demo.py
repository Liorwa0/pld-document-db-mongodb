"""Compare a collection scan with an explicit index-backed query."""
from pymongo import MongoClient

from config import COLLECTION_NAME, DB_NAME, MONGO_URI

QUERY = {"genres": "jazz"}
INDEX_NAME = "genres_1"


def explain_cost(tracks, query, hint=None):
    """Return documents examined and execution time for a query plan."""
    cursor = tracks.find(query)
    if hint is not None:
        cursor = cursor.hint(hint)
    stats = cursor.explain()["executionStats"]
    return stats["totalDocsExamined"], stats["executionTimeMillis"]


def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        tracks = client[DB_NAME][COLLECTION_NAME]
        # Use a collection scan explicitly; do not drop indexes that users
        # may already rely on.
        examined, millis = explain_cost(tracks, QUERY, hint={"$natural": 1})
        print(f"Collection scan: {examined} documents examined, {millis} ms")

        tracks.create_index("genres", name=INDEX_NAME)
        examined, millis = explain_cost(tracks, QUERY, hint=INDEX_NAME)
        print(f"Indexed query:   {examined} documents examined, {millis} ms")
    finally:
        client.close()


if __name__ == "__main__":
    main()
