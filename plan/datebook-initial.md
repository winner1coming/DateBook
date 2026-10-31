# Human Review Plan v2: DateBook Android 完整实现与测试

> 历史计划：本文件记录首次单文件源码交付的任务与当时约束。2026-11-01 已改为正常工程目录，后续以 [开发与验收计划](../docs/development/DEVELOPMENT_PLAN.md) 和 [实现状态](../docs/development/IMPLEMENTATION_STATUS.md) 为准；T007 的单文件发布方式不再是当前交付要求。任务存在不等于功能已验收。

## Plan Metadata

| Field | Value |
| --- | --- |
| Plan Format Version | 2 |
| Branch | main |
| Safe Branch | datebook-initial |
| Stack | android |
| Target Unit | - |
| Target Package | - |
| Field Naming Policy | local |
| Spec Language | zh |
| Review Level | HIGH |
| Plan File | plan/datebook-initial.md |
| PRD Link | - |

---

## 需求总结

1. 无账号无服务器，所有业务本机保存；App首次离线可用。
2. 本、标签、首页排序与固定、三层手动事件、每级独立背景和单段寄语；只显示直属下一级。
3. 生日年度、正倒数、公农历、重复与提醒、目标阶段和行动记录。
4. 文本独立副本/图片卡片、加密全备份与合并替换、可恢复错误和权限降级。
5. 桌面组件、日历复制和选择导入、搜索/批量/归档回收站/应用锁/日期工具、无障碍与主题。
6. 先规划再实现，不中途等待；最终一个源码总文件并交付指定GitHub仓库。

---

## 技术实施方案

原生Kotlin/Compose/Room，core/app两模块按包隔离；构造器注入，固定离线农历包；单进程Mutex代次门、事务/outbox与持久通知票据、逻辑文件协议与AtomicFile切库。所有可测试业务和文件放纯JVM。计划含HIGH风险，但用户已授权连续推进；不把待实测结果记为通过。

| 方案点 | 依据 | 实现方式 | 对应任务 |
| --- | --- | --- | --- |
| 工程与共享类型 | - | 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权；本机无账号无网络；SDK及固定依赖完整；共享字段与TD一致；Release Manifest不包含网络权限；应用从私有noBackup目录读取 | T001 |
| 日期与业务用例 | - | 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权；生日跨日/重复/DST/农历边界；树最多三层且只查直属；所有CRUD和状态按TD执行；目标行动、标签批量、移动复制、原因集归档回收站、容量与错误原子性；不以TODO替代 | T002 |
| Room与安全切库 | - | 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权；规范化表和基础约束、触发器、版本与幂等、outbox、资产租约；无单JSON表降级；候选库校验和原子指针切换；并发revision变化拒绝提交；失败保留原库 | T003 |
| 文件与系统能力 | - | 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权；完整JSON/CSV/备份容器，AES-GCM认证、有界解包、引用语义校验与导入去重；通知票据防崩溃丢失、权限降级、组件、日历、背景与长图卡片、锁、长任务持久登记 | T004 |
| Compose页面与完整接线 | - | 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权；首页/本/搜索/日历/事件/目标/创建编辑/行动/分享/备份/导入/诊断/组件/回收站/锁/工具可进入；一级只列二级、二级只列三级、三级禁增；真实用例接线，不用演示toast代替保存 | T005 |
| 综合测试和还原说明 | - | 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权；需求到测试逐项追踪；执行可用编译/单测/静态校验；保留失败证据与未测项；SDK/设备测试、性能、恶意文件、恢复杀进程、无障碍有具体操作与判定；完整还原指南 | T006 |
| 单文件封装与仓库交付 | - | 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权；一个明文可读总文件包含计划/目录/源码/资源/测试/报告；逐文件SHA256可验；还原默认拒绝覆盖、禁止路径穿越；只上传最终总文件到用户指定仓库，不含凭据/本机路径/临时产物 | T007 |

---

## 影响范围

