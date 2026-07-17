# 数据契约

## 目录分层

| 路径 | 内容 | Git |
| --- | --- | --- |
| `data/raw/` | 按接口和抓取日期保存的原始快照 | 忽略 |
| `data/interim/` | 清洗、统一类型后的 ETF 表 | 忽略 |
| `data/processed/` | ETF 池快照及生成明细 | 忽略 |

表格默认使用 UTF-8 CSV，运行元数据使用 JSON。Tushare 的 `YYYYMMDD` 日期在进入 interim 层时转换为 ISO `YYYY-MM-DD` 字符串。

## ETF 基础表

- 建议路径：`raw/tushare/etf_basic/as_of_date=YYYY-MM-DD/part.csv`
- 自然键：快照内 `ts_code`
- 必需字段：`ts_code`, `list_date`, `list_status`, `exchange`, `index_code`, `mgr_name`, `etf_type`
- 元数据：`source`, `fetched_at`, `as_of_date`, `schema_version`

每次抓取保存独立快照，不用新的上市列表覆盖旧快照。

## ETF 日行情表

- 建议路径：`raw/tushare/fund_daily/year=YYYY/month=MM/part.csv`
- 自然键：`(ts_code, trade_date)`
- 必需字段：`open`, `high`, `low`, `close`, `pre_close`, `vol`, `amount`
- 单位：以 Tushare 接口定义为准，并在落盘元数据中固定。

写入前检查键唯一、日期合法、OHLC 关系合法、成交量与成交额非负。无成交和缺失行情必须显式保留或标记。

## ETF 筛选指标表

- 自然键：`(as_of_date, ts_code)`
- 必需字段：`listing_days`, `history_days`, `avg_amount_20d`
- 可扩展字段：基金规模、管理费率、份额、数据缺失率和跟踪指数分类。
- 指标字段名或元数据必须明确窗口、单位及缺失值处理。

## ETF 池快照

- 建议路径：`processed/pools/as_of_date=YYYY-MM-DD/pool.csv`
- 自然键：`(as_of_date, ts_code)`
- 必需字段：`eligible`, `exclusion_reason`, `selected`, `index_code`, `config_hash`, `data_cutoff`

配套的 `metadata.json` 记录代码版本、完整配置、生成时间、输入数据快照和警告。池快照只表达标的集合，不包含仓位或交易指令。
