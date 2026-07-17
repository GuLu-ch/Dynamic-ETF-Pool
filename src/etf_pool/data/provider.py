"""兼容Tushare接口的ETF数据源。"""

import importlib
from dataclasses import dataclass
from typing import Any

from etf_pool.config import Settings

SUPPORTED_PROVIDERS = {"tushare", "tnskhdata"}


@dataclass
class TushareETFProvider:
    """官方或代理Tushare兼容SDK的轻量适配器。"""

    client: Any

    @classmethod
    def from_settings(cls, settings: Settings):
        if settings.data_provider not in SUPPORTED_PROVIDERS:
            supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
            raise ValueError(f"不支持数据源{settings.data_provider!r}，可选值：{supported}")
        sdk = importlib.import_module(settings.data_provider)
        client = sdk.pro_api(settings.require_token())
        return cls(client=client)

    def fetch_etf_basic(self, list_status: str = "L"):
        fields = ",".join(
            [
                "ts_code",
                "extname",
                "index_code",
                "index_name",
                "exchange",
                "mgr_name",
            ]
        )
        return self.client.etf_basic(list_status=list_status, fields=fields)

    def fetch_fund_daily(self, ts_code: str, start_date: str, end_date: str):
        return self.client.fund_daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            fields="ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount",
        )
