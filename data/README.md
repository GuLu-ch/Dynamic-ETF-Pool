# 本地数据目录

- `raw/`：不可变的 API 原始快照。
- `interim/`：清洗、统一类型和时点化后的中间数据。
- `processed/`：筛选指标、ETF 池及生成元数据。

目录内容默认被 Git 忽略。具体主键、字段和落盘规范见 `docs/data-contracts.md`。
