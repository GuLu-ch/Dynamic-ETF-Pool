"""按轮动研究口径对ETF进行可审计分类。"""

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

import pandas as pd

CONFIDENCE_VALUES = {"high", "medium", "low"}


def _normalize(value: Any):
    if value is None or pd.isna(value):
        return ""
    return "".join(str(value).upper().split())


def _validate_config(config: Mapping[str, Any]):
    required = {"version", "categories", "archive_statuses", "text_fields", "rules"}
    missing = sorted(required.difference(config))
    if missing:
        raise ValueError(f"分类配置缺少字段：{', '.join(missing)}")

    categories = set(config["categories"])
    archive_statuses = set(config["archive_statuses"])
    for rule in config["rules"]:
        target = rule.get("target")
        value = rule.get("value")
        if target == "pool_category" and value not in categories:
            raise ValueError(f"分类规则{rule.get('rule_id')!r}使用未知类别：{value}")
        if target == "archive_status" and value not in archive_statuses:
            raise ValueError(f"分类规则{rule.get('rule_id')!r}使用未知归档状态：{value}")
        if target not in {"pool_category", "archive_status"}:
            raise ValueError(f"分类规则{rule.get('rule_id')!r}的target无效：{target}")
        if rule.get("confidence") not in CONFIDENCE_VALUES:
            raise ValueError(f"分类规则{rule.get('rule_id')!r}的confidence无效")


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


def _match_rule(value: str, rule: Mapping[str, Any]):
    excluded = [_normalize(keyword) for keyword in rule.get("exclude_keywords", [])]
    if any(keyword and keyword in value for keyword in excluded):
        return None

    for keyword in rule["keywords"]:
        normalized_keyword = _normalize(keyword)
        if normalized_keyword and normalized_keyword in value:
            return str(keyword)
    return None


def _classify_row(row: pd.Series, config: Mapping[str, Any]):
    evidence_confidence = config.get("evidence_confidence", {})
    for field in config["text_fields"]:
        value = _evidence_text(row, str(field))
        if not value:
            continue
        for rule in config["rules"]:
            keyword = _match_rule(value, rule)
            if keyword is None:
                continue
            confidence = evidence_confidence.get(field, rule["confidence"])
            pool_category = rule["value"] if rule["target"] == "pool_category" else pd.NA
            archive_status = rule["value"] if rule["target"] == "archive_status" else pd.NA
            return {
                "pool_category": pool_category,
                "archive_status": archive_status,
                "classification_rule": rule["rule_id"],
                "classification_source": f"tushare.etf_basic.{field}",
                "classification_reason": f"字段{field}命中关键词{keyword}",
                "matched_keyword": keyword,
                "classification_confidence": confidence,
                "needs_review": confidence != "high",
            }

    return {
        "pool_category": pd.NA,
        "archive_status": "unknown",
        "classification_rule": "unclassified",
        "classification_source": "none",
        "classification_reason": "未命中已配置分类规则",
        "matched_keyword": pd.NA,
        "classification_confidence": "low",
        "needs_review": True,
    }


def _propagate_same_index(result: pd.DataFrame):
    if "index_code" not in result.columns:
        return result

    propagated = result.copy()
    index_codes = propagated["index_code"].fillna("").astype(str).str.strip()
    for index_code, indexes in propagated[index_codes.ne("")].groupby(index_codes).groups.items():
        normalized_index_code = str(index_code)
        category_counts = propagated.loc[indexes, "pool_category"].dropna().value_counts()
        categories = category_counts.index.tolist()
        if len(categories) > 1 and int(category_counts.iloc[0]) > int(category_counts.iloc[1]):
            winner = categories[0]
            mismatched = propagated.loc[indexes, "pool_category"].ne(winner)
            mismatched_indexes = mismatched[mismatched].index
            propagated.loc[mismatched_indexes, "pool_category"] = winner
            propagated.loc[mismatched_indexes, "classification_rule"] = "same_index_consensus"
            propagated.loc[mismatched_indexes, "classification_source"] = (
                "tushare.etf_basic.index_code"
            )
            propagated.loc[mismatched_indexes, "classification_reason"] = (
                f"同一指数{normalized_index_code}多数产品归类为{winner}"
            )
            propagated.loc[mismatched_indexes, "matched_keyword"] = normalized_index_code
            propagated.loc[mismatched_indexes, "classification_confidence"] = "medium"
            propagated.loc[mismatched_indexes, "needs_review"] = True
            categories = [winner]
        elif len(categories) > 1:
            propagated.loc[indexes, "classification_confidence"] = "low"
            propagated.loc[indexes, "needs_review"] = True
            propagated.loc[indexes, "classification_reason"] = (
                propagated.loc[indexes, "classification_reason"]
                + f"；同一指数{normalized_index_code}分类冲突"
            )
            continue
        if len(categories) != 1:
            continue

        unknown = propagated.loc[indexes, "archive_status"].eq("unknown")
        unknown_indexes = unknown[unknown].index
        if unknown_indexes.empty:
            continue
        propagated.loc[unknown_indexes, "pool_category"] = categories[0]
        propagated.loc[unknown_indexes, "archive_status"] = pd.NA
        propagated.loc[unknown_indexes, "classification_rule"] = "same_index_propagation"
        propagated.loc[unknown_indexes, "classification_source"] = "tushare.etf_basic.index_code"
        propagated.loc[unknown_indexes, "classification_reason"] = (
            f"同一指数{normalized_index_code}已有唯一分类"
        )
        propagated.loc[unknown_indexes, "matched_keyword"] = normalized_index_code
        propagated.loc[unknown_indexes, "classification_confidence"] = "medium"
        propagated.loc[unknown_indexes, "needs_review"] = True
    return propagated


def classify_etfs(
    etfs: pd.DataFrame,
    config: Mapping[str, Any],
    classified_at: str | None = None,
):
    """为每只ETF添加唯一轮动类别或非轮动归档状态。"""
    _validate_config(config)
    if "ts_code" not in etfs.columns:
        raise ValueError("ETF基础表缺少字段：ts_code")
    duplicates = etfs["ts_code"].duplicated(keep=False)
    if duplicates.any():
        duplicate_codes = sorted(etfs.loc[duplicates, "ts_code"].astype(str).unique())
        raise ValueError(f"ETF基础表存在重复ts_code：{', '.join(duplicate_codes)}")

    decisions = pd.DataFrame(
        [_classify_row(row, config) for _, row in etfs.iterrows()],
        index=etfs.index,
    )
    result = pd.concat([etfs.copy(), decisions], axis=1)
    result = _propagate_same_index(result)
    result["classification_version"] = str(config["version"])
    result["classified_at"] = classified_at or datetime.now(timezone.utc).isoformat()

    both_set = result["pool_category"].notna() & result["archive_status"].notna()
    neither_set = result["pool_category"].isna() & result["archive_status"].isna()
    if both_set.any() or neither_set.any():
        raise AssertionError("分类结果必须且只能填写pool_category或archive_status之一")
    return result
