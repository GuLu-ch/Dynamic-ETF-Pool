"""Tushare-compatible ETF data provider."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

import pandas as pd

from etf_pool.config import Settings

SUPPORTED_PROVIDERS = {"tushare", "tnskhdata"}


@dataclass
class TushareETFProvider:
    """Thin adapter around the official or proxy Tushare-compatible SDK."""

    client: Any

    @classmethod
    def from_settings(cls, settings: Settings) -> TushareETFProvider:
        if settings.data_provider not in SUPPORTED_PROVIDERS:
            supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
            raise ValueError(f"Unsupported provider {settings.data_provider!r}; choose {supported}")
        sdk = importlib.import_module(settings.data_provider)
        client = sdk.pro_api(settings.require_token())
        return cls(client=client)

    def fetch_etf_basic(self, list_status: str = "L") -> pd.DataFrame:
        fields = ",".join(
            [
                "ts_code",
                "csname",
                "extname",
                "cname",
                "index_code",
                "index_name",
                "setup_date",
                "list_date",
                "list_status",
                "exchange",
                "mgr_name",
                "mgt_fee",
                "etf_type",
            ]
        )
        return self.client.etf_basic(list_status=list_status, fields=fields)

    def fetch_fund_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        return self.client.fund_daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            fields="ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount",
        )
