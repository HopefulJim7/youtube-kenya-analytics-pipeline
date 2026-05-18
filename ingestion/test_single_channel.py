import os
from pathlib import Path

from dotenv import load_dotenv

from youtube_client import YouTubeClient


def main():
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise ValueError("Missing YOUTUBE_API_KEY. Add it to your .env file.")

    youtube = YouTubeClient(api_key)

    channel_name = "Citizen TV Kenya"
    print(f"Searching for channel: {channel_name}")

    response = youtube.search_channel(channel_name)

    for item in response.get("items", []):
        snippet = item["snippet"]
        channel_id = item["snippet"]["channelId"]

        print("-" * 60)
        print(f"Title: {snippet.get('title')}")
        print(f"Channel ID: {channel_id}")
        print(f"Description: {snippet.get('description')[:120]}")

    print("-" * 60)
    print("Done.")


if __name__ == "__main__":
    main()
