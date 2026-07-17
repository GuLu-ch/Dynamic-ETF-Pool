# Git 提交规范

## 格式

```text
type(scope): subject

optional body

optional footer
```

- `type` 必填，使用下表中的固定值。
- `scope` 可选，使用小写英文，表示主要影响模块。
- `subject` 必填，简洁说明本次变更，首行最多 72 个字符，末尾不加句号。
- 正文用于解释变更原因、约束或迁移方式，不重复文件清单。
- 不兼容变更在类型或 scope 后加 `!`，并在页脚写 `BREAKING CHANGE: ...`。

## 类型

| Type | 用途 |
| --- | --- |
| `feat` | 新增 ETF 池能力 |
| `fix` | 修复缺陷 |
| `data` | 数据源、字段、schema 或质量规则变更 |
| `docs` | 仅文档变更 |
| `test` | 仅测试变更 |
| `refactor` | 不改变行为的内部重构 |
| `perf` | 性能改进 |
| `build` | 依赖、构建或打包变更 |
| `ci` | CI/CD 配置变更 |
| `chore` | 仓库维护 |
| `revert` | 撤销已有提交 |

常用 scope：`data`、`tushare`、`screening`、`config`、`cli`、`docs`、`git`。

## 示例

```text
feat(screening): add liquidity eligibility rule
fix(data): reject duplicate ETF daily rows
data(tushare): add ETF basic snapshot fields
docs: clarify ETF pool output contract
test(screening): cover missing liquidity values
chore(git): standardize commit message format
```

## 本地启用

```bash
make git-setup
```

该命令配置 `.gitmessage` 为提交模板，并启用 `.githooks/commit-msg` 校验。钩子只检查提交首行格式和长度；合并提交与 Git 自动生成的撤销提交不受限制。
