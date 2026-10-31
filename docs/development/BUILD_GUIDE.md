# 构建与运行指南

仓库根目录就是 Android 工程。它不是网页，也不需要先运行历史 Python 总文件。只想看产品和开发文档时，直接在 GitHub 浏览 [docs](../README.md)。

## 环境

| 项目 | 项目基线 |
|---|---|
| 系统 | Android Studio 支持的 Windows、macOS 或 Linux |
| JDK | 17，Gradle 和 Kotlin 编译工具链均使用17 |
| Gradle | 使用仓库 Wrapper 9.4.1，不需要另装全局Gradle |
| AGP / Kotlin / KSP | 9.2.1 / 2.2.10 / 2.3.10，已在 version catalog 固定 |
| Android SDK | compile/target37；按 AGP 提示安装配套 Build Tools |
| 设备 | Android8.0/API26或更高；真机需开启开发者选项及USB调试 |

Android Studio 的 Gradle JDK 不是普通代码编辑器的运行 JDK。即使电脑装有其他 JDK，也请显式选17。SDK 许可由使用者自行阅读和确认；脚本不自动接受。

## Android Studio

1. Clone 仓库，或下载完整工程 ZIP 后解压到普通目录。
2. Open → 选择包含 `settings.gradle.kts` 的根目录，不要只打开 `app/`。
3. Settings → Build Tools → Gradle，将 Gradle JDK 设为17；使用项目 Wrapper。
4. SDK Manager 安装 API37 平台与配套工具，完成许可确认。
5. Sync Project。首次需要从 Google Maven/Maven Central 下载依赖；运行时不需要服务器。
6. 选择 `app` 配置和设备，运行。没有设备时先通过 Device Manager 创建模拟器。

## 命令行

配置好 `JAVA_HOME`、`ANDROID_HOME`（或 `ANDROID_SDK_ROOT`），或由 Android Studio 生成本机 `local.properties`。不要把这些本机路径提交到Git。

```bash
java -version
./gradlew --version
python3 tools/check_android_sdk.py
./gradlew :core:test --no-daemon
./gradlew :app:testDebugUnitTest :app:lintDebug :app:assembleDebug --no-daemon
./gradlew :app:connectedDebugAndroidTest --no-daemon
```

Windows PowerShell 把 `./gradlew` 换成 `.\gradlew.bat`。构建成功后 Debug APK 在 `app/build/outputs/apk/debug/app-debug.apk`；单测报告通常在模块 `build/reports/tests/`，lint在 `app/build/reports/`。已连接设备可运行 `./gradlew :app:installDebug`。

## 还没有 Android SDK 时

```bash
python3 tools/verify_delivery.py
python3 tools/verify_repository.py
```

这两项只验证源码/文档/SQLite，不会生成APK。安装 Kotlin2.2.10 CLI 和JDK17+后，也可运行 `sh tools/host_test.sh`，执行85项纯JVM测试；该脚本首次下载小型Maven测试依赖，不安装Android SDK。推荐后续使用Gradle统一执行。

## GitHub Actions

`.github/workflows/verify.yml` 包含仓库检查、核心单测和Android构建。它使用官方Actions固定提交和只读仓库权限，不包含发布、签名、服务部署或业务云资源。

Android任务先检查runner已有SDK37；缺失时明确失败，不通过“跳过构建但显示成功”掩盖，也不运行自动接受SDK许可的命令。工作流运行与否、成功与否，以对应提交的Actions结果为准。即使Debug构建通过，设备仪器化和真机提醒仍须单独验收。

## 常见问题

| 提示 | 处理 |
|---|---|
| 找不到JDK17/toolchain | 安装或在Studio配置JDK17，检查Gradle JDK而非只检查PATH |
| SDK location not found | 在Studio配置SDK目录；本机local.properties不进Git |
| android-37不存在 | 安装API37；不要随意降低compileSdk掩盖依赖要求 |
| Permission denied: gradlew | `chmod +x gradlew`；Windows使用bat |
| Google Maven/Gradle下载失败 | 检查网络/企业代理；不把令牌或代理密码提交到版本库 |
| kotlin.sourceSets兼容报错 | 确认KSP仍为2.3.10；不要退回旧2.2.10-2.0.2或关闭守卫 |
| 设备没有提醒 | 先检查通知/精准闹钟权限、省电、强停和规则时间；参考测试计划，不能仅凭保存成功判断系统已准点安排 |

源码提交不包含release签名配置。正式发布需要单独完成密钥管理、签名、隐私审查和[发布清单](../testing/RELEASE_CHECKLIST.md)。
