# 开发指南

## 初始化环境

```bash
conda env update -n quant -f environment.yml
conda activate quant
python -m etf_pool doctor
```

`environment.yml` 会以 editable 模式安装当前包。也可以在已激活环境运行 `pip install -e ".[dev]"`。

基础环境只包含运行和测试所需依赖。Ruff、Mypy 等可选工具通过 `make install-dev` 安装。

## 配置

从 `.env.example` 创建本地 `.env`。应用读取 `TUSHARE_TOKEN`；筛选参数只放在 `configs/`，密钥和机器路径只放在 `.env`。

## 验证

```bash
pytest
ruff check .
mypy src
```

默认测试不得访问网络或读取真实 Token。外部 API 行为使用伪造客户端或 fixture 验证。

## 新增数据接口

1. 在 `src/etf_pool/data/` 扩展适配器。
2. 在 `docs/data-contracts.md` 定义主键、字段、单位和日期口径。
3. 用伪造客户端测试请求参数与返回字段。
4. 原始响应先落 raw，再由独立步骤生成 interim 表。

## 新增筛选规则

1. 明确规则用途、输入字段、阈值单位和缺失值行为。
2. 将可调整阈值加入 `configs/default.json`。
3. 在 `src/etf_pool/screening/` 实现纯计算逻辑。
4. 增加通过、拒绝、边界值和缺失字段测试。
5. 更新 ETF 池输出契约。