| Dimension | Details |
| --- | --- |
| New code files | `core/src/main/kotlin/cn/datebook/core/Models.kt`, `settings.gradle.kts`, `build.gradle.kts`, `gradle.properties`, `gradle/libs.versions.toml`, `core/build.gradle.kts`, `app/build.gradle.kts`, `app/src/main/AndroidManifest.xml`, `app/src/main/res/values/strings.xml`, `app/src/main/res/values/themes.xml`, `app/src/main/res/xml/backup_rules.xml`, `app/src/main/res/xml/data_extraction_rules.xml`, `app/src/main/res/xml/file_paths.xml`, `app/src/main/res/xml/widget_info.xml`, `app/src/main/res/drawable/ic_datebook.xml`, `docs/IMPLEMENTATION_CONTRACT.md`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt`, `core/src/test/kotlin/cn/datebook/core/CoreTests.kt`, `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `app/src/main/kotlin/cn/datebook/app/data/Entities.kt`, `app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt`, `app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt`, `core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt`, `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt`, `app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt`, `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt`, `app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt`, `app/src/main/kotlin/cn/datebook/app/MainActivity.kt`, `app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt`, `app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt`, `app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt`, `app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt`, `tools/host_test.sh`, `tools/verify_delivery.py`, `docs/TEST_PLAN.md`, `docs/TEST_REPORT.md`, `README.md`, `docs/ADR.md`, `THIRD_PARTY_NOTICES.md`, `app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt`, `app/schemas/cn.datebook.app.data.DateBookDatabase/1.json`, `docs/file_contracts_v1.schema.json`, `app/proguard-rules.pro`, `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.properties`, `gradle/wrapper/gradle-wrapper.jar`, `../build_datebook_bundle.py`, `../../outputs/DateBook_AllInOne.py` |

---

## 实施步骤

### Wave 1: 工程与共享类型

**Step 1** — 工程与共享类型

- **Task**: T001
- **Task Name**: t001-datebook
- **Solution Ref**: S001
- **Unit ID**: datebook
- **Unit Root**: `.`
- **Files**: `core/src/main/kotlin/cn/datebook/core/Models.kt`, `settings.gradle.kts`, `build.gradle.kts`, `gradle.properties`, `gradle/libs.versions.toml`, `core/build.gradle.kts`, `app/build.gradle.kts`, `app/src/main/AndroidManifest.xml`, `app/src/main/res/values/strings.xml`, `app/src/main/res/values/themes.xml`, `app/src/main/res/xml/backup_rules.xml`, `app/src/main/res/xml/data_extraction_rules.xml`, `app/src/main/res/xml/file_paths.xml`, `app/src/main/res/xml/widget_info.xml`, `app/src/main/res/drawable/ic_datebook.xml`, `docs/IMPLEMENTATION_CONTRACT.md`
- **Approach**:
  - 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权
  - 本机无账号无网络；SDK及固定依赖完整；共享字段与TD一致
  - Release Manifest不包含网络权限；应用从私有noBackup目录读取
- **Acceptance Criteria**:
  - 本机无账号无网络；SDK及固定依赖完整；共享字段与TD一致
  - Release Manifest不包含网络权限；应用从私有noBackup目录读取
- **Pattern**: 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权,本机无账号无网络；SDK及固定依赖完整；共享字段与TD一致,Release Manifest不包含网络权限；应用从私有noBackup目录读取
- **Spec Refs**: TD v1.1 对应章节（外部设计文档，不是正式spec/）
- **Review Points**: 数据不丢失、线程与代次隔离、取消语义、无静默截断；需求覆盖和实际验证分开

### Wave 2: 日期、存储与系统能力

**Step 2** — 日期与业务用例

- **Task**: T002
- **Task Name**: t002-datebook
- **Solution Ref**: S002
- **Unit ID**: datebook
- **Unit Root**: `.`
- **Files**: `core/src/main/kotlin/cn/datebook/core/DateEngine.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt`, `core/src/test/kotlin/cn/datebook/core/CoreTests.kt`
- **Approach**:
  - 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权
  - 生日跨日/重复/DST/农历边界；树最多三层且只查直属；所有CRUD和状态按TD执行
  - 目标行动、标签批量、移动复制、原因集归档回收站、容量与错误原子性；不以TODO替代
- **Acceptance Criteria**:
  - 生日跨日/重复/DST/农历边界；树最多三层且只查直属；所有CRUD和状态按TD执行
  - 目标行动、标签批量、移动复制、原因集归档回收站、容量与错误原子性；不以TODO替代
