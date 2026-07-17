# Dynamic ETF Pool

一个专注于 ETF 池构建的研究项目。系统从 Tushare 获取 ETF 数据，依据上市状态、数据完整性、流动性等客观条件筛选标的，最终输出可追溯的 ETF 池快照。

## 项目范围

本项目负责：

- 获取并整理 ETF 基础信息和日行情。
- 检查数据完整性、重复键、日期和字段质量。
- 按配置执行 ETF 准入筛选。
- 对跟踪同一指数的 ETF 做识别和去重。
- 输出包含入池状态、排除原因、数据截止日和配置版本的 ETF 池。

本项目不负责交易信号、仓位管理、组合优化、收益评估或交易执行。

## 快速开始

项目使用本机 Conda 环境 `quant` 和 Python 3.10。

```bash
conda env update -n quant -f environment.yml
conda activate quant

# 仅在本地尚无 .env 时执行
cp .env.example .env
# 编辑 .env，填写 TUSHARE_TOKEN

python -m etf_pool doctor
pytest
```

`.env` 与 `.env.example` 使用相同变量名，其中真实 Token 不得提交到 Git。

## 目录结构

```text
.
├── configs/               # ETF 池筛选参数，不含密钥
├── data/
│   ├── raw/               # Tushare 原始快照
│   ├── interim/           # 清洗后的中间表
│   └── processed/         # ETF 池及其生成明细
├── docs/                  # 架构、数据契约、构建流程和路线图
├── src/etf_pool/
│   ├── data/              # Tushare 适配和本地存储
│   └── screening/         # ETF 准入与排除原因
└── tests/                 # 单元测试
```

## 默认筛选配置

`configs/default.json` 是合法的纯 JSON，不放注释。当前参数含义如下：

| 参数 | 含义 |
| --- | --- |
| `universe.exchanges` | 纳入的交易所，`SH` 为上交所、`SZ` 为深交所 |
| `universe.list_status` | Tushare 上市状态，`L` 表示上市 |
| `universe.include_qdii` | 是否允许 QDII ETF 进入初始集合 |
| `screening.min_listing_days` | 最少上市自然日数 |
| `screening.min_history_days` | 最少有效日行情条数 |
| `screening.min_avg_amount_20d` | 最近 20 个交易日日均成交额下限，单位为元 |

这些数值是初始筛选口径，可以根据 ETF 池的用途调整，但每次输出必须记录实际使用的配置。生成表默认使用 UTF-8 CSV，避免引入额外二进制存储依赖。

## 常用命令

```bash
python -m etf_pool doctor
python -m etf_pool show-config
pytest
ruff check .
mypy src
```

`pytest` 随基础环境安装；Ruff 和 Mypy 属于可选开发工具，先运行 `make install-dev` 再使用。

## 数据源

默认使用官方 `tushare` SDK。仓库内的 [ETF 接口参考](docs/reference/Tushare文档-ETF专题.md) 记录了相关接口；[代理说明](docs/reference/Tushare代理说明.md) 中的 `tnskhdata` 可通过 `ETF_DATA_PROVIDER=tnskhdata` 切换，但不是默认依赖。

## Git

远程仓库：<https://github.com/GuLu-ch/Dynamic-ETF-Pool.git>

首次克隆后运行 `make git-setup`，启用统一的提交模板与格式检查。提交采用 `type(scope): subject` 格式，完整规则见 [Git 提交规范](docs/git-conventions.md)。

本地数据、生成结果和 `.env` 均被忽略。提交前至少运行 `pytest`，并用 `git status --ignored` 确认密钥与数据没有进入待提交文件。
