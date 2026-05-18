import os
from datetime import date
from pathlib import Path

import yaml
from dotenv import load_dotenv

from youtube_client import YouTubeClient

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from storage.local_storage import write_json
from storage.raw_path_builder import build_raw_path


def load_channels(config_path: Path) -> list[dict]:
    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data["channels"]


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise ValueError("Missing YOUTUBE_API_KEY. Add it to your .env file.")

    youtube = YouTubeClient(api_key)

    channels = load_channels(PROJECT_ROOT / "config" / "channels.yml")
    snapshot_date = date.today()

    channel_stats = []

    for channel in channels:
        channel_id = channel["channel_id"]
        response = youtube.get_channel_by_id(channel_id)

        channel_stats.append(
            {
                "configured_name": channel["name"],
                "configured_niche": channel["niche"],
                "configured_country": channel["country"],
                "channel_id": channel_id,
                "snapshot_date": snapshot_date.isoformat(),
                "api_response": response,
            }
        )

        print(f"Fetched channel stats for: {channel['name']}")

    raw_relative_path = build_raw_path(
        entity="channel_stats",
        snapshot_date=snapshot_date,
        filename="channel_stats.json",
    )

    raw_local_dir = os.getenv("RAW_LOCAL_DIR", "data/raw")
    output_path = PROJECT_ROOT / raw_local_dir / raw_relative_path.replace("raw/", "")

    saved_path = write_json(channel_stats, str(output_path))

    print("-" * 60)
    print(f"Saved raw channel stats to: {saved_path}")


if __name__ == "__main__":
    main()
