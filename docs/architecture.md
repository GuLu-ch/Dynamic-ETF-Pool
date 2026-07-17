# 系统架构

## 数据流

```text
Tushare API
    -> data provider
    -> raw snapshots
    -> validation and normalization
    -> interim ETF tables
    -> ETF classification and review list
    -> eligibility metrics
    -> screening and index deduplication
    -> processed ETF pool snapshot
```

## 模块职责

| 模块 | 职责 | 不应承担 |
| --- | --- | --- |
| `data` | API 适配、快照同步、字段规范化、数据校验、CSV 落盘 | 决定 ETF 是否入池 |
| `screening` | ETF 分类、准入条件、排除原因、同指数识别与池生成 | 网络访问或修改原始数据 |
| `cli` | 参数解析、调用应用服务、返回运行状态 | 内嵌筛选细节 |

依赖方向为 `cli -> screening -> data models`。外部 SDK 只允许出现在 `data` 层；筛选代码接受 DataFrame 或明确的数据模型。

## 配置边界

- `configs/default.json`：进入 Git 的 ETF 范围和筛选参数。
- `configs/classification.json`：进入 Git 的分类词表、规则顺序和分类版本。
- `configs/secondary-classification.json`：进入 Git 的二级相关暴露分组及其版本。
- `.env`：Token、数据源和本机路径，只存在本地。
- 命令行参数：单次运行的数据截止日、输入和输出路径。

## 设计原则

- 原始数据不可变，清洗表和 ETF 池可从原始数据重建。
- 每张表都有主键、字段类型、日期口径和质量检查。
- 所有入池与排除结果都可解释。
- 生成结果同时保存输入数据版本和筛选配置。
