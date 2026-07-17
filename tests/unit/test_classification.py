from pathlib import Path

import pandas as pd
import pytest

from etf_pool.config import load_classification_config
from etf_pool.screening.classification import classify_etfs


@pytest.fixture
def classification_config():
    return load_classification_config()


def _etfs(rows: list[tuple[str, str, str, str]]):
    return pd.DataFrame(
        rows,
        columns=["ts_code", "extname", "index_code", "index_name"],
    ).assign(exchange="SH", mgr_name="测试基金")


def test_classification_config_is_valid_json():
    config = load_classification_config(Path("configs/classification.json"))

    assert set(config["categories"]) == {
        "broad_market",
        "sector",
        "theme",
        "overseas",
        "fixed_income",
        "commodity",
    }


def test_classifies_rotation_categories_and_archive_status(classification_config):
    frame = _etfs(
        [
            ("510300.SH", "沪深300ETF", "000300.SH", "沪深300指数"),
            ("159949.SZ", "创业板50ETF", "399673.SZ", "创业板50指数"),
            ("512760.SH", "芯片ETF", "990001.CSI", "中华交易服务半导体芯片行业指数"),
            ("516160.SH", "新能源ETF", "990002.CSI", "新能源产业指数"),
            ("513100.SH", "纳指ETF", "NDX.GI", "纳斯达克100指数"),
            ("513180.SH", "恒生科技ETF", "HSTECH.HI", "恒生科技指数"),
            ("511010.SH", "国债ETF", "000012.SH", "上证5年期国债指数"),
            ("518880.SH", "黄金ETF", "AU9999.SGE", "黄金现货合约"),
            ("511990.SH", "货币ETF", "", "交易型货币市场基金"),
            ("599999.SH", "待识别ETF", "UNKNOWN", "待识别指数"),
        ]
    )

    result = classify_etfs(frame, classification_config, classified_at="2026-07-17T00:00:00Z")

    assert result["pool_category"].tolist()[:8] == [
        "broad_market",
        "broad_market",
        "sector",
        "theme",
        "overseas",
        "overseas",
        "fixed_income",
        "commodity",
    ]
    assert result.loc[8, "archive_status"] == "money_market"
    assert result.loc[9, "archive_status"] == "unknown"
    assert bool(result.loc[9, "needs_review"])


def test_theme_precedes_sector_and_gold_equity_is_not_commodity(classification_config):
    frame = _etfs(
        [
            ("516160.SH", "新能源ETF", "1.CSI", "新能源产业指数"),
            ("517520.SH", "黄金股ETF", "2.CSI", "黄金股票指数"),
            ("517400.SH", "中证沪深港黄金产业股票ETF", "3.CSI", "SSH黄金股票"),
        ]
    )

    result = classify_etfs(frame, classification_config)

    assert result.loc[0, "pool_category"] == "theme"
    assert pd.isna(result.loc[1, "pool_category"])
    assert result.loc[1, "archive_status"] == "unknown"
    assert result.loc[2, "pool_category"] == "overseas"


def test_index_name_precedes_manager_text_and_strategy_is_broad(classification_config):
    frame = _etfs(
        [
            ("159821.SZ", "中银证券创业板ETF", "399006.SZ", "创业板指数"),
            ("563180.SH", "银华中证高股息策略ETF", "1.CSI", "中证高股息策略指数"),
        ]
    )
    frame.loc[0, "mgr_name"] = "中银证券"

    result = classify_etfs(frame, classification_config)

    assert result["pool_category"].tolist() == ["broad_market", "broad_market"]
    assert result["classification_source"].tolist() == [
        "tushare.etf_basic.index_name",
        "tushare.etf_basic.index_name",
    ]


def test_ai_industrial_internet_and_smart_ev_are_themes(classification_config):
    frame = _etfs(
        [
            ("159022.SZ", "科创创业人工智能ETF", "1.CSI", "科创创业AI"),
            ("159013.SZ", "工业互联网主题ETF", "2.CSI", "中证工业互联"),
            ("159720.SZ", "智能电动汽车ETF", "3.CSI", "中证智能电车"),
        ]
    )

    result = classify_etfs(frame, classification_config)

    assert result["pool_category"].tolist() == ["theme", "theme", "theme"]


def test_primary_consistency_corrections(classification_config):
    frame = _etfs(
        [
            ("159176.SZ", "中证全指家用电器ETF", "930697.CSI", "中证家用电器"),
            ("159546.SZ", "中证全指集成电路ETF", "932087.CSI", "中证集成电路"),
            ("513400.SH", "道琼斯工业平均ETF", "DJIA.UN", "道琼斯工业平均"),
            ("513310.SH", "中韩半导体ETF", "931790.CSI", "中证中韩半导体"),
            ("159188.SZ", "标普中国A股红利100ETF", "SPCADMCP.OTH", "标普中国A股红利100"),
        ]
    )

    result = classify_etfs(frame, classification_config)

    assert result["pool_category"].tolist() == [
        "sector",
        "sector",
        "overseas",
        "overseas",
        "broad_market",
    ]


def test_same_index_propagates_unique_category(classification_config):
    frame = _etfs(
        [
            ("512760.SH", "芯片ETF", "990001.CSI", "半导体芯片行业指数"),
            ("159999.SZ", "指数ETF二号", "990001.CSI", ""),
        ]
    )

    result = classify_etfs(frame, classification_config)

    assert result.loc[1, "pool_category"] == "sector"
    assert pd.isna(result.loc[1, "archive_status"])
    assert result.loc[1, "classification_rule"] == "same_index_propagation"
    assert result.loc[1, "classification_confidence"] == "medium"


def test_same_index_conflict_requires_review(classification_config):
    frame = _etfs(
        [
            ("512760.SH", "芯片ETF", "CONFLICT.CSI", "芯片指数"),
            ("516160.SH", "新能源ETF", "CONFLICT.CSI", "新能源指数"),
        ]
    )

    result = classify_etfs(frame, classification_config)

    assert result["needs_review"].tolist() == [True, True]
    assert result["classification_confidence"].tolist() == ["low", "low"]
    assert result["classification_reason"].str.contains("分类冲突").all()


def test_rejects_duplicate_etf_codes(classification_config):
    frame = _etfs(
        [
            ("510300.SH", "沪深300ETF", "000300.SH", "沪深300指数"),
            ("510300.SH", "沪深300ETF", "000300.SH", "沪深300指数"),
        ]
    )

    with pytest.raises(ValueError, match="重复ts_code"):
        classify_etfs(frame, classification_config)
