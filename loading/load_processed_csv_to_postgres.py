import argparse
import csv
import os
from datetime import date
from pathlib import Path

import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load processed CSV files into PostgreSQL.")
    parser.add_argument(
        "--snapshot-date",
        help="Snapshot date to load in YYYY-MM-DD format. Defaults to today if available, otherwise the latest available snapshot.",
    )
    return parser.parse_args()


def get_db_connection():
    load_dotenv(PROJECT_ROOT / ".env")

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5433"),
        dbname=os.getenv("POSTGRES_DB", "youtube_analytics"),
        user=os.getenv("POSTGRES_USER", "youtube_user"),
        password=os.getenv("POSTGRES_PASSWORD", "youtube_password"),
    )


def execute_sql_file(connection, sql_path: Path) -> None:
    with sql_path.open("r", encoding="utf-8") as file:
        sql = file.read()

    with connection.cursor() as cursor:
        cursor.execute(sql)

    connection.commit()


def get_latest_snapshot_date(processed_entity: str) -> str:
    processed_dir = PROJECT_ROOT / "data" / "processed" / processed_entity
    snapshot_dirs = sorted(processed_dir.glob("snapshot_date=*"))

    if not snapshot_dirs:
        raise FileNotFoundError(f"No processed snapshots found in {processed_dir}")

    latest_snapshot_dir = snapshot_dirs[-1]
    return latest_snapshot_dir.name.replace("snapshot_date=", "")


def resolve_snapshot_date(requested_snapshot_date: str | None, processed_entity: str) -> str:
    if requested_snapshot_date:
        return requested_snapshot_date

    today = date.today().isoformat()
    today_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / processed_entity
        / f"snapshot_date={today}"
    )

    if today_path.exists():
        return today

    latest_snapshot_date = get_latest_snapshot_date(processed_entity)
    print(f"No processed {processed_entity} snapshot found for {today}. Using latest available snapshot: {latest_snapshot_date}")
    return latest_snapshot_date


def read_csv_rows(csv_path: Path) -> list[dict]:
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def none_if_empty(value):
    return value if value != "" else None


def load_rows(connection, table_name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows available to load into {table_name}.")

    columns = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(columns))
    column_names = ", ".join(columns)

    insert_sql = f"""
        INSERT INTO {table_name} ({column_names})
        VALUES ({placeholders})
    """

    values = [
        tuple(none_if_empty(row[column]) for column in columns)
        for row in rows
    ]

    with connection.cursor() as cursor:
        cursor.executemany(insert_sql, values)

    connection.commit()


def delete_existing_snapshot(connection, table_name: str, snapshot_date: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"DELETE FROM {table_name} WHERE snapshot_date = %s",
            (snapshot_date,),
        )

    connection.commit()


def main():
    args = parse_args()

    channel_snapshot_date = resolve_snapshot_date(args.snapshot_date, "channel_stats")
    video_snapshot_date = resolve_snapshot_date(args.snapshot_date, "videos")

    channel_csv_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "channel_stats"
        / f"snapshot_date={channel_snapshot_date}"
        / "channel_stats.csv"
    )

    video_csv_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "videos"
        / f"snapshot_date={video_snapshot_date}"
        / "videos.csv"
    )

    channel_rows = read_csv_rows(channel_csv_path)
    video_rows = read_csv_rows(video_csv_path)

    connection = get_db_connection()

    try:
        execute_sql_file(connection, PROJECT_ROOT / "loading" / "create_tables.sql")

        delete_existing_snapshot(connection, "raw_channel_stats", channel_snapshot_date)
        delete_existing_snapshot(connection, "raw_video_metadata", video_snapshot_date)

        load_rows(connection, "raw_channel_stats", channel_rows)
        load_rows(connection, "raw_video_metadata", video_rows)

        print(f"Loaded {len(channel_rows)} rows into raw_channel_stats.")
        print(f"Loaded {len(video_rows)} rows into raw_video_metadata.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
