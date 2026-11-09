# PLD: Document Database with MongoDB

Proof of concept for a Peer Learning Day on document databases using MongoDB and a Spotify tracks dataset.

## Data transformation
The source CSV contains repeated rows for tracks associated with different genres. The preparation step creates one document per track:
- repeated genre values become a unique `genres` array;
- artists remain an array;
- audio measurements are grouped in `audio_features`;
- the source track identifier becomes MongoDB's `_id`.

The reported source dataset has approximately 114,000 rows and the original analysis produced 89,741 unique track documents. Re-run the preparation script against the provided dataset to reproduce the count.

## Requirements
- Python 3.10+
- MongoDB Community Server or Docker
- Dependencies: `pip install -r requirements.txt`

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker run --name mongo -p 27017:27017 -d mongo:7
python prepare_data.py
python -m unittest discover -s tests -v
python import_data.py
```

The importer refuses to erase a non-empty collection by default. To intentionally replace its contents, run `python import_data.py --replace`. This operation is destructive; back up data first.

## CRUD exercises
```bash
python create.py
python read.py
python update.py
python delete.py
``

The CRUD scripts are educational demonstrations and may mutate the local demo collection.

## Index experiment
```bash
python index_demo.py
```
The experiment compares a forced collection scan with a query explicitly hinted to use the `genres_1` index. It no longer drops an existing index before the experiment. Query times vary with hardware, MongoDB version, cache state, and dataset size; no fixed speedup is claimed.

## Key files
| File | Responsibility |
|---|---|
| `config.py` | Environment-overridable connection and path settings |
| `prepare_data.py` | CSV normalization and deduplication |
| `import_data.py` | Batched import with explicit destructive opt-in |
| `create.py`, `read.py`, `update.py`, `delete.py` | CRUD examples |
| `index_demo.py` | Collection-scan versus indexed query plan |
| `tests/` | Offline tests for transformation logic |

## Configuration
Defaults to `mongodb://localhost:27017/`, database `pld_db`, collection `tracks`. Override with `MONGO_URI`, `MONGO_DB`, `MONGO_COLLECTION`, or `DATA_FILE`.

## Limitations
This is a learning exercise, not a production ingestion pipeline. It does not yet provide schema versioning, resumable imports, data-quality reports, or a production-grade migration strategy. Dataset contents and license should be checked against the original Kaggle source before redistribution.
