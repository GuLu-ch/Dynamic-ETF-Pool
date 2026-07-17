"""在一级轮动类别内按共同基准或暴露生成二级分类。"""

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

import pandas as pd

CONFIDENCE_VALUES = {"high", "medium", "low"}


def _normalize(value: Any):
    if value is None or pd.isna(value):
        return ""
    return "".join(str(value).upper().split())


def _evidence_text(row: pd.Series, field: str):
    value = _normalize(row.get(field))
    if field != "extname" or not value:
        return value

    manager = _normalize(row.get("mgr_name"))
    suffixes = ["基金管理股份有限公司", "基金管理有限公司", "股份有限公司", "有限公司", "基金"]
    for suffix in suffixes:
        if manager.endswith(suffix):
            manager = manager[: -len(suffix)]
            break
    if manager and value.startswith(manager):
        return value[len(manager) :]
    return value


def _validate_config(config: Mapping[str, Any]):
    required = {"version", "evidence_fields", "fallbacks", "archive_groups", "groups"}
    missing = sorted(required.difference(config))
    if missing:
        raise ValueError(f"二级分类配置缺少字段：{', '.join(missing)}")

    fallback_categories = set(config["fallbacks"])
    group_categories = set(config["groups"])
    if fallback_categories != group_categories:
        raise ValueError("二级分类的groups与fallbacks一级类别必须一致")

    values: set[str] = set()
    for primary_category, rules in config["groups"].items():
        for rule in rules:
            required_rule = {"value", "label", "keywords"}
            missing_rule = sorted(required_rule.difference(rule))
            if missing_rule:
                raise ValueError(
                    f"二级分类{primary_category}规则缺少字段：{', '.join(missing_rule)}"
                )
            value = str(rule["value"])
            if value in values:
                raise ValueError(f"二级分类值重复：{value}")
            values.add(value)


def _rule_keyword(value: str, rule: Mapping[str, Any]):
    excluded = [_normalize(keyword) for keyword in rule.get("exclude_keywords", [])]
    if any(keyword and keyword in value for keyword in excluded):
        return None
    for keyword in rule["keywords"]:
        normalized_keyword = _normalize(keyword)
        if normalized_keyword and normalized_keyword in value:
            return str(keyword)
    return None


def _decision(rule: Mapping[str, Any], source: str, reason: str, confidence: str):
    return {
        "secondary_category": rule["value"],
        "secondary_category_name": rule["label"],
        "secondary_classification_rule": f"secondary_{rule['value']}",
        "secondary_classification_source": source,
        "secondary_classification_reason": reason,
        "secondary_classification_confidence": confidence,
        "needs_secondary_review": confidence != "high",
    }


def _classify_rotation_row(row: pd.Series, config: Mapping[str, Any]):
    primary_category = str(row["pool_category"])
    rules = config["groups"][primary_category]
    index_code = _normalize(row.get("index_code"))
    if index_code:
        for rule in rules:
            configured_codes = {_normalize(code) for code in rule.get("index_codes", [])}
            if index_code in configured_codes:
                return _decision(
                    rule,
                    "tushare.etf_basic.index_code",
                    f"指数代码{row.get('index_code')}命中二级组",
                    "high",
                )

    for field in config["evidence_fields"]:
        value = _evidence_text(row, str(field))
        if not value:
            continue
        for rule in rules:
            keyword = _rule_keyword(value, rule)
            if keyword is None:
                continue
            confidence = "high" if field == "index_name" else "medium"
            return _decision(
                rule,
                f"tushare.etf_basic.{field}",
                f"字段{field}命中二级关键词{keyword}",
                confidence,
            )

    fallback = config["fallbacks"][primary_category]
    return {
        "secondary_category": fallback["value"],
        "secondary_category_name": fallback["label"],
        "secondary_classification_rule": "secondary_fallback",
        "secondary_classification_source": "none",
        "secondary_classification_reason": f"未命中{primary_category}的二级分类规则",
        "secondary_classification_confidence": "low",
        "needs_secondary_review": True,
    }


