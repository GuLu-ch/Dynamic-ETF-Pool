import pandas as pd

from etf_pool.data.provider import TushareETFProvider


class FakeClient:
    def __init__(self):
        self.kwargs = {}

    def etf_basic(self, **kwargs):
        self.kwargs = kwargs
        return pd.DataFrame()


def test_fetch_etf_basic_uses_requested_full_market_fields():
    client = FakeClient()
    provider = TushareETFProvider(client=client)

    provider.fetch_etf_basic()

    assert client.kwargs == {
        "list_status": "L",
        "fields": "ts_code,extname,index_code,index_name,exchange,mgr_name",
    }
