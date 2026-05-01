import csv
from pathlib import Path
from typing import Dict, List



def read_csv_rows(file_path: Path) -> List[Dict[str, str]]:
    with file_path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))



def load_dashboard_payload(results_dir: Path) -> Dict[str, object]:
    tables_dir = results_dir / "tables"
    comparison_rows = read_csv_rows(tables_dir / "weekly_daily_comparison.csv")
    std_rows = read_csv_rows(tables_dir / "std_xt_paths.csv")

    weekly_std = []
    daily_std = []
    for row in std_rows:
        record = {"t": float(row["t"]), "std_X_t": float(row["std_X_t"]) }
        if row["schedule"] == "weekly":
            weekly_std.append(record)
        else:
            daily_std.append(record)

    return {
        "comparison_rows": comparison_rows,
        "weekly_std": weekly_std,
        "daily_std": daily_std,
        "figure_paths": {
            "weekly_std": str(results_dir / "figures" / "weekly_std_xt.png"),
            "daily_std": str(results_dir / "figures" / "daily_std_xt.png"),
            "overlay_std": str(results_dir / "figures" / "weekly_daily_std_xt_overlay.png"),
            "weekly_hist": str(results_dir / "figures" / "weekly_terminal_xt_hist.png"),
            "daily_hist": str(results_dir / "figures" / "daily_terminal_xt_hist.png"),
            "mean_comp": str(results_dir / "figures" / "mean_xt_comparison.png"),
            "std_comp": str(results_dir / "figures" / "std_xt_terminal_comparison.png"),
        },
    }
