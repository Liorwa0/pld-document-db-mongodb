import unittest

from prepare_data import AUDIO_FEATURES, build_document, transform_rows


def row(track_id="track-1", genre="jazz"):
    values = {
        "track_id": track_id,
        "track_name": "Example",
        "album_name": "Album",
        "artists": "Artist A;Artist B",
        "track_genre": genre,
        "popularity": "75",
        "duration_ms": "210000",
        "explicit": "True",
    }
    values.update({feature: "0.5" for feature in AUDIO_FEATURES})
    return values


class PrepareDataTests(unittest.TestCase):
    def test_build_document_creates_nested_shape_and_types(self):
        document = build_document(row())
        self.assertEqual(document["_id"], "track-1")
        self.assertEqual(document["artists"], ["Artist A", "Artist B"])
        self.assertEqual(document["genres"], ["jazz"])
        self.assertIsInstance(document["audio_features"]["energy"], float)
        self.assertTrue(document["explicit"])

    def test_transform_rows_merges_genres_for_duplicate_tracks(self):
        documents = transform_rows([row(genre="jazz"), row(genre="pop"), row(genre="jazz")])
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["genres"], ["jazz", "pop"])

    def test_transform_rows_keeps_different_tracks(self):
        documents = transform_rows([row("one"), row("two")])
        self.assertEqual({item["_id"] for item in documents}, {"one", "two"})

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(transform_rows([]), [])

    def test_empty_track_id_is_skipped(self):
        self.assertEqual(transform_rows([row(track_id="")]), [])


if __name__ == "__main__":
    unittest.main()
