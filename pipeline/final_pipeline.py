from pathlib import Path
from typing import Dict, List

from Config import RESULTS_DIR
from Main import build_stage6_summary, build_stage7_summary
from pipeline.validation import assert_all_files_exist



def run_final_pipeline() -> Dict[str, object]:
    stage6_summary = build_stage6_summary()
    stage7_summary = build_stage7_summary()

    required_files: List[Path] = [
        Path(stage6_summary["comparison_table_file"]),
        Path(stage6_summary["std_xt_table_file"]),
        Path(stage7_summary["dashboard_file"]),
    ] + [Path(p) for p in stage6_summary["generated_figures"]]

    assert_all_files_exist(required_files)

    return {
        "results_dir": str(RESULTS_DIR),
        "stage6_summary": stage6_summary,
        "stage7_summary": stage7_summary,
        "validated_file_count": len(required_files),
    }