- **Pattern**: 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权,生日跨日/重复/DST/农历边界；树最多三层且只查直属；所有CRUD和状态按TD执行,目标行动、标签批量、移动复制、原因集归档回收站、容量与错误原子性；不以TODO替代
- **Depends On**: T001
- **Spec Refs**: TD v1.1 对应章节（外部设计文档，不是正式spec/）
- **Review Points**: 数据不丢失、线程与代次隔离、取消语义、无静默截断；需求覆盖和实际验证分开

**Step 3** — Room与安全切库

- **Task**: T003
- **Task Name**: t003-datebook
- **Solution Ref**: S003
- **Unit ID**: datebook
- **Unit Root**: `.`
- **Files**: `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `app/src/main/kotlin/cn/datebook/app/data/Entities.kt`, `app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt`, `app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt`
- **Approach**:
  - 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权
  - 规范化表和基础约束、触发器、版本与幂等、outbox、资产租约；无单JSON表降级
  - 候选库校验和原子指针切换；并发revision变化拒绝提交；失败保留原库
- **Acceptance Criteria**:
  - 规范化表和基础约束、触发器、版本与幂等、outbox、资产租约；无单JSON表降级
  - 候选库校验和原子指针切换；并发revision变化拒绝提交；失败保留原库
- **Pattern**: 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权,规范化表和基础约束、触发器、版本与幂等、outbox、资产租约；无单JSON表降级,候选库校验和原子指针切换；并发revision变化拒绝提交；失败保留原库
- **Depends On**: T001
- **Spec Refs**: TD v1.1 对应章节（外部设计文档，不是正式spec/）
- **Review Points**: 数据不丢失、线程与代次隔离、取消语义、无静默截断；需求覆盖和实际验证分开

**Step 4** — 文件与系统能力

- **Task**: T004
- **Task Name**: t004-datebook
- **Solution Ref**: S004
- **Unit ID**: datebook
- **Unit Root**: `.`
- **Files**: `core/src/main/kotlin/cn/datebook/core/FileCodec.kt`, `core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt`, `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt`, `app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt`, `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt`, `app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt`
- **Approach**:
  - 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权
  - 完整JSON/CSV/备份容器，AES-GCM认证、有界解包、引用语义校验与导入去重
  - 通知票据防崩溃丢失、权限降级、组件、日历、背景与长图卡片、锁、长任务持久登记
- **Acceptance Criteria**:
  - 完整JSON/CSV/备份容器，AES-GCM认证、有界解包、引用语义校验与导入去重
  - 通知票据防崩溃丢失、权限降级、组件、日历、背景与长图卡片、锁、长任务持久登记
- **Pattern**: 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权,完整JSON/CSV/备份容器，AES-GCM认证、有界解包、引用语义校验与导入去重,通知票据防崩溃丢失、权限降级、组件、日历、背景与长图卡片、锁、长任务持久登记
- **Depends On**: T001
- **Spec Refs**: TD v1.1 对应章节（外部设计文档，不是正式spec/）
- **Review Points**: 数据不丢失、线程与代次隔离、取消语义、无静默截断；需求覆盖和实际验证分开

### Wave 3: Page & Routing

**Step 5** — Compose页面与完整接线

- **Task**: T005
- **Task Name**: t005-datebook
- **Solution Ref**: S005
- **Unit ID**: datebook
- **Unit Root**: `.`
- **Files**: `app/src/main/kotlin/cn/datebook/app/MainActivity.kt`, `app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt`, `app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt`, `app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt`, `app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt`
- **Approach**:
  - 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权
  - 首页/本/搜索/日历/事件/目标/创建编辑/行动/分享/备份/导入/诊断/组件/回收站/锁/工具可进入
  - 一级只列二级、二级只列三级、三级禁增；真实用例接线，不用演示toast代替保存
- **Acceptance Criteria**:
  - 首页/本/搜索/日历/事件/目标/创建编辑/行动/分享/备份/导入/诊断/组件/回收站/锁/工具可进入
  - 一级只列二级、二级只列三级、三级禁增；真实用例接线，不用演示toast代替保存
- **Pattern**: 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权,首页/本/搜索/日历/事件/目标/创建编辑/行动/分享/备份/导入/诊断/组件/回收站/锁/工具可进入,一级只列二级、二级只列三级、三级禁增；真实用例接线，不用演示toast代替保存
- **Depends On**: T002, T003, T004
- **Spec Refs**: TD v1.1 对应章节（外部设计文档，不是正式spec/）
- **Review Points**: 数据不丢失、线程与代次隔离、取消语义、无静默截断；需求覆盖和实际验证分开

### Wave 4: 综合测试和还原说明

**Step 6** — 综合测试和还原说明

- **Task**: T006
- **Task Name**: t006-datebook
- **Solution Ref**: S006
- **Unit ID**: datebook
- **Unit Root**: `.`
- **Files**: `tools/host_test.sh`, `tools/verify_delivery.py`, `docs/TEST_PLAN.md`, `docs/TEST_REPORT.md`, `README.md`, `docs/ADR.md`, `THIRD_PARTY_NOTICES.md`, `app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt`, `app/schemas/cn.datebook.app.data.DateBookDatabase/1.json`, `docs/file_contracts_v1.schema.json`, `app/proguard-rules.pro`, `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.properties`, `gradle/wrapper/gradle-wrapper.jar`
- **Approach**:
  - 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权
  - 需求到测试逐项追踪；执行可用编译/单测/静态校验；保留失败证据与未测项
  - SDK/设备测试、性能、恶意文件、恢复杀进程、无障碍有具体操作与判定；完整还原指南
- **Acceptance Criteria**:
  - 需求到测试逐项追踪；执行可用编译/单测/静态校验；保留失败证据与未测项
  - SDK/设备测试、性能、恶意文件、恢复杀进程、无障碍有具体操作与判定；完整还原指南
- **Pattern**: 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权,需求到测试逐项追踪；执行可用编译/单测/静态校验；保留失败证据与未测项,SDK/设备测试、性能、恶意文件、恢复杀进程、无障碍有具体操作与判定；完整还原指南
- **Depends On**: T005
- **Spec Refs**: TD v1.1 对应章节（外部设计文档，不是正式spec/）
- **Review Points**: 数据不丢失、线程与代次隔离、取消语义、无静默截断；需求覆盖和实际验证分开

### Wave 5: 单文件封装与仓库交付

**Step 7** — 单文件封装与仓库交付

- **Task**: T007
- **Task Name**: t007-datebook
- **Solution Ref**: S007
- **Unit ID**: datebook
- **Unit Root**: `.`
- **Files**: `../build_datebook_bundle.py`, `../../outputs/DateBook_AllInOne.py`
- **Approach**:
  - 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权
  - 一个明文可读总文件包含计划/目录/源码/资源/测试/报告；逐文件SHA256可验
  - 还原默认拒绝覆盖、禁止路径穿越；只上传最终总文件到用户指定仓库，不含凭据/本机路径/临时产物
- **Acceptance Criteria**:
  - 一个明文可读总文件包含计划/目录/源码/资源/测试/报告；逐文件SHA256可验
  - 还原默认拒绝覆盖、禁止路径穿越；只上传最终总文件到用户指定仓库，不含凭据/本机路径/临时产物
- **Pattern**: 遵循 docs/IMPLEMENTATION_CONTRACT.md 的固定方法、字段与文件所有权,一个明文可读总文件包含计划/目录/源码/资源/测试/报告；逐文件SHA256可验,还原默认拒绝覆盖、禁止路径穿越；只上传最终总文件到用户指定仓库，不含凭据/本机路径/临时产物
- **Depends On**: T006
- **Spec Refs**: TD v1.1 对应章节（外部设计文档，不是正式spec/）
- **Review Points**: 数据不丢失、线程与代次隔离、取消语义、无静默截断；需求覆盖和实际验证分开

---

## Non-Goals

- 不做iOS、登录账号、云同步、网络共享或服务器推送。
- 不宣称未运行的APK构建、真机、性能或安全审计通过。
- 不接受SDK许可或改系统安装；缺Android环境时交付可运行测试源码及设备验收步骤。
- 不提交开发机器的路径、凭据、缓存、工具下载或用户资料。

---

## Review Level

**HIGH**

<!-- Generated by skill-spec-to-plan -->
