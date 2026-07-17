"""Local tabular storage conventions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_csv(frame: pd.DataFrame, path: Path) -> Path:
    """Write a UTF-8, index-free CSV dataset."""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")
    return path


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)
