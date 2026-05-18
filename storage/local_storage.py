import json
from pathlib import Path
from typing import Any

def write_json(data: Any, output_path: str) -> Path:
    """
    Writes data to a local JSON file.
    
    Example output_path:
    data/raw/channel_stats/snapshot_date=2026-05-18/channel_stats.json
    """
    
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        
    return path
        