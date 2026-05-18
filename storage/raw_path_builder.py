from datetime import date


def build_raw_path(entity: str, snapshot_date: date | None = None, filename: str | None = None) -> str:
    """
    Builds a partition-style raw storage path.

    Example:
    raw/videos/snapshot_date=2026-05-18/videos.json
    """

    snapshot_date = snapshot_date or date.today()
    filename = filename or f"{entity}.json"

    return f"raw/{entity}/snapshot_date={snapshot_date.isoformat()}/{filename}"
