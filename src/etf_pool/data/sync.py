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
from etf_pool.screening.secondary import classify_secondary_etfs

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


def _secondary_paths(
    data_dir: Path,
    as_of_date: str,
    primary_version: str,
    secondary_version: str,
):
    primary_dir = (
        data_dir
        / "interim"
        / "classification"
        / f"as_of_date={as_of_date}"
        / f"version={primary_version}"
    )
    output_dir = (
        data_dir
        / "interim"
        / "secondary_classification"
        / f"as_of_date={as_of_date}"
        / f"primary_version={primary_version}"
        / f"secondary_version={secondary_version}"
    )
    return {
        "primary_csv": primary_dir / "etf_classification.csv",
        "primary_summary": primary_dir / "summary.json",
        "classification_csv": output_dir / "etf_classification.csv",
        "summary": output_dir / "summary.json",
    }


def _secondary_summary(
    classified: pd.DataFrame,
    primary_summary: Mapping[str, Any],
    secondary_config: Mapping[str, Any],
    as_of_date: str,
    input_snapshot: Path,
):
    counts = (
        classified.groupby(
            ["pool_category", "secondary_category", "secondary_category_name"],
            dropna=False,
        )
        .size()
        .reset_index(name="group_count")
    )
    groups = [
        {
            "pool_category": (
                None if pd.isna(record["pool_category"]) else str(record["pool_category"])
            ),
            "secondary_category": str(record["secondary_category"]),
            "secondary_category_name": str(record["secondary_category_name"]),
            "count": int(record["group_count"]),
        }
        for record in counts.to_dict(orient="records")
    ]
    return {
        "source": primary_summary.get("source", "unknown"),
        "as_of_date": as_of_date,
        "primary_classification_version": str(primary_summary["classification_version"]),
        "primary_classification_config_hash": primary_summary["classification_config_hash"],
        "secondary_classification_version": str(secondary_config["version"]),
        "secondary_classification_config_hash": _config_hash(secondary_config),
        "code_version": _code_version(),
        "input_snapshot": str(input_snapshot),
        "total_count": int(len(classified)),
        "rotation_count": int(classified["pool_category"].notna().sum()),
        "archived_count": int(classified["archive_status"].notna().sum()),
        "fallback_count": int(
            classified["secondary_classification_rule"].eq("secondary_fallback").sum()
        ),
        "needs_secondary_review_count": int(classified["needs_secondary_review"].sum()),
        "group_counts": groups,
    }


def classify_secondary_snapshot(
    data_dir: Path,
    primary_version: str,
    secondary_config: Mapping[str, Any],
    as_of_date: str,
    classified_at: str | None = None,
):
    """从版本化一级分类快照生成二级相关暴露分组。"""
    normalized_date = _validate_as_of_date(as_of_date)
    paths = _secondary_paths(
        data_dir,
        normalized_date,
        primary_version,
        str(secondary_config["version"]),
    )
    if not paths["primary_csv"].exists() or not paths["primary_summary"].exists():
        raise FileNotFoundError(f"找不到一级分类快照：{paths['primary_csv']}")
    _ensure_new_snapshot(
        {
            "classification_csv": paths["classification_csv"],
            "summary": paths["summary"],
        }
    )

    primary = read_csv(paths["primary_csv"])
    versions = {str(value) for value in primary["classification_version"].dropna().unique()}
    if versions != {primary_version}:
        raise ValueError(f"一级分类版本不匹配：期望{primary_version}，实际{sorted(versions)}")
    timestamp = classified_at or datetime.now(timezone.utc).isoformat()
    classified = classify_secondary_etfs(primary, secondary_config, classified_at=timestamp)
    primary_summary = json.loads(paths["primary_summary"].read_text(encoding="utf-8"))
    summary = _secondary_summary(
        classified,
        primary_summary,
        secondary_config,
        normalized_date,
        paths["primary_csv"],
    )
    write_csv(classified, paths["classification_csv"])
    write_json(summary, paths["summary"])
    return summary
