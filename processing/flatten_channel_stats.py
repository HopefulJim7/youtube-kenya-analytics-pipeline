import argparse
import csv
import json
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_json(input_path: Path) -> list[dict]:
    with input_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_csv(rows: list[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        raise ValueError("No rows available to write.")

    fieldnames = list(rows[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def flatten_channel_stats(raw_records: list[dict]) -> list[dict]:
    rows = []

    for record in raw_records:
        api_items = record.get("api_response", {}).get("items", [])

        if not api_items:
            continue

        item = api_items[0]
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})

        rows.append(
            {
                "snapshot_date": record.get("snapshot_date"),
                "channel_id": record.get("channel_id"),
                "configured_name": record.get("configured_name"),
                "channel_title": snippet.get("title"),
                "channel_description": snippet.get("description"),
                "published_at": snippet.get("publishedAt"),
                "country": snippet.get("country"),
                "configured_country": record.get("configured_country"),
                "configured_niche": record.get("configured_niche"),
                "subscriber_count": statistics.get("subscriberCount"),
                "view_count": statistics.get("viewCount"),
                "video_count": statistics.get("videoCount"),
                "hidden_subscriber_count": statistics.get("hiddenSubscriberCount"),
            }
        )

    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flatten raw YouTube channel stats JSON to CSV.")
    parser.add_argument(
        "--snapshot-date",
        help="Snapshot date to process in YYYY-MM-DD format. Defaults to today if available, otherwise the latest available snapshot.",
    )
    return parser.parse_args()


def build_input_path(snapshot_date: str) -> Path:
    return (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "channel_stats"
        / f"snapshot_date={snapshot_date}"
        / "channel_stats.json"
    )


def get_latest_snapshot_date() -> str:
    raw_dir = PROJECT_ROOT / "data" / "raw" / "channel_stats"
    snapshot_dirs = sorted(raw_dir.glob("snapshot_date=*"))

    if not snapshot_dirs:
        raise FileNotFoundError(f"No channel stats snapshots found in {raw_dir}")

    latest_snapshot_dir = snapshot_dirs[-1]
    return latest_snapshot_dir.name.replace("snapshot_date=", "")


def resolve_snapshot_date(requested_snapshot_date: str | None) -> str:
    if requested_snapshot_date:
        return requested_snapshot_date

    today = date.today().isoformat()
    if build_input_path(today).exists():
        return today

    latest_snapshot_date = get_latest_snapshot_date()
    print(f"No raw snapshot found for {today}. Using latest available snapshot: {latest_snapshot_date}")
    return latest_snapshot_date


def main():
    args = parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date)
    input_path = build_input_path(snapshot_date)

    output_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "channel_stats"
        / f"snapshot_date={snapshot_date}"
        / "channel_stats.csv"
    )

    raw_records = read_json(input_path)
    rows = flatten_channel_stats(raw_records)
    saved_path = write_csv(rows, output_path)

    print(f"Flattened {len(rows)} channel stat records.")
    print(f"Saved processed CSV to: {saved_path}")


if __name__ == "__main__":
    main()
