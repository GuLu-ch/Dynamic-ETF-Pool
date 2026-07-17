import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from etf_pool.config import load_classification_config
from etf_pool.data.sync import ETF_BASIC_FIELDS, classify_etf_snapshot, sync_and_classify_etfs


class FakeProvider:
    def __init__(self, frame: pd.DataFrame):
        self.frame = frame
        self.calls: list[str] = []

    def fetch_etf_basic(self, list_status: str = "L"):
        self.calls.append(list_status)
        return self.frame.copy()


def _frame():
    return pd.DataFrame(
        {
            "ts_code": ["510300.SH", "513100.SH", "518880.SH"],
            "extname": ["沪深300ETF", "纳指ETF", "黄金ETF"],
            "index_code": ["000300.SH", "NDX.GI", "AU9999.SGE"],
            "index_name": ["沪深300指数", "纳斯达克100指数", "黄金现货合约"],
            "exchange": ["SH", "SH", "SH"],
            "mgr_name": ["甲基金", "乙基金", "丙基金"],
        }
    )


def test_sync_writes_immutable_snapshot_and_classification(tmp_path: Path):
    provider = FakeProvider(_frame())
    as_of_date = date.today().isoformat()
    classification_version = str(load_classification_config()["version"])

    summary = sync_and_classify_etfs(
        provider=provider,
        data_dir=tmp_path,
        source="tushare",
        classification_config=load_classification_config(),
        as_of_date=as_of_date,
        fetched_at="2026-07-17T00:00:00+00:00",
    )

    raw_dir = tmp_path / "raw" / "tushare" / "etf_basic" / f"as_of_date={as_of_date}"
    output_dir = (
        tmp_path
        / "interim"
        / "classification"
        / f"as_of_date={as_of_date}"
        / f"version={classification_version}"
    )
    raw = pd.read_csv(raw_dir / "part.csv")
    classified = pd.read_csv(output_dir / "etf_classification.csv")
    metadata = json.loads((raw_dir / "metadata.json").read_text(encoding="utf-8"))

    assert provider.calls == ["L"]
    assert raw.columns.tolist() == ETF_BASIC_FIELDS
    assert classified["pool_category"].tolist() == ["broad_market", "overseas", "commodity"]
    assert metadata["request"]["fields"] == ",".join(ETF_BASIC_FIELDS)
    assert summary["total_count"] == 3
    assert summary["categorized_count"] == 3
    assert summary["needs_review_count"] == 0

    with pytest.raises(FileExistsError, match="禁止静默覆盖"):
        sync_and_classify_etfs(
            provider=provider,
            data_dir=tmp_path,
            source="tushare",
            classification_config=load_classification_config(),
            as_of_date=as_of_date,
        )

    next_config = deepcopy(load_classification_config())
    next_config["version"] = "test-next"
    next_summary = classify_etf_snapshot(
        data_dir=tmp_path,
        source="tushare",
        classification_config=next_config,
        as_of_date=as_of_date,
        classified_at="2026-07-17T01:00:00+00:00",
    )
    next_output = output_dir.parent / "version=test-next" / "etf_classification.csv"
    assert next_output.exists()
    assert next_summary["classification_version"] == "test-next"


def test_sync_rejects_duplicate_natural_keys(tmp_path: Path):
    duplicated = pd.concat([_frame(), _frame().iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="重复ts_code"):
        sync_and_classify_etfs(
            provider=FakeProvider(duplicated),
            data_dir=tmp_path,
            source="tushare",
            classification_config=load_classification_config(),
            as_of_date=date.today().isoformat(),
        )
