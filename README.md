# Spotify Music Analytics — AWS + Databricks + Snowflake + Power BI

An end-to-end data engineering portfolio project that processes a million-row music catalog dataset. It demonstrates ingestion, lakehouse medallion layers, warehouse loading, analytics SQL, and dashboard modeling.

> **Dataset disclaimer:** The included generator creates synthetic practice data. Track names, artists, albums, popularity, follower counts, and audio-feature values are fictional. They are not Spotify catalog data, streaming counts, or listening-history data. Do not describe generated values as real Spotify metrics.

## Architecture

```text
Synthetic CSV.GZ data
       |
       v
   AWS S3 (raw)
       |
       v
 Databricks / PySpark
 Bronze -> Silver -> Gold (Delta)
       |
       v
 AWS S3 (curated Parquet)
       |
       v
 Snowflake external stage + COPY INTO
       |
       v
 SQL analytics / Power BI
```

## Data volumes

Run `python scripts/generate_data.py --tracks 1000000 --artists 100000 --albums 200000`.

| File | Rows |
|---|---:|
| tracks.csv.gz | 1,000,000 |
| artists.csv.gz | 100,000 |
| albums.csv.gz | 200,000 |
| genres.csv | 50 |

The generator writes in batches to keep memory use bounded. Files are compressed CSV and should not be committed to GitHub; upload them to your own S3 bucket instead.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│   └── generate_data.py
├── aws/
│   └── databricks_s3_policy.json
├── databricks/
│   └── spotify_pipeline.py
├── snowflake/
│   ├── 01_setup.sql
│   ├── 02_load.sql
│   └── 03_analytics.sql
├── powerbi/
│   └── measures.dax
└── docs/
    └── data_dictionary.md
```

## 1. Generate the datasets

Python 3.10+:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py --tracks 1000000 --artists 100000 --albums 200000 --output data
```

The script emits deterministic synthetic records (seed defaults to 42). You can reduce counts for a quick smoke test.

## 2. Upload to AWS S3

Create a private bucket and upload:

- `data/tracks.csv.gz` -> `s3://YOUR_BUCKET/raw/tracks/`
- `data/artists.csv.gz` -> `s3://YOUR_BUCKET/raw/artists/`
- `data/albums.csv.gz` -> `s3://YOUR_BUCKET/raw/albums/`

Use an IAM role / instance profile or Unity Catalog storage credential for Databricks. Review `aws/databricks_s3_policy.json` and replace the bucket placeholder. Restrict permissions to the project bucket. Do not commit access keys, secret keys, session tokens, or account credentials.

## 3. Databricks pipeline

Create a Unity Catalog catalog and schema, and a volume named `pipeline_data` in that schema. Configure S3 access using your workspace's approved credential mechanism. Edit the S3 paths and output paths near the top of `databricks/spotify_pipeline.py`, then run it as a notebook/source file.

The pipeline:
- reads the compressed raw CSV files from S3;
- writes Bronze Delta with ingestion metadata;
- validates, standardizes and deduplicates Silver tracks;
- derives Gold track, artist, genre, and release-year summaries;
- writes Gold Delta tables and Parquet files to the curated S3 prefix.

Check the row counts and data quality before moving to Snowflake. The sample's track-to-album/artist assignments are synthetic and independently generated; they are suitable for pipeline exercises, not referentially accurate catalog reporting.

## 4. Snowflake

Follow Snowflake's current documentation to create an S3 storage integration and configure the AWS IAM trust relationship using the values returned by `DESC INTEGRATION SPOTIFY_S3_INT`. Do not put AWS keys in SQL.

Then:
1. Replace placeholders in `snowflake/01_setup.sql` and execute it with a role that can create storage integrations.
2. Confirm the integration is enabled and the stage can list files.
3. Run `snowflake/02_load.sql`.
4. Run `snowflake/03_analytics.sql`.

The Snowflake Parquet loads use VARIANT field extraction. Verify the stage paths and Parquet column names match the Databricks output. For production use, add file-format objects, COPY history checks, reject handling, and a controlled reprocessing strategy.

## 5. Power BI

Connect Power BI Desktop to the Snowflake account using the native Snowflake connector. Import the Gold tables and add measures from `powerbi/measures.dax`. Suggested visuals:
- KPI cards: total tracks, average popularity, total genres;
- bar chart: average popularity by genre;
- table: top tracks;
- scatter: energy vs. danceability;
- line chart: track count by release year.

## Suggested extensions

- Add incremental ingestion with an ingestion date or source-file manifest.
- Use Delta MERGE for upserts and implement SCD Type 2 for artist attributes.
- Add data-quality expectations and quarantine invalid records.
- Orchestrate with Databricks Workflows.
- Add Snowflake Streams/Tasks only when you have a well-defined incremental change stream.
- Add CI checks for Python syntax and SQL linting.

## Important cost and security notes

Cloud services may incur charges. Use small test data first, auto-stop compute, and delete unused resources. Never publish credentials, private datasets, or personally identifying information.
