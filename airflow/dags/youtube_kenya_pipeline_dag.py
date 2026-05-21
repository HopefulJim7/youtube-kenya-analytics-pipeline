import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_ROOT = os.getenv("YOUTUBE_PIPELINE_PROJECT_ROOT", "/opt/airflow/project")
PYTHON_BIN = os.getenv("YOUTUBE_PIPELINE_PYTHON_BIN", "python")
DBT_BIN = os.getenv("YOUTUBE_PIPELINE_DBT_BIN", "dbt")
DBT_PROFILES_DIR = os.getenv(
    "YOUTUBE_PIPELINE_DBT_PROFILES_DIR",
    f"{PROJECT_ROOT}/dbt_youtube_analytics",
)
USE_EXISTING_RAW = os.getenv("YOUTUBE_PIPELINE_USE_EXISTING_RAW", "false").lower() == "true"
SNAPSHOT_DATE = os.getenv("YOUTUBE_PIPELINE_SNAPSHOT_DATE", "")
SNAPSHOT_DATE_ARG = f" --snapshot-date {SNAPSHOT_DATE}" if SNAPSHOT_DATE else ""


def python_command(script_path: str, extra_args: str = "") -> str:
    return f"cd {PROJECT_ROOT} && {PYTHON_BIN} {script_path}{extra_args}"


def skip_existing_raw_message(entity_name: str) -> str:
    return (
        f"echo 'Using existing raw {entity_name} snapshot. "
        "Skipping YouTube API extraction.'"
    )


default_args = {
    "owner": "youtube-kenya-analytics",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="youtube_kenya_daily_pipeline",
    description="Daily YouTube Kenya analytics ingestion, processing, loading, and dbt transformation pipeline.",
    default_args=default_args,
    start_date=datetime(2026, 5, 18),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    # max_active_tasks=1,
    tags=["youtube", "kenya", "analytics"],
) as dag:
    extract_channel_stats = BashOperator(
        task_id="extract_channel_stats",
        bash_command=(
            skip_existing_raw_message("channel stats")
            if USE_EXISTING_RAW
            else python_command("ingestion/extract_channel_stats.py")
        ),
    )

    extract_video_metadata = BashOperator(
        task_id="extract_video_metadata",
        bash_command=(
            skip_existing_raw_message("video metadata")
            if USE_EXISTING_RAW
            else python_command("ingestion/extract_video_metadata.py")
        ),
    )

    flatten_channel_stats = BashOperator(
        task_id="flatten_channel_stats",
        bash_command=python_command("processing/flatten_channel_stats.py", SNAPSHOT_DATE_ARG),
    )

    flatten_video_metadata = BashOperator(
        task_id="flatten_video_metadata",
        bash_command=python_command("processing/flatten_video_metadata.py", SNAPSHOT_DATE_ARG),
    )

    load_processed_csvs = BashOperator(
        task_id="load_processed_csvs_to_postgres",
        bash_command=python_command("loading/load_processed_csv_to_postgres.py", SNAPSHOT_DATE_ARG),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"cd {PROJECT_ROOT}/dbt_youtube_analytics "
            f"&& {DBT_BIN} run --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {PROJECT_ROOT}/dbt_youtube_analytics "
            f"&& {DBT_BIN} test --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    extract_channel_stats >> flatten_channel_stats
    extract_video_metadata >> flatten_video_metadata

    [flatten_channel_stats, flatten_video_metadata] >> load_processed_csvs
    load_processed_csvs >> dbt_run >> dbt_test
