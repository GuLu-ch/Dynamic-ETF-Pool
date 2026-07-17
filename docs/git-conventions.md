# Git 提交规范

## 格式

```text
type(scope): subject

optional body

optional footer
```

- `type` 必填，使用下表中的固定值。
- `scope` 可选，使用小写英文，表示主要影响模块。
- `subject` 必填，使用简洁中文说明实际完成的动作和对象，描述部分至少 6 个字符。
- 首行最多 72 个字符，末尾不加句号，不使用全大写。
- 禁止使用“更新文件”“修复问题”“其他修改”“临时修改”“调整代码”等模糊描述。
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
feat(screening): 增加流动性准入规则
fix(data): 拒绝重复的ETF日行情记录
data(tushare): 增加ETF基础信息快照字段
docs: 明确ETF池输出数据契约
test(screening): 覆盖流动性字段缺失场景
chore(git): 统一提交说明格式
```

## 本地启用

```bash
make git-setup
```

该命令配置 `.gitmessage` 为提交模板，并启用 `.githooks/commit-msg` 校验。钩子检查标题格式、长度、描述清晰度和 breaking change 页脚；合并提交与 Git 自动生成的撤销提交不受限制。
