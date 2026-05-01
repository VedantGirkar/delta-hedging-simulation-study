from pathlib import Path
from typing import Iterable



def assert_file_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")



def assert_all_files_exist(paths: Iterable[Path]) -> None:
    for path in paths:
        assert_file_exists(path)
