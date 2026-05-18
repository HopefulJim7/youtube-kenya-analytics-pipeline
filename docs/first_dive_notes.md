# First Dive Notes

## Goal

Validate that the project can connect to the YouTube Data API and identify target Kenyan channels.

## First Milestone

Successfully search for `Citizen TV Kenya` and print possible channel matches with their channel IDs.

## Why This Matters

Before building daily snapshots, dbt models, Airflow DAGs, or dashboards, we need reliable channel identifiers. YouTube channel names and handles can change, but channel IDs are stable.

## Next Step After This

Once the API test works, update `config/channels.yml` with confirmed `channel_id` values.

## Second Milestone

Fetch channel statistics for all configured Kenyan channels and save the raw API responses locally using a date-partitioned folder structure.

Example output:

```text
data/raw/channel_stats/snapshot_date=YYYY-MM-DD/channel_stats.json
```

## Why Raw Storage Comes First

Raw storage preserves the original API response before any cleaning or transformation. This gives us a reliable source of truth for debugging, reprocessing, and later dbt modeling.

## Third Milestone

Fetch recent video metadata for all configured Kenyan channels and save the raw API responses locally using the same date-partitioned storage convention.

Example output:

```text
data/raw/videos/snapshot_date=YYYY-MM-DD/videos.json
```

## Development Quota Strategy

The video metadata ingestion starts with a limit of 25 recent videos per channel. This confirms the extraction workflow without using excessive YouTube API quota. A later historical backfill script can remove or parameterize this limit.
