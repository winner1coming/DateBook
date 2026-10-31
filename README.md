# DateBook 重要的日子

原生 Android 倒数日、纪念日与目标记录应用。Kotlin + Jetpack Compose + Room，业务资料保存在手机本地，无账号、云数据库或应用网络权限。

这是可直接被 Android Studio 导入的标准工程，不再需要先运行 Python 还原源码。**工程结构可直接使用，不代表完整 APK 构建、真机验收或所有 PRD 条目已经通过。** 请先看[实现状态与已知差异](docs/development/IMPLEMENTATION_STATUS.md)。

## 开始运行

```bash
git clone https://github.com/winner1coming/DateBook.git
cd DateBook
```

Android Studio 选择 Open，打开仓库根目录；配置 **JDK 17** 和 **Android SDK 37**，完成 Gradle Sync，选择 API 26 或以上的设备运行 `app`。只阅读源码或文档不需要安装 Android Studio。首次下载构建依赖需要联网，应用本身离线工作。

```bash
# macOS / Linux
./gradlew :core:test
./gradlew :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
./gradlew :app:connectedDebugAndroidTest

# Windows PowerShell 使用 .\gradlew.bat 对应命令
```

完整操作及常见问题见[构建运行指南](docs/development/BUILD_GUIDE.md)。Debug APK 构建成功后位于 `app/build/outputs/apk/debug/app-debug.apk`；仓库不包含已经构建好的 APK 或签名密钥。

## 工程目录

```text
DateBook/
├── app/                       Android 入口、页面、数据库与系统集成
│   ├── src/main/kotlin/cn/datebook/app/
│   │   ├── data/              Room、事务、媒体与资料库代次
│   │   ├── platform/          提醒、组件、日历、分享、应用锁
│   │   └── ui/                Compose、导航、状态与草稿
│   ├── src/main/res/          Android 资源
│   ├── src/test/              农历黄金样例 JVM 测试
│   ├── src/androidTest/       数据库与页面仪器化测试
│   └── schemas/               Room 实际导出的规范化表结构
├── core/                      纯 Kotlin 日期、业务规则与文件协议
│   └── src/test/              核心和文件协议 JVM 测试
├── docs/                      产品、技术、开发、测试与原型文档
├── gradle/                    Wrapper 和固定依赖版本
├── tools/                     源码、数据库、文档与 SDK 检查工具
├── .github/workflows/         自动检查与 Android 构建入口
├── archive/                   上一版单文件快照，仅用于历史对照
├── plan/                      初次实现计划的历史记录
├── CONTRIBUTING.md            开发约定与验证要求
└── gradlew / gradlew.bat       项目构建入口
```

以后修改业务代码直接编辑 `app/` 和 `core/`；不要修改历史快照再重新覆盖工程。

## 文档入口

| 想了解的内容 | 入口 |
|---|---|
| 全部文档 | [文档导航](docs/README.md) |
| 产品定位、范围和规则 | [PRD](docs/product/PRD.md) · [详细需求](docs/product/REQUIREMENTS.md) |
| 原始产品/技术 Word 文档 | [文档原件](docs/source/README.md) |
| 技术设计和当前代码职责 | [TD](docs/technical/TD.md) · [当前架构](docs/technical/ARCHITECTURE.md) |
| 方法与文件契约 | [实施契约](docs/technical/IMPLEMENTATION_CONTRACT.md) · [错误码](docs/technical/ERROR_CODES.md) · [文件 schema](docs/contracts/file_contracts_v1.schema.json) |
| 环境搭建和开发顺序 | [构建指南](docs/development/BUILD_GUIDE.md) · [开发计划](docs/development/DEVELOPMENT_PLAN.md) |
| 测试与发布门禁 | [测试计划](docs/testing/TEST_PLAN.md) · [测试报告](docs/testing/TEST_REPORT.md) · [发布清单](docs/testing/RELEASE_CHECKLIST.md) |
| 原型与数据库设计 | [页面原型说明](docs/design/README.md) · [数据库说明](docs/database/README.md) |
| 技术选型变更 | [架构决策 ADR](docs/decisions/ADR.md) |

## 测试状态

现有主机验证基线：85 项 JVM 测试（核心49、文件24、真实农历12）通过；Android API 源码编译、真实 Room/KSP 生成及35项仪器化测试的**代码编译**通过。35项仪器化测试没有在设备上执行；完整 APK/合并 Manifest/DEX/R8、真机提醒、组件及性能验收仍待完成。

```bash
# 不需要 Android SDK 的源码/SQLite与仓库检查
python3 tools/verify_delivery.py
python3 tools/verify_repository.py
```

GitHub Actions 配置在 `.github/workflows/verify.yml`：源文件检查、核心 Gradle 单测、Android 构建分别报告。配置文件存在不等于 CI 已运行或通过；Android 构建要求 runner 已安装并获授权使用 SDK37，工作流不自动接受 SDK 许可。

## 数据与安全边界

- 不做登录、云端恢复或在线共同编辑；换手机需要手动导出和导入完整备份。
- 最多三级手动事件；详情只列直属子事件；每级独立背景及一段寄语。
- 应用锁是访问锁，不是数据库加密；完整备份若密码留空即为明文。
- 本地提醒受系统权限、省电与强制停止影响，不承诺必达；日历由用户明确操作后复制。
- PRD 是目标需求，不是实现证明。未实现与尚未验收的内容在实现状态文档中分别标记。

第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。历史总文件保存在 [archive](archive/README.md)，原始 Git 提交历史保留，不需要再次解包才能开发。
