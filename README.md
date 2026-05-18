# YouTube Kenya Analytics Pipeline

An end-to-end data engineering project that ingests YouTube channel and video metrics for Kenyan content creators and media houses, stores raw snapshots, transforms analytics-ready models with dbt, orchestrates the workflow with Airflow, and powers BI dashboards.

## First Dive

The first implementation slice focuses on:

1. Defining target Kenyan YouTube channels.
2. Setting up YouTube API access.
3. Testing a single channel lookup.
4. Creating the raw storage path convention.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`:

```env
YOUTUBE_API_KEY=your_real_api_key_here
RAW_BUCKET_NAME=youtube-kenya-analytics
RAW_STORAGE_BACKEND=local
RAW_LOCAL_DIR=data/raw
```

Run the first API test:

```bash
cd ingestion
python test_single_channel.py
```

## Run Channel Stats Ingestion

Fetch raw channel statistics for all configured channels:

```bash
cd ingestion
python extract_channel_stats.py
```

This writes raw JSON to:

```text
data/raw/channel_stats/snapshot_date=YYYY-MM-DD/channel_stats.json
```

## Run Limited Video Metadata Ingestion

Fetch recent video metadata for all configured channels:

```bash
cd ingestion
python extract_video_metadata.py
```

The current script fetches up to 25 recent videos per channel to keep API quota usage low during development.

This writes raw JSON to:

```text
data/raw/videos/snapshot_date=YYYY-MM-DD/videos.json
```
