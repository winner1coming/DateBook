# DateBook 文档导航

本目录将产品目标、设计基线、实际代码状态和测试证据分开保存。原有 Word 文件原样保留；Markdown 阅读版便于在 GitHub 上查看与评审。后续变更应同步维护对应文档，而不是修改历史总文件。

| 分类 | 文件与用途 |
|---|---|
| 产品 | [PRD](product/PRD.md)：定位与范围；[详细需求](product/REQUIREMENTS.md)：交互与验收规则 |
| 技术 | [TD](technical/TD.md)：原始技术设计；[当前架构](technical/ARCHITECTURE.md)：源码职责与入口 |
| 接口 | [实施契约](technical/IMPLEMENTATION_CONTRACT.md)；[错误码](technical/ERROR_CODES.md)；[JSON schema](contracts/file_contracts_v1.schema.json) |
| 开发 | [开发计划](development/DEVELOPMENT_PLAN.md)；[构建指南](development/BUILD_GUIDE.md)；[实现状态](development/IMPLEMENTATION_STATUS.md) |
| 测试 | [测试计划](testing/TEST_PLAN.md)；[测试报告](testing/TEST_REPORT.md)；[发布清单](testing/RELEASE_CHECKLIST.md) |
| 设计 | [原型入口及注意事项](design/README.md)，HTML 原型可下载后在浏览器打开 |
| 数据库 | [设计与实际 Schema 的关系](database/README.md)；实际 Room schema 在 [app/schemas](../app/schemas/) |
| 决策 | [ADR](decisions/ADR.md)：两模块、手动依赖注入、KSP兼容性等实际调整 |
| 原件 | [PRD、需求、TD Word 原件](source/README.md) |

## 阅读顺序

产品同学先看 PRD → 详细需求 → 实现状态；开发先看构建指南 → 当前架构 → 实施契约 → TD / ADR；测试先看实现状态 → 测试计划 → 测试报告 → 发布清单。

“已实现”“主机验证通过”“正式 Android 构建通过”“真机验收通过”是不同状态。若设计与代码不一致，先记录差异并确认，不把代码现状静默改写成产品已同意的新需求。详情层级以最新确认的“只列直属下一级”规则为准。
