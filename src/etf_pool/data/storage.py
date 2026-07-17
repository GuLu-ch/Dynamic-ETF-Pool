"""本地表格存储约定。"""

from pathlib import Path

import pandas as pd


def write_csv(frame: pd.DataFrame, path: Path):
    """写入不包含索引的UTF-8 CSV数据集。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")
    return path


def read_csv(path: Path):
    return pd.read_csv(path)
