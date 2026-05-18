import os
import sys
from datetime import date
from pathlib import Path

import yaml
from dotenv import load_dotenv

from youtube_client import YouTubeClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from storage.local_storage import write_json
from storage.raw_path_builder import build_raw_path

MAX_VIDEOS_PER_CHANNEL = 25


def load_channels(config_path: Path) -> list[dict]:
    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data["channels"]


def fetch_recent_video_ids(
    youtube: YouTubeClient,
    uploads_playlist_id: str,
    max_videos: int,
) -> list[str]:
    video_ids = []
    page_token = None

    while len(video_ids) < max_videos:
        response = youtube.get_playlist_items(
            playlist_id=uploads_playlist_id,
            page_token=page_token,
            max_results=min(50, max_videos - len(video_ids)),
        )

        for item in response.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id:
                video_ids.append(video_id)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return video_ids


def chunk_list(values: list[str], chunk_size: int) -> list[list[str]]:
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise ValueError("Missing YOUTUBE_API_KEY. Add it to your .env file.")

    youtube = YouTubeClient(api_key)
    channels = load_channels(PROJECT_ROOT / "config" / "channels.yml")
    snapshot_date = date.today()

    video_metadata = []

    for channel in channels:
        channel_id = channel["channel_id"]
        uploads_playlist_id = youtube.get_uploads_playlist_id(channel_id)

        if not uploads_playlist_id:
            print(f"Skipped channel without uploads playlist: {channel['name']}")
            continue

        video_ids = fetch_recent_video_ids(
            youtube=youtube,
            uploads_playlist_id=uploads_playlist_id,
            max_videos=MAX_VIDEOS_PER_CHANNEL,
        )

        for video_id_batch in chunk_list(video_ids, 50):
            response = youtube.get_videos_by_ids(video_id_batch)
            video_metadata.append(
                {
                    "configured_channel_name": channel["name"],
                    "configured_niche": channel["niche"],
                    "configured_country": channel["country"],
                    "channel_id": channel_id,
                    "uploads_playlist_id": uploads_playlist_id,
                    "snapshot_date": snapshot_date.isoformat(),
                    "api_response": response,
                }
            )

        print(f"Fetched {len(video_ids)} videos for: {channel['name']}")

    raw_relative_path = build_raw_path(
        entity="videos",
        snapshot_date=snapshot_date,
        filename="videos.json",
    )

    raw_local_dir = os.getenv("RAW_LOCAL_DIR", "data/raw")
    output_path = PROJECT_ROOT / raw_local_dir / raw_relative_path.replace("raw/", "")

    saved_path = write_json(video_metadata, str(output_path))

    print("-" * 60)
    print(f"Saved raw video metadata to: {saved_path}")


if __name__ == "__main__":
    main()
