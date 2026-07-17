import pandas as pd
import pytest

from etf_pool.screening.rules import ScreeningCriteria, apply_eligibility_rules


@pytest.fixture
def criteria() -> ScreeningCriteria:
    return ScreeningCriteria(
        min_listing_days=120,
        min_history_days=120,
        min_avg_amount_20d=20_000_000,
    )


def test_rules_keep_auditable_rejection_reasons(criteria: ScreeningCriteria) -> None:
    metrics = pd.DataFrame(
        {
            "ts_code": ["510300.SH", "159001.SZ"],
            "listing_days": [500, 20],
            "history_days": [500, 20],
            "avg_amount_20d": [100_000_000, 1_000_000],
        }
    )

    result = apply_eligibility_rules(metrics, criteria)

    assert result["eligible"].tolist() == [True, False]
    assert result.loc[0, "exclusion_reason"] == ""
    assert result.loc[1, "exclusion_reason"] == "listing_history,price_history,liquidity"


def test_rules_reject_missing_columns(criteria: ScreeningCriteria) -> None:
    with pytest.raises(ValueError, match="avg_amount_20d"):
        apply_eligibility_rules(pd.DataFrame({"listing_days": [], "history_days": []}), criteria)
