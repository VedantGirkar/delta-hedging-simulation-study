import csv
from pathlib import Path
from typing import Dict, List



def write_dict_rows_to_csv(rows: List[Dict[str, object]], file_path: Path) -> None:
    if not rows:
        raise ValueError("rows cannot be empty")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with file_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
