"""Transparent baseline eligibility rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd


@dataclass(frozen=True)
class ScreeningCriteria:
    min_listing_days: int
    min_history_days: int
    min_avg_amount_20d: float

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> ScreeningCriteria:
        values = config["screening"]
        return cls(
            min_listing_days=int(values["min_listing_days"]),
            min_history_days=int(values["min_history_days"]),
            min_avg_amount_20d=float(values["min_avg_amount_20d"]),
        )


def apply_eligibility_rules(
    metrics: pd.DataFrame, criteria: ScreeningCriteria
) -> pd.DataFrame:
    """Annotate a metrics table with eligibility and auditable rejection reasons."""
    required = {"listing_days", "history_days", "avg_amount_20d"}
    missing = sorted(required.difference(metrics.columns))
    if missing:
        raise ValueError(f"Missing screening columns: {', '.join(missing)}")

    checks = {
        "listing_history": metrics["listing_days"].ge(criteria.min_listing_days),
        "price_history": metrics["history_days"].ge(criteria.min_history_days),
        "liquidity": metrics["avg_amount_20d"].ge(criteria.min_avg_amount_20d),
    }
    result = metrics.copy()
    result["eligible"] = pd.concat(checks, axis=1).all(axis=1)
    result["exclusion_reason"] = [
        ",".join(name for name, mask in checks.items() if not bool(mask.loc[index]))
        for index in result.index
    ]
    return result