def _classify_archive_row(row: pd.Series, config: Mapping[str, Any]):
    archive_status = str(row["archive_status"])
    group = config["archive_groups"].get(archive_status)
    if group is None:
        raise ValueError(f"二级分类配置不支持归档状态：{archive_status}")
    return {
        "secondary_category": group["value"],
        "secondary_category_name": group["label"],
        "secondary_classification_rule": "secondary_archive",
        "secondary_classification_source": "archive_status",
        "secondary_classification_reason": f"沿用归档状态{archive_status}",
        "secondary_classification_confidence": "high",
        "needs_secondary_review": False,
    }


def _classify_row(row: pd.Series, config: Mapping[str, Any]):
    if pd.notna(row["pool_category"]):
        return _classify_rotation_row(row, config)
    return _classify_archive_row(row, config)


def _reconcile_same_index(result: pd.DataFrame):
    reconciled = result.copy()
    index_codes = reconciled["index_code"].fillna("").astype(str).str.strip()
    for index_code, indexes in reconciled[index_codes.ne("")].groupby(index_codes).groups.items():
        rotation_indexes = [
            index for index in indexes if pd.notna(reconciled.at[index, "pool_category"])
        ]
        if len(rotation_indexes) < 2:
            continue
        primary_categories = reconciled.loc[rotation_indexes, "pool_category"].dropna().unique()
        if len(primary_categories) != 1:
            continue
        counts = reconciled.loc[rotation_indexes, "secondary_category"].value_counts()
        if len(counts) == 1:
            continue
        normalized_index_code = str(index_code)
        if int(counts.iloc[0]) > int(counts.iloc[1]):
            winner = str(counts.index[0])
            winner_name = str(
                reconciled.loc[
                    reconciled["secondary_category"].eq(winner), "secondary_category_name"
                ].iloc[0]
            )
            mismatched = reconciled.loc[rotation_indexes, "secondary_category"].ne(winner)
            mismatched_indexes = mismatched[mismatched].index
            reconciled.loc[mismatched_indexes, "secondary_category"] = winner
            reconciled.loc[mismatched_indexes, "secondary_category_name"] = winner_name
            reconciled.loc[mismatched_indexes, "secondary_classification_rule"] = (
                "secondary_same_index_consensus"
            )
            reconciled.loc[mismatched_indexes, "secondary_classification_source"] = (
                "tushare.etf_basic.index_code"
            )
            reconciled.loc[mismatched_indexes, "secondary_classification_reason"] = (
                f"同一指数{normalized_index_code}多数产品归入{winner_name}"
            )
            reconciled.loc[mismatched_indexes, "secondary_classification_confidence"] = "medium"
            reconciled.loc[mismatched_indexes, "needs_secondary_review"] = True
            continue

        reconciled.loc[rotation_indexes, "secondary_classification_confidence"] = "low"
        reconciled.loc[rotation_indexes, "needs_secondary_review"] = True
        reconciled.loc[rotation_indexes, "secondary_classification_reason"] = (
            reconciled.loc[rotation_indexes, "secondary_classification_reason"]
            + f"；同一指数{normalized_index_code}二级分类冲突"
        )
    return reconciled


def classify_secondary_etfs(
    classified_etfs: pd.DataFrame,
    config: Mapping[str, Any],
    classified_at: str | None = None,
):
    """在现有一级分类内为每只ETF添加唯一二级分类。"""
    _validate_config(config)
    required = {"ts_code", "pool_category", "archive_status", "index_code"}
    missing = sorted(required.difference(classified_etfs.columns))
    if missing:
        raise ValueError(f"一级分类表缺少字段：{', '.join(missing)}")
    duplicates = classified_etfs["ts_code"].duplicated(keep=False)
    if duplicates.any():
        duplicate_codes = sorted(classified_etfs.loc[duplicates, "ts_code"].astype(str).unique())
        raise ValueError(f"一级分类表存在重复ts_code：{', '.join(duplicate_codes)}")

    decisions = pd.DataFrame(
        [_classify_row(row, config) for _, row in classified_etfs.iterrows()],
        index=classified_etfs.index,
    )
    result = pd.concat([classified_etfs.copy(), decisions], axis=1)
    result = _reconcile_same_index(result)
    result["secondary_classification_version"] = str(config["version"])
    result["secondary_classified_at"] = classified_at or datetime.now(timezone.utc).isoformat()
    if result["secondary_category"].isna().any():
        raise AssertionError("二级分类结果不允许secondary_category为空")
    return result
