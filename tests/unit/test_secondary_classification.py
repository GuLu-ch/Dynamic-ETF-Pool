from pathlib import Path

import pandas as pd
import pytest

from etf_pool.config import load_secondary_classification_config
from etf_pool.screening.secondary import classify_secondary_etfs


@pytest.fixture
def secondary_config():
    return load_secondary_classification_config()


def _classified_rows():
    return pd.DataFrame(
        {
            "ts_code": [
                "510300.SH",
                "561990.SH",
                "512760.SH",
                "159801.SZ",
                "588730.SH",
                "513100.SH",
                "511010.SH",
                "518880.SH",
                "511990.SH",
            ],
            "extname": [
                "沪深300ETF",
                "沪深300增强ETF",
                "芯片ETF",
                "半导体ETF",
                "科创人工智能ETF",
                "纳指ETF",
                "5年期国债ETF",
                "黄金ETF",
                "货币ETF",
            ],
            "index_code": [
                "000300.SH",
                "000300.SH",
                "1.CSI",
                "2.CSI",
                "3.CSI",
                "NDX.NASDAQ",
                "H00140.CSI",
                "AU9999.SGE",
                "",
            ],
            "index_name": [
                "沪深300",
                "沪深300",
                "中证芯片产业",
                "国证半导体芯片",
                "科创AI",
                "纳斯达克100指数",
                "上证5年国债",
                "黄金9999",
                "交易型货币",
            ],
            "mgr_name": ["测试基金"] * 9,
            "pool_category": [
                "broad_market",
                "broad_market",
                "sector",
                "sector",
                "theme",
                "overseas",
                "fixed_income",
                "commodity",
                pd.NA,
            ],
            "archive_status": [pd.NA] * 8 + ["money_market"],
        }
    )


def test_secondary_config_is_valid_json():
    config = load_secondary_classification_config(
        Path("configs/secondary-classification.json")
    )

    assert set(config["groups"]) == {
        "broad_market",
        "sector",
        "theme",
        "overseas",
        "fixed_income",
        "commodity",
    }


def test_groups_related_etfs_across_all_primary_categories(secondary_config):
    result = classify_secondary_etfs(
        _classified_rows(),
        secondary_config,
        classified_at="2026-07-17T00:00:00Z",
    )

    assert result["secondary_category"].tolist() == [
        "csi_300",
        "csi_300",
        "semiconductor",
        "semiconductor",
        "artificial_intelligence",
        "nasdaq_100",
        "treasury_short_medium",
        "gold",
        "money_market",
    ]
    assert result["secondary_category_name"].tolist()[:4] == [
        "沪深300",
        "沪深300",
        "芯片半导体",
        "芯片半导体",
    ]


def test_fallback_is_explicit_and_requires_review(secondary_config):
    frame = _classified_rows().iloc[[0]].copy()
    frame["ts_code"] = "599999.SH"
    frame["extname"] = "未定义ETF"
    frame["index_code"] = "UNKNOWN"
    frame["index_name"] = "未定义指数"

    result = classify_secondary_etfs(frame, secondary_config)

    assert result.loc[result.index[0], "secondary_category"] == "other_broad_market"
    assert result.loc[result.index[0], "secondary_classification_rule"] == "secondary_fallback"
    assert bool(result.loc[result.index[0], "needs_secondary_review"])


def test_abbreviated_biotech_index_uses_healthcare_group(secondary_config):
    frame = _classified_rows().iloc[[2]].copy()
    frame["ts_code"] = "159837.SZ"
    frame["extname"] = "中证生物科技主题ETF"
    frame["index_code"] = "930743.CSI"
    frame["index_name"] = "中证生科"

    result = classify_secondary_etfs(frame, secondary_config)

    assert result.loc[result.index[0], "secondary_category"] == "healthcare"
    assert not bool(result.loc[result.index[0], "needs_secondary_review"])


def test_rejects_duplicate_etf_codes(secondary_config):
    frame = pd.concat([_classified_rows().iloc[[0]]] * 2, ignore_index=True)

    with pytest.raises(ValueError, match="重复ts_code"):
        classify_secondary_etfs(frame, secondary_config)
