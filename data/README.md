# 本地数据目录

- `raw/`：不可变的 API 原始快照。
- `interim/`：清洗、统一类型和时点化后的中间数据。
- `processed/`：筛选指标、ETF 池及生成元数据。

当前全量分类实验输出：

- `raw/PROVIDER/etf_basic/as_of_date=YYYY-MM-DD/`：指定六字段的全部上市 ETF 原始快照及抓取元数据。
- `interim/classification/as_of_date=YYYY-MM-DD/version=VERSION/`：六类轮动分类、复核标记和分类统计。
- `interim/secondary_classification/as_of_date=YYYY-MM-DD/primary_version=VERSION/secondary_version=VERSION/`：二级相关暴露分组及统计。

目录内容默认被 Git 忽略。具体主键、字段和落盘规范见 `docs/data-contracts.md`。
