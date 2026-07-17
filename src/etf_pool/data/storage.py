"""本地表格存储约定。"""

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_csv(frame: pd.DataFrame, path: Path):
    """写入不包含索引的UTF-8 CSV数据集。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")
    return path


def read_csv(path: Path):
    return pd.read_csv(path)


def write_json(data: dict[str, Any], path: Path):
    """以稳定格式写入不含密钥的运行元数据。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
