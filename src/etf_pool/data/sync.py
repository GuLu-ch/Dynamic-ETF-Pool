"""同步ETF基础快照并生成第一版分类实验结果。"""

import hashlib
import json
import subprocess
from collections.abc import Mapping
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from etf_pool.config import PROJECT_ROOT
from etf_pool.data.storage import read_csv, write_csv, write_json
from etf_pool.screening.classification import classify_etfs

ETF_BASIC_FIELDS = [
    "ts_code",
    "extname",
    "index_code",
    "index_name",
    "exchange",
    "mgr_name",
]


def _validate_as_of_date(as_of_date: str):
    try:
        parsed = date.fromisoformat(as_of_date)
    except ValueError as exc:
        raise ValueError("as_of_date必须使用YYYY-MM-DD格式") from exc
    if parsed > date.today():
        raise ValueError("as_of_date不能晚于当前日期")
    return parsed.isoformat()


def _validate_etf_basic(frame: pd.DataFrame):
    missing = sorted(set(ETF_BASIC_FIELDS).difference(frame.columns))
    if missing:
        raise ValueError(f"etf_basic返回缺少字段：{', '.join(missing)}")
    if frame.empty:
        raise ValueError("etf_basic未返回任何上市ETF")
    if frame["ts_code"].isna().any():
        raise ValueError("etf_basic存在空ts_code")
    duplicates = frame["ts_code"].duplicated(keep=False)
    if duplicates.any():
        codes = sorted(frame.loc[duplicates, "ts_code"].astype(str).unique())
        raise ValueError(f"etf_basic存在重复ts_code：{', '.join(codes)}")
    invalid_exchanges = sorted(set(frame["exchange"].dropna().astype(str)).difference({"SH", "SZ"}))
    if invalid_exchanges:
        raise ValueError(f"etf_basic返回未知交易所：{', '.join(invalid_exchanges)}")


def _config_hash(config: Mapping[str, Any]):
    serialized = json.dumps(config, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _code_version():
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if revision.returncode != 0:
        return "unknown"
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    dirty_suffix = "+dirty" if status.returncode == 0 and status.stdout.strip() else ""
    return revision.stdout.strip() + dirty_suffix


def _snapshot_paths(
    data_dir: Path,
    source: str,
    as_of_date: str,
    classification_version: str,
):
    raw_dir = data_dir / "raw" / source / "etf_basic" / f"as_of_date={as_of_date}"
    classification_dir = (
        data_dir
        / "interim"
        / "classification"
        / f"as_of_date={as_of_date}"
        / f"version={classification_version}"
    )
    return {
        "raw_csv": raw_dir / "part.csv",
        "raw_metadata": raw_dir / "metadata.json",
        "classification_csv": classification_dir / "etf_classification.csv",
        "summary": classification_dir / "summary.json",
    }


def _ensure_new_snapshot(paths: Mapping[str, Path]):
    existing = [str(path) for path in paths.values() if path.exists()]
    if existing:
        raise FileExistsError(f"快照已存在，禁止静默覆盖：{', '.join(existing)}")


def _summary(
    classified: pd.DataFrame,
    config: Mapping[str, Any],
    source: str,
    as_of_date: str,
    fetched_at: str,
    raw_csv: Path,
):
    category_counts = {
        str(key): int(value)
        for key, value in classified["pool_category"].dropna().value_counts().sort_index().items()
    }
    archive_counts = {
        str(key): int(value)
        for key, value in classified["archive_status"].dropna().value_counts().sort_index().items()
    }
    return {
        "source": source,
        "as_of_date": as_of_date,
        "fetched_at": fetched_at,
        "classified_at": str(classified["classified_at"].iloc[0]),
        "classification_version": str(config["version"]),
        "classification_config_hash": _config_hash(config),
        "code_version": _code_version(),
        "input_snapshot": str(raw_csv),
        "total_count": int(len(classified)),
        "categorized_count": int(classified["pool_category"].notna().sum()),
        "archived_count": int(classified["archive_status"].notna().sum()),
        "needs_review_count": int(classified["needs_review"].sum()),
        "category_counts": category_counts,
        "archive_counts": archive_counts,
    }


def sync_and_classify_etfs(
    provider: Any,
    data_dir: Path,
    source: str,
    classification_config: Mapping[str, Any],
    as_of_date: str,
    fetched_at: str | None = None,
):
    """调用指定etf_basic接口，保存原始快照和分类实验结果。"""
    normalized_date = _validate_as_of_date(as_of_date)
    paths = _snapshot_paths(
        data_dir,
        source,
        normalized_date,
        str(classification_config["version"]),
    )
    _ensure_new_snapshot(paths)

    try:
        frame = provider.fetch_etf_basic(list_status="L")
    except Exception as exc:
        raise RuntimeError(f"{source}的etf_basic请求失败：{exc}") from exc
    _validate_etf_basic(frame)
    raw = frame.loc[:, ETF_BASIC_FIELDS].copy()

    timestamp = fetched_at or datetime.now(timezone.utc).isoformat()
    classified = classify_etfs(raw, classification_config, classified_at=timestamp)
    summary = _summary(
        classified,
        classification_config,
        source,
        normalized_date,
        timestamp,
        paths["raw_csv"],
    )
    metadata = {
        "source": source,
        "interface": "etf_basic",
        "request": {
            "list_status": "L",
            "fields": ",".join(ETF_BASIC_FIELDS),
        },
        "fetched_at": timestamp,
        "as_of_date": normalized_date,
        "schema_version": "1.0",
        "row_count": int(len(raw)),
        "natural_key": ["ts_code"],
    }

    write_csv(raw, paths["raw_csv"])
    write_json(metadata, paths["raw_metadata"])
    write_csv(classified, paths["classification_csv"])
    write_json(summary, paths["summary"])
    return summary


def classify_etf_snapshot(
    data_dir: Path,
    source: str,
    classification_config: Mapping[str, Any],
    as_of_date: str,
    classified_at: str | None = None,
):
    """使用已有不可变原始快照生成新的分类规则版本。"""
    normalized_date = _validate_as_of_date(as_of_date)
    paths = _snapshot_paths(
        data_dir,
        source,
        normalized_date,
        str(classification_config["version"]),
    )
    if not paths["raw_csv"].exists() or not paths["raw_metadata"].exists():
        raise FileNotFoundError(f"找不到ETF基础快照：{paths['raw_csv']}")
    _ensure_new_snapshot(
        {
            "classification_csv": paths["classification_csv"],
            "summary": paths["summary"],
        }
    )

    raw = read_csv(paths["raw_csv"])
    _validate_etf_basic(raw)
    metadata = json.loads(paths["raw_metadata"].read_text(encoding="utf-8"))
    timestamp = classified_at or datetime.now(timezone.utc).isoformat()
    classified = classify_etfs(raw, classification_config, classified_at=timestamp)
    summary = _summary(
        classified,
        classification_config,
        source,
        normalized_date,
        str(metadata["fetched_at"]),
        paths["raw_csv"],
    )
    write_csv(classified, paths["classification_csv"])
    write_json(summary, paths["summary"])
    return summary
