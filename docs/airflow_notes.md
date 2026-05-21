# Airflow Notes

## Current Status

The DAG `youtube_kenya_daily_pipeline` is working end to end.

Latest confirmed successful manual run:

- Run ID: `manual__2026-05-21T23:10:22.240540+00:00`
- State: `success`
- `dbt run`: passed with 6 models
- `dbt test`: passed with 28 tests

## Local Development Mode

During local debugging, prefer reusing stored raw YouTube snapshots instead of calling the YouTube API every time.

Use:

```env
YOUTUBE_PIPELINE_USE_EXISTING_RAW=true
```

This lets the DAG skip fresh API extraction and continue with:

1. Flatten raw JSON to processed CSV.
2. Load processed CSVs into PostgreSQL.
3. Run dbt models.
4. Run dbt tests.

## Important Docker Note

If `docker-compose.yml` or `.env` environment variables change, use recreate instead of restart:

```bash
docker compose up -d --force-recreate airflow
```

`docker compose restart airflow` restarts the existing container, but it does not always apply new environment variables.

## Fresh YouTube Pull Mode

When ready to collect a new daily snapshot from the YouTube API, set:

```env
YOUTUBE_PIPELINE_USE_EXISTING_RAW=false
```

Then recreate Airflow:

```bash
docker compose up -d --force-recreate airflow
```
