#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DateBook · Android 本地倒数日 · 规划、完整源码与测试单文件交付

交付日期：2026-11-01。无登录 / 无服务器 / 无应用网络权限。
先阅读本文档下方各“BEGIN FILE”区块；业务源码是明文 Kotlin，不是压缩后的不透明数据。
唯一二进制是官方 Gradle wrapper JAR，以 Base64 明确标注并附校验值。

使用（Python 3.10+，无需先安装 Android Studio）：
  python3 DateBook_AllInOne.py --plan
  python3 DateBook_AllInOne.py --list
  python3 DateBook_AllInOne.py --verify
  python3 DateBook_AllInOne.py --read app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt
  python3 DateBook_AllInOne.py --extract DateBook

提取后是正常的 core/app Android Studio 工程；默认拒绝覆盖既有目录。
本文件不连接网络、不上传文件、不读取凭据、不安装软件、不接受 Android SDK 许可。

实际通过：85项JVM测试；真实Gradle配置、Room/KSP生成、Android API源码编译；
35项Android仪器化测试代码编译、实际Room25表/42守卫/24条平台SQL与SQLite回归。
未运行：完整APK构建/资源和合并Manifest/DEX、安装、真机提醒组件、仪器化执行、性能与安全审计。
源码实现交付不代表已可直接上架；具体证据边界和接手门禁见内嵌TEST_REPORT/TEST_PLAN。

完整目录：
DateBook/
  .gitignore
  README.md
  THIRD_PARTY_NOTICES.md
  app/build.gradle.kts
  app/proguard-rules.pro
  app/schemas/cn.datebook.app.data.DateBookDatabase/1.json
  app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt
  app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt
  app/src/main/AndroidManifest.xml
  app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt
  app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt
  app/src/main/kotlin/cn/datebook/app/MainActivity.kt
  app/src/main/kotlin/cn/datebook/app/data/Entities.kt
  app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt
  app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt
  app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt
  app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt
  app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt
  app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt
  app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt
  app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt
  app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt
  app/src/main/res/drawable/ic_datebook.xml
  app/src/main/res/values/strings.xml
  app/src/main/res/values/themes.xml
  app/src/main/res/xml/backup_rules.xml
  app/src/main/res/xml/data_extraction_rules.xml
  app/src/main/res/xml/file_paths.xml
  app/src/main/res/xml/widget_info.xml
  app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt
  build.gradle.kts
  core/build.gradle.kts
  core/src/main/kotlin/cn/datebook/core/DateBookService.kt
  core/src/main/kotlin/cn/datebook/core/DateEngine.kt
  core/src/main/kotlin/cn/datebook/core/FileCodec.kt
  core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt
  core/src/main/kotlin/cn/datebook/core/Models.kt
  core/src/test/kotlin/cn/datebook/core/CoreTests.kt
  core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt
  docs/ADR.md
  docs/ERROR_CODES.md
  docs/IMPLEMENTATION_CONTRACT.md
  docs/TEST_PLAN.md
  docs/TEST_REPORT.md
  docs/file_contracts_v1.schema.json
  gradle.properties
  gradle/libs.versions.toml
  gradle/wrapper/gradle-wrapper.jar  [binary, Base64 below]
  gradle/wrapper/gradle-wrapper.properties
  gradlew
  gradlew.bat
  licenses/gradle-APACHE-2.0.txt
  plan/datebook-initial.md
  settings.gradle.kts
  tools/host_test.sh
  tools/verify_bundle.py
  tools/verify_delivery.py
"""
from pathlib import Path, PurePosixPath
import argparse
import base64
import hashlib

FILES = {}
BINARY_BASE64 = {}


# ============================================================================
# BEGIN FILE: README.md
# ============================================================================
FILES['README.md'] = r'''# DateBook · 重要的日子

Android 原生、本机优先的倒数日 / 纪念日 / 目标记录应用。无账号、无服务器、无网络权限。

## 交付形式

GitHub 中的 `DateBook_AllInOne.py` 是唯一源码总文件，不是 APK，也不是只能观看的伪代码。它以明文分区记录本计划、目录、全部 Kotlin / Gradle / XML / 测试和文档，并附各文件 SHA-256。只有官方 Gradle wrapper 二进制是明确标注的 Base64。

不需要先安装 Android Studio 才能阅读。需要还原工程时，在安装 Python 3.10+ 的电脑执行：

```sh
python3 DateBook_AllInOne.py --plan
python3 DateBook_AllInOne.py --list
python3 DateBook_AllInOne.py --verify
python3 DateBook_AllInOne.py --extract DateBook
```

提取默认拒绝覆盖任何现有目录，不会改动其他项目。不执行上传、不读取凭据、不自动接受 Android SDK 许可。

## 后续在 Android Studio 中打开

1. 安装支持 AGP 9.2 的 Android Studio 稳定版，安装 API 37 SDK。SDK 许可由使用者阅读并确认。
2. Open → 选择提取出的 `DateBook` 根目录，而不是里面的 app 目录。
3. Gradle JDK 选择 JDK 17。首次 Gradle Sync 需要联网下载构建依赖，**应用运行本身不需要网络**。
4. 选择 Android 8.0 / API 26 或更高版本的设备 / 模拟器，运行 app。
5. 先完成下方构建与测试，再进行发布签名。仓库不含任何签名密钥或账号凭据。

```sh
# macOS/Linux：提取脚本已设置 gradlew 可执行权限
./gradlew :core:test :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
./gradlew :app:connectedDebugAndroidTest
# Windows 使用 gradlew.bat 对应命令
python3 tools/verify_delivery.py
python3 tools/verify_bundle.py ../DateBook_AllInOne.py
```

如果没有 JDK17，Gradle 工具链不会冒充已安装；请先配置 Android Studio 的 JDK。首次运行不依赖应用商店、Google 账号或网络服务。

## 主要功能

- 本子、封面、图标、标签、搜索、筛选、置顶、手动顺序、自动 / 固定首页卡片。
- 公历 / 农历、生日年度循环、闰日策略、定时 / 全天、正倒数、多种重复与截止日期。
- 最多三级手动事件；详情只列直属下一级；每级有独立背景与唯一一段寄语。
- 目标、直属阶段完成率与独立时间进度、行动日期 / 内容 / 用时。
- 子树移动 / 复制、原因集归档、30 天回收站与恢复。
- JSON / CSV 独立副本交换、图片卡片与长寄语分图；完整加密备份、合并 / 替换恢复。
- 本机提醒及精准权限降级、持久通知票据、系统日历显式复制、桌面组件与隐私配置。
- PIN / 生物识别访问锁、草稿、浅深主题、日期工具。没有 PIN 云端找回。

## 目录与边界

`core`：共享模型、日期引擎、业务服务、校验、文件协议和纯 JVM 测试。
`app/data`：25 张规范化 Room 表、触发器、幂等事务、代次切换、媒体租约。
`app/platform`：提醒 / 组件 / 日历 / 卡片 / 应用锁 / 持久文件任务。
`app/ui`：Compose 页面、页面路由、编辑草稿、状态和业务接线。
`docs` / `plan`：开发测试规划、决策、覆盖矩阵、测试报告、接口契约。

## 安全与限制

应用锁不是数据库加密；操作系统沙盒不防已 Root 的设备。完整备份若留空密码则是明文；请主动设置密码并保管。没有账号和服务器，因此换手机必须通过文件迁移，实时共享 / 云同步不在范围内。系统日历可能属于用户已同步的其他服务，应用只在明确操作后交给系统日历处理，不把它伪装成本地云同步。

静态法定节假日可以手动创建和按年重复；不在线拉取调休安排。普通提醒受系统和省电影响；强制停止后需重新打开应用。后台调度、厂商策略和组件刷新不能仅靠 JVM 测试证明。

**交付状态：源码实现及可用主机测试交付，不等于已通过 Android 安装验收或可直接上架。** 详见 `docs/TEST_REPORT.md`；不能把待运行项视为通过。
'''
# END FILE: README.md


# ============================================================================
# BEGIN FILE: docs/TEST_PLAN.md
# ============================================================================
FILES['docs/TEST_PLAN.md'] = r'''# 开发与测试详细规划

## 1. 目标与交付口径

范围以 PRD / 详细需求 v1.1、TD v1.1 和本轮“详情只展示直属下一级”确认项为依据。先形成计划、固定接口，再实现、集成、测试和单文件交付。本次不部署任何服务，不创建登录；最终唯一源码总文件可还原 Android Studio 工程。

源码实现完成 ≠ APK 验收完成 ≠ 发布完成。每项报告必须标记实际执行 / 未运行 / 阻断，不能以“代码里有方法”代替验收。上线前必须通过 Android 构建、设备及权限提醒验收。

## 2. 工作分解与依赖

| 阶段 | 任务与产出 | 依赖 | 开发完成判据 | 测试出口 |
|---|---|---|---|---|
| T001 | Gradle、Manifest、核心模型、固定接口、版本目录 | 无 | 无网络/账号，core/app 依赖方向正确 | 版本真实存在、插件配置、Manifest权限检查 |
| T002 | 日期与重复、树、书本标签、目标行动、生命周期、幂等 | T001 | 所有写操作经领域校验和仓库事务 | 日期/树/状态/失败回滚 JVM 单测 |
| T003 | 25表、触发器、Room仓库、媒体、代次CAS恢复 | T001 | 无 JSON 单表替代，无破坏性迁移降级 | 实际SQLite绕过测试、RoomKSP、仪器化事务/杀进程 |
| T004 | 文件协议、加密备份、通知、组件、日历、锁、文件任务 | T001 | 严格协议、有界输入、可见权限降级 | 协议/攻击样例/JCA互通、设备通知/组件/锁 |
| T005 | 首页/本/目标/设置、编辑/详情/搜索/日历/回收站/分享/恢复 | T002–T004 | 页面按钮有实际用例，三级行为一致 | Compose API编译、UI自动化、人工视觉/无障碍 |
| T006 | 完整回归、需求追踪、运行说明、风险报告 | T005 | 实际结果与未测项分开 | 下方门禁全部有记录 |
| T007 | 明文总文件、目录与哈希、提取器、仓库上传 | T006 | 不覆盖现有目录，提取后字节一致 | 自校验、还原比较、防穿越、GitHub文件确认 |

实施顺序为 T001 → 并行模块 T002/T003/T004 → T005 → T006 → T007。契约冻结后允许先编写 UI 接线，必须在接口集成后重新编译。详见 `plan/datebook-initial.md`。

## 3. 后续团队排期参考

以下是接手后的计划估算，不是本轮已经投入的工时，也不承诺固定发布日期。

- D1–D2：Android Studio 导入、JDK/SDK/依赖同步、正式 Gradle/资源/Manifest/KSP构建、修复环境差异。
- D3–D5：API26/29/31/33/35/37仪器化、数据库/文件/页面集成回归，回归修改后重跑全部主机测试。
- D6–D8：Pixel及至少两类国内厂商真机，通知权限、精准闹钟、重启/时区、后台省电、桌面组件与日历。
- D9–D10：性能、TalkBack/大字体、深色、长图视觉、错误恢复演练、隐私审查、发布签名与离线安装验收。

若有 P0/P1 数据丢失、绕锁、崩溃、提醒失效问题，停止发布而不是缩减测试。修复后回归受影响模块和全部日期/文件单测。

## 4. 测试分层和数据

L1 纯 JVM：固定 Clock、MemoryRepository、离线算法和实际文件字节。边界包括 2/29、月31日、农历闰六月/小月、DST重叠/缺口；不依赖当天日期碰巧满足。

L2 存储：真实SQLite建表和触发器；真实Room/KSP生成；设备上Room事务、FK、receipt/outbox、切库/资产租约。临时 API stub 编译只用于发现类型问题，不作为设备证明。

L3 Android集成：Compose测试、Permission拒绝、SAF文件结果、真实Notification/Alarm/Widget/Calendar/Biometric。

L4 非功能：冷启动/滚动/内存/耗电、容量上限、备份攻击、可访问性、隐私和发布包。与功能测试分开记录。

准备资料：空库、5默认本、3级树、父20/21/40/41/101项、2000事件/200本/10000行动、中文/组合音标/家庭emoji、60字标题/2000字寄语、25MiB照片、损坏图、20MiB以上文本、错误密码和ZIP穿越样例。每个破坏性场景只在专门测试安装和可丢弃资料上运行。

## 5. 需求到验收矩阵

| ID | 需求/操作步骤 | 必须观察到的结果 | 自动化来源/运行层 |
|---|---|---|---|
| R01 | 飞行模式首次启动，新建/重开 | 无登录，5默认本，资料持久；不请求网络 | Manifest检查 + Android |
| R02 | 创建生日，模拟当天及次日 | 当天“今天生日”；次日下一年，不新增副本；-7及当天09:00规则 | CoreTests + 设备提醒 |
| R03 | 未知出生年、2/29两种策略 | 不虚构年龄；2/28或3/1清晰且稳定 | CoreTests |
| R04 | 公/农历、闰月/小月/算法范围 | 固定版本HKO样例一致；非法/越界拒绝，不在线查询 | LunarGoldenTests |
| R05 | 每月31/每周/每N/截止/定时跨DST | 不丢锚点，月末回退；截止后无下次；投影边界正确 | CoreTests |
| R06 | 根→二级→三级，尝试第四级 | 根只列二级，二级只列三级；三级禁增；领域和DB均拒绝绕过 | CoreTests / UiTests / DatabaseTests |
| R07 | 21/41直属孩子分页，点入返回 | 每次20，不混入孙级；滚动位置保留；变更后游标过期拒绝 | CoreTests + UI/人工 |
| R08 | 修改各级背景/寄语并分享 | 互不继承覆盖；仅一段寄语；卡片不带子树或行动 | FileCodecTests + Android视觉 |
| R09 | 新建/改名/删本、封面图标颜色、排序 | 同名拒绝；未分类保护；删本明确迁移/回收；内容不丢 | CoreTests + Android |
| R10 | 标签、新建事件一起失败/并发版本冲突 | 不遗留半成功标签；NFC名称去重；草稿保留，版本冲突不覆盖 | CoreTests + UI |
| R11 | 搜索标题/寄语/标签/本，跨层级查看 | 全局结果标层级；详情仍只查直属 | CoreTests + Android |
| R12 | 固定/自动最近首页、置顶、手动顺序 | 已归档/回收/取消不抢首页；固定失效有安全回退 | CoreTests + Android |
| R13 | 移动/复制含三级子树、跨本/循环/超深 | 合法移动整棵原子；非法不写；副本ID独立且提醒关闭 | CoreTests / DatabaseTests |
| R14 | 父归档+子单独归档，再撤父批次 | 子仍受自身原因隐藏；恢复不意外启用所有后代 | CoreTests / DatabaseTests |
| R15 | 回收/30天清理/恢复/永久删除 | 原因集合不丢；永久删除需确认且仅回收站子树；清理不用递归误删目录 | CoreTests + 设备时钟 |
| R16 | 目标开始/完成/取消/重开、直属阶段 | 父子状态独立；取消/归档阶段不计完成分母；时间进度不是完成率 | CoreTests + UI |
| R17 | 行动增改删、未来日期/1441分钟/1001字 | 非法整条拒绝；有效日期/用时/内容独立保留 | CoreTests + UI |
| R18 | JSON导出子树，另一库导入两次 | 根提升，ID重映射，无祖先泄露；来源去重；照片回退、提醒关闭 | FileCodecTests |
| R19 | CSV含逗号/引号/换行/公式/旧六列 | 可逆；逐行原始行号；混合转义拒绝；复杂字段不默默丢失 | FileCodecTests |
| R20 | 空本/未用标签/照片全备份并合并 | 不丢空容器、媒体字节、来源历史；已有导入子节点继续正确归属 | FileCodecTests + DB |
| R21 | Unicode密码、错密码/篡改/重复键/错类型 | 认证失败无明文候选；JCA PBKDF2互通；严格UTF8/schema | FileCodecTests |
| R22 | ZIP路径穿越/超限/压缩炸弹/假图片元数据 | 不写出暂存根，不先解包后认证；图片真实尺寸MIME校验；失败清理 | FileCodecTests + Android |
| R23 | 预览后改库/30分钟后提交、恢复前后杀进程 | CAS/TTL拒绝；指针提交点明确；旧库或新库完整，绝无半库 | DatabaseTests + 手工杀进程 |
| R24 | 备份过程取消 / commit时取消 | 提交前可取消不改事实；提交阶段不可取消；重启任务显示中断 | JobManager + Android |
| R25 | API33拒绝通知、API31拒绝精准 | 可保存；普通降级/状态清楚；不假装精准或已授权 | 设备权限矩阵 |
| R26 | due→票据事务后、notify前后各杀进程 | 重启可重放同tag；不丢票据；过期跳过而非无限补发 | 设备故障注入 |
| R27 | -7/当天窗口、定时迟到15分钟、改日期/禁用 | 规则版本/epoch失效旧票据，新规则不补过去 | 设备 + 源码审查 |
| R28 | 换时区、调时、重启、更新安装、强制停止 | 本地09:00重算；恢复调度；强停后必须重开且有告知 | Pixel/OEM真机 |
| R29 | 添加单项/最近组件；开启应用锁 | 默认不含照片寄语；锁开启后安全入口；旧epoch点击不跳新库同ID | 设备Widget |
| R30 | 日历复制取消/授权读取/选择批次 | 不要求WRITE_CALENDAR；不自动写同步；批量全部成功或回滚；长文本不截断 | CoreTests + Calendar设备 |
| R31 | PIN错误5次、重启、强生物识别失败/成功 | 持久冷却、不降级绕锁；失败不展示内容；截图保护 | 真机 Biometric |
| R32 | 锁开启时选照片/SAF，返回后解锁继续 | 选择器触发自动锁；选中URI暂挂，解锁后续行；页面/草稿未丢失 | Android重点回归 |
| R33 | 忘记PIN，错备份/真备份替换/清空 | 错文件不清锁；有效替换后先设新PIN；明确清空才删除旧资料 | Android安全验收 |
| R34 | 草稿、旋转、后台、进程回收 | 保存前不覆盖事实；草稿能续写；旧版本草稿不自动覆盖新版本 | Android |
| R35 | 日历月视图、周起始、日期计算/农历转换 | 展开重复发生日；工具不写业务资料 | JVM + Android |
| R36 | 2000事件冷启/搜索/滚动/卡片/备份 | 见性能基线；不得ANR或OOM | 真机Profiler |
| R37 | 字体200%、TalkBack、深浅主题 | 正文可读/按钮可达/读屏语义/不靠颜色单独传状态 | 手工无障碍 |
| R38 | 总文件 verify/extract/再次extract | 哈希一致、目录完整、拒绝覆盖及路径穿越、不含凭据 | tools/verify_delivery.py + 总文件自检 |

## 6. 页面手工回归路线

首页 → 新建事件 → 编辑各字段/选图/寄语/提醒 → 保存 → 详情 → 添加二级 → 二级添加三级 → 三级确认禁增 → 返回检查滚动 → 目标改状态/行动 → 本子批量操作 → 搜索/标签 → 日历 → 分享长卡 → 设置/锁 → 文件导入预览 → 合并/替换 → 回收恢复 → 重启应用。

每次外部系统Activity返回都测试“锁关闭 / 锁开启”两种情况；测试取消和成功。照片与DocumentProvider权限只按需请求；授权拒绝后不能丢草稿。

## 7. 非功能门禁

目标基线（待实测，非已达成）：中端6GB设备，2000事件，冷启动P95≤2s、列表常规交互P95≤200ms、无主线程重IO/ANR；长图和256MiB容器不得OOM；备份可报告进度；回收清理不得删除快照租约保护的图片。使用Macrobenchmark/Profiler记录设备/系统/数据量/样本数，不用开发机时间冒充。

安全门禁：Android包无INTERNET/账户权限；检查合并Manifest；noBackup及云/设备迁移排除；不记录PIN/密码/寄语/路径到日志；FileProvider只开放cache/shares；导入后背景真实解码；URI旧epoch拒绝；无破坏性迁移；密码输错不清库；开启锁后通知和组件不泄露标题。

## 8. 发布出口与缺陷等级

- P0：数据不可恢复丢失、目录越界写删、认证绕过；立即停止交付发布并保全证据。
- P1：关键用例崩溃/保存错误、三级关系损坏、有效提醒持久失效、误导安全承诺；修复并回归后才能候选发布。
- P2：非阻断交互/布局/性能尾部问题；记录设备、步骤、期望与实际，可明确接受风险，但不能偷偷关闭。

发布前：正式 Gradle 构建 + lint + 全部单测 + 仪器化 + 权限真机矩阵 + 备份跨设备迁移 + 锁恢复 + 无障碍基本路径均有证据；所有 P0/P1 关闭；生成签名包由用户保管密钥。当前未安装 SDK 不改变这些门槛。
'''
# END FILE: docs/TEST_PLAN.md


# ============================================================================
# BEGIN FILE: plan/datebook-initial.md
# ============================================================================
FILES['plan/datebook-initial.md'] = r'''# Human Review Plan v2: DateBook Android 完整实现与测试

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
'''
# END FILE: plan/datebook-initial.md


# ============================================================================
# BEGIN FILE: docs/ADR.md
# ============================================================================
FILES['docs/ADR.md'] = r'''# 架构决策与开发基线

1. **完全本地**：不实现登录、邮箱唯一性、云库或云身份。Room 保存业务；noBackup 保存库、媒体、锁和任务。Manifest 无 INTERNET；外部文件和系统日历只在用户动作后访问。
2. **原生技术**：Kotlin、Jetpack Compose、Room、Coroutines / Flow、WorkManager、AlarmManager、Glance、DataStore。用 Android Studio 打开；非跨平台 / WebView。
3. **两个物理模块**：core/app；app 内用 data/platform/ui 包隔离。相较 TD 的多层物理模块，依赖方向相同，减少单文件交付构建复杂度。构造器注入代替 Hilt；不改变功能范围。
4. **固定版本**：AGP9.2.1、Gradle9.4.1、Kotlin2.2.10、KSP2.3.10、JDK17、API26–37。AGP 使用内建 Kotlin，不能重复应用 kotlin-android 插件。旧KSP2.2.10-2.0.2在真实AGP配置中触发kotlin.sourceSets不兼容错误，故升级到支持AGP9的KSP2.3.10，不通过禁用守卫掩盖。明确选择已存在稳定版本，不声称都是最新版本。精确列表见 version catalog。
5. **固定离线农历**：lunar-java1.7.7，独立 LunarPort，1901–2099；不是系统 ICU，不在线拉取。HKO 黄金样例注释在 LunarGoldenTests。无在线自动调休服务。
6. **单进程代次门**：协程 Mutex 保护短 DB / OS 发布临界区；导出长 IO 走快照租约，不持锁做图片与备份。禁止缓存跨代 Room 句柄；禁止 withDb 嵌套。
7. **规范化事实**：25 张表，不用一个 JSON 表冒充数据库。JSON 只用于协议、草稿和幂等操作结果元数据。基础结构由 Room、触发器及领域验证共同防守。
8. **恢复提交点**：私有暂存 → 文件认证 / 校验 → 候选建库 → epoch/revision CAS → AtomicFile 指针。提交后不可取消；进程退出按指针而不是猜测 journal 恢复。失败保留旧库。
9. **通知**：规则推进与持久 delivery ticket 同一事务，之后通知；相同 tag 可幂等重发，不能承诺 OS 的绝对 exactly-once。全天在提醒日末失效，定时 15 分钟；新建 / 导入 / 重新启用不追补过去。时区变化重建本地时刻。普通模式不保证秒级。
10. **本地访问锁**：PIN PBKDF2 校验及递增冷却；强生物识别由系统成功回调解锁；锁配置不进备份。忘记 PIN 只能强生物识别、验证全量备份后替换，或确认清空；不能先解锁再验证文件。
11. **文本分享与全备份分开**：JSON 是独立副本交换，照片主题回退，提醒关闭；CSV 不能偷偷丢失树 / 目标等复杂字段，必须显式拒绝并提示改 JSON。全备份为有界 ZIP + 明确容器、AES256-GCM / PBKDF2-HMAC-SHA256、严格 UTF8 密码。无格式嗅探执行内容。
12. **日期字段**：生日未知年用 null；年度到期不改原日期。存事实，展示由时钟投影。英文枚举不随 UI 中文改动。父子最多三级，同本，不自动创建 100 / 1000 天。
13. **页面决策**：详情只显示一级直属子事件；点击进入；首版无内联展开所有后代。分页20（上限100），返回保留 LazyListState。搜索可跨层级，但标明层级；不改变详情约束。
14. **取消与大文件**：文件任务持久登记；准备中可取消，原子提交阶段不可取消。导出先在私有目录生成完整文件再写用户目标 URI；不声称外部 DocumentProvider 支持断电原子重命名，写入失败时提示用户删除不完整外部文件并重新导出。
15. **交付验收**：先主机测试，再 Android API 编译 / 正式构建 / 模拟器 / 真机 / 发布。无本机 Android SDK、模拟器的测试不能标成通过。源代码完整度与运行验收是两个状态。

## 官方技术依据

- https://developer.android.com/build/releases/agp-9-2-0-release-notes
- https://developer.android.com/jetpack/androidx/releases/room
- https://developer.android.com/develop/ui/compose/bom
- https://developer.android.com/develop/background-work/services/alarms/schedule
- https://developer.android.com/develop/ui/views/appwidgets/glance
- https://github.com/6tail/lunar-java/tree/v1.7.7

本交付不包含待用户审批才能实现的服务端依赖。后续若增加实时共享、账号或云备份，需要另立架构与隐私方案，不悄悄改变本地承诺。
'''
# END FILE: docs/ADR.md


# ============================================================================
# BEGIN FILE: docs/TEST_REPORT.md
# ============================================================================
FILES['docs/TEST_REPORT.md'] = r'''# 交付测试报告

日期：2026-10-31 至 2026-11-01。结论：源码与测试实现交付；**未完成 Android 安装 / 真机验收，不是已可上架的发布包**。

## 已实际执行

| 项目 | 结果与证据边界 |
|---|---|
| 开发计划结构检查 | Human Review Plan v2 官方解析/检查器通过，7任务、5波次；没有伪造正式Spec基线 |
| Kotlin纯JVM编译 | Kotlin2.2.10、serialization编译插件、JVM target17；使用本机已有JBR25运行编译器，非声称本机装有JDK17 |
| 核心用例 | 49项CoreTests通过，覆盖日期/树/原子保存/批量移动/状态/生命周期/版本/容量 |
| 真实农历 | 12项LunarGoldenTests通过，真实lunar1.7.7及香港天文台黄金样例，不是只测fake |
| 文件协议 | 24项FileCodecTests通过，包括独立JCA Unicode密码互通、错误密码/篡改、穿越、哈希、CSV、照片及导入来源 |
| 应用实际API编译 | 对真实Android17/API37 Maven Android jar及129份官方AndroidX/Maven工件编译所有app Kotlin，启用Compose与serialization编译器；仅生成R常量用验证stub；不是APK构建 |
| 真实Room代码生成 | Gradle9.4.1 + KSP2.3.10 + Room2.8.5，实际生成Database_Impl/Dao_Impl并编译，输出schema/1.json |
| 实际Gradle工程配置 | AGP9.2.1/KSP2.3.10 `tasks --all`成功，kspDebugKotlin及AndroidTest任务注册；没有关闭sourceSets守卫 |
| 仪器化测试源码编译 | 27项DatabaseTests + 8项UiTests针对真实Android测试库通过API编译；**没有运行这35项测试** |
| 主机SQLite | 实际Room导出25表建库；42个守卫SQL正文匹配；9项关系/绕过回归；24条系统模块SQL prepare通过 |
| Gradle wrapper | 官方生成脚本及JAR；发行版和wrapper SHA256记录于THIRD_PARTY_NOTICES，发行版校验启用 |
| 总文件还原 | `--verify`完整SHA256；tools/verify_bundle.py提取后逐文件字节一致，重复提取拒绝覆盖，8类非法路径、篡改哈希拒绝 |

交付脚本 `tools/host_test.sh` 重跑全部85项JVM测试；`tools/verify_delivery.py` 重跑配置/源码/实际Room DDL门禁。单文件自带 `--verify`、`--list` 和拒绝覆盖的 `--extract`，提取后逐文件哈希比较。仓库状态以最终交付消息为准，不能把上传前文案当作上传成功证据。

## 已发现并修复的整合问题

1. 旧KSP2.2.10-2.0.2在真实AGP9内建Kotlin下配置失败；升级KSP2.3.10并重新验证。
2. Compose导航hasRoute导入、跨模块nullable智能转换、实验API opt-in、Glance Intent重载等真实API编译错误。
3. 新标签先落库而事件失败、日历选择循环写入、批量移动部分提交；统一改为原子业务接口并加回归。
4. 核心import格式与协议/DB格式不同，显式映射，不混用枚举。
5. 数据库提交与StateFlow发布之间取消竞争；同一NonCancellable窗口发布。
6. 时区变化保留旧09:00队列；先作废本地时区队列再重建；锁开启时通知标题改为通用文案。
7. 日历长文本静默截断、卡片固定区域截断长寄语/标题；改为拒绝无损导入失败及按完整行分页。
8. 恢复假图片元数据、同路径同长度不同字节；真实图片解码/元数据校验和SHA256对比。
9. 选择器导致自动锁后URI操作失败；以epoch绑定的授权续行队列等待解锁，锁屏覆盖隐藏并保留原页面。
10. 恢复预览/合并暂存清理、30分钟预览有效期、锁定替换后的新PIN设置门禁；新PIN原子覆写验证资料，锁定时另窗对话框也隐藏。
11. 快照租约关闭改为NonCancellable；真实生产SnapshotLease的JVM取消清理探针执行通过（不等于Android DB删除已测）；文件任务启动失败及磁盘满终态安全处理。

## 未运行，必须由后续Android环境验收

- 完整`:app:assembleDebug`、资源编译/合并Manifest、DEX/R8、APK安装及签名包。
- 实际`:app:lintDebug`、Gradle全量unit test任务（本轮用实际Kotlin/JUnit CLI替代纯业务部分）。
- 35项Android仪器化的运行结果；设备SQLite/Room迁移及进程崩溃恢复。
- API26/29/31/33/35/37、Pixel与国内厂商的通知/精准闹钟、重启/调时、省电、组件、日历、SAF和强生物识别。
- 页面截图视觉验收、200%字体/TalkBack、横屏/折叠屏/平板、外部选择器+应用锁返回重点路径。
- 性能/内存/耗电基线、压力、独立安全审计、模糊测试和发布隐私审核。

未运行原因：本机未配置Android SDK、模拟器或测试手机；未替用户接受SDK许可。源码API编译、Room代码生成及Gradle配置成功不能替代上述验收。

## 残留风险与接手顺序

先按README还原并做正式构建，再执行TEST_PLAN矩阵。所有P0/P1阻断发布。访问锁不是数据库加密；正常提醒不能承诺系统准时；外部DocumentProvider写入不能承诺断电原子性；系统强停后没有服务器补发。后续实际构建/设备差异若出现问题，必须修复并重跑，而不是把本报告改成“全部已通过”。

正式Spec门禁标为不适用：本项目来源为TD/PRD文档，没有`spec/_settings.md`或code baseline；本次用计划验证、需求覆盖矩阵和上述编译/测试，不伪造Full Spec的通过记录。
'''
# END FILE: docs/TEST_REPORT.md


# ============================================================================
# BEGIN FILE: docs/IMPLEMENTATION_CONTRACT.md
# ============================================================================
FILES['docs/IMPLEMENTATION_CONTRACT.md'] = r'''# DateBook 实施契约

依据 TD v1.1，所有讲解中文，Kotlin 标识符英文。主交付是 Android 应用，core 为纯 JVM 支持模块，不是服务端。交付一个可读、可验证、可还原的 Python 总文件，最终 GitHub 仓库只提交该总文件；中间源码目录仅用于集成和测试。

## 固定模型与分工

共享字段以 core/Models.kt 为准，禁止模块私自重命名。文件协议按 TD 附属 JSON Schema，内部模型通过显式 mapper 转换；导出不带 epoch 或设备设置。

- 核心：core/DateEngine.kt、DateBookService.kt、MemoryRepository.kt 与核心测试。DateEngine(clock, lunar: LunarPort)；evaluate(input:DateInput, now:Instant=clock.instant(), zone:ZoneId=clock.zone):DateProjection；occurrences(input,from:LocalDate,to:LocalDate):List<Occurrence>；nextOccurrence(input,after:LocalDate,inclusive:Boolean=true):Occurrence?。农历使用固定 cn.6tail:lunar:1.7.7 的离线算法与数据，限定1901至2099，独立 LunarPort 适配器，MIT 许可随包记录。
- DateBookService(repo,dates,clock) 提供 saveEvent(Event,expectedVersion:Long?=null,operationId:String=newId()):Event；saveBook(Book,expectedVersion:Long?=null):Book；deleteBook(id,trashContents:Boolean)；moveSubtree(id,destinationBookId,destinationParentId:String?)；copySubtree(id,wholeTree:Boolean=true):String；setLifecycle(rootIds:List<String>,action:String):String；restoreCause(causeId)；purge(rootIds)；purgeExpired()；setGoalState(id,state)；saveAction(ActionRecord,expectedVersion:Long?=null):ActionRecord；deleteAction(id)；saveTag(Tag):Tag；setTags(eventIds,tagIds)；saveHome(HomeConfig)。查询提供 search(snapshot,query,scope="active",bookId:String?=null):List<Event>、directChildren(snapshot,parentId,sortMode="date",cursor:String?=null,pageSize:Int=20):ChildPage、homeEvents(snapshot,bookId:String?=null):List<Event>、completionRate(snapshot,id):Pair<Int,Int>?、timeProgress(snapshot,id):Double。所有 suspend 变更通过 repo.transaction 保持原子性；输入完整校验、版本、幂等、revision、outbox 由明确层负责。
- 存储：app/data/RoomStore.kt、Entities.kt、SchemaGuards.kt。RoomStore(context) 实现 LibraryRepository；公开 suspend fun <T> withDb(block:suspend (DateBookDatabase,LibraryState,File)->T):T 使用同一代次 Mutex 租约，不能嵌套调用；suspend leaseSnapshot():SnapshotLease，SnapshotLease.state/root/close()；suspend addAsset(source:File,mime:String,width:Int,height:Int):Asset；fun assetFile(relativePath:String):File（安全相对路径、当前代次）；suspend gc()；val root:File 为全局noBackup根。数据库与 assets 在独立代次目录。getCurrent db 不得被跨代缓存。install 在独占租约外候选建库、提交时CAS检查expectedEpoch/revision，AtomicFile current指针唯一提交点。媒体租约防止导出期间GC。25张设计表/等价守卫及实际持久业务模型，不用单JSON表替代；基础 CHECK 守卫需新建和迁移一致。
- 数据库 DateBookDatabase 公开 dao():DeviceDao。DeviceDao 的集成调用统一采用 suspend fun query(sql:String):List<Map<String,String?>> 不便Room泛型，改为 RoomStore.withDb 的 db.openHelper.writableDatabase.execSQL/query 原生接口处理设备表，仍由Room管理业务表。系统模块不缓存连接。设备处理者可用 db.withTransaction，不能事务内调用OS。
- 文件与系统：core/FileCodec.kt（纯JVM，java IO/crypto/zip，Json），app/platform/SystemServices.kt、LockManager.kt、JobManager.kt、DateBookWidget.kt。FileCodec(dates:DateEngine) 的 public API 在实现后发主代理并与UI对接。必须实现正式JSON、CSV、安全备份容器，不以 LibraryState.serializer()直接冒充契约。输入有界，树和语义校验。SystemServices(context,store,dates) 提供 suspend reconcile(), suspend deliver(epoch:String,token:String), suspend refreshWidgets(), fun notificationAllowed():Boolean, fun exactAllowed():Boolean, fun requestNotificationSettings():Intent, fun requestExactSettings():Intent, fun calendarAdd(event:Event):Intent, suspend calendarImport(from:LocalDate,to:LocalDate):List<Event>, suspend stagePhoto(uri:Uri):Asset, suspend renderCard(event:Event,includeGreeting:Boolean,ratio:String):List<File>, fun share(files:List<File>):Intent。ReminderReceiver / RebuildReceiver / MaintenanceWorker 同文件可独立类；同应用单进程。通知发布持有代次租约、持久票据+推进同事务；PendingIntent以URI隔离epoch。静态卡片空寄语重排、长寄语分图、不截断。Glance提供单项/最近列表及配置Activity，隐私设备偏好默认关闭照片寄语。
- LockManager(context) 及JobManager的API实现后通知主代理。锁设置不在业务备份；应用锁不声称数据库加密；无账号找回。UI必须实现生物识别/PIN入口和锁定清空恢复边界。
- 主代理负责Gradle、Manifest、依赖、LunarPortAdapter、Application、Compose页面、导航、ViewModel、设置/导入/恢复/卡片所有交互接线、测试集成、单文件封装和GitHub上传。UI不能只是占位按钮，必须对接真实用例及系统端口。

## 技术基线与ADR

AGP9.2.1 / Gradle9.4.1 / JDK17，AGP内建Kotlin2.2.10，Compose compiler和serialization插件2.2.10；minSdk26、compile/target37。Room2.8.5、KSP2.3.10（旧2.2.10-2.0.2实际AGP配置失败，故升级），Compose BOM2025.08.01，Activity1.10.1，Navigation2.9.3，Lifecycle2.9.2，Coroutines1.10.2，Serialization1.9.0，DataStore1.1.7，WorkManager2.10.3，Glance1.1.1，Biometric1.1.0，lunar1.7.7。不使用预发布依赖。ADR01：首版两Gradle模块core/app，逻辑按domain/data/platform/ui包隔离；构造器手动DI代替Hilt以降低单文件交付的构建插件耦合，不改变业务功能；ADR02：单进程协程Mutex实现代次临界区（比共享读锁保守），不持锁做备份大IO或图片处理，快照资产通过租约保护；ADR03：固定第三方离线农历算法包而非运行时系统ICU，需权威样例回归，禁止自动在线节假日或调休推断。

## 必须验收

只看直属下一级、三级禁增；单段寄语；生日年度与-7/当天09:00；闰日农历/DST；正数与目标；全本/标签/批量/复制移动/原因集归档回收站30天；JSON/CSV独立副本与卡片；加密全备份及合并替换与幂等；无网络/登录；通知降级/崩溃恢复；组件隐私；日历显式复制/选择导入；应用锁/草稿/搜索/工具；错误与权限拒绝保留已存资料。

不能将未运行的Android构建、仪器化、设备提醒、性能或安全审计标记通过。交付测试报告记录actual/not_run和残留项。用户已要求规划后立即代码生成，不因HIGH review或语言确认额外停顿。
'''
# END FILE: docs/IMPLEMENTATION_CONTRACT.md


# ============================================================================
# BEGIN FILE: docs/ERROR_CODES.md
# ============================================================================
FILES['docs/ERROR_CODES.md'] = r'''# 错误码目录

由生产源码中稳定字符串枚举汇总。错误不会携带密码、PIN或寄语到持久任务日志。错误说明用于接手定位；界面常见错误由AppViewModel.friendly映射，未知码保留机器码并提示不清空已存资料。

| 错误码 | 处理约定 | 生产来源 |
|---|---|---|
| `ACTION_FUTURE_DATE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `ACTION_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `ASSET_CORRUPT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `ASSET_HASH_MISMATCH` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `ASSET_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `ASSET_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `ASSET_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `BACKUP_ASSET_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `BACKUP_AUTH_FAILED` | 密码错误或认证失败；不解包、不清锁、不清库。 | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `BACKUP_CHECKSUM_INVALID` | 内容与清单不一致；拒绝恢复。 | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `BACKUP_FILE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `BACKUP_MANIFEST_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `BACKUP_PATH_INVALID` | 备份含非法路径或重复项；拒绝并清理暂存。 | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `BOOK_BUILTIN_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `BOOK_NAME_CONFLICT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `BOOK_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `BOOK_PROTECTED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `CALENDAR_PERMISSION_REQUIRED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `CALENDAR_TEXT_TOO_LONG` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `CALENDAR_WINDOW_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `CAPACITY_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `CARD_LAYOUT_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `CARD_LIMIT_EXCEEDED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `CARD_WRITE_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `CAUSE_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `COMMAND_RECEIPT_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `COMMAND_RESULT_UNSUPPORTED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `CSV_COLUMN_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `CSV_ESCAPE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `CSV_HEADER_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `CSV_LOSS_REQUIRES_JSON` | CSV不能无损表达；改用JSON或完整备份。 | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `CSV_SYNTAX_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `CSV_VALUE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `CURSOR_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `CURSOR_STALE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `DATE_EXHAUSTED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `DATE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_KIND_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_OUT_OF_RANGE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `DATE_RANGE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_REPEAT_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_TIME_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_UNTIL_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_WINDOW_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_WINDOW_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DATE_YEAR_REQUIRED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `DAYBOOK1` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `DB_CHECKPOINT_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_CLOSED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_EPOCH_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_EVENT_APPEARANCE_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_EVENT_DATE_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_EVENT_RECURRENCE_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_FOREIGN_KEY_CHECK_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt` |
| `DB_GENERATION_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_GUARDS_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt` |
| `DB_HOME_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_IMPORT_FORMAT_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_LIBRARY_MISSING` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_NOT_READY` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_NULL_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_OPEN_FAILED` | 保留库文件，显示启动错误；禁止用空库降级。 | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_POINTER_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_POINTER_MISSING` | 已有代次但指针丢失；保留现场，不自动新建。 | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `DB_ROUNDTRIP_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `EVENT_IN_TRASH` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `EVENT_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt`, `core/src/main/kotlin/cn/datebook/core/Models.kt` |
| `FILE_AUTH_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `FILE_DUPLICATE_KEY` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `FILE_ENCODING_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `FILE_IO_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `FILE_LIMIT_EXCEEDED` | 超过安全大小/数量限制；拒绝文件，不截断。 | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `FILE_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `FILE_PASSWORD_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `FILE_PATH_UNSAFE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `FILE_REF_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `FILE_SCHEMA_INVALID` | 字段/类型/枚举/必填项无效；修正文件后重试。 | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `FILE_VERSION_UNSUPPORTED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `GOAL_DATE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `GOAL_HAS_HISTORY` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `GOAL_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `GOAL_RANGE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `GOAL_STATE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `GOAL_STATE_TRANSITION` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `HOME_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `IMPORT_DUPLICATE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `IMPORT_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `IMPORT_LIMIT_EXCEEDED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `INPUT_BYTE_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `INPUT_DUPLICATE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `INPUT_ENUM` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/DateEngine.kt` |
| `INPUT_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt`, `core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt` |
| `INPUT_RANGE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `INPUT_REQUIRED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `INPUT_TOO_LONG` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `JOB_CANCELED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt` |
| `JOB_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt` |
| `JOB_INTERRUPTED` | 进程退出中断了尚未提交的任务；重新选择文件操作。 | `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt` |
| `JOB_JOURNAL_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt` |
| `JOB_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt` |
| `JOB_STAGE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt` |
| `JOB_TYPE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt` |
| `LIBRARY_IDENTITY_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt` |
| `LIBRARY_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `LIBRARY_LIMIT_EXCEEDED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `LIBRARY_STALE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt` |
| `LIFECYCLE_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `LOCK_RATE_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `LOCK_REQUIRED` | 需先解锁；外部选择器结果等解锁后续行。 | `app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `LOCK_STATE_CORRUPT` | 访问锁验证文件损坏；安全锁定，不能默认解锁。 | `app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt` |
| `MEDIA_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `MEDIA_PATH_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `MEDIA_SIZE_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt` |
| `PARENT_NOT_ACTIVE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `PASSWORD_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `PASSWORD_REQUIRED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `PERMISSION_DENIED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `PHOTO_DECODE_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `PHOTO_DIMENSIONS_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `PHOTO_ENCODE_FAILED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `PHOTO_TOO_LARGE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `PHOTO_UNREADABLE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `PIN_INCORRECT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `PIN_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `PREVIEW_EXPIRED` | 预览超过30分钟；重新验证文件。 | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `PREVIEW_STALE` | 预览后库发生变化；重新预览文件。 | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt`, `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt` |
| `PURGE_NOT_IN_TRASH` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `REMINDER_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `REMINDER_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `REPEAT_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `REPLACE_CONFIRM_REQUIRED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `SHARE_EMPTY` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt` |
| `STAGING_NOT_EMPTY` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/FileCodec.kt` |
| `TAG_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `TAG_NAME_CONFLICT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `TAG_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `TEXT_REQUIRED` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `TEXT_TOO_LONG` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `TREE_BOOK_MISMATCH` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `TREE_CYCLE` | 不能移动到自身或自身后代；调整目标。 | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `TREE_DEPTH_EXCEEDED` | 最多三级，移动或导入后也不例外；调整目标上级。 | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `TREE_DEPTH_LIMIT` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `TREE_PARENT_NOT_FOUND` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `TREE_TOO_DEEP` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt` |
| `UNCHECKED_CAST` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt`, `core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt` |
| `USE_MOVE_SUBTREE` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `VERSION_CONFLICT` | 实体已更新；保留草稿并重新加载，不覆盖新版本。 | `app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt`, `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |
| `VERSION_INVALID` | 拒绝当前操作并保留已提交事实；根据字段修正输入/权限/文件或重试，禁止静默降级。  | `core/src/main/kotlin/cn/datebook/core/DateBookService.kt` |

数据库触发器另有CHECK_*诊断，用于阻止绕过领域层的非法写入；UI不应直接依赖SQLite自然语言错误。错误码不等于HTTP状态码，本应用没有HTTP服务。
'''
# END FILE: docs/ERROR_CODES.md


# ============================================================================
# BEGIN FILE: THIRD_PARTY_NOTICES.md
# ============================================================================
FILES['THIRD_PARTY_NOTICES.md'] = r'''# Third-party notices

Source dependencies are downloaded by Gradle from official repositories, not embedded application binaries in this delivery (except Gradle wrapper). Gradle/AndroidX/Kotlin/Kotlinx use their respective Apache-2.0 or compatible published licenses. Distribution must retain applicable upstream notices. This document does not grant Android SDK rights or auto-accept any SDK license.

## lunar-java 1.7.7 — MIT

Source: https://github.com/6tail/lunar-java/tree/v1.7.7
License: https://github.com/6tail/lunar-java/blob/v1.7.7/LICENSE

MIT License

Copyright (c) 2018 6tail

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Gradle wrapper 9.4.1 — Apache License 2.0

Official source and license: https://github.com/gradle/gradle/tree/v9.4.1
License text: https://www.apache.org/licenses/LICENSE-2.0
Copyright Gradle, Inc. and contributors. Distributed under the Apache License, Version 2.0, without warranties or conditions of any kind.

Official wrapper SHA256: `55243ef57851f12b070ad14f7f5bb8302daceeebc5bce5ece5fa6edb23e1145c`.
Distribution SHA256: `2ab2958f2a1e51120c326cad6f385153bb11ee93b3c216c5fccebfdfbb7ec6cb`.

## Golden lunar examples

Hong Kong Observatory calendar conversions are referenced by URL in LunarGoldenTests; no external calendar dataset or remote fetch is used at app runtime.
'''
# END FILE: THIRD_PARTY_NOTICES.md


# ============================================================================
# BEGIN FILE: .gitignore
# ============================================================================
FILES['.gitignore'] = r'''.gradle/
.kotlin/
.idea/
**/build/
local.properties
*.jks
*.keystore
captures/
host-test-results/
*.db
*.db-shm
*.db-wal
'''
# END FILE: .gitignore


# ============================================================================
# BEGIN FILE: app/build.gradle.kts
# ============================================================================
FILES['app/build.gradle.kts'] = r'''plugins {
 alias(libs.plugins.android.application)
 alias(libs.plugins.kotlin.compose)
 alias(libs.plugins.kotlin.serialization)
 alias(libs.plugins.ksp)
 alias(libs.plugins.room)
}
android {
 namespace = "cn.datebook.app"
 compileSdk = 37
 defaultConfig {
  applicationId = "cn.datebook.app"
  minSdk = 26
  targetSdk = 37
  versionCode = 1
  versionName = "1.0.0"
  testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
 }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
 buildFeatures { compose = true; buildConfig = true }
 buildTypes { release { isMinifyEnabled = true; proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro") } }
 packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}
room { schemaDirectory("$projectDir/schemas") }
dependencies {
 implementation(project(":core"))
 implementation(platform(libs.compose.bom))
 implementation(libs.compose.ui); implementation(libs.compose.preview); implementation(libs.compose.material3); implementation(libs.compose.icons)
 implementation(libs.activity); implementation(libs.lifecycle.runtime); implementation(libs.lifecycle.viewmodel); implementation(libs.navigation)
 implementation(libs.room.runtime); implementation(libs.room.ktx); ksp(libs.room.compiler)
 implementation(libs.coroutines.android); implementation(libs.serialization.json); implementation(libs.datastore)
 implementation(libs.work); implementation(libs.glance); implementation(libs.biometric); implementation(libs.lunar)
 implementation("androidx.core:core-ktx:1.16.0")
 debugImplementation(libs.compose.tooling)
 testImplementation(libs.junit)
 androidTestImplementation("androidx.test.ext:junit:1.2.1")
 androidTestImplementation("androidx.test:runner:1.6.2")
 androidTestImplementation("androidx.room:room-testing:2.8.5")
 androidTestImplementation(platform(libs.compose.bom))
 androidTestImplementation("androidx.compose.ui:ui-test-junit4")
 debugImplementation("androidx.compose.ui:ui-test-manifest")
}
'''
# END FILE: app/build.gradle.kts


# ============================================================================
# BEGIN FILE: app/proguard-rules.pro
# ============================================================================
FILES['app/proguard-rules.pro'] = r'''# Room and Compose ship consumer rules. Keep serialization companions for explicit generic command receipts.
-keepattributes Signature,InnerClasses,EnclosingMethod,RuntimeVisibleAnnotations,AnnotationDefault
-if @kotlinx.serialization.Serializable class **
-keepclassmembers class <1> { static <1>$Companion Companion; }
-keep,includedescriptorclasses class cn.datebook.core.**$$serializer { *; }
-dontwarn javax.annotation.**
'''
# END FILE: app/proguard-rules.pro


# ============================================================================
# BEGIN FILE: app/schemas/cn.datebook.app.data.DateBookDatabase/1.json
# ============================================================================
FILES['app/schemas/cn.datebook.app.data.DateBookDatabase/1.json'] = r'''{
  "formatVersion": 1,
  "database": {
    "version": 1,
    "identityHash": "719c9fc919783e4de813424b248a4b6c",
    "entities": [
      {
        "tableName": "library",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `singleton` INTEGER NOT NULL DEFAULT 1, `name` TEXT NOT NULL, `content_revision` INTEGER NOT NULL DEFAULT 0, `created_at` INTEGER NOT NULL, `updated_at` INTEGER NOT NULL, PRIMARY KEY(`id`))",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "singleton",
            "columnName": "singleton",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          },
          {
            "fieldPath": "name",
            "columnName": "name",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "content_revision",
            "columnName": "content_revision",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "updated_at",
            "columnName": "updated_at",
            "affinity": "INTEGER",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_library_singleton",
            "unique": true,
            "columnNames": [
              "singleton"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_library_singleton` ON `${TABLE_NAME}` (`singleton`)"
          }
        ]
      },
      {
        "tableName": "asset",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `sha256` TEXT NOT NULL, `relative_path` TEXT NOT NULL, `mime_type` TEXT NOT NULL, `byte_size` INTEGER NOT NULL, `width` INTEGER NOT NULL, `height` INTEGER NOT NULL, `created_at` INTEGER NOT NULL, PRIMARY KEY(`id`))",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "sha256",
            "columnName": "sha256",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "relative_path",
            "columnName": "relative_path",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "mime_type",
            "columnName": "mime_type",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "byte_size",
            "columnName": "byte_size",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "width",
            "columnName": "width",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "height",
            "columnName": "height",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_asset_sha256",
            "unique": true,
            "columnNames": [
              "sha256"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_asset_sha256` ON `${TABLE_NAME}` (`sha256`)"
          },
          {
            "name": "index_asset_relative_path",
            "unique": true,
            "columnNames": [
              "relative_path"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_asset_relative_path` ON `${TABLE_NAME}` (`relative_path`)"
          }
        ]
      },
      {
        "tableName": "book",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `library_id` TEXT NOT NULL, `name` TEXT NOT NULL, `name_key` TEXT NOT NULL, `builtin_key` TEXT, `is_protected` INTEGER NOT NULL DEFAULT 0, `icon_key` TEXT NOT NULL DEFAULT 'book', `color_argb` INTEGER NOT NULL DEFAULT -13278421, `cover_asset_id` TEXT, `sort_rank` INTEGER NOT NULL DEFAULT 0, `created_at` INTEGER NOT NULL, `updated_at` INTEGER NOT NULL, `version` INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(`id`), FOREIGN KEY(`library_id`) REFERENCES `library`(`id`) ON UPDATE NO ACTION ON DELETE RESTRICT , FOREIGN KEY(`cover_asset_id`) REFERENCES `asset`(`id`) ON UPDATE NO ACTION ON DELETE RESTRICT )",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "library_id",
            "columnName": "library_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "name",
            "columnName": "name",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "name_key",
            "columnName": "name_key",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "builtin_key",
            "columnName": "builtin_key",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "is_protected",
            "columnName": "is_protected",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "icon_key",
            "columnName": "icon_key",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'book'"
          },
          {
            "fieldPath": "color_argb",
            "columnName": "color_argb",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "-13278421"
          },
          {
            "fieldPath": "cover_asset_id",
            "columnName": "cover_asset_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "sort_rank",
            "columnName": "sort_rank",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "updated_at",
            "columnName": "updated_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "version",
            "columnName": "version",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_book_name_key",
            "unique": true,
            "columnNames": [
              "name_key"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_book_name_key` ON `${TABLE_NAME}` (`name_key`)"
          },
          {
            "name": "index_book_builtin_key",
            "unique": true,
            "columnNames": [
              "builtin_key"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_book_builtin_key` ON `${TABLE_NAME}` (`builtin_key`)"
          },
          {
            "name": "index_book_library_id",
            "unique": false,
            "columnNames": [
              "library_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_book_library_id` ON `${TABLE_NAME}` (`library_id`)"
          },
          {
            "name": "index_book_cover_asset_id",
            "unique": false,
            "columnNames": [
              "cover_asset_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_book_cover_asset_id` ON `${TABLE_NAME}` (`cover_asset_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "library",
            "onDelete": "RESTRICT",
            "onUpdate": "NO ACTION",
            "columns": [
              "library_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "asset",
            "onDelete": "RESTRICT",
            "onUpdate": "NO ACTION",
            "columns": [
              "cover_asset_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "event",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `book_id` TEXT NOT NULL, `parent_id` TEXT, `title` TEXT NOT NULL, `kind` TEXT NOT NULL, `count_mode` TEXT NOT NULL, `include_start_day` INTEGER NOT NULL DEFAULT 0, `greeting` TEXT NOT NULL DEFAULT '', `home_visible` INTEGER NOT NULL DEFAULT 1, `pinned` INTEGER NOT NULL DEFAULT 0, `sort_rank` INTEGER NOT NULL DEFAULT 0, `created_at` INTEGER NOT NULL, `updated_at` INTEGER NOT NULL, `version` INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(`id`), FOREIGN KEY(`book_id`) REFERENCES `book`(`id`) ON UPDATE NO ACTION ON DELETE RESTRICT , FOREIGN KEY(`parent_id`, `book_id`) REFERENCES `event`(`id`, `book_id`) ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED)",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "book_id",
            "columnName": "book_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "parent_id",
            "columnName": "parent_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "title",
            "columnName": "title",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "kind",
            "columnName": "kind",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "count_mode",
            "columnName": "count_mode",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "include_start_day",
            "columnName": "include_start_day",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "greeting",
            "columnName": "greeting",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "''"
          },
          {
            "fieldPath": "home_visible",
            "columnName": "home_visible",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          },
          {
            "fieldPath": "pinned",
            "columnName": "pinned",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "sort_rank",
            "columnName": "sort_rank",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "updated_at",
            "columnName": "updated_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "version",
            "columnName": "version",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_event_id_book_id",
            "unique": true,
            "columnNames": [
              "id",
              "book_id"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_event_id_book_id` ON `${TABLE_NAME}` (`id`, `book_id`)"
          },
          {
            "name": "event_by_parent",
            "unique": false,
            "columnNames": [
              "parent_id",
              "sort_rank",
              "id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `event_by_parent` ON `${TABLE_NAME}` (`parent_id`, `sort_rank`, `id`)"
          },
          {
            "name": "event_by_book",
            "unique": false,
            "columnNames": [
              "book_id",
              "sort_rank",
              "id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `event_by_book` ON `${TABLE_NAME}` (`book_id`, `sort_rank`, `id`)"
          },
          {
            "name": "event_by_home",
            "unique": false,
            "columnNames": [
              "home_visible",
              "pinned",
              "updated_at"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `event_by_home` ON `${TABLE_NAME}` (`home_visible`, `pinned`, `updated_at`)"
          },
          {
            "name": "index_event_parent_id_book_id",
            "unique": false,
            "columnNames": [
              "parent_id",
              "book_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_event_parent_id_book_id` ON `${TABLE_NAME}` (`parent_id`, `book_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "book",
            "onDelete": "RESTRICT",
            "onUpdate": "NO ACTION",
            "columns": [
              "book_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "event",
            "onDelete": "NO ACTION",
            "onUpdate": "NO ACTION",
            "columns": [
              "parent_id",
              "book_id"
            ],
            "referencedColumns": [
              "id",
              "book_id"
            ]
          }
        ]
      },
      {
        "tableName": "event_date",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`event_id` TEXT NOT NULL, `calendar_type` TEXT NOT NULL, `anchor_year` INTEGER, `anchor_month` INTEGER NOT NULL, `anchor_day` INTEGER NOT NULL, `is_leap_month` INTEGER NOT NULL DEFAULT 0, `all_day` INTEGER NOT NULL DEFAULT 1, `local_time` TEXT, `zone_id` TEXT, `feb29_policy` TEXT NOT NULL DEFAULT 'feb28', `lunar_leap_policy` TEXT NOT NULL DEFAULT 'normal_fallback', `lunar_small_month_policy` TEXT NOT NULL DEFAULT 'month_end', `calendar_engine_version` TEXT NOT NULL DEFAULT 'calendar-v1', PRIMARY KEY(`event_id`), FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "calendar_type",
            "columnName": "calendar_type",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "anchor_year",
            "columnName": "anchor_year",
            "affinity": "INTEGER"
          },
          {
            "fieldPath": "anchor_month",
            "columnName": "anchor_month",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "anchor_day",
            "columnName": "anchor_day",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "is_leap_month",
            "columnName": "is_leap_month",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "all_day",
            "columnName": "all_day",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          },
          {
            "fieldPath": "local_time",
            "columnName": "local_time",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "zone_id",
            "columnName": "zone_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "feb29_policy",
            "columnName": "feb29_policy",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'feb28'"
          },
          {
            "fieldPath": "lunar_leap_policy",
            "columnName": "lunar_leap_policy",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'normal_fallback'"
          },
          {
            "fieldPath": "lunar_small_month_policy",
            "columnName": "lunar_small_month_policy",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'month_end'"
          },
          {
            "fieldPath": "calendar_engine_version",
            "columnName": "calendar_engine_version",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'calendar-v1'"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "event_id"
          ]
        },
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "recurrence",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`event_id` TEXT NOT NULL, `frequency` TEXT NOT NULL, `interval_days` INTEGER, `until_iso` TEXT, PRIMARY KEY(`event_id`), FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "frequency",
            "columnName": "frequency",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "interval_days",
            "columnName": "interval_days",
            "affinity": "INTEGER"
          },
          {
            "fieldPath": "until_iso",
            "columnName": "until_iso",
            "affinity": "TEXT"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "event_id"
          ]
        },
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "appearance",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`event_id` TEXT NOT NULL, `background_kind` TEXT NOT NULL DEFAULT 'gradient', `asset_id` TEXT, `preset_key` TEXT NOT NULL DEFAULT 'forest', `solid_argb` INTEGER NOT NULL DEFAULT -13278421, `focus_x` REAL NOT NULL DEFAULT 0.5, `focus_y` REAL NOT NULL DEFAULT 0.5, `dim_amount` REAL NOT NULL DEFAULT 0.35, `text_color_mode` TEXT NOT NULL DEFAULT 'auto', `font_key` TEXT NOT NULL DEFAULT 'system', PRIMARY KEY(`event_id`), FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`asset_id`) REFERENCES `asset`(`id`) ON UPDATE NO ACTION ON DELETE RESTRICT )",
        "fields": [
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "background_kind",
            "columnName": "background_kind",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'gradient'"
          },
          {
            "fieldPath": "asset_id",
            "columnName": "asset_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "preset_key",
            "columnName": "preset_key",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'forest'"
          },
          {
            "fieldPath": "solid_argb",
            "columnName": "solid_argb",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "-13278421"
          },
          {
            "fieldPath": "focus_x",
            "columnName": "focus_x",
            "affinity": "REAL",
            "notNull": true,
            "defaultValue": "0.5"
          },
          {
            "fieldPath": "focus_y",
            "columnName": "focus_y",
            "affinity": "REAL",
            "notNull": true,
            "defaultValue": "0.5"
          },
          {
            "fieldPath": "dim_amount",
            "columnName": "dim_amount",
            "affinity": "REAL",
            "notNull": true,
            "defaultValue": "0.35"
          },
          {
            "fieldPath": "text_color_mode",
            "columnName": "text_color_mode",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'auto'"
          },
          {
            "fieldPath": "font_key",
            "columnName": "font_key",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'system'"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "event_id"
          ]
        },
        "indices": [
          {
            "name": "index_appearance_asset_id",
            "unique": false,
            "columnNames": [
              "asset_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_appearance_asset_id` ON `${TABLE_NAME}` (`asset_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "asset",
            "onDelete": "RESTRICT",
            "onUpdate": "NO ACTION",
            "columns": [
              "asset_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "goal_detail",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`event_id` TEXT NOT NULL, `start_iso` TEXT NOT NULL, `state` TEXT NOT NULL, `completed_at` INTEGER, `include_in_parent` INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(`event_id`), FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "start_iso",
            "columnName": "start_iso",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "state",
            "columnName": "state",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "completed_at",
            "columnName": "completed_at",
            "affinity": "INTEGER"
          },
          {
            "fieldPath": "include_in_parent",
            "columnName": "include_in_parent",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "event_id"
          ]
        },
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "action_record",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `goal_event_id` TEXT NOT NULL, `action_date_iso` TEXT NOT NULL, `body` TEXT NOT NULL, `minutes` INTEGER, `created_at` INTEGER NOT NULL, `updated_at` INTEGER NOT NULL, `version` INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(`id`), FOREIGN KEY(`goal_event_id`) REFERENCES `goal_detail`(`event_id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "goal_event_id",
            "columnName": "goal_event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "action_date_iso",
            "columnName": "action_date_iso",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "body",
            "columnName": "body",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "minutes",
            "columnName": "minutes",
            "affinity": "INTEGER"
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "updated_at",
            "columnName": "updated_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "version",
            "columnName": "version",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "actions_by_goal_date",
            "unique": false,
            "columnNames": [
              "goal_event_id",
              "action_date_iso",
              "id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `actions_by_goal_date` ON `${TABLE_NAME}` (`goal_event_id`, `action_date_iso`, `id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "goal_detail",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "goal_event_id"
            ],
            "referencedColumns": [
              "event_id"
            ]
          }
        ]
      },
      {
        "tableName": "lifecycle_cause",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `kind` TEXT NOT NULL, `source_event_id` TEXT, `source_book_id` TEXT, `created_at` INTEGER NOT NULL, `purge_after` INTEGER, PRIMARY KEY(`id`), FOREIGN KEY(`source_event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE SET NULL , FOREIGN KEY(`source_book_id`) REFERENCES `book`(`id`) ON UPDATE NO ACTION ON DELETE SET NULL )",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "kind",
            "columnName": "kind",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "source_event_id",
            "columnName": "source_event_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "source_book_id",
            "columnName": "source_book_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "purge_after",
            "columnName": "purge_after",
            "affinity": "INTEGER"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_lifecycle_cause_source_event_id",
            "unique": false,
            "columnNames": [
              "source_event_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_lifecycle_cause_source_event_id` ON `${TABLE_NAME}` (`source_event_id`)"
          },
          {
            "name": "index_lifecycle_cause_source_book_id",
            "unique": false,
            "columnNames": [
              "source_book_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_lifecycle_cause_source_book_id` ON `${TABLE_NAME}` (`source_book_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "SET NULL",
            "onUpdate": "NO ACTION",
            "columns": [
              "source_event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "book",
            "onDelete": "SET NULL",
            "onUpdate": "NO ACTION",
            "columns": [
              "source_book_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "lifecycle_member",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`cause_id` TEXT NOT NULL, `event_id` TEXT NOT NULL, PRIMARY KEY(`cause_id`, `event_id`), FOREIGN KEY(`cause_id`) REFERENCES `lifecycle_cause`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "cause_id",
            "columnName": "cause_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "cause_id",
            "event_id"
          ]
        },
        "indices": [
          {
            "name": "lifecycle_by_event",
            "unique": false,
            "columnNames": [
              "event_id",
              "cause_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `lifecycle_by_event` ON `${TABLE_NAME}` (`event_id`, `cause_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "lifecycle_cause",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "cause_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "tag",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `name` TEXT NOT NULL, `name_key` TEXT NOT NULL, `created_at` INTEGER NOT NULL, PRIMARY KEY(`id`))",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "name",
            "columnName": "name",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "name_key",
            "columnName": "name_key",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_tag_name_key",
            "unique": true,
            "columnNames": [
              "name_key"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_tag_name_key` ON `${TABLE_NAME}` (`name_key`)"
          }
        ]
      },
      {
        "tableName": "event_tag",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`event_id` TEXT NOT NULL, `tag_id` TEXT NOT NULL, PRIMARY KEY(`event_id`, `tag_id`), FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`tag_id`) REFERENCES `tag`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "tag_id",
            "columnName": "tag_id",
            "affinity": "TEXT",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "event_id",
            "tag_id"
          ]
        },
        "indices": [
          {
            "name": "index_event_tag_tag_id",
            "unique": false,
            "columnNames": [
              "tag_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_event_tag_tag_id` ON `${TABLE_NAME}` (`tag_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "tag",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "tag_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "reminder_rule",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `event_id` TEXT NOT NULL, `enabled` INTEGER NOT NULL DEFAULT 0, `offset_unit` TEXT NOT NULL, `offset_value` INTEGER NOT NULL, `local_time` TEXT, `precision_mode` TEXT NOT NULL DEFAULT 'normal', `version` INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(`id`), FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "enabled",
            "columnName": "enabled",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "offset_unit",
            "columnName": "offset_unit",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "offset_value",
            "columnName": "offset_value",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "local_time",
            "columnName": "local_time",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "precision_mode",
            "columnName": "precision_mode",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'normal'"
          },
          {
            "fieldPath": "version",
            "columnName": "version",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "1"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "reminder_by_event",
            "unique": false,
            "columnNames": [
              "event_id",
              "enabled"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `reminder_by_event` ON `${TABLE_NAME}` (`event_id`, `enabled`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "home_config",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`singleton` INTEGER NOT NULL, `hero_mode` TEXT NOT NULL DEFAULT 'auto', `fixed_event_id` TEXT, `sort_mode` TEXT NOT NULL DEFAULT 'date', `selected_book_id` TEXT, PRIMARY KEY(`singleton`), FOREIGN KEY(`fixed_event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE SET NULL , FOREIGN KEY(`selected_book_id`) REFERENCES `book`(`id`) ON UPDATE NO ACTION ON DELETE SET NULL )",
        "fields": [
          {
            "fieldPath": "singleton",
            "columnName": "singleton",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "hero_mode",
            "columnName": "hero_mode",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'auto'"
          },
          {
            "fieldPath": "fixed_event_id",
            "columnName": "fixed_event_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "sort_mode",
            "columnName": "sort_mode",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'date'"
          },
          {
            "fieldPath": "selected_book_id",
            "columnName": "selected_book_id",
            "affinity": "TEXT"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "singleton"
          ]
        },
        "indices": [
          {
            "name": "index_home_config_fixed_event_id",
            "unique": false,
            "columnNames": [
              "fixed_event_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_home_config_fixed_event_id` ON `${TABLE_NAME}` (`fixed_event_id`)"
          },
          {
            "name": "index_home_config_selected_book_id",
            "unique": false,
            "columnNames": [
              "selected_book_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_home_config_selected_book_id` ON `${TABLE_NAME}` (`selected_book_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "SET NULL",
            "onUpdate": "NO ACTION",
            "columns": [
              "fixed_event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "book",
            "onDelete": "SET NULL",
            "onUpdate": "NO ACTION",
            "columns": [
              "selected_book_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "import_batch",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `format` TEXT NOT NULL, `source_export_id` TEXT NOT NULL, `file_sha256` TEXT NOT NULL, `imported_at` INTEGER NOT NULL, PRIMARY KEY(`id`))",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "format",
            "columnName": "format",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "source_export_id",
            "columnName": "source_export_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "file_sha256",
            "columnName": "file_sha256",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "imported_at",
            "columnName": "imported_at",
            "affinity": "INTEGER",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_import_batch_file_sha256",
            "unique": true,
            "columnNames": [
              "file_sha256"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_import_batch_file_sha256` ON `${TABLE_NAME}` (`file_sha256`)"
          },
          {
            "name": "index_import_batch_id_source_export_id",
            "unique": true,
            "columnNames": [
              "id",
              "source_export_id"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_import_batch_id_source_export_id` ON `${TABLE_NAME}` (`id`, `source_export_id`)"
          }
        ]
      },
      {
        "tableName": "import_provenance",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`batch_id` TEXT NOT NULL, `source_export_id` TEXT NOT NULL, `source_ref` TEXT NOT NULL, `local_event_id` TEXT, PRIMARY KEY(`batch_id`, `source_ref`), FOREIGN KEY(`batch_id`) REFERENCES `import_batch`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`local_event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE SET NULL , FOREIGN KEY(`batch_id`, `source_export_id`) REFERENCES `import_batch`(`id`, `source_export_id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "batch_id",
            "columnName": "batch_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "source_export_id",
            "columnName": "source_export_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "source_ref",
            "columnName": "source_ref",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "local_event_id",
            "columnName": "local_event_id",
            "affinity": "TEXT"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "batch_id",
            "source_ref"
          ]
        },
        "indices": [
          {
            "name": "index_import_provenance_source_export_id_source_ref",
            "unique": true,
            "columnNames": [
              "source_export_id",
              "source_ref"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_import_provenance_source_export_id_source_ref` ON `${TABLE_NAME}` (`source_export_id`, `source_ref`)"
          },
          {
            "name": "index_import_provenance_local_event_id",
            "unique": false,
            "columnNames": [
              "local_event_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_import_provenance_local_event_id` ON `${TABLE_NAME}` (`local_event_id`)"
          },
          {
            "name": "index_import_provenance_batch_id_source_export_id",
            "unique": false,
            "columnNames": [
              "batch_id",
              "source_export_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_import_provenance_batch_id_source_export_id` ON `${TABLE_NAME}` (`batch_id`, `source_export_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "import_batch",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "batch_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "event",
            "onDelete": "SET NULL",
            "onUpdate": "NO ACTION",
            "columns": [
              "local_event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          },
          {
            "table": "import_batch",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "batch_id",
              "source_export_id"
            ],
            "referencedColumns": [
              "id",
              "source_export_id"
            ]
          }
        ]
      },
      {
        "tableName": "device_epoch",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`singleton` INTEGER NOT NULL, `epoch` TEXT NOT NULL, `plan_token` TEXT NOT NULL, `schedule_revision` INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(`singleton`))",
        "fields": [
          {
            "fieldPath": "singleton",
            "columnName": "singleton",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "epoch",
            "columnName": "epoch",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "plan_token",
            "columnName": "plan_token",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "schedule_revision",
            "columnName": "schedule_revision",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "singleton"
          ]
        }
      },
      {
        "tableName": "reminder_queue",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`rule_id` TEXT NOT NULL, `occurrence_key` TEXT NOT NULL, `fire_at` INTEGER NOT NULL, `rule_version` INTEGER NOT NULL, `event_version` INTEGER NOT NULL, `epoch` TEXT NOT NULL, PRIMARY KEY(`rule_id`), FOREIGN KEY(`rule_id`) REFERENCES `reminder_rule`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "rule_id",
            "columnName": "rule_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "occurrence_key",
            "columnName": "occurrence_key",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "fire_at",
            "columnName": "fire_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "rule_version",
            "columnName": "rule_version",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "event_version",
            "columnName": "event_version",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "epoch",
            "columnName": "epoch",
            "affinity": "TEXT",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "rule_id"
          ]
        },
        "indices": [
          {
            "name": "reminder_by_fire",
            "unique": false,
            "columnNames": [
              "fire_at",
              "rule_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `reminder_by_fire` ON `${TABLE_NAME}` (`fire_at`, `rule_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "reminder_rule",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "rule_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "delivery_log",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`epoch` TEXT NOT NULL, `rule_id` TEXT NOT NULL, `occurrence_key` TEXT NOT NULL, `event_id` TEXT NOT NULL, `rule_version` INTEGER NOT NULL, `event_version` INTEGER NOT NULL, `fire_at` INTEGER NOT NULL, `valid_until` INTEGER NOT NULL, `state` TEXT NOT NULL, `notification_tag` TEXT NOT NULL, `attempted_at` INTEGER, `attempt_count` INTEGER NOT NULL DEFAULT 0, `next_attempt_at` INTEGER NOT NULL, `last_error_code` TEXT, PRIMARY KEY(`epoch`, `rule_id`, `rule_version`, `occurrence_key`))",
        "fields": [
          {
            "fieldPath": "epoch",
            "columnName": "epoch",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "rule_id",
            "columnName": "rule_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "occurrence_key",
            "columnName": "occurrence_key",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "rule_version",
            "columnName": "rule_version",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "event_version",
            "columnName": "event_version",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "fire_at",
            "columnName": "fire_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "valid_until",
            "columnName": "valid_until",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "state",
            "columnName": "state",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "notification_tag",
            "columnName": "notification_tag",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "attempted_at",
            "columnName": "attempted_at",
            "affinity": "INTEGER"
          },
          {
            "fieldPath": "attempt_count",
            "columnName": "attempt_count",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "next_attempt_at",
            "columnName": "next_attempt_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "last_error_code",
            "columnName": "last_error_code",
            "affinity": "TEXT"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "epoch",
            "rule_id",
            "rule_version",
            "occurrence_key"
          ]
        },
        "indices": [
          {
            "name": "delivery_by_state_retry",
            "unique": false,
            "columnNames": [
              "state",
              "next_attempt_at"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `delivery_by_state_retry` ON `${TABLE_NAME}` (`state`, `next_attempt_at`)"
          }
        ]
      },
      {
        "tableName": "device_binding",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `event_id` TEXT, `kind` TEXT NOT NULL, `external_id` TEXT NOT NULL, `calendar_id` TEXT, `last_written_hash` TEXT, `coverage_json` TEXT NOT NULL DEFAULT '[]', `epoch` TEXT NOT NULL, `state` TEXT NOT NULL, PRIMARY KEY(`id`), FOREIGN KEY(`event_id`) REFERENCES `event`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "event_id",
            "columnName": "event_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "kind",
            "columnName": "kind",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "external_id",
            "columnName": "external_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "calendar_id",
            "columnName": "calendar_id",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "last_written_hash",
            "columnName": "last_written_hash",
            "affinity": "TEXT"
          },
          {
            "fieldPath": "coverage_json",
            "columnName": "coverage_json",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'[]'"
          },
          {
            "fieldPath": "epoch",
            "columnName": "epoch",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "state",
            "columnName": "state",
            "affinity": "TEXT",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_device_binding_kind_external_id",
            "unique": true,
            "columnNames": [
              "kind",
              "external_id"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_device_binding_kind_external_id` ON `${TABLE_NAME}` (`kind`, `external_id`)"
          },
          {
            "name": "index_device_binding_event_id",
            "unique": false,
            "columnNames": [
              "event_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_device_binding_event_id` ON `${TABLE_NAME}` (`event_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "event",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "event_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "effect_outbox",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `kind` TEXT NOT NULL, `scope_id` TEXT NOT NULL DEFAULT 'library', `target_revision` INTEGER NOT NULL, `epoch` TEXT NOT NULL, `attempts` INTEGER NOT NULL DEFAULT 0, `next_attempt_at` INTEGER NOT NULL, `created_at` INTEGER NOT NULL, PRIMARY KEY(`id`))",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "kind",
            "columnName": "kind",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "scope_id",
            "columnName": "scope_id",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'library'"
          },
          {
            "fieldPath": "target_revision",
            "columnName": "target_revision",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "epoch",
            "columnName": "epoch",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "attempts",
            "columnName": "attempts",
            "affinity": "INTEGER",
            "notNull": true,
            "defaultValue": "0"
          },
          {
            "fieldPath": "next_attempt_at",
            "columnName": "next_attempt_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "created_at",
            "columnName": "created_at",
            "affinity": "INTEGER",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        },
        "indices": [
          {
            "name": "index_effect_outbox_kind_scope_id_target_revision_epoch",
            "unique": true,
            "columnNames": [
              "kind",
              "scope_id",
              "target_revision",
              "epoch"
            ],
            "orders": [],
            "createSql": "CREATE UNIQUE INDEX IF NOT EXISTS `index_effect_outbox_kind_scope_id_target_revision_epoch` ON `${TABLE_NAME}` (`kind`, `scope_id`, `target_revision`, `epoch`)"
          }
        ]
      },
      {
        "tableName": "backup_receipt",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`id` TEXT NOT NULL, `snapshot_revision` INTEGER NOT NULL, `backup_id` TEXT NOT NULL, `completed_at` INTEGER NOT NULL, `encrypted` INTEGER NOT NULL, `file_sha256` TEXT NOT NULL, PRIMARY KEY(`id`))",
        "fields": [
          {
            "fieldPath": "id",
            "columnName": "id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "snapshot_revision",
            "columnName": "snapshot_revision",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "backup_id",
            "columnName": "backup_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "completed_at",
            "columnName": "completed_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "encrypted",
            "columnName": "encrypted",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "file_sha256",
            "columnName": "file_sha256",
            "affinity": "TEXT",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "id"
          ]
        }
      },
      {
        "tableName": "asset_lease",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`job_id` TEXT NOT NULL, `asset_id` TEXT NOT NULL, `expires_at` INTEGER NOT NULL, PRIMARY KEY(`job_id`, `asset_id`), FOREIGN KEY(`asset_id`) REFERENCES `asset`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )",
        "fields": [
          {
            "fieldPath": "job_id",
            "columnName": "job_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "asset_id",
            "columnName": "asset_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "expires_at",
            "columnName": "expires_at",
            "affinity": "INTEGER",
            "notNull": true
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "job_id",
            "asset_id"
          ]
        },
        "indices": [
          {
            "name": "lease_by_expiry",
            "unique": false,
            "columnNames": [
              "expires_at"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `lease_by_expiry` ON `${TABLE_NAME}` (`expires_at`)"
          },
          {
            "name": "index_asset_lease_asset_id",
            "unique": false,
            "columnNames": [
              "asset_id"
            ],
            "orders": [],
            "createSql": "CREATE INDEX IF NOT EXISTS `index_asset_lease_asset_id` ON `${TABLE_NAME}` (`asset_id`)"
          }
        ],
        "foreignKeys": [
          {
            "table": "asset",
            "onDelete": "CASCADE",
            "onUpdate": "NO ACTION",
            "columns": [
              "asset_id"
            ],
            "referencedColumns": [
              "id"
            ]
          }
        ]
      },
      {
        "tableName": "command_receipt",
        "createSql": "CREATE TABLE IF NOT EXISTS `${TABLE_NAME}` (`operation_id` TEXT NOT NULL, `command_hash` TEXT NOT NULL, `epoch` TEXT NOT NULL, `entity_id` TEXT NOT NULL, `entity_version` INTEGER NOT NULL, `content_revision` INTEGER NOT NULL, `committed_at` INTEGER NOT NULL, `result_type` TEXT NOT NULL DEFAULT 'unit', `result_json` TEXT NOT NULL DEFAULT 'null', PRIMARY KEY(`operation_id`))",
        "fields": [
          {
            "fieldPath": "operation_id",
            "columnName": "operation_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "command_hash",
            "columnName": "command_hash",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "epoch",
            "columnName": "epoch",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "entity_id",
            "columnName": "entity_id",
            "affinity": "TEXT",
            "notNull": true
          },
          {
            "fieldPath": "entity_version",
            "columnName": "entity_version",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "content_revision",
            "columnName": "content_revision",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "committed_at",
            "columnName": "committed_at",
            "affinity": "INTEGER",
            "notNull": true
          },
          {
            "fieldPath": "result_type",
            "columnName": "result_type",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'unit'"
          },
          {
            "fieldPath": "result_json",
            "columnName": "result_json",
            "affinity": "TEXT",
            "notNull": true,
            "defaultValue": "'null'"
          }
        ],
        "primaryKey": {
          "autoGenerate": false,
          "columnNames": [
            "operation_id"
          ]
        }
      }
    ],
    "setupQueries": [
      "CREATE TABLE IF NOT EXISTS room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)",
      "INSERT OR REPLACE INTO room_master_table (id,identity_hash) VALUES(42, '719c9fc919783e4de813424b248a4b6c')"
    ]
  }
}'''
# END FILE: app/schemas/cn.datebook.app.data.DateBookDatabase/1.json


# ============================================================================
# BEGIN FILE: app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt
# ============================================================================
FILES['app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt'] = r'''package cn.datebook.app

import android.content.Context
import android.content.ContextWrapper
import androidx.room.Room
import androidx.room.withTransaction
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import cn.datebook.app.data.*
import cn.datebook.core.*
import kotlinx.coroutines.*
import org.junit.*
import org.junit.Assert.*
import org.junit.runner.RunWith
import java.io.File

/** Must run with connectedDebugAndroidTest. Host SQLite checks are not a substitute. */
@RunWith(AndroidJUnit4::class)
class DatabaseTests {
 private lateinit var db: DateBookDatabase
 private lateinit var sandbox: File
 private lateinit var context: Context
 @Before fun setup() {
  val base = InstrumentationRegistry.getInstrumentation().targetContext
  sandbox = File(base.cacheDir, "database-test-${newId()}").apply { mkdirs() }
  context = object : ContextWrapper(base) {
   override fun getApplicationContext(): Context = this
   override fun getNoBackupFilesDir(): File = File(sandbox, "private").apply { mkdirs() }
  }
  db = Room.inMemoryDatabaseBuilder(context, DateBookDatabase::class.java).allowMainThreadQueries().addCallback(SchemaGuards).build()
  val sql = db.openHelper.writableDatabase
  sql.execSQL("INSERT INTO library(id,name,created_at,updated_at) VALUES('l','测试',0,0)")
  sql.execSQL("INSERT INTO book(id,library_id,name,name_key,builtin_key,is_protected,created_at,updated_at) VALUES('b','l','默认','默认','uncategorized',1,0,0)")
  sql.execSQL("INSERT INTO book(id,library_id,name,name_key,created_at,updated_at) VALUES('other','l','其他','其他',0,0)")
 }
 @After fun teardown() { db.close(); sandbox.deleteRecursively() }

 private fun insert(id: String, parent: String? = null, book: String = "b") = db.openHelper.writableDatabase.execSQL(
  "INSERT INTO event(id,book_id,parent_id,title,kind,count_mode,created_at,updated_at) VALUES(?,?,?,?,'ordinary','down',0,0)", arrayOf(id, book, parent, id))
 private fun rejected(fragment: String, action: () -> Unit) {
  val error = runCatching(action).exceptionOrNull()
  assertNotNull("Expected rejection $fragment", error)
  assertTrue("Wrong diagnostic: $error", error.toString().contains(fragment))
 }
 private fun count(table: String): Int = db.openHelper.writableDatabase.query("SELECT count(*) FROM `$table`").use { it.moveToFirst(); it.getInt(0) }

 @Test fun twentyFiveNormalizedTablesAndFortyTwoGuards() {
  db.openHelper.writableDatabase.query("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT IN ('android_metadata','room_master_table')").use {
   it.moveToFirst(); assertEquals(25, it.getInt(0))
  }
  SchemaGuards.verify(db.openHelper.writableDatabase)
 }
 @Test fun missingParentIsRejectedImmediately() { rejected("TREE_PARENT_NOT_FOUND") { insert("child", "missing") }; assertEquals(0, count("event")) }
 @Test fun reverseInsertionCannotBypassDeferredForeignKeys() = runBlocking {
  rejected("TREE_PARENT_NOT_FOUND") { insert("d", "c") }; assertEquals(0, count("event"))
 }
 @Test fun threeLevelsAreAllowedAndFourthIsRejected() {
  insert("a"); insert("b", "a"); insert("c", "b")
  rejected("TREE_DEPTH_EXCEEDED") { insert("d", "c") }; assertEquals(3, count("event"))
 }
 @Test fun selfParentAndCycleMoveAreRejected() {
  insert("a"); insert("b", "a")
  rejected("TREE_CYCLE") { db.openHelper.writableDatabase.execSQL("UPDATE event SET parent_id='b' WHERE id='a'") }
  rejected("TREE_CYCLE") { db.openHelper.writableDatabase.execSQL("UPDATE event SET parent_id='a' WHERE id='a'") }
 }
 @Test fun movingWholeSubtreeChecksItsHeight() {
  insert("a"); insert("b", "a"); insert("c", "b"); insert("r"); insert("s", "r")
  rejected("TREE_DEPTH_EXCEEDED") { db.openHelper.writableDatabase.execSQL("UPDATE event SET parent_id='s' WHERE id='b'") }
 }
 @Test fun idIsImmutable() {
  insert("a"); rejected("EVENT_ID_IMMUTABLE") { db.openHelper.writableDatabase.execSQL("UPDATE event SET id='changed' WHERE id='a'") }
 }
 @Test fun subtreeBookMoveCanCommitAsOneTransaction() = runBlocking {
  insert("a"); insert("b", "a"); insert("c", "b")
  db.withTransaction { db.openHelper.writableDatabase.execSQL("UPDATE event SET book_id='other' WHERE id IN ('a','b','c')") }
  db.openHelper.writableDatabase.query("PRAGMA foreign_key_check").use { assertFalse(it.moveToFirst()) }
 }
 @Test fun protectedBookCannotBeDeleted() { rejected("BOOK_PROTECTED") { db.openHelper.writableDatabase.execSQL("DELETE FROM book WHERE id='b'") } }
 @Test fun utf8ByteCapsDoNotPretendToBeGraphemeCaps() {
  insert("a")
  val sixtyFamilies = "👨‍👩‍👧‍👦".repeat(60)
  db.openHelper.writableDatabase.execSQL("UPDATE event SET title=? WHERE id='a'", arrayOf(sixtyFamilies))
  rejected("CHECK_event") { db.openHelper.writableDatabase.execSQL("UPDATE event SET title=? WHERE id='a'", arrayOf("a".repeat(4097))) }
 }
 @Test fun everyNDaysRequiresANonNullIntervalOnInsertAndUpdate() {
  insert("a")
  rejected("CHECK_recurrence") { db.openHelper.writableDatabase.execSQL("INSERT INTO recurrence(event_id,frequency) VALUES('a','every_n_days')") }
  db.openHelper.writableDatabase.execSQL("INSERT INTO recurrence(event_id,frequency,interval_days) VALUES('a','every_n_days',7)")
  rejected("CHECK_recurrence") { db.openHelper.writableDatabase.execSQL("UPDATE recurrence SET interval_days=NULL WHERE event_id='a'") }
 }
 @Test fun checkedEnumsAndAppearanceRangesRejectRawSqlBypasses() {
  insert("a")
  rejected("CHECK_event") { db.openHelper.writableDatabase.execSQL("UPDATE event SET kind='unknown' WHERE id='a'") }
  rejected("CHECK_appearance") { db.openHelper.writableDatabase.execSQL("INSERT INTO appearance(event_id,focus_x) VALUES('a',2)") }
  rejected("CHECK_appearance") { db.openHelper.writableDatabase.execSQL("INSERT INTO appearance(event_id,background_kind) VALUES('a','photo')") }
 }
 @Test fun sixthReminderCannotBeInsertedOrMoved() {
  insert("a"); insert("b")
  for (i in 1..5) db.openHelper.writableDatabase.execSQL("INSERT INTO reminder_rule(id,event_id,offset_unit,offset_value) VALUES(?,'a','days',0)", arrayOf("r$i"))
  rejected("REMINDER_LIMIT") { db.openHelper.writableDatabase.execSQL("INSERT INTO reminder_rule(id,event_id,offset_unit,offset_value) VALUES('sixth','a','days',0)") }
  db.openHelper.writableDatabase.execSQL("INSERT INTO reminder_rule(id,event_id,offset_unit,offset_value) VALUES('other-rule','b','days',0)")
  rejected("REMINDER_LIMIT") { db.openHelper.writableDatabase.execSQL("UPDATE reminder_rule SET event_id='a' WHERE id='other-rule'") }
 }
 @Test fun importProvenanceIsUniqueAcrossBatches() {
  val sql = db.openHelper.writableDatabase
  sql.execSQL("INSERT INTO import_batch VALUES('one','events_json','export','hash1',0)")
  sql.execSQL("INSERT INTO import_batch VALUES('two','events_json','export','hash2',0)")
  sql.execSQL("INSERT INTO import_provenance VALUES('one','export','source',NULL)")
  rejected("UNIQUE") { sql.execSQL("INSERT INTO import_provenance VALUES('two','export','source',NULL)") }
 }
 @Test fun outboxScopeIsNonNullAndDuplicateEffectsCoalesce() {
  val sql = db.openHelper.writableDatabase
  sql.execSQL("INSERT INTO effect_outbox(id,kind,target_revision,epoch,next_attempt_at,created_at) VALUES('a','replan',1,'e',0,0)")
  rejected("UNIQUE") { sql.execSQL("INSERT INTO effect_outbox(id,kind,target_revision,epoch,next_attempt_at,created_at) VALUES('b','replan',1,'e',0,0)") }
  rejected("NOT NULL") { sql.execSQL("INSERT INTO effect_outbox(id,kind,scope_id,target_revision,epoch,next_attempt_at,created_at) VALUES('b','replan',NULL,1,'e',0,0)") }
 }
 @Test fun failedFactTransactionRollsBackEverything() = runBlocking {
  runCatching { db.withTransaction { insert("a"); insert("b", "missing") } }
  assertEquals(0, count("event"))
 }
 @Test fun roomStorePersistsFullIndependentEventFactsAndReopens() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  val book = store.state.value.books.first()
  val event = Event(bookId = book.id, title = "独立事件", date = DateSpec(year = 2027, month = 6, day = 1),
   greeting = "每一级都有自己的文字", appearance = Appearance(backgroundKind = "solid", solidArgb = -12345),
   reminders = listOf(ReminderRule(enabled = true)))
  store.transaction("save") { Change(it.copy(events = listOf(event)), event) }
  val firstEpoch = store.state.value.epoch
  store.close()
  val reopened = RoomStore(context)
  try { reopened.awaitReady(); assertEquals(event, reopened.state.value.events.single()); assertEquals(firstEpoch, reopened.state.value.epoch) }
  finally { reopened.close() }
 }
 @Test fun durableReceiptReplaysWithoutExecutingCommandAgain() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  val id = store.transaction("idempotent") { Change(it, "result") }
  assertEquals("result", id); store.close()
  val reopened = RoomStore(context)
  try {
   reopened.awaitReady()
   val result: String = reopened.transaction("idempotent") { throw AssertionError("Receipt must prevent reexecution") }
   assertEquals("result", result)
  } finally { reopened.close() }
 }
 @Test fun importFormatMapperPreservesSharedModelAndDesignEnum() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  val batch = ImportBatch(format = "json", sourceExportId = "external-export", fileSha256 = "a".repeat(64), importedAt = 1)
  try {
   store.transaction("import-metadata") { Change(it.copy(imports = listOf(batch)), Unit) }
   store.withDb { database, _, _ -> database.openHelper.writableDatabase.query("SELECT format FROM import_batch").use {
    assertTrue(it.moveToFirst()); assertEquals("events_json", it.getString(0))
   } }
  } finally { store.close() }
  val reopened = RoomStore(context)
  try { reopened.awaitReady(); assertEquals(batch, reopened.state.value.imports.single()) } finally { reopened.close() }
 }
 @Test fun cancellationBeforeCommitDoesNotPublishPartialFacts() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  try {
   val original = store.state.value
   val command = launch {
    store.transaction("cancel-before-commit") {
     cancel()
     Change(it.copy(name = "不应提交"), Unit)
    }
   }
   command.join()
   assertEquals(original, store.state.value)
   store.withDb { database, _, _ -> database.openHelper.writableDatabase.query("SELECT name FROM library").use {
    assertTrue(it.moveToFirst()); assertEquals(original.name, it.getString(0))
   } }
  } finally { store.close() }
 }
 @Test fun staleRestoreCannotReplaceChangedData() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  try {
   val old = store.state.value
   store.transaction("rename") { Change(it.copy(name = "已更新"), Unit) }
   val error = runCatching { store.install(old, old.revision, old.epoch) }.exceptionOrNull()
   assertEquals("PREVIEW_STALE", (error as AppException).code)
   assertEquals("已更新", store.state.value.name)
  } finally { store.close() }
 }
 @Test fun successfulRestoreHasNewEpochAndSurvivesReopen() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  val old = store.state.value
  val installed = store.install(old.copy(name = "恢复结果"), old.revision, old.epoch)
  assertNotEquals(old.epoch, installed.epoch); assertEquals(old.revision + 1, installed.revision)
  store.close()
  val reopened = RoomStore(context)
  try { reopened.awaitReady(); assertEquals(installed, reopened.state.value) } finally { reopened.close() }
 }
 @Test fun assetLeaseProtectsUnattachedPhotoUntilClosed() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  try {
   val source = File(sandbox, "pixel.png").apply { writeBytes(byteArrayOf(1,2,3)) }
   val asset = store.addAsset(source, "image/png", 1, 1)
   store.transaction("age-photo") { Change(it.copy(assets = it.assets.map { a -> a.copy(createdAt = 0) }), Unit) }
   val lease = store.leaseSnapshot()
   store.gc(); assertTrue(store.assetFile(asset.relativePath).isFile)
   lease.close(); store.gc(); assertFalse(store.assetFile(asset.relativePath).exists())
  } finally { store.close() }
 }
 @Test fun canceledExporterReleasesItsLeaseInFinally() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  try {
   val source = File(sandbox, "leased.png").apply { writeBytes(byteArrayOf(1,2,3)) }
   val asset = store.addAsset(source, "image/png", 1, 1)
   store.transaction("age-canceled-photo") { Change(it.copy(assets = it.assets.map { a -> a.copy(createdAt = 0) }), Unit) }
   val acquired = CompletableDeferred<Unit>()
   val exporter = launch {
    val lease = store.leaseSnapshot()
    try { acquired.complete(Unit); awaitCancellation() } finally { lease.close() }
   }
   acquired.await()
   exporter.cancelAndJoin()
   store.withDb { database, _, _ -> database.openHelper.writableDatabase.query("SELECT count(*) FROM asset_lease").use {
    assertTrue(it.moveToFirst()); assertEquals(0, it.getInt(0))
   } }
   store.gc()
   assertFalse(store.assetFile(asset.relativePath).exists())
  } finally { store.close() }
 }
 @Test fun pathTraversalAndSymlinkEscapeAreRejected() = runBlocking {
  val store = RoomStore(context); store.awaitReady()
  try {
   listOf("../escape", "/absolute", "assets/../../escape", "assets\\escape").forEach { path ->
    val error = runCatching { store.assetFile(path) }.exceptionOrNull()
    assertEquals("MEDIA_PATH_INVALID", (error as AppException).code)
   }
  } finally { store.close() }
 }
 @Test fun invalidPointerIsSurfacedAndNeverCreatesAnEmptyLibrary() = runBlocking {
  val storage = File(context.noBackupFilesDir, "datebook").apply { mkdirs() }
  File(storage, "current").writeText("../../outside")
  val store = RoomStore(context)
  try {
   val error = runCatching { store.awaitReady() }.exceptionOrNull()
   assertNotNull(error); assertNotNull(store.startupError.value); assertFalse(store.ready.value)
   assertEquals("../../outside", File(storage, "current").readText())
  } finally { store.close() }
 }
 @Test fun committedPointerWinsOverLeftoverCrashJournal() = runBlocking {
  val first = RoomStore(context); first.awaitReady()
  first.transaction("name") { Change(it.copy(name = "已提交"), Unit) }; first.close()
  val root = File(context.noBackupFilesDir, "datebook")
  File(root, "commit-journal").writeText("old-generation\nnew-generation\nold-epoch")
  val reopened = RoomStore(context)
  try { reopened.awaitReady(); assertEquals("已提交", reopened.state.value.name); assertFalse(File(root, "commit-journal").exists()) }
  finally { reopened.close() }
 }
}
'''
# END FILE: app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt


# ============================================================================
# BEGIN FILE: app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt
# ============================================================================
FILES['app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt'] = r'''package cn.datebook.app

import android.content.Intent
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import cn.datebook.core.*
import kotlinx.coroutines.runBlocking
import org.junit.*
import java.time.LocalDate

/** Authored device tests; run connectedDebugAndroidTest. They are not host tests. */
class UiTests {
 @get:Rule val compose=createEmptyComposeRule()
 private lateinit var graph:AppGraph
 private var activity:ActivityScenario<MainActivity>?=null
 private lateinit var root:Event
 private lateinit var second:Event
 private lateinit var third:Event
 @Before fun seed()=runBlocking {
  val app=InstrumentationRegistry.getInstrumentation().targetContext.applicationContext as DateBookApplication
  graph=app.graph;graph.store.awaitReady();graph.lock.clearForReplacement()
  val old=graph.store.state.value;val state=defaultLibrary();val book=state.books.first().id
  val date=LocalDate.now().plusDays(30);val d=DateSpec(year=date.year,month=date.monthValue,day=date.dayOfMonth)
  root=Event(bookId=book,title="测试根",date=d,greeting="仅属于根的寄语")
  second=Event(bookId=book,parentId=root.id,title="测试二级",date=d,greeting="仅属于二级的寄语")
  third=Event(bookId=book,parentId=second.id,title="测试三级",date=d,greeting="仅属于三级的寄语")
  graph.store.install(state.copy(events=listOf(root,second,third)),old.revision,old.epoch)
 }
 private fun launch(id:String?=null) {
  val context=InstrumentationRegistry.getInstrumentation().targetContext
  activity=ActivityScenario.launch(Intent(context,MainActivity::class.java).apply{id?.let{putExtra("eventId",it)}})
  compose.waitForIdle()
 }
 @After fun close(){activity?.close();graph.lock.clearForReplacement()}
 @Test fun homeListsOnlyOptedInRoot(){launch();compose.onAllNodesWithText("测试根").onFirst().assertExists();compose.onNodeWithText("测试二级").assertDoesNotExist();compose.onNodeWithText("测试三级").assertDoesNotExist()}
 @Test fun rootDetailOnlyShowsItsImmediateChildren(){launch(root.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("测试二级"));compose.onNodeWithText("测试二级").assertExists();compose.onNodeWithText("测试三级").assertDoesNotExist();compose.onNodeWithText("仅属于二级的寄语",useUnmergedTree=true).assertExists()}
 @Test fun secondDetailShowsThirdNotItsDescendants(){launch(second.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("测试三级"));compose.onNodeWithText("测试三级").assertExists();compose.onNodeWithText("仅属于根的寄语").assertDoesNotExist()}
 @Test fun thirdDetailCannotCreateFourth(){launch(third.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("已到第三级，不支持继续新增下级"));compose.onNodeWithText("已到第三级，不支持继续新增下级").assertIsDisplayed();compose.onNodeWithText("添加子事件").assertDoesNotExist()}
 @Test fun greetingIsSingleCurrentEventText(){launch(root.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("仅属于根的寄语"));compose.onNodeWithText("仅属于根的寄语").assertExists();compose.onNodeWithText("小纸条").assertDoesNotExist()}
 @Test fun missingDeepLinkDoesNotCreateAnEvent(){launch(newId());compose.onNodeWithText("重要的日子").assertExists();Assert.assertEquals(3,graph.store.state.value.events.size)}
 @Test fun appLockHidesLibraryBeforeUnlock(){graph.lock.setPin("123456".toCharArray());graph.lock.lock();launch(root.id);compose.onNodeWithText("请解锁本机资料库").assertExists();compose.onNodeWithText("测试根").assertDoesNotExist()}
 @Test fun appDeclaresNoInternetOrAccountsPermission(){
  val c=InstrumentationRegistry.getInstrumentation().targetContext
  @Suppress("DEPRECATION") val requested=c.packageManager.getPackageInfo(c.packageName,android.content.pm.PackageManager.GET_PERMISSIONS).requestedPermissions.orEmpty()
  Assert.assertFalse("android.permission.INTERNET" in requested);Assert.assertFalse("android.permission.GET_ACCOUNTS" in requested)
 }
}
'''
# END FILE: app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt


# ============================================================================
# BEGIN FILE: app/src/main/AndroidManifest.xml
# ============================================================================
FILES['app/src/main/AndroidManifest.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
 <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
 <uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM"/>
 <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
 <uses-permission android:name="android.permission.USE_BIOMETRIC"/>
 <uses-permission android:name="android.permission.READ_CALENDAR"/>
 <application android:name=".DateBookApplication" android:allowBackup="false" android:fullBackupContent="@xml/backup_rules" android:dataExtractionRules="@xml/data_extraction_rules" android:label="@string/app_name" android:icon="@drawable/ic_datebook" android:theme="@style/Theme.DateBook" android:supportsRtl="true">
  <activity android:name=".MainActivity" android:exported="true" android:windowSoftInputMode="adjustResize">
   <intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
  </activity>
  <receiver android:name=".platform.ReminderReceiver" android:exported="false"/>
  <receiver android:name=".platform.RebuildReceiver" android:exported="false">
   <intent-filter><action android:name="android.intent.action.BOOT_COMPLETED"/><action android:name="android.intent.action.MY_PACKAGE_REPLACED"/><action android:name="android.intent.action.TIME_SET"/><action android:name="android.intent.action.TIMEZONE_CHANGED"/><action android:name="android.app.action.SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED"/></intent-filter>
  </receiver>
  <receiver android:name=".platform.DateBookWidgetReceiver" android:exported="true">
   <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE"/></intent-filter>
   <meta-data android:name="android.appwidget.provider" android:resource="@xml/widget_info"/>
  </receiver>
  <activity android:name=".platform.WidgetConfigureActivity" android:exported="true">
   <intent-filter><action android:name="android.appwidget.action.APPWIDGET_CONFIGURE"/></intent-filter>
  </activity>
  <provider android:name="androidx.core.content.FileProvider" android:authorities="${applicationId}.files" android:exported="false" android:grantUriPermissions="true">
   <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/file_paths"/>
  </provider>
 </application>
</manifest>
'''
# END FILE: app/src/main/AndroidManifest.xml


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt'] = r'''package cn.datebook.app

import android.app.Application
import android.content.Context
import androidx.work.*
import cn.datebook.app.data.RoomStore
import cn.datebook.app.platform.*
import cn.datebook.core.*
import kotlinx.coroutines.*
import java.time.Clock
import java.util.concurrent.TimeUnit

class DateBookApplication : Application() {
 lateinit var graph: AppGraph; private set
 override fun onCreate() {
  super.onCreate()
  graph = AppGraph(this)
  // Previews are process-local. Snapshot only pre-existing private staging paths;
  // never sweep a newly-created current-process restore or a user-picked backup.
  val orphanStaging=cacheDir.listFiles().orEmpty().filter{it.name.matches(Regex("(?:restore|merge)-[0-9a-f-]{36}"))}
  val orphanFiles=cacheDir.listFiles().orEmpty().filter{it.name.matches(Regex("export-[0-9a-f-]{36}\\.tmp|photo-[0-9-]+\\.(?:tmp|jpg)"))}+
   graph.store.root.listFiles().orEmpty().filter{it.name.matches(Regex("datebook-payload-[0-9-]+\\.zip"))}
  graph.scope.launch {
   orphanFiles.forEach { file -> runCatching {
    if(file.parentFile?.canonicalFile in setOf(cacheDir.canonicalFile,graph.store.root.canonicalFile))java.nio.file.Files.deleteIfExists(file.toPath())
   } }
   orphanStaging.forEach { directory -> runCatching {
    if(directory.parentFile?.canonicalFile==cacheDir.canonicalFile)java.nio.file.Files.walkFileTree(directory.toPath(),object:java.nio.file.SimpleFileVisitor<java.nio.file.Path>() {
     override fun visitFile(file:java.nio.file.Path,attrs:java.nio.file.attribute.BasicFileAttributes):java.nio.file.FileVisitResult {java.nio.file.Files.deleteIfExists(file);return java.nio.file.FileVisitResult.CONTINUE}
     override fun postVisitDirectory(dir:java.nio.file.Path,error:java.io.IOException?):java.nio.file.FileVisitResult {if(error!=null)throw error;java.nio.file.Files.deleteIfExists(dir);return java.nio.file.FileVisitResult.CONTINUE}
    })
   } }
  }
  graph.scope.launch {
   try {
    graph.store.awaitReady()
    graph.service.purgeExpired()
    graph.systems.reconcile()
    graph.systems.refreshWidgets()
    graph.store.gc()
   } catch (_: Exception) { /* Startup error is exposed by RoomStore, never replace data. */ }
  }
  WorkManager.getInstance(this).enqueueUniquePeriodicWork("datebook-maintenance", ExistingPeriodicWorkPolicy.KEEP,
   PeriodicWorkRequestBuilder<MaintenanceWorker>(12, TimeUnit.HOURS).build())
 }
}

class AppGraph(context: Context) {
 val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
 val store = RoomStore(context)
 val dates = DateEngine(Clock.systemDefaultZone(), LunarAdapter())
 val service = DateBookService(store, dates, Clock.systemDefaultZone())
 val codec = FileCodec(dates)
 val lock = LockManager(context)
 val jobs = JobManager(store.root, scope)
 val systems = SystemServices(context, store, dates)
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt'] = r'''package cn.datebook.app

import cn.datebook.core.LunarPort
import com.nlf.calendar.Lunar
import com.nlf.calendar.LunarYear
import com.nlf.calendar.Solar
import java.time.LocalDate

/** Pinned offline engine; never consults device ICU or the network. */
class LunarAdapter : LunarPort {
 override fun solar(year: Int, month: Int, day: Int, leapMonth: Boolean, leapPolicy: String, smallMonthPolicy: String): LocalDate? {
  if (year !in 1901..2099 || month !in 1..12 || day !in 1..30) return null
  val lunarYear = LunarYear.fromYear(year)
  var target = lunarYear.getMonth(if (leapMonth) -month else month)
  if (target == null && leapMonth && leapPolicy == "normal_fallback") target = lunarYear.getMonth(month)
  target ?: return null
  if (day > target.dayCount && smallMonthPolicy == "skip") return null
  val solar = Lunar.fromYmd(year, target.month, minOf(day, target.dayCount)).solar
  return LocalDate.of(solar.year, solar.month, solar.day)
 }
 override fun lunarYear(date: LocalDate): Int = Solar.fromYmd(date.year, date.monthValue, date.dayOfMonth).lunar.year
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/MainActivity.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/MainActivity.kt'] = r'''package cn.datebook.app

import android.content.Intent
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.fragment.app.FragmentActivity
import cn.datebook.app.ui.AppViewModel
import cn.datebook.app.ui.DateBookRoot
import kotlinx.coroutines.flow.MutableStateFlow

class MainActivity : FragmentActivity() {
 private val model: AppViewModel by viewModels()
 private val requestedEvent=MutableStateFlow<String?>(null)
 override fun onCreate(savedInstanceState:Bundle?) {
  super.onCreate(savedInstanceState)
  window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
  readIntent(intent)
  setContent { DateBookRoot(model,this,requestedEvent) { requestedEvent.value=null } }
 }
 override fun onNewIntent(intent:Intent) { super.onNewIntent(intent); setIntent(intent);readIntent(intent) }
 private fun readIntent(intent:Intent?) {
  val uri=intent?.data
  requestedEvent.value=if(uri?.scheme=="daybook"&&uri.host=="event"&&uri.pathSegments.size==2)uri.pathSegments.joinToString("/")
   else intent?.getStringExtra("eventId")?:intent?.getStringExtra("event_id")?:intent?.getStringExtra("id")
 }
 override fun onStop() { super.onStop(); if(!isChangingConfigurations) (application as DateBookApplication).graph.lock.lock() }
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/MainActivity.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/data/Entities.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/data/Entities.kt'] = r'''package cn.datebook.app.data

import android.database.Cursor
import androidx.room.*
import androidx.sqlite.db.SupportSQLiteQuery

// Normalized facts; device-only rows are deliberately not part of LibraryState backups.

@Entity(tableName = "library", primaryKeys = ["id"], indices = [
 Index(value = ["singleton"], unique = true)])
data class DbLibrary(
 val id: String,
 @ColumnInfo(defaultValue = "1") val singleton: Long,
 val name: String,
 @ColumnInfo(defaultValue = "0") val content_revision: Long,
 val created_at: Long,
 val updated_at: Long
)

@Entity(tableName = "asset", primaryKeys = ["id"], indices = [
 Index(value = ["sha256"], unique = true),
 Index(value = ["relative_path"], unique = true)])
data class DbAsset(
 val id: String,
 val sha256: String,
 val relative_path: String,
 val mime_type: String,
 val byte_size: Long,
 val width: Long,
 val height: Long,
 val created_at: Long
)

@Entity(tableName = "book", primaryKeys = ["id"], indices = [
 Index(value = ["name_key"], unique = true),
 Index(value = ["builtin_key"], unique = true),
 Index(value = ["library_id"], unique = false),
 Index(value = ["cover_asset_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbLibrary::class, parentColumns = ["id"], childColumns = ["library_id"], onDelete = ForeignKey.RESTRICT, deferred = false),
 ForeignKey(entity = DbAsset::class, parentColumns = ["id"], childColumns = ["cover_asset_id"], onDelete = ForeignKey.RESTRICT, deferred = false)])
data class DbBook(
 val id: String,
 val library_id: String,
 val name: String,
 val name_key: String,
 val builtin_key: String?,
 @ColumnInfo(defaultValue = "0") val is_protected: Long,
 @ColumnInfo(defaultValue = "'book'") val icon_key: String,
 @ColumnInfo(defaultValue = "-13278421") val color_argb: Long,
 val cover_asset_id: String?,
 @ColumnInfo(defaultValue = "0") val sort_rank: Long,
 val created_at: Long,
 val updated_at: Long,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "event", primaryKeys = ["id"], indices = [
 Index(value = ["id", "book_id"], unique = true),
 Index(value = ["parent_id", "sort_rank", "id"], unique = false, name = "event_by_parent"),
 Index(value = ["book_id", "sort_rank", "id"], unique = false, name = "event_by_book"),
 Index(value = ["home_visible", "pinned", "updated_at"], unique = false, name = "event_by_home"),
 Index(value = ["parent_id", "book_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbBook::class, parentColumns = ["id"], childColumns = ["book_id"], onDelete = ForeignKey.RESTRICT, deferred = false),
 ForeignKey(entity = DbEvent::class, parentColumns = ["id", "book_id"], childColumns = ["parent_id", "book_id"], onDelete = ForeignKey.NO_ACTION, deferred = true)])
data class DbEvent(
 val id: String,
 val book_id: String,
 val parent_id: String?,
 val title: String,
 val kind: String,
 val count_mode: String,
 @ColumnInfo(defaultValue = "0") val include_start_day: Long,
 @ColumnInfo(defaultValue = "''") val greeting: String,
 @ColumnInfo(defaultValue = "1") val home_visible: Long,
 @ColumnInfo(defaultValue = "0") val pinned: Long,
 @ColumnInfo(defaultValue = "0") val sort_rank: Long,
 val created_at: Long,
 val updated_at: Long,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "event_date", primaryKeys = ["event_id"], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbEventDate(
 val event_id: String,
 val calendar_type: String,
 val anchor_year: Long?,
 val anchor_month: Long,
 val anchor_day: Long,
 @ColumnInfo(defaultValue = "0") val is_leap_month: Long,
 @ColumnInfo(defaultValue = "1") val all_day: Long,
 val local_time: String?,
 val zone_id: String?,
 @ColumnInfo(defaultValue = "'feb28'") val feb29_policy: String,
 @ColumnInfo(defaultValue = "'normal_fallback'") val lunar_leap_policy: String,
 @ColumnInfo(defaultValue = "'month_end'") val lunar_small_month_policy: String,
 @ColumnInfo(defaultValue = "'calendar-v1'") val calendar_engine_version: String
)

@Entity(tableName = "recurrence", primaryKeys = ["event_id"], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbRecurrence(
 val event_id: String,
 val frequency: String,
 val interval_days: Long?,
 val until_iso: String?
)

@Entity(tableName = "appearance", primaryKeys = ["event_id"], indices = [
 Index(value = ["asset_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbAsset::class, parentColumns = ["id"], childColumns = ["asset_id"], onDelete = ForeignKey.RESTRICT, deferred = false)])
data class DbAppearance(
 val event_id: String,
 @ColumnInfo(defaultValue = "'gradient'") val background_kind: String,
 val asset_id: String?,
 @ColumnInfo(defaultValue = "'forest'") val preset_key: String,
 @ColumnInfo(defaultValue = "-13278421") val solid_argb: Long,
 @ColumnInfo(defaultValue = "0.5") val focus_x: Double,
 @ColumnInfo(defaultValue = "0.5") val focus_y: Double,
 @ColumnInfo(defaultValue = "0.35") val dim_amount: Double,
 @ColumnInfo(defaultValue = "'auto'") val text_color_mode: String,
 @ColumnInfo(defaultValue = "'system'") val font_key: String
)

@Entity(tableName = "goal_detail", primaryKeys = ["event_id"], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbGoalDetail(
 val event_id: String,
 val start_iso: String,
 val state: String,
 val completed_at: Long?,
 @ColumnInfo(defaultValue = "1") val include_in_parent: Long
)

@Entity(tableName = "action_record", primaryKeys = ["id"], indices = [
 Index(value = ["goal_event_id", "action_date_iso", "id"], unique = false, name = "actions_by_goal_date")], foreignKeys = [
 ForeignKey(entity = DbGoalDetail::class, parentColumns = ["event_id"], childColumns = ["goal_event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbActionRecord(
 val id: String,
 val goal_event_id: String,
 val action_date_iso: String,
 val body: String,
 val minutes: Long?,
 val created_at: Long,
 val updated_at: Long,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "lifecycle_cause", primaryKeys = ["id"], indices = [
 Index(value = ["source_event_id"], unique = false),
 Index(value = ["source_book_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["source_event_id"], onDelete = ForeignKey.SET_NULL, deferred = false),
 ForeignKey(entity = DbBook::class, parentColumns = ["id"], childColumns = ["source_book_id"], onDelete = ForeignKey.SET_NULL, deferred = false)])
data class DbLifecycleCause(
 val id: String,
 val kind: String,
 val source_event_id: String?,
 val source_book_id: String?,
 val created_at: Long,
 val purge_after: Long?
)

@Entity(tableName = "lifecycle_member", primaryKeys = ["cause_id", "event_id"], indices = [
 Index(value = ["event_id", "cause_id"], unique = false, name = "lifecycle_by_event")], foreignKeys = [
 ForeignKey(entity = DbLifecycleCause::class, parentColumns = ["id"], childColumns = ["cause_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbLifecycleMember(
 val cause_id: String,
 val event_id: String
)

@Entity(tableName = "tag", primaryKeys = ["id"], indices = [
 Index(value = ["name_key"], unique = true)])
data class DbTag(
 val id: String,
 val name: String,
 val name_key: String,
 val created_at: Long
)

@Entity(tableName = "event_tag", primaryKeys = ["event_id", "tag_id"], indices = [
 Index(value = ["tag_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbTag::class, parentColumns = ["id"], childColumns = ["tag_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbEventTag(
 val event_id: String,
 val tag_id: String
)

@Entity(tableName = "reminder_rule", primaryKeys = ["id"], indices = [
 Index(value = ["event_id", "enabled"], unique = false, name = "reminder_by_event")], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbReminderRule(
 val id: String,
 val event_id: String,
 @ColumnInfo(defaultValue = "0") val enabled: Long,
 val offset_unit: String,
 val offset_value: Long,
 val local_time: String?,
 @ColumnInfo(defaultValue = "'normal'") val precision_mode: String,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "home_config", primaryKeys = ["singleton"], indices = [
 Index(value = ["fixed_event_id"], unique = false),
 Index(value = ["selected_book_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["fixed_event_id"], onDelete = ForeignKey.SET_NULL, deferred = false),
 ForeignKey(entity = DbBook::class, parentColumns = ["id"], childColumns = ["selected_book_id"], onDelete = ForeignKey.SET_NULL, deferred = false)])
data class DbHomeConfig(
 val singleton: Long,
 @ColumnInfo(defaultValue = "'auto'") val hero_mode: String,
 val fixed_event_id: String?,
 @ColumnInfo(defaultValue = "'date'") val sort_mode: String,
 val selected_book_id: String?
)

@Entity(tableName = "import_batch", primaryKeys = ["id"], indices = [
 Index(value = ["file_sha256"], unique = true),
 Index(value = ["id", "source_export_id"], unique = true)])
data class DbImportBatch(
 val id: String,
 val format: String,
 val source_export_id: String,
 val file_sha256: String,
 val imported_at: Long
)

@Entity(tableName = "import_provenance", primaryKeys = ["batch_id", "source_ref"], indices = [
 Index(value = ["source_export_id", "source_ref"], unique = true),
 Index(value = ["local_event_id"], unique = false),
 Index(value = ["batch_id", "source_export_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbImportBatch::class, parentColumns = ["id"], childColumns = ["batch_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["local_event_id"], onDelete = ForeignKey.SET_NULL, deferred = false),
 ForeignKey(entity = DbImportBatch::class, parentColumns = ["id", "source_export_id"], childColumns = ["batch_id", "source_export_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbImportProvenance(
 val batch_id: String,
 val source_export_id: String,
 val source_ref: String,
 val local_event_id: String?
)

@Entity(tableName = "device_epoch", primaryKeys = ["singleton"])
data class DbDeviceEpoch(
 val singleton: Long,
 val epoch: String,
 val plan_token: String,
 @ColumnInfo(defaultValue = "0") val schedule_revision: Long
)

@Entity(tableName = "reminder_queue", primaryKeys = ["rule_id"], indices = [
 Index(value = ["fire_at", "rule_id"], unique = false, name = "reminder_by_fire")], foreignKeys = [
 ForeignKey(entity = DbReminderRule::class, parentColumns = ["id"], childColumns = ["rule_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbReminderQueue(
 val rule_id: String,
 val occurrence_key: String,
 val fire_at: Long,
 val rule_version: Long,
 val event_version: Long,
 val epoch: String
)

@Entity(tableName = "delivery_log", primaryKeys = ["epoch", "rule_id", "rule_version", "occurrence_key"], indices = [
 Index(value = ["state", "next_attempt_at"], unique = false, name = "delivery_by_state_retry")])
data class DbDeliveryLog(
 val epoch: String,
 val rule_id: String,
 val occurrence_key: String,
 val event_id: String,
 val rule_version: Long,
 val event_version: Long,
 val fire_at: Long,
 val valid_until: Long,
 val state: String,
 val notification_tag: String,
 val attempted_at: Long?,
 @ColumnInfo(defaultValue = "0") val attempt_count: Long,
 val next_attempt_at: Long,
 val last_error_code: String?
)

@Entity(tableName = "device_binding", primaryKeys = ["id"], indices = [
 Index(value = ["kind", "external_id"], unique = true),
 Index(value = ["event_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbDeviceBinding(
 val id: String,
 val event_id: String?,
 val kind: String,
 val external_id: String,
 val calendar_id: String?,
 val last_written_hash: String?,
 @ColumnInfo(defaultValue = "'[]'") val coverage_json: String,
 val epoch: String,
 val state: String
)

@Entity(tableName = "effect_outbox", primaryKeys = ["id"], indices = [
 Index(value = ["kind", "scope_id", "target_revision", "epoch"], unique = true)])
data class DbEffectOutbox(
 val id: String,
 val kind: String,
 @ColumnInfo(defaultValue = "'library'") val scope_id: String,
 val target_revision: Long,
 val epoch: String,
 @ColumnInfo(defaultValue = "0") val attempts: Long,
 val next_attempt_at: Long,
 val created_at: Long
)

@Entity(tableName = "backup_receipt", primaryKeys = ["id"])
data class DbBackupReceipt(
 val id: String,
 val snapshot_revision: Long,
 val backup_id: String,
 val completed_at: Long,
 val encrypted: Long,
 val file_sha256: String
)

@Entity(tableName = "asset_lease", primaryKeys = ["job_id", "asset_id"], indices = [
 Index(value = ["expires_at"], unique = false, name = "lease_by_expiry"),
 Index(value = ["asset_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbAsset::class, parentColumns = ["id"], childColumns = ["asset_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbAssetLease(
 val job_id: String,
 val asset_id: String,
 val expires_at: Long
)

@Entity(tableName = "command_receipt", primaryKeys = ["operation_id"])
data class DbCommandReceipt(
 val operation_id: String,
 val command_hash: String,
 val epoch: String,
 val entity_id: String,
 val entity_version: Long,
 val content_revision: Long,
 val committed_at: Long,
 @ColumnInfo(defaultValue = "'unit'") val result_type: String,
 @ColumnInfo(defaultValue = "'null'") val result_json: String
)

@Dao interface DeviceDao {
 @RawQuery fun query(query: SupportSQLiteQuery): Cursor
}
@Database(entities = [DbLibrary::class, DbAsset::class, DbBook::class, DbEvent::class, DbEventDate::class, DbRecurrence::class, DbAppearance::class, DbGoalDetail::class, DbActionRecord::class, DbLifecycleCause::class, DbLifecycleMember::class, DbTag::class, DbEventTag::class, DbReminderRule::class, DbHomeConfig::class, DbImportBatch::class, DbImportProvenance::class, DbDeviceEpoch::class, DbReminderQueue::class, DbDeliveryLog::class, DbDeviceBinding::class, DbEffectOutbox::class, DbBackupReceipt::class, DbAssetLease::class, DbCommandReceipt::class], version = 1, exportSchema = true)
abstract class DateBookDatabase : RoomDatabase() {
 abstract fun dao(): DeviceDao
}

'''
# END FILE: app/src/main/kotlin/cn/datebook/app/data/Entities.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt'] = r'''package cn.datebook.app.data

import android.content.Context
import android.util.AtomicFile
import androidx.room.Room
import androidx.room.withTransaction
import androidx.sqlite.db.SupportSQLiteDatabase
import cn.datebook.core.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import java.io.Closeable
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.security.MessageDigest
import java.text.Normalizer
import java.util.Locale

/** Single-process generation gate. Never retain a Room handle beyond withDb. */
class RoomStore(context: Context) : LibraryRepository, Closeable {
 private val app = context.applicationContext
 val root = File(app.noBackupFilesDir, "datebook").apply { mkdirs() }
 private val gate = Mutex()
 private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
 private val pointer = AtomicFile(File(root, "current"))
 private val journal = AtomicFile(File(root, "commit-journal"))
 private val initialized = CompletableDeferred<Unit>()
 private val mutableState = MutableStateFlow(LibraryState())
 override val state: StateFlow<LibraryState> = mutableState.asStateFlow()
 private val mutableError = MutableStateFlow<AppException?>(null)
 val startupError: StateFlow<AppException?> = mutableError.asStateFlow()
 private val mutableReady = MutableStateFlow(false)
 val ready: StateFlow<Boolean> = mutableReady.asStateFlow()
 @Volatile private var current: Generation? = null
 @Volatile private var closed = false
 private val json = Json { encodeDefaults = true; ignoreUnknownKeys = false }
 private data class Generation(val name: String, val directory: File, val db: DateBookDatabase)

 init {
  scope.launch {
   try {
    gate.withLock {
     current = if (pointer.baseFile.exists() || File(root, "current.bak").exists()) {
      openGeneration(readAtomic(pointer).trim())
     } else {
      // A damaged existing installation is never replaced by an empty library.
      demand(root.listFiles().orEmpty().none { it.isDirectory && it.name.startsWith("g-") }, "DB_POINTER_MISSING")
      val first = createGeneration(defaultLibrary())
      atomicWrite(pointer, first.name)
      first
     }
     mutableState.value = load(current!!.db)
     LibraryValidator.validate(mutableState.value)
     // The atomic pointer is the commit point. A journal only identifies cleanup work.
     if (journal.baseFile.exists() || File(root, "commit-journal.bak").exists()) journal.delete()
     mutableReady.value = true
    }
    initialized.complete(Unit)
   } catch (error: Throwable) {
    val reported = if (error is AppException) error else AppException("DB_OPEN_FAILED", message = error.message ?: "无法打开本机数据库")
    mutableError.value = reported
    initialized.completeExceptionally(reported)
   }
  }
 }

 suspend fun awaitReady() { initialized.await(); demand(!closed, "DB_CLOSED") }

 /** The callback runs on IO under a coroutine Mutex, not a thread-affine lock. */
 suspend fun <T> withDb(block: suspend (DateBookDatabase, LibraryState, File) -> T): T = withContext(Dispatchers.IO) {
  awaitReady()
  gate.withLock {
   demand(!closed, "DB_CLOSED")
   val generation = current ?: throw AppException("DB_OPEN_FAILED")
   block(generation.db, mutableState.value, generation.directory)
  }
 }

 @Suppress("UNCHECKED_CAST")
 override suspend fun <T> transaction(operationId: String, expectedEpoch: String?, block: (LibraryState) -> Change<T>): T =
  withDb { database, old, _ ->
   demand(operationId.isNotBlank() && operationId.length <= 128, "INPUT_INVALID", "operationId")
   demand(expectedEpoch == null || expectedEpoch == old.epoch, "LIBRARY_STALE")
   val sql = database.openHelper.writableDatabase
   val replay = rows(sql, "command_receipt", "operation_id=?", arrayOf(operationId)).firstOrNull()
   if (replay != null) {
    demand(replay.s("epoch") == old.epoch, "LIBRARY_STALE")
    return@withDb decodeResult(replay.s("result_type"), replay.s("result_json")) as T
   }
   val change = block(old)
   demand(change.state.id == old.id && change.state.epoch == old.epoch && change.state.revision == old.revision, "LIBRARY_IDENTITY_INVALID")
   LibraryValidator.validate(change.state)
   val result = encodeResult(change.result) // Fail unsupported result types before committing facts.
   val next = if (change.state == old) old else change.state.copy(revision = old.revision + 1, updatedAt = System.currentTimeMillis())
   currentCoroutineContext().ensureActive()
   withContext(NonCancellable) {
    database.withTransaction {
     if (next != old) { persist(sql, next, old); enqueueEffects(sql, next) }
     write(sql, "command_receipt", mapOf("operation_id" to operationId, "command_hash" to hash(result.second.toByteArray()),
      "epoch" to next.epoch, "entity_id" to resultId(change.result), "entity_version" to resultVersion(change.result),
      "content_revision" to next.revision, "committed_at" to System.currentTimeMillis(), "result_type" to result.first, "result_json" to result.second), listOf("operation_id"))
    }
    mutableState.value = next
   }
   change.result
  }

 override suspend fun install(candidate: LibraryState, expectedRevision: Long, expectedEpoch: String): LibraryState =
  installFrom(candidate, null, expectedRevision, expectedEpoch)

 /** mediaRoot is a trusted private extraction directory, with asset relative paths below it. */
 suspend fun installFrom(candidate: LibraryState, mediaRoot: File?, expectedRevision: Long, expectedEpoch: String): LibraryState = withContext(Dispatchers.IO) {
  awaitReady()
  LibraryValidator.validate(candidate)
  val source = leaseSnapshot()
  var staged: Generation? = null
  var committed = false
  try {
   demand(source.state.epoch == expectedEpoch && source.state.revision == expectedRevision, "PREVIEW_STALE")
   val next = candidate.copy(epoch = newId(), revision = expectedRevision + 1, updatedAt = System.currentTimeMillis())
   val prepared = createGeneration(next, mediaRoot ?: source.root)
   staged = prepared
   gate.withLock {
    demand(!closed, "DB_CLOSED")
    val old = mutableState.value
    demand(old.epoch == expectedEpoch && old.revision == expectedRevision, "PREVIEW_STALE")
    // Device bindings are kept as historical, untrusted references; restore never writes a calendar.
    val prior = current!!
    prepared.db.withTransaction {
     val target = prepared.db.openHelper.writableDatabase
     for (binding in rows(prior.db.openHelper.writableDatabase, "device_binding")) {
      val eventId = binding["event_id"]
      if (eventId == null || next.events.any { it.id == eventId }) {
       val preserved = binding.toMutableMap<String, Any?>()
       preserved["state"] = "unknown"
       write(target, "device_binding", preserved, listOf("id"))
      }
     }
     enqueueEffects(target, next)
    }
    atomicWrite(journal, prior.name + "\n" + prepared.name + "\n" + old.epoch)
    atomicWrite(pointer, prepared.name)
    // Do not suspend between pointer commit and in-memory handle publication.
    current = prepared
    mutableState.value = next
    committed = true
    prior.db.close()
    journal.delete()
   }
   next
  } finally {
   withContext(NonCancellable) {
    source.close()
    if (!committed) staged?.let { it.db.close(); deleteGeneration(it.directory) }
   }
  }
 }

 class SnapshotLease internal constructor(val state: LibraryState, val root: File, private val release: suspend () -> Unit) {
  private val mutex = Mutex()
  private var closed = false
  suspend fun close() = withContext(NonCancellable) {
   mutex.withLock { if (!closed) { release(); closed = true } }
  }
 }

 suspend fun leaseSnapshot(): SnapshotLease = withDb { database, snapshot, directory ->
  val jobId = newId()
  val expires = System.currentTimeMillis() + 24 * 60 * 60 * 1000L
  database.withTransaction {
   val sql = database.openHelper.writableDatabase
   snapshot.assets.forEach { asset -> write(sql, "asset_lease", mapOf("job_id" to jobId, "asset_id" to asset.id, "expires_at" to expires), listOf("job_id", "asset_id")) }
  }
  // Backup IO runs without holding the generation gate. The lease pins the old generation too.
  SnapshotLease(snapshot, directory) {
   withContext(Dispatchers.IO) {
    gate.withLock {
     val existing = current?.takeIf { it.directory == directory }
     val temporary = if (existing == null && directory.exists()) openGeneration(directory.name) else null
     try { (existing ?: temporary)?.db?.openHelper?.writableDatabase?.execSQL("DELETE FROM asset_lease WHERE job_id=?", arrayOf(jobId)) }
     finally { temporary?.db?.close() }
    }
   }
  }
 }

 suspend fun addAsset(source: File, mime: String, width: Int, height: Int): Asset = withContext(Dispatchers.IO) {
  demand(mime in setOf("image/jpeg", "image/png", "image/webp") && width > 0 && height > 0, "MEDIA_INVALID")
  demand(source.isFile && source.length() in 1..(25L * 1024 * 1024) && width.toLong() * height <= 40000000, "MEDIA_SIZE_LIMIT")
  val suffix = when (mime) { "image/jpeg" -> "jpg"; "image/png" -> "png"; else -> "webp" }
  val scratch = File(root, "asset-${newId()}.tmp")
  copySynced(source, scratch)
  val checksum = hashFile(scratch)
  try {
   withDb { database, old, directory ->
    old.assets.firstOrNull { it.sha256 == checksum }?.let { return@withDb it }
    val relative = "assets/$checksum.$suffix"
    val destination = safeFile(directory, relative)
    destination.parentFile!!.mkdirs()
    if (!scratch.renameTo(destination)) copySynced(scratch, destination)
    val asset = Asset(sha256 = checksum, relativePath = relative, mimeType = mime, bytes = destination.length(), width = width, height = height, createdAt = System.currentTimeMillis())
    val next = old.copy(assets = old.assets + asset, revision = old.revision + 1, updatedAt = System.currentTimeMillis())
    LibraryValidator.validate(next)
    currentCoroutineContext().ensureActive()
    withContext(NonCancellable) {
     database.withTransaction { persist(database.openHelper.writableDatabase, next, old); enqueueEffects(database.openHelper.writableDatabase, next) }
     mutableState.value = next
    }
    asset
   }
  } finally { scratch.delete() }
 }

 /** For short UI reads only. Long readers must use leaseSnapshot and its root. */
 fun assetFile(relativePath: String): File {
  demand(relativePath.startsWith("assets/"), "MEDIA_PATH_INVALID")
  return safeFile(current?.directory ?: throw AppException("DB_NOT_READY"), relativePath)
 }

 suspend fun gc() = withDb { database, old, directory ->
  val sql = database.openHelper.writableDatabase
  val now = System.currentTimeMillis()
  sql.execSQL("DELETE FROM asset_lease WHERE expires_at < ?", arrayOf(now))
  val leased = rows(sql, "asset_lease").map { it.s("asset_id") }.toSet()
  val referenced = old.events.mapNotNull { it.appearance.assetId }.toSet() + old.books.mapNotNull { it.coverAssetId }
  // Unattached newly selected photos are kept for 24 h so drafts can still refer to them.
  val expired = old.assets.filter { it.id !in leased && it.id !in referenced && now - it.createdAt >= 24 * 60 * 60 * 1000L }
  if (expired.isNotEmpty()) {
   val next = old.copy(assets = old.assets - expired.toSet(), revision = old.revision + 1, updatedAt = now)
   currentCoroutineContext().ensureActive()
   withContext(NonCancellable) {
    database.withTransaction { persist(sql, next, old); enqueueEffects(sql, next) }
    mutableState.value = next
   }
   expired.forEach { safeFile(directory, it.relativePath).delete() }
  }
  val registered = mutableState.value.assets.map { safeFile(directory, it.relativePath).canonicalPath }.toSet()
  File(directory, "assets").listFiles().orEmpty().filter {
   it.isFile && it.canonicalPath !in registered && now - it.lastModified() >= 24 * 60 * 60 * 1000L
  }.forEach { orphan -> safeFile(directory, "assets/${orphan.name}").delete() }
  // Only app-owned immutable generations below this precise root can be removed.
  root.listFiles().orEmpty().filter { it.isDirectory && it.name.matches(GENERATION) && it != directory }.forEach { other ->
   val candidate = runCatching { openGeneration(other.name) }.getOrNull()
   if (candidate != null) {
    val live = rows(candidate.db.openHelper.writableDatabase, "asset_lease").any { it.l("expires_at") >= now }
    candidate.db.close()
    if (!live) deleteGeneration(other)
   }
  }
 }

 override fun close() { closed = true; scope.cancel(); current?.db?.close() }

 private fun openGeneration(name: String): Generation {
  demand(name.matches(GENERATION), "DB_POINTER_INVALID")
  val directory = File(root, name)
  demand(directory.isDirectory && File(directory, "library.db").isFile, "DB_GENERATION_MISSING")
  return Generation(name, directory, openDb(directory))
 }
 private fun openDb(directory: File): DateBookDatabase = Room.databaseBuilder(app, DateBookDatabase::class.java, File(directory, "library.db").absolutePath)
  .addCallback(SchemaGuards).setJournalMode(androidx.room.RoomDatabase.JournalMode.WRITE_AHEAD_LOGGING).build().also { it.openHelper.writableDatabase }

 private suspend fun createGeneration(snapshot: LibraryState, mediaRoot: File? = null): Generation {
  val name = "g-${newId()}"
  val directory = File(root, name).apply { check(mkdirs()) }
  var database: DateBookDatabase? = null
  try {
   for (asset in snapshot.assets) {
    val source = safeFile(mediaRoot ?: directory, asset.relativePath)
    demand(source.isFile && source.length() == asset.bytes && hashFile(source) == asset.sha256, "BACKUP_ASSET_INVALID", asset.id)
    val destination = safeFile(directory, asset.relativePath)
    destination.parentFile!!.mkdirs(); copySynced(source, destination)
   }
   val opened = openDb(directory); database = opened
   opened.withTransaction {
    persist(opened.openHelper.writableDatabase, snapshot, null)
    write(opened.openHelper.writableDatabase, "device_epoch", mapOf("singleton" to 1, "epoch" to snapshot.epoch, "plan_token" to newId(), "schedule_revision" to 0), listOf("singleton"))
   }
   SchemaGuards.verify(opened.openHelper.writableDatabase)
   demand(canonical(load(opened)) == canonical(snapshot), "DB_ROUNDTRIP_INVALID")
   opened.openHelper.writableDatabase.query("PRAGMA wal_checkpoint(FULL)").use {
    demand(it.moveToFirst() && it.getInt(0) == 0, "DB_CHECKPOINT_FAILED")
   }
   return Generation(name, directory, opened)
  } catch (error: Throwable) { database?.close(); deleteGeneration(directory); throw error }
 }

 private fun deleteGeneration(directory: File) {
  demand(directory.parentFile?.canonicalFile == root.canonicalFile && directory.name.matches(GENERATION), "MEDIA_PATH_INVALID")
  directory.deleteRecursively()
 }
 private fun atomicWrite(file: AtomicFile, value: String) {
  val output = file.startWrite()
  try { output.write(value.toByteArray(Charsets.UTF_8)); file.finishWrite(output) }
  catch (error: Throwable) { file.failWrite(output); throw error }
 }
 private fun readAtomic(file: AtomicFile): String = file.openRead().use { String(it.readBytes(), Charsets.UTF_8) }

 private fun enqueueEffects(sql: SupportSQLiteDatabase, state: LibraryState) {
  listOf("replan", "widget_refresh", "media_gc", "calendar_review").forEach { kind ->
   sql.execSQL("INSERT OR IGNORE INTO effect_outbox(id,kind,scope_id,target_revision,epoch,attempts,next_attempt_at,created_at) VALUES(?,?,?,?,?,0,?,?)",
    arrayOf<Any?>(newId(), kind, "library", state.revision, state.epoch, System.currentTimeMillis(), System.currentTimeMillis()))
  }
 }

 private fun persist(sql: SupportSQLiteDatabase, next: LibraryState, old: LibraryState?) {
  // No OS calls here. Existing device delivery/log/outbox/receipts remain intact.
  write(sql, "library", mapOf("id" to next.id, "singleton" to 1, "name" to next.name, "content_revision" to next.revision, "created_at" to next.createdAt, "updated_at" to next.updatedAt), listOf("id"))
  val oldAssets = old?.assets.orEmpty().associateBy { it.id }
  val oldBooks = old?.books.orEmpty().associateBy { it.id }
  val oldEvents = old?.events.orEmpty().associateBy { it.id }
  next.assets.filter { oldAssets[it.id] != it }.forEach { a -> write(sql, "asset", mapOf("id" to a.id, "sha256" to a.sha256, "relative_path" to a.relativePath, "mime_type" to a.mimeType, "byte_size" to a.bytes, "width" to a.width, "height" to a.height, "created_at" to a.createdAt), listOf("id")) }
  next.books.filter { oldBooks[it.id] != it }.forEach { b -> write(sql, "book", mapOf("id" to b.id, "library_id" to next.id, "name" to b.name, "name_key" to key(b.name), "builtin_key" to b.builtinKey, "is_protected" to b.isProtected, "icon_key" to b.iconKey, "color_argb" to b.colorArgb, "cover_asset_id" to b.coverAssetId, "sort_rank" to b.sortRank, "created_at" to b.createdAt, "updated_at" to b.updatedAt, "version" to b.version), listOf("id")) }
  // Remove retired rule IDs first, so replacing five rules never transiently exceeds five.
  retain(sql, "reminder_rule", "id", next.events.flatMap { it.reminders }.map { it.id }.toSet())
  next.events.filter { oldEvents[it.id] != it }.sortedBy { depth(it, next.events) }.forEach { e ->
   write(sql, "event", mapOf("id" to e.id, "book_id" to e.bookId, "parent_id" to e.parentId, "title" to e.title, "kind" to e.kind, "count_mode" to e.countMode, "include_start_day" to e.includeStartDay, "greeting" to e.greeting, "home_visible" to e.homeVisible, "pinned" to e.pinned, "sort_rank" to e.sortRank, "created_at" to e.createdAt, "updated_at" to e.updatedAt, "version" to e.version), listOf("id"))
   val d = e.date
   write(sql, "event_date", mapOf("event_id" to e.id, "calendar_type" to d.calendar, "anchor_year" to d.year, "anchor_month" to d.month, "anchor_day" to d.day, "is_leap_month" to d.leapMonth, "all_day" to d.allDay, "local_time" to d.localTime, "zone_id" to d.zoneId, "feb29_policy" to d.feb29Policy, "lunar_leap_policy" to d.lunarLeapPolicy, "lunar_small_month_policy" to d.lunarSmallMonthPolicy, "calendar_engine_version" to d.calendarEngineVersion), listOf("event_id"))
   write(sql, "recurrence", mapOf("event_id" to e.id, "frequency" to e.repeat.frequency, "interval_days" to e.repeat.intervalDays, "until_iso" to e.repeat.until), listOf("event_id"))
   val a = e.appearance
   write(sql, "appearance", mapOf("event_id" to e.id, "background_kind" to a.backgroundKind, "asset_id" to a.assetId, "preset_key" to a.presetKey, "solid_argb" to a.solidArgb, "focus_x" to a.focusX, "focus_y" to a.focusY, "dim_amount" to a.dimAmount, "text_color_mode" to a.textColorMode, "font_key" to a.fontKey), listOf("event_id"))
   e.goal?.let { g -> write(sql, "goal_detail", mapOf("event_id" to e.id, "start_iso" to g.startDate, "state" to g.state, "completed_at" to g.completedAt, "include_in_parent" to g.includeInParent), listOf("event_id")) }
   e.reminders.forEach { r -> write(sql, "reminder_rule", mapOf("id" to r.id, "event_id" to e.id, "enabled" to r.enabled, "offset_unit" to r.offsetUnit, "offset_value" to r.offsetValue, "local_time" to r.localTime, "precision_mode" to r.precisionMode, "version" to r.version), listOf("id")) }
  }
  val oldActions = old?.actions.orEmpty().associateBy { it.id }
  next.actions.filter { oldActions[it.id] != it }.forEach { a -> write(sql, "action_record", mapOf("id" to a.id, "goal_event_id" to a.goalEventId, "action_date_iso" to a.date, "body" to a.body, "minutes" to a.minutes, "created_at" to a.createdAt, "updated_at" to a.updatedAt, "version" to a.version), listOf("id")) }
  retain(sql, "action_record", "id", next.actions.map { it.id }.toSet())
  retain(sql, "goal_detail", "event_id", next.events.filter { it.goal != null }.map { it.id }.toSet())
  next.tags.forEach { t -> write(sql, "tag", mapOf("id" to t.id, "name" to t.name, "name_key" to key(t.name), "created_at" to t.createdAt), listOf("id")) }
  next.events.filter { oldEvents[it.id]?.tagIds != it.tagIds }.forEach { e ->
   sql.execSQL("DELETE FROM event_tag WHERE event_id=?", arrayOf(e.id))
   e.tagIds.forEach { tag -> write(sql, "event_tag", mapOf("event_id" to e.id, "tag_id" to tag), listOf("event_id", "tag_id")) }
  }
  retain(sql, "tag", "id", next.tags.map { it.id }.toSet())
  next.causes.forEach { c -> write(sql, "lifecycle_cause", mapOf("id" to c.id, "kind" to c.kind, "source_event_id" to c.sourceEventId, "source_book_id" to c.sourceBookId, "created_at" to c.createdAt, "purge_after" to c.purgeAfter), listOf("id")) }
  if (old?.causes != next.causes) {
   sql.execSQL("DELETE FROM lifecycle_member")
   next.causes.forEach { c -> c.members.forEach { event -> write(sql, "lifecycle_member", mapOf("cause_id" to c.id, "event_id" to event), listOf("cause_id", "event_id")) } }
  }
  retain(sql, "lifecycle_cause", "id", next.causes.map { it.id }.toSet())
  next.imports.forEach { b -> write(sql, "import_batch", mapOf("id" to b.id, "format" to formatToDb(b.format), "source_export_id" to b.sourceExportId, "file_sha256" to b.fileSha256, "imported_at" to b.importedAt), listOf("id")) }
  if (old?.imports != next.imports) {
   sql.execSQL("DELETE FROM import_provenance")
   next.imports.forEach { b -> b.provenance.forEach { p -> write(sql, "import_provenance", mapOf("batch_id" to b.id, "source_export_id" to b.sourceExportId, "source_ref" to p.sourceRef, "local_event_id" to p.localEventId), listOf("batch_id", "source_ref")) } }
  }
  retain(sql, "import_batch", "id", next.imports.map { it.id }.toSet())
  val ids = next.events.map { it.id }.toSet()
  old?.events?.filter { it.id !in ids }?.sortedByDescending { depth(it, old.events) }?.forEach { sql.execSQL("DELETE FROM event WHERE id=?", arrayOf(it.id)) }
  retain(sql, "book", "id", next.books.map { it.id }.toSet())
  val h = next.home
  write(sql, "home_config", mapOf("singleton" to 1, "hero_mode" to h.heroMode, "fixed_event_id" to h.fixedEventId, "sort_mode" to h.sortMode, "selected_book_id" to h.selectedBookId), listOf("singleton"))
  retain(sql, "asset", "id", next.assets.map { it.id }.toSet())
 }

 private fun load(database: DateBookDatabase): LibraryState {
  val sql = database.openHelper.writableDatabase
  val library = rows(sql, "library").singleOrNull() ?: throw AppException("DB_LIBRARY_MISSING")
  val epoch = rows(sql, "device_epoch").singleOrNull()?.s("epoch") ?: throw AppException("DB_EPOCH_MISSING")
  val dates = rows(sql, "event_date").associateBy { it.s("event_id") }
  val recurrences = rows(sql, "recurrence").associateBy { it.s("event_id") }
  val appearances = rows(sql, "appearance").associateBy { it.s("event_id") }
  val goals = rows(sql, "goal_detail").associateBy { it.s("event_id") }
  val rules = rows(sql, "reminder_rule").groupBy { it.s("event_id") }
  val tags = rows(sql, "event_tag").groupBy { it.s("event_id") }
  val members = rows(sql, "lifecycle_member").groupBy { it.s("cause_id") }
  val origins = rows(sql, "import_provenance").groupBy { it.s("batch_id") }
  val home = rows(sql, "home_config").singleOrNull() ?: throw AppException("DB_HOME_MISSING")
  return LibraryState(
   id = library.s("id"), name = library.s("name"), revision = library.l("content_revision"), epoch = epoch,
   createdAt = library.l("created_at"), updatedAt = library.l("updated_at"),
   books = rows(sql, "book").map { b -> Book(b.s("id"), b.s("name"), b["builtin_key"], b.s("icon_key"), b.l("color_argb").toInt(), b["cover_asset_id"], b.l("sort_rank"), b.l("created_at"), b.l("updated_at"), b.l("version"), b.bool("is_protected")) },
   assets = rows(sql, "asset").map { a -> Asset(a.s("id"), a.s("sha256"), a.s("relative_path"), a.s("mime_type"), a.l("byte_size"), a.l("width").toInt(), a.l("height").toInt(), a.l("created_at")) },
   events = rows(sql, "event").map { e ->
    val id = e.s("id")
    val d = dates[id] ?: throw AppException("DB_EVENT_DATE_MISSING")
    val r = recurrences[id] ?: throw AppException("DB_EVENT_RECURRENCE_MISSING")
    val a = appearances[id] ?: throw AppException("DB_EVENT_APPEARANCE_MISSING")
    val g = goals[id]
    Event(id, e.s("book_id"), e["parent_id"], e.s("title"), e.s("kind"), e.s("count_mode"), e.bool("include_start_day"), e.s("greeting"), e.bool("home_visible"), e.bool("pinned"), e.l("sort_rank"),
     DateSpec(d.s("calendar_type"), d["anchor_year"]?.toInt(), d.l("anchor_month").toInt(), d.l("anchor_day").toInt(), d.bool("is_leap_month"), d.bool("all_day"), d["local_time"], d["zone_id"], d.s("feb29_policy"), d.s("lunar_leap_policy"), d.s("lunar_small_month_policy"), d.s("calendar_engine_version")),
     RecurrenceSpec(r.s("frequency"), r["interval_days"]?.toInt(), r["until_iso"]),
     Appearance(a.s("background_kind"), a["asset_id"], a.s("preset_key"), a.l("solid_argb").toInt(), a.s("focus_x").toDouble(), a.s("focus_y").toDouble(), a.s("dim_amount").toDouble(), a.s("text_color_mode"), a.s("font_key")),
     g?.let { GoalDetail(it.s("start_iso"), it.s("state"), it["completed_at"]?.toLong(), it.bool("include_in_parent")) },
     rules[id].orEmpty().map { q -> ReminderRule(q.s("id"), q.bool("enabled"), q.s("offset_unit"), q.l("offset_value").toInt(), q["local_time"], q.s("precision_mode"), q.l("version")) },
     tags[id].orEmpty().map { it.s("tag_id") }, e.l("created_at"), e.l("updated_at"), e.l("version"))
   },
   actions = rows(sql, "action_record").map { a -> ActionRecord(a.s("id"), a.s("goal_event_id"), a.s("action_date_iso"), a.s("body"), a["minutes"]?.toInt(), a.l("created_at"), a.l("updated_at"), a.l("version")) },
   tags = rows(sql, "tag").map { t -> Tag(t.s("id"), t.s("name"), t.l("created_at")) },
   causes = rows(sql, "lifecycle_cause").map { c -> LifecycleCause(c.s("id"), c.s("kind"), c["source_event_id"], c["source_book_id"], c.l("created_at"), c["purge_after"]?.toLong(), members[c.s("id")].orEmpty().map { it.s("event_id") }) },
   home = HomeConfig(home.s("hero_mode"), home["fixed_event_id"], home.s("sort_mode"), home["selected_book_id"]),
   imports = rows(sql, "import_batch").map { b -> ImportBatch(b.s("id"), formatFromDb(b.s("format")), b.s("source_export_id"), b.s("file_sha256"), b.l("imported_at"), origins[b.s("id")].orEmpty().map { ImportOrigin(it.s("source_ref"), it["local_event_id"]) }) }
  )
 }

 private fun rows(sql: SupportSQLiteDatabase, table: String, where: String? = null, args: Array<String> = emptyArray()): List<Map<String, String?>> =
  sql.query("SELECT * FROM `$table`" + if (where == null) "" else " WHERE $where", args).use { cursor ->
   buildList { while (cursor.moveToNext()) add(cursor.columnNames.indices.associate { cursor.columnNames[it] to if (cursor.isNull(it)) null else cursor.getString(it) }) }
  }
 private fun write(sql: SupportSQLiteDatabase, table: String, values: Map<String, Any?>, primary: List<String>) {
  val normalized = values.mapValues { if (it.value is Boolean) if (it.value == true) 1 else 0 else it.value }
  val where = primary.joinToString(" AND ") { "`$it`=?" }
  val keys = primary.map { normalized[it] }.toTypedArray()
  val exists = sql.query("SELECT 1 FROM `$table` WHERE $where", keys).use { it.moveToFirst() }
  if (exists) {
   val changed = normalized.filterKeys { it !in primary }
   if (changed.isNotEmpty()) sql.execSQL("UPDATE `$table` SET " + changed.keys.joinToString(",") { "`$it`=?" } + " WHERE $where", (changed.values + keys.toList()).toTypedArray())
  } else sql.execSQL("INSERT INTO `$table` (" + normalized.keys.joinToString(",") { "`$it`" } + ") VALUES(" + normalized.keys.joinToString(",") { "?" } + ")", normalized.values.toTypedArray())
 }
 private fun retain(sql: SupportSQLiteDatabase, table: String, column: String, ids: Set<String>) {
  rows(sql, table).map { it.s(column) }.filter { it !in ids }.forEach { sql.execSQL("DELETE FROM `$table` WHERE `$column`=?", arrayOf(it)) }
 }
 private fun depth(event: Event, events: List<Event>): Int {
  val byId = events.associateBy { it.id }; var parent = event.parentId; var level = 1
  while (parent != null) { demand(level++ <= 3, "TREE_CYCLE"); parent = byId[parent]?.parentId }
  return level
 }
 private fun key(value: String) = Normalizer.normalize(value.trim(), Normalizer.Form.NFC).lowercase(Locale.ROOT)
 private fun formatToDb(value: String): String = when (value) {
  "json" -> "events_json"; "csv" -> "events_csv"; "backup" -> "full_backup"; else -> throw AppException("IMPORT_INVALID")
 }
 private fun formatFromDb(value: String): String = when (value) {
  "events_json" -> "json"; "events_csv" -> "csv"; "full_backup" -> "backup"; else -> throw AppException("DB_IMPORT_FORMAT_INVALID")
 }
 private fun canonical(state: LibraryState): LibraryState = state.copy(
  books = state.books.sortedBy { it.id }, assets = state.assets.sortedBy { it.id },
  events = state.events.map { it.copy(reminders = it.reminders.sortedBy { r -> r.id }, tagIds = it.tagIds.sorted()) }.sortedBy { it.id },
  actions = state.actions.sortedBy { it.id }, tags = state.tags.sortedBy { it.id },
  causes = state.causes.map { it.copy(members = it.members.sorted()) }.sortedBy { it.id },
  imports = state.imports.map { it.copy(provenance = it.provenance.sortedBy { p -> p.sourceRef }) }.sortedBy { it.id })
 private fun safeFile(base: File, relative: String): File {
  demand(relative.isNotBlank() && !relative.startsWith('/') && !relative.contains('\\') && relative.split('/').none { it.isBlank() || it == "." || it == ".." }, "MEDIA_PATH_INVALID")
  val file = File(base, relative).canonicalFile
  demand(file.path.startsWith(base.canonicalPath + File.separator), "MEDIA_PATH_INVALID")
  return file
 }
 private fun copySynced(source: File, destination: File) {
  FileInputStream(source).use { input -> FileOutputStream(destination).use { output -> input.copyTo(output); output.fd.sync() } }
 }
 private fun hashFile(file: File): String {
  val digest = MessageDigest.getInstance("SHA-256")
  file.inputStream().use { input -> val buffer = ByteArray(64 * 1024); while (true) { val count = input.read(buffer); if (count < 0) break; digest.update(buffer, 0, count) } }
  return digest.digest().joinToString("") { "%02x".format(it) }
 }
 private fun hash(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
 private fun Map<String, String?>.s(key: String) = this[key] ?: throw AppException("DB_NULL_INVALID", key)
 private fun Map<String, String?>.l(key: String) = s(key).toLong()
 private fun Map<String, String?>.bool(key: String) = l(key) != 0L

 private fun encodeResult(value: Any?): Pair<String, String> = when (value) {
  null -> "null" to "null"; is Unit -> "unit" to "null"
  is Event -> "event" to json.encodeToString(value); is Book -> "book" to json.encodeToString(value)
  is ActionRecord -> "action" to json.encodeToString(value); is Tag -> "tag" to json.encodeToString(value)
  is String -> "string" to json.encodeToString(value); is Boolean -> "boolean" to value.toString()
  is Int -> "int" to value.toString(); is Long -> "long" to value.toString()
  else -> throw AppException("COMMAND_RESULT_UNSUPPORTED")
 }
 private fun decodeResult(type: String, value: String): Any? = when (type) {
  "null" -> null; "unit" -> Unit; "event" -> json.decodeFromString<Event>(value); "book" -> json.decodeFromString<Book>(value)
  "action" -> json.decodeFromString<ActionRecord>(value); "tag" -> json.decodeFromString<Tag>(value)
  "string" -> json.decodeFromString<String>(value); "boolean" -> value.toBooleanStrict(); "int" -> value.toInt(); "long" -> value.toLong()
  else -> throw AppException("COMMAND_RECEIPT_INVALID")
 }
 private fun resultId(value: Any?) = when (value) { is Event -> value.id; is Book -> value.id; is ActionRecord -> value.id; is Tag -> value.id; is String -> value; else -> "library" }
 private fun resultVersion(value: Any?) = when (value) { is Event -> value.version; is Book -> value.version; is ActionRecord -> value.version; else -> 0L }
 private companion object { val GENERATION = Regex("g-[0-9a-f-]{36}") }
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt'] = r'''package cn.datebook.app.data

import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase

/** CHECK-equivalent guards run on BOTH fresh create and every open/migration. */
object SchemaGuards : RoomDatabase.Callback() {
 override fun onCreate(db: SupportSQLiteDatabase) { install(db) }
 override fun onOpen(db: SupportSQLiteDatabase) { install(db); verify(db) }
 fun install(db: SupportSQLiteDatabase) {
  db.execSQL("PRAGMA foreign_keys=ON")
  for (statement in statements) db.execSQL(statement)
 }
 fun verify(db: SupportSQLiteDatabase) {
  db.query("PRAGMA foreign_key_check").use { check(!it.moveToFirst()) { "DB_FOREIGN_KEY_CHECK_FAILED" } }
  db.query("SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'guard_%'").use {
   check(it.moveToFirst() && it.getInt(0) == 36) { "DB_GUARDS_MISSING" }
  }
  for (statement in statements) {
   val name = Regex("CREATE (?:TRIGGER|VIEW) IF NOT EXISTS (\\w+)").find(statement)!!.groupValues[1]
   db.query("SELECT sql FROM sqlite_master WHERE name=?", arrayOf(name)).use {
    check(it.moveToFirst() && normalize(it.getString(0)) == normalize(statement)) { "DB_GUARD_CHANGED:$name" }
   }
  }
 }
 private fun normalize(sql: String) = sql.replace(" IF NOT EXISTS", "").trim().trimEnd(';').replace(Regex("\\s+"), " ")
 private val statements = listOf(
  """CREATE VIEW IF NOT EXISTS event_lifecycle AS
 SELECT e.id,
 CASE WHEN EXISTS(SELECT 1 FROM lifecycle_member m JOIN lifecycle_cause c ON c.id=m.cause_id WHERE m.event_id=e.id AND c.kind='trash') THEN 'trash'
 WHEN EXISTS(SELECT 1 FROM lifecycle_member m JOIN lifecycle_cause c ON c.id=m.cause_id WHERE m.event_id=e.id AND c.kind='archive') THEN 'archived'
 ELSE 'active' END AS lifecycle FROM event e;""",
  """CREATE TRIGGER IF NOT EXISTS protect_default_book_delete BEFORE DELETE ON book
 WHEN OLD.is_protected = 1
 BEGIN SELECT RAISE(ABORT,'BOOK_PROTECTED'); END;""",
  """CREATE TRIGGER IF NOT EXISTS tree_depth_insert BEFORE INSERT ON event WHEN NEW.parent_id IS NOT NULL
BEGIN
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM event WHERE id=NEW.parent_id)
  THEN RAISE(ABORT,'TREE_PARENT_NOT_FOUND') END;
 SELECT CASE WHEN (
  WITH RECURSIVE ancestors(id,parent_id) AS (
   SELECT id,parent_id FROM event WHERE id=NEW.parent_id
   UNION SELECT e.id,e.parent_id FROM event e JOIN ancestors a ON e.id=a.parent_id
  ) SELECT count(*) FROM ancestors
 ) >= 3 THEN RAISE(ABORT,'TREE_DEPTH_EXCEEDED') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS tree_move_guard BEFORE UPDATE OF parent_id ON event WHEN NEW.parent_id IS NOT NULL
BEGIN
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM event WHERE id=NEW.parent_id)
  THEN RAISE(ABORT,'TREE_PARENT_NOT_FOUND') END;
 SELECT CASE WHEN EXISTS (
  WITH RECURSIVE descendants(id) AS (
   SELECT OLD.id UNION SELECT e.id FROM event e JOIN descendants d ON e.parent_id=d.id
  ) SELECT 1 FROM descendants WHERE id=NEW.parent_id
 ) THEN RAISE(ABORT,'TREE_CYCLE') END;
 SELECT CASE WHEN (
  WITH RECURSIVE ancestors(id,parent_id) AS (
   SELECT id,parent_id FROM event WHERE id=NEW.parent_id
   UNION SELECT e.id,e.parent_id FROM event e JOIN ancestors a ON e.id=a.parent_id
  ), descendants(id,rel) AS (
   SELECT OLD.id,0 UNION ALL SELECT e.id,d.rel+1 FROM event e JOIN descendants d ON e.parent_id=d.id
  ) SELECT (SELECT count(*) FROM ancestors)+1+(SELECT max(rel) FROM descendants)
 ) > 3 THEN RAISE(ABORT,'TREE_DEPTH_EXCEEDED') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS event_id_immutable BEFORE UPDATE OF id ON event
 WHEN NEW.id <> OLD.id
 BEGIN SELECT RAISE(ABORT,'EVENT_ID_IMMUTABLE'); END;""",
  """CREATE TRIGGER IF NOT EXISTS reminder_limit BEFORE INSERT ON reminder_rule
 WHEN (SELECT count(*) FROM reminder_rule WHERE event_id=NEW.event_id)>=5
 BEGIN SELECT RAISE(ABORT,'REMINDER_LIMIT'); END;""",
  """CREATE TRIGGER IF NOT EXISTS reminder_limit_update BEFORE UPDATE OF event_id ON reminder_rule
 WHEN NEW.event_id<>OLD.event_id AND (SELECT count(*) FROM reminder_rule WHERE event_id=NEW.event_id)>=5
 BEGIN SELECT RAISE(ABORT,'REMINDER_LIMIT'); END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_library_insert BEFORE INSERT ON library
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_library_0') END;
 SELECT CASE WHEN NOT (NEW.content_revision >= 0) THEN RAISE(ABORT,'CHECK_library_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_library_update BEFORE UPDATE ON library
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_library_0') END;
 SELECT CASE WHEN NOT (NEW.content_revision >= 0) THEN RAISE(ABORT,'CHECK_library_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_asset_insert BEFORE INSERT ON asset
BEGIN
 SELECT CASE WHEN NOT (NEW.mime_type IN ('image/jpeg','image/png','image/webp')) THEN RAISE(ABORT,'CHECK_asset_0') END;
 SELECT CASE WHEN NOT (NEW.byte_size >= 0) THEN RAISE(ABORT,'CHECK_asset_1') END;
 SELECT CASE WHEN NOT (NEW.width > 0) THEN RAISE(ABORT,'CHECK_asset_2') END;
 SELECT CASE WHEN NOT (NEW.height > 0) THEN RAISE(ABORT,'CHECK_asset_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_asset_update BEFORE UPDATE ON asset
BEGIN
 SELECT CASE WHEN NOT (NEW.mime_type IN ('image/jpeg','image/png','image/webp')) THEN RAISE(ABORT,'CHECK_asset_0') END;
 SELECT CASE WHEN NOT (NEW.byte_size >= 0) THEN RAISE(ABORT,'CHECK_asset_1') END;
 SELECT CASE WHEN NOT (NEW.width > 0) THEN RAISE(ABORT,'CHECK_asset_2') END;
 SELECT CASE WHEN NOT (NEW.height > 0) THEN RAISE(ABORT,'CHECK_asset_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_book_insert BEFORE INSERT ON book
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.name AS BLOB)) BETWEEN 1 AND 2048) THEN RAISE(ABORT,'CHECK_book_0') END;
 SELECT CASE WHEN NOT (NEW.builtin_key IS NULL OR NEW.builtin_key IN ('birthday','memorial','holiday','goal','uncategorized')) THEN RAISE(ABORT,'CHECK_book_1') END;
 SELECT CASE WHEN NOT (NEW.is_protected IN (0,1)) THEN RAISE(ABORT,'CHECK_book_2') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_book_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_book_update BEFORE UPDATE ON book
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.name AS BLOB)) BETWEEN 1 AND 2048) THEN RAISE(ABORT,'CHECK_book_0') END;
 SELECT CASE WHEN NOT (NEW.builtin_key IS NULL OR NEW.builtin_key IN ('birthday','memorial','holiday','goal','uncategorized')) THEN RAISE(ABORT,'CHECK_book_1') END;
 SELECT CASE WHEN NOT (NEW.is_protected IN (0,1)) THEN RAISE(ABORT,'CHECK_book_2') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_book_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_insert BEFORE INSERT ON event
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.title AS BLOB)) BETWEEN 1 AND 4096) THEN RAISE(ABORT,'CHECK_event_0') END;
 SELECT CASE WHEN NOT (NEW.kind IN ('birthday','memorial','holiday','goal','ordinary')) THEN RAISE(ABORT,'CHECK_event_1') END;
 SELECT CASE WHEN NOT (NEW.count_mode IN ('down','up')) THEN RAISE(ABORT,'CHECK_event_2') END;
 SELECT CASE WHEN NOT (NEW.include_start_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_3') END;
 SELECT CASE WHEN NOT (length(CAST(NEW.greeting AS BLOB)) <= 65536) THEN RAISE(ABORT,'CHECK_event_4') END;
 SELECT CASE WHEN NOT (NEW.home_visible IN (0,1)) THEN RAISE(ABORT,'CHECK_event_5') END;
 SELECT CASE WHEN NOT (NEW.pinned IN (0,1)) THEN RAISE(ABORT,'CHECK_event_6') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_event_7') END;
 SELECT CASE WHEN NOT (NEW.parent_id IS NULL OR NEW.parent_id <> NEW.id) THEN RAISE(ABORT,'CHECK_event_8') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_update BEFORE UPDATE ON event
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.title AS BLOB)) BETWEEN 1 AND 4096) THEN RAISE(ABORT,'CHECK_event_0') END;
 SELECT CASE WHEN NOT (NEW.kind IN ('birthday','memorial','holiday','goal','ordinary')) THEN RAISE(ABORT,'CHECK_event_1') END;
 SELECT CASE WHEN NOT (NEW.count_mode IN ('down','up')) THEN RAISE(ABORT,'CHECK_event_2') END;
 SELECT CASE WHEN NOT (NEW.include_start_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_3') END;
 SELECT CASE WHEN NOT (length(CAST(NEW.greeting AS BLOB)) <= 65536) THEN RAISE(ABORT,'CHECK_event_4') END;
 SELECT CASE WHEN NOT (NEW.home_visible IN (0,1)) THEN RAISE(ABORT,'CHECK_event_5') END;
 SELECT CASE WHEN NOT (NEW.pinned IN (0,1)) THEN RAISE(ABORT,'CHECK_event_6') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_event_7') END;
 SELECT CASE WHEN NOT (NEW.parent_id IS NULL OR NEW.parent_id <> NEW.id) THEN RAISE(ABORT,'CHECK_event_8') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_date_insert BEFORE INSERT ON event_date
BEGIN
 SELECT CASE WHEN NOT (NEW.calendar_type IN ('gregorian','lunar')) THEN RAISE(ABORT,'CHECK_event_date_0') END;
 SELECT CASE WHEN NOT (NEW.anchor_year IS NULL OR NEW.anchor_year BETWEEN 1900 AND 2100) THEN RAISE(ABORT,'CHECK_event_date_1') END;
 SELECT CASE WHEN NOT (NEW.anchor_month BETWEEN 1 AND 12) THEN RAISE(ABORT,'CHECK_event_date_2') END;
 SELECT CASE WHEN NOT (NEW.anchor_day BETWEEN 1 AND 31) THEN RAISE(ABORT,'CHECK_event_date_3') END;
 SELECT CASE WHEN NOT (NEW.is_leap_month IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_4') END;
 SELECT CASE WHEN NOT (NEW.all_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_5') END;
 SELECT CASE WHEN NOT (NEW.feb29_policy IN ('feb28','mar01')) THEN RAISE(ABORT,'CHECK_event_date_6') END;
 SELECT CASE WHEN NOT (NEW.lunar_leap_policy IN ('normal_fallback','leap_only')) THEN RAISE(ABORT,'CHECK_event_date_7') END;
 SELECT CASE WHEN NOT (NEW.lunar_small_month_policy IN ('month_end','skip')) THEN RAISE(ABORT,'CHECK_event_date_8') END;
 SELECT CASE WHEN NOT ((NEW.all_day=1 AND NEW.local_time IS NULL AND NEW.zone_id IS NULL) OR
       (NEW.all_day=0 AND NEW.local_time IS NOT NULL AND NEW.zone_id IS NOT NULL)) THEN RAISE(ABORT,'CHECK_event_date_9') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='lunar' OR NEW.is_leap_month=0) THEN RAISE(ABORT,'CHECK_event_date_10') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='gregorian' OR NEW.all_day=1) THEN RAISE(ABORT,'CHECK_event_date_11') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_date_update BEFORE UPDATE ON event_date
BEGIN
 SELECT CASE WHEN NOT (NEW.calendar_type IN ('gregorian','lunar')) THEN RAISE(ABORT,'CHECK_event_date_0') END;
 SELECT CASE WHEN NOT (NEW.anchor_year IS NULL OR NEW.anchor_year BETWEEN 1900 AND 2100) THEN RAISE(ABORT,'CHECK_event_date_1') END;
 SELECT CASE WHEN NOT (NEW.anchor_month BETWEEN 1 AND 12) THEN RAISE(ABORT,'CHECK_event_date_2') END;
 SELECT CASE WHEN NOT (NEW.anchor_day BETWEEN 1 AND 31) THEN RAISE(ABORT,'CHECK_event_date_3') END;
 SELECT CASE WHEN NOT (NEW.is_leap_month IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_4') END;
 SELECT CASE WHEN NOT (NEW.all_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_5') END;
 SELECT CASE WHEN NOT (NEW.feb29_policy IN ('feb28','mar01')) THEN RAISE(ABORT,'CHECK_event_date_6') END;
 SELECT CASE WHEN NOT (NEW.lunar_leap_policy IN ('normal_fallback','leap_only')) THEN RAISE(ABORT,'CHECK_event_date_7') END;
 SELECT CASE WHEN NOT (NEW.lunar_small_month_policy IN ('month_end','skip')) THEN RAISE(ABORT,'CHECK_event_date_8') END;
 SELECT CASE WHEN NOT ((NEW.all_day=1 AND NEW.local_time IS NULL AND NEW.zone_id IS NULL) OR
       (NEW.all_day=0 AND NEW.local_time IS NOT NULL AND NEW.zone_id IS NOT NULL)) THEN RAISE(ABORT,'CHECK_event_date_9') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='lunar' OR NEW.is_leap_month=0) THEN RAISE(ABORT,'CHECK_event_date_10') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='gregorian' OR NEW.all_day=1) THEN RAISE(ABORT,'CHECK_event_date_11') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_recurrence_insert BEFORE INSERT ON recurrence
BEGIN
 SELECT CASE WHEN NOT (NEW.frequency IN ('none','yearly','monthly','weekly','every_n_days')) THEN RAISE(ABORT,'CHECK_recurrence_0') END;
 SELECT CASE WHEN NOT ((NEW.frequency='every_n_days' AND NEW.interval_days IS NOT NULL AND NEW.interval_days BETWEEN 1 AND 365) OR
       (NEW.frequency<>'every_n_days' AND NEW.interval_days IS NULL)) THEN RAISE(ABORT,'CHECK_recurrence_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_recurrence_update BEFORE UPDATE ON recurrence
BEGIN
 SELECT CASE WHEN NOT (NEW.frequency IN ('none','yearly','monthly','weekly','every_n_days')) THEN RAISE(ABORT,'CHECK_recurrence_0') END;
 SELECT CASE WHEN NOT ((NEW.frequency='every_n_days' AND NEW.interval_days IS NOT NULL AND NEW.interval_days BETWEEN 1 AND 365) OR
       (NEW.frequency<>'every_n_days' AND NEW.interval_days IS NULL)) THEN RAISE(ABORT,'CHECK_recurrence_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_appearance_insert BEFORE INSERT ON appearance
BEGIN
 SELECT CASE WHEN NOT (NEW.background_kind IN ('gradient','solid','photo')) THEN RAISE(ABORT,'CHECK_appearance_0') END;
 SELECT CASE WHEN NOT (NEW.focus_x BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_1') END;
 SELECT CASE WHEN NOT (NEW.focus_y BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_2') END;
 SELECT CASE WHEN NOT (NEW.dim_amount BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_3') END;
 SELECT CASE WHEN NOT (NEW.text_color_mode IN ('auto','light','dark')) THEN RAISE(ABORT,'CHECK_appearance_4') END;
 SELECT CASE WHEN NOT (NEW.background_kind<>'photo' OR NEW.asset_id IS NOT NULL) THEN RAISE(ABORT,'CHECK_appearance_5') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_appearance_update BEFORE UPDATE ON appearance
BEGIN
 SELECT CASE WHEN NOT (NEW.background_kind IN ('gradient','solid','photo')) THEN RAISE(ABORT,'CHECK_appearance_0') END;
 SELECT CASE WHEN NOT (NEW.focus_x BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_1') END;
 SELECT CASE WHEN NOT (NEW.focus_y BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_2') END;
 SELECT CASE WHEN NOT (NEW.dim_amount BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_3') END;
 SELECT CASE WHEN NOT (NEW.text_color_mode IN ('auto','light','dark')) THEN RAISE(ABORT,'CHECK_appearance_4') END;
 SELECT CASE WHEN NOT (NEW.background_kind<>'photo' OR NEW.asset_id IS NOT NULL) THEN RAISE(ABORT,'CHECK_appearance_5') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_goal_detail_insert BEFORE INSERT ON goal_detail
BEGIN
 SELECT CASE WHEN NOT (NEW.state IN ('not_started','in_progress','completed','canceled')) THEN RAISE(ABORT,'CHECK_goal_detail_0') END;
 SELECT CASE WHEN NOT (NEW.include_in_parent IN (0,1)) THEN RAISE(ABORT,'CHECK_goal_detail_1') END;
 SELECT CASE WHEN NOT ((NEW.state='completed' AND NEW.completed_at IS NOT NULL) OR
       (NEW.state<>'completed' AND NEW.completed_at IS NULL)) THEN RAISE(ABORT,'CHECK_goal_detail_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_goal_detail_update BEFORE UPDATE ON goal_detail
BEGIN
 SELECT CASE WHEN NOT (NEW.state IN ('not_started','in_progress','completed','canceled')) THEN RAISE(ABORT,'CHECK_goal_detail_0') END;
 SELECT CASE WHEN NOT (NEW.include_in_parent IN (0,1)) THEN RAISE(ABORT,'CHECK_goal_detail_1') END;
 SELECT CASE WHEN NOT ((NEW.state='completed' AND NEW.completed_at IS NOT NULL) OR
       (NEW.state<>'completed' AND NEW.completed_at IS NULL)) THEN RAISE(ABORT,'CHECK_goal_detail_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_action_record_insert BEFORE INSERT ON action_record
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.body AS BLOB)) BETWEEN 1 AND 32768) THEN RAISE(ABORT,'CHECK_action_record_0') END;
 SELECT CASE WHEN NOT (NEW.minutes BETWEEN 0 AND 1440) THEN RAISE(ABORT,'CHECK_action_record_1') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_action_record_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_action_record_update BEFORE UPDATE ON action_record
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.body AS BLOB)) BETWEEN 1 AND 32768) THEN RAISE(ABORT,'CHECK_action_record_0') END;
 SELECT CASE WHEN NOT (NEW.minutes BETWEEN 0 AND 1440) THEN RAISE(ABORT,'CHECK_action_record_1') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_action_record_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_lifecycle_cause_insert BEFORE INSERT ON lifecycle_cause
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('archive','trash')) THEN RAISE(ABORT,'CHECK_lifecycle_cause_0') END;
 SELECT CASE WHEN NOT ((NEW.kind='trash' AND NEW.purge_after IS NOT NULL) OR(NEW.kind='archive' AND NEW.purge_after IS NULL)) THEN RAISE(ABORT,'CHECK_lifecycle_cause_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_lifecycle_cause_update BEFORE UPDATE ON lifecycle_cause
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('archive','trash')) THEN RAISE(ABORT,'CHECK_lifecycle_cause_0') END;
 SELECT CASE WHEN NOT ((NEW.kind='trash' AND NEW.purge_after IS NOT NULL) OR(NEW.kind='archive' AND NEW.purge_after IS NULL)) THEN RAISE(ABORT,'CHECK_lifecycle_cause_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_reminder_rule_insert BEFORE INSERT ON reminder_rule
BEGIN
 SELECT CASE WHEN NOT (NEW.enabled IN (0,1)) THEN RAISE(ABORT,'CHECK_reminder_rule_0') END;
 SELECT CASE WHEN NOT (NEW.offset_unit IN ('days','hours','minutes')) THEN RAISE(ABORT,'CHECK_reminder_rule_1') END;
 SELECT CASE WHEN NOT (NEW.offset_value BETWEEN 0 AND 525600) THEN RAISE(ABORT,'CHECK_reminder_rule_2') END;
 SELECT CASE WHEN NOT (NEW.precision_mode IN ('normal','precise')) THEN RAISE(ABORT,'CHECK_reminder_rule_3') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_reminder_rule_4') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_reminder_rule_update BEFORE UPDATE ON reminder_rule
BEGIN
 SELECT CASE WHEN NOT (NEW.enabled IN (0,1)) THEN RAISE(ABORT,'CHECK_reminder_rule_0') END;
 SELECT CASE WHEN NOT (NEW.offset_unit IN ('days','hours','minutes')) THEN RAISE(ABORT,'CHECK_reminder_rule_1') END;
 SELECT CASE WHEN NOT (NEW.offset_value BETWEEN 0 AND 525600) THEN RAISE(ABORT,'CHECK_reminder_rule_2') END;
 SELECT CASE WHEN NOT (NEW.precision_mode IN ('normal','precise')) THEN RAISE(ABORT,'CHECK_reminder_rule_3') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_reminder_rule_4') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_home_config_insert BEFORE INSERT ON home_config
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_home_config_0') END;
 SELECT CASE WHEN NOT (NEW.hero_mode IN ('auto','fixed')) THEN RAISE(ABORT,'CHECK_home_config_1') END;
 SELECT CASE WHEN NOT (NEW.sort_mode IN ('date','manual')) THEN RAISE(ABORT,'CHECK_home_config_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_home_config_update BEFORE UPDATE ON home_config
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_home_config_0') END;
 SELECT CASE WHEN NOT (NEW.hero_mode IN ('auto','fixed')) THEN RAISE(ABORT,'CHECK_home_config_1') END;
 SELECT CASE WHEN NOT (NEW.sort_mode IN ('date','manual')) THEN RAISE(ABORT,'CHECK_home_config_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_import_batch_insert BEFORE INSERT ON import_batch
BEGIN
 SELECT CASE WHEN NOT (NEW.format IN ('events_json','events_csv','full_backup')) THEN RAISE(ABORT,'CHECK_import_batch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_import_batch_update BEFORE UPDATE ON import_batch
BEGIN
 SELECT CASE WHEN NOT (NEW.format IN ('events_json','events_csv','full_backup')) THEN RAISE(ABORT,'CHECK_import_batch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_epoch_insert BEFORE INSERT ON device_epoch
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_device_epoch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_epoch_update BEFORE UPDATE ON device_epoch
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_device_epoch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_delivery_log_insert BEFORE INSERT ON delivery_log
BEGIN
 SELECT CASE WHEN NOT (NEW.valid_until >= NEW.fire_at) THEN RAISE(ABORT,'CHECK_delivery_log_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('pending','posting','posted','skipped','failed')) THEN RAISE(ABORT,'CHECK_delivery_log_1') END;
 SELECT CASE WHEN NOT (NEW.attempt_count >= 0) THEN RAISE(ABORT,'CHECK_delivery_log_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_delivery_log_update BEFORE UPDATE ON delivery_log
BEGIN
 SELECT CASE WHEN NOT (NEW.valid_until >= NEW.fire_at) THEN RAISE(ABORT,'CHECK_delivery_log_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('pending','posting','posted','skipped','failed')) THEN RAISE(ABORT,'CHECK_delivery_log_1') END;
 SELECT CASE WHEN NOT (NEW.attempt_count >= 0) THEN RAISE(ABORT,'CHECK_delivery_log_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_binding_insert BEFORE INSERT ON device_binding
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('calendar','widget')) THEN RAISE(ABORT,'CHECK_device_binding_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('active','unknown','conflict','invalid')) THEN RAISE(ABORT,'CHECK_device_binding_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_binding_update BEFORE UPDATE ON device_binding
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('calendar','widget')) THEN RAISE(ABORT,'CHECK_device_binding_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('active','unknown','conflict','invalid')) THEN RAISE(ABORT,'CHECK_device_binding_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_effect_outbox_insert BEFORE INSERT ON effect_outbox
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('replan','widget_refresh','media_gc','calendar_review')) THEN RAISE(ABORT,'CHECK_effect_outbox_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_effect_outbox_update BEFORE UPDATE ON effect_outbox
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('replan','widget_refresh','media_gc','calendar_review')) THEN RAISE(ABORT,'CHECK_effect_outbox_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_backup_receipt_insert BEFORE INSERT ON backup_receipt
BEGIN
 SELECT CASE WHEN NOT (NEW.encrypted IN (0,1)) THEN RAISE(ABORT,'CHECK_backup_receipt_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_backup_receipt_update BEFORE UPDATE ON backup_receipt
BEGIN
 SELECT CASE WHEN NOT (NEW.encrypted IN (0,1)) THEN RAISE(ABORT,'CHECK_backup_receipt_0') END;
END;"""
 )
}

'''
# END FILE: app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt'] = r'''package cn.datebook.app.platform

import android.app.Activity
import android.appwidget.AppWidgetManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.AtomicFile
import android.widget.*
import androidx.glance.*
import androidx.glance.appwidget.action.actionStartActivity
import androidx.glance.action.clickable
import androidx.glance.appwidget.*
import androidx.glance.layout.*
import androidx.glance.text.Text
import androidx.glance.text.TextStyle
import androidx.glance.unit.ColorProvider
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import cn.datebook.app.DateBookApplication
import cn.datebook.app.MainActivity
import cn.datebook.core.*
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.File

data class WidgetConfig(val mode:String="recent",val eventId:String?=null,val showGreeting:Boolean=false,val showPhoto:Boolean=false)
object WidgetPreferences {
 private fun file(context:Context,id:Int)=AtomicFile(File(context.noBackupFilesDir,"widgets/$id.json").also{it.parentFile!!.mkdirs()})
 fun read(context:Context,id:Int):WidgetConfig=try{val o=JSONObject(file(context,id).openRead().bufferedReader().use{it.readText()});WidgetConfig(o.optString("mode","recent"),o.optString("eventId").takeIf{it.isNotBlank()},o.optBoolean("showGreeting",false),o.optBoolean("showPhoto",false))}catch(_:Exception){WidgetConfig()}
 fun write(context:Context,id:Int,value:WidgetConfig){val f=file(context,id);val out=f.startWrite();try{out.write(JSONObject().put("mode",value.mode).put("eventId",value.eventId).put("showGreeting",value.showGreeting).put("showPhoto",value.showPhoto).toString().toByteArray());f.finishWrite(out)}catch(e:Exception){f.failWrite(out);throw e}}
 fun delete(context:Context,id:Int)=file(context,id).delete()
}
class DateBookWidget:GlanceAppWidget(){
 override suspend fun provideGlance(context:Context,id:GlanceId){
  val g=(context.applicationContext as DateBookApplication).graph;g.store.awaitReady();val widgetId=GlanceAppWidgetManager(context).getAppWidgetId(id);val config=WidgetPreferences.read(context,widgetId)
  // Snapshot assets are leased through rendering; no generation file is held across library installs.
  val snapshot=g.store.leaseSnapshot();try{val state=snapshot.state;val locked=g.lock.enabled
   val active=state.events.filter{state.lifecycle(it.id)=="active"&&it.goal?.state !in setOf("completed","canceled")};val selected=if(config.mode=="single")active.filter{it.id==config.eventId}.take(1)else active.filter{it.homeVisible}.sortedWith(compareBy<Event>{!it.pinned}.thenBy{g.dates.evaluate(it.dateInput()).occurrence?.date}).take(3)
   val photo=if(!locked&&config.showPhoto&&selected.size==1)selected.first().appearance.assetId?.let{key->state.assets.firstOrNull{it.id==key}}?.let{File(snapshot.root,it.relativePath).takeIf(File::isFile)?.let{f->android.graphics.BitmapFactory.decodeFile(f.path)}}else null
   provideContent {GlanceTheme{Box(modifier=GlanceModifier.fillMaxSize().background(ColorProvider(Color(0xFF173D30))).padding(16.dp).clickable(actionStartActivity(Intent(context,MainActivity::class.java)))){if(photo!=null)Image(provider=ImageProvider(photo),contentDescription=null,modifier=GlanceModifier.fillMaxSize(),contentScale=ContentScale.Crop);Column{Text("DateBook",style=TextStyle(color=ColorProvider(Color.White),fontSize=15.sp));Spacer(GlanceModifier.height(8.dp));when{locked->Text("应用锁已开启，请打开应用查看",style=TextStyle(color=ColorProvider(Color.White)));selected.isEmpty()->Text("暂无可显示的日子，请重新配置",style=TextStyle(color=ColorProvider(Color.White)));else->selected.forEach{e->Column(modifier=GlanceModifier.padding(bottom=8.dp).clickable(actionStartActivity(Intent(context,MainActivity::class.java).setData(android.net.Uri.parse("daybook://event/${state.epoch}/${e.id}"))))){Text(e.title,style=TextStyle(color=ColorProvider(Color.White),fontSize=17.sp),maxLines=2);Text(g.dates.evaluate(e.dateInput()).label,style=TextStyle(color=ColorProvider(Color.White),fontSize=22.sp));if(config.showGreeting&&e.greeting.isNotBlank())Text(e.greeting,style=TextStyle(color=ColorProvider(Color.White),fontSize=12.sp),maxLines=2)}}}}}}}
  }finally{snapshot.close()}
 }
}
class DateBookWidgetReceiver:GlanceAppWidgetReceiver(){override val glanceAppWidget:GlanceAppWidget=DateBookWidget();override fun onDeleted(context:Context,appWidgetIds:IntArray){appWidgetIds.forEach{WidgetPreferences.delete(context,it)};super.onDeleted(context,appWidgetIds)}}
class WidgetConfigureActivity:Activity(){
 private var id=AppWidgetManager.INVALID_APPWIDGET_ID
 override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);setResult(RESULT_CANCELED);id=intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,AppWidgetManager.INVALID_APPWIDGET_ID);if(id==AppWidgetManager.INVALID_APPWIDGET_ID){finish();return};val g=(application as DateBookApplication).graph
  val layout=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(32,32,32,32)};layout.addView(TextView(this).apply{text="选择桌面组件内容";textSize=22f});setContentView(layout)
  if(g.lock.enabled){layout.addView(TextView(this).apply{text="应用锁已开启。桌面仅显示安全入口；在应用关闭锁后可重新配置。"});layout.addView(Button(this).apply{text="添加安全入口";setOnClickListener{finishConfig(WidgetConfig())}});return}
  val loading=TextView(this).apply{text="正在加载本机事件…"};layout.addView(loading)
  g.scope.launch(Dispatchers.Main){try{g.store.awaitReady();layout.removeView(loading);val rows=g.store.state.value.events.filter{g.store.state.value.lifecycle(it.id)=="active"};val mode=Spinner(this@WidgetConfigureActivity);mode.adapter=ArrayAdapter(this@WidgetConfigureActivity,android.R.layout.simple_spinner_dropdown_item,listOf("最近三个日子","指定一个日子"));layout.addView(mode);val selection=Spinner(this@WidgetConfigureActivity);selection.adapter=ArrayAdapter(this@WidgetConfigureActivity,android.R.layout.simple_spinner_dropdown_item,rows.map{it.title}.ifEmpty{listOf("暂无事件")});layout.addView(selection);val greeting=CheckBox(this@WidgetConfigureActivity).apply{text="在桌面公开寄语（默认关闭）"};val photo=CheckBox(this@WidgetConfigureActivity).apply{text="在桌面公开背景照片（默认关闭）"};layout.addView(greeting);layout.addView(photo);layout.addView(Button(this@WidgetConfigureActivity).apply{text="保存并添加";setOnClickListener{if(mode.selectedItemPosition==1&&rows.isEmpty())return@setOnClickListener;finishConfig(WidgetConfig(if(mode.selectedItemPosition==1)"single"else"recent",rows.getOrNull(selection.selectedItemPosition)?.id,greeting.isChecked,photo.isChecked))}})}catch(_:Exception){loading.text="数据加载失败，请返回应用检查"}}
 }
 private fun finishConfig(config:WidgetConfig){WidgetPreferences.write(this,id,config);val g=(application as DateBookApplication).graph;g.scope.launch{DateBookWidget().updateAll(this@WidgetConfigureActivity)};setResult(RESULT_OK,Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,id));finish()}
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt'] = r'''package cn.datebook.app.platform

import android.util.AtomicFile
import cn.datebook.core.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONObject
import java.io.File
import java.util.concurrent.ConcurrentHashMap

data class JobSnapshot(val id:String,val type:String,val state:String="preparing",val stage:String="准备中",val current:Long?=null,val total:Long?=null,val error:String?=null,val result:String?=null,val createdAt:Long=System.currentTimeMillis())
class JobManager(root:File,private val scope:CoroutineScope) {
 private val directory=File(root,"jobs").apply{mkdirs()}
 private val records=ConcurrentHashMap<String,MutableStateFlow<JobSnapshot>>()
 private val tasks=ConcurrentHashMap<String,Job>()
 init {directory.listFiles()?.filter{it.extension=="json"}?.forEach{f->try{val o=JSONObject(f.readText());val s=JobSnapshot(o.getString("id"),o.getString("type"),o.getString("state"),o.optString("stage",""),error=o.optString("error").takeIf{it.isNotEmpty()},createdAt=o.optLong("createdAt",f.lastModified()));val recovered=if(s.state in setOf("completed","canceled","failed"))s else s.copy(state="failed",stage="任务被进程退出中断，请重新操作",error="JOB_INTERRUPTED");records[s.id]=MutableStateFlow(recovered);save(recovered)}catch(_:Exception){f.delete()}}}
 @Synchronized fun start(type:String,block:suspend JobContext.()->String):String {demand(type.matches(Regex("[a-z_]{1,48}")),"JOB_TYPE_INVALID");val id=newId();val flow=MutableStateFlow(JobSnapshot(id,type));records[id]=flow;save(flow.value);tasks[id]=scope.launch(Dispatchers.IO,start=CoroutineStart.LAZY){try{val result=JobContext(id).block();update(id){it.copy(state="completed",stage="已完成",result=result)}}catch(e:CancellationException){update(id){it.copy(state="canceled",stage="已取消")}}catch(e:Exception){update(id){it.copy(state="failed",stage="操作失败",error=(e as? AppException)?.code?:"JOB_FAILED")}}finally{tasks.remove(id)}};tasks.getValue(id).start();return id}
 fun observe(id:String):StateFlow<JobSnapshot> = records[id]?:throw AppException("JOB_NOT_FOUND")
 fun latest():List<JobSnapshot> = records.values.map{it.value}.sortedByDescending{it.createdAt}.take(100)
 @Synchronized fun cancel(id:String):Boolean {val s=records[id]?.value?:throw AppException("JOB_NOT_FOUND");if(s.state=="committing"||s.state in setOf("completed","failed","canceled"))return false;update(id){it.copy(state="canceled",stage="正在取消")};tasks[id]?.cancel();return true}
 inner class JobContext internal constructor(private val id:String) {
  suspend fun progress(stage:String,current:Long?=null,total:Long?=null){currentCoroutineContext().ensureActive();demand(stage.length<=120,"JOB_STAGE_INVALID");update(id){demand(it.state!="canceled","JOB_CANCELED");it.copy(state=if(it.state=="committing")"committing"else"progress",stage=stage,current=current,total=total)}}
  /** The cancellation/commit decision uses the same monitor. Commit must finish atomically. */
  fun committing(){synchronized(this@JobManager){val s=records.getValue(id).value;demand(s.state!="canceled"&&tasks[id]?.isActive==true,"JOB_CANCELED");update(id){it.copy(state="committing",stage="正在提交，请勿关闭应用")}}}
 }
 @Synchronized private fun update(id:String,f:(JobSnapshot)->JobSnapshot){val flow=records.getValue(id);val next=f(flow.value);try{save(next)}catch(e:Exception){if(next.state !in setOf("completed","failed","canceled"))throw AppException("JOB_JOURNAL_FAILED");flow.value=next.copy(error=next.error?:"JOB_JOURNAL_FAILED",stage=if(next.state=="completed")"操作已完成，但任务记录写入失败"else next.stage);return};flow.value=next}
 private fun save(s:JobSnapshot){val f=AtomicFile(File(directory,"${s.id}.json"));val out=f.startWrite();try{val o=JSONObject().put("id",s.id).put("type",s.type).put("state",s.state).put("stage",s.stage).put("current",s.current).put("total",s.total).put("error",s.error).put("createdAt",s.createdAt);out.write(o.toString().toByteArray());f.finishWrite(out)}catch(e:Exception){f.failWrite(out);throw e}}
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt'] = r'''package cn.datebook.app.platform

import android.content.Context
import android.os.SystemClock
import android.util.AtomicFile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONObject
import java.io.File
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec
import cn.datebook.core.AppException
import cn.datebook.core.demand

/** A UI access lock, not database encryption. The verifier stays in noBackup storage. */
class LockManager(context:Context) {
 private val file=AtomicFile(File(context.noBackupFilesDir,"lock.json"))
 var error:AppException?=null
  private set
 private var config=read()
 private val mutableLocked=MutableStateFlow(config!=null)
 val locked:StateFlow<Boolean> = mutableLocked
 val enabled:Boolean get()=synchronized(this){config!=null}
 private var failures=0
 private var deadline=0L
 init { config?.let { failures=it.optInt("failures",0); val persisted=it.optLong("retryAt",0);deadline=SystemClock.elapsedRealtime()+(persisted-System.currentTimeMillis()).coerceIn(0,300000) } }
 @Synchronized fun setPin(pin:CharArray){demand(!enabled||!mutableLocked.value,"LOCK_REQUIRED");replacePinAfterLibraryReplacement(pin)}
 /** Coordinator-only: require its durable, validated replacement-epoch gate first. No delete gap. */
 @Synchronized fun replacePinAfterLibraryReplacement(pin:CharArray){validate(pin);val salt=ByteArray(16).also{SecureRandom().nextBytes(it)};val hash=hash(pin,salt);try{val next=JSONObject().put("salt",android.util.Base64.encodeToString(salt,2)).put("hash",android.util.Base64.encodeToString(hash,2)).put("failures",0).put("retryAt",0);persist(next);config=next;error=null;failures=0;deadline=0;mutableLocked.value=false}finally{hash.fill(0)}}
 @Synchronized fun unlock(pin:CharArray):Boolean {
  error?.let{throw it}
  if(!enabled){mutableLocked.value=false;return true};if(remainingLockMillis()>0)return false
  val c=config!!;val salt=android.util.Base64.decode(c.getString("salt"),2);val actual=hash(pin,salt);val expected=android.util.Base64.decode(c.getString("hash"),2);val good=MessageDigest.isEqual(actual,expected);actual.fill(0);expected.fill(0)
  if(good){failures=0;deadline=0;mutableLocked.value=false}else{failures++;val wait=if(failures<5)0L else (30000L shl (failures-5).coerceAtMost(3)).coerceAtMost(300000);deadline=SystemClock.elapsedRealtime()+wait};c.put("failures",failures).put("retryAt",System.currentTimeMillis()+remainingLockMillis());persist();return good
 }
 @Synchronized fun biometricUnlock(){error?.let{throw it};if(enabled){mutableLocked.value=false;failures=0;deadline=0;config!!.put("failures",0).put("retryAt",0);persist()}}
 @Synchronized fun lock(){if(enabled)mutableLocked.value=true}
 @Synchronized fun disable(pin:CharArray){demand(unlock(pin),"PIN_INCORRECT");file.delete();config=null;mutableLocked.value=false}
 /** Only after an authenticated replacement has committed, never before backup validation. */
 @Synchronized fun clearForReplacement(){file.delete();config=null;error=null;failures=0;deadline=0;mutableLocked.value=false}
 fun remainingLockMillis()=(deadline-SystemClock.elapsedRealtime()).coerceAtLeast(0)
 private fun validate(pin:CharArray){demand(pin.size in 6..12&&pin.all{it in '0'..'9'},"PIN_INVALID")}
 private fun hash(pin:CharArray,salt:ByteArray):ByteArray{validate(pin);val spec=PBEKeySpec(pin,salt,210000,256);return try{SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).encoded}finally{spec.clearPassword()}}
 private fun read():JSONObject?=try{if(file.baseFile.exists()||File(file.baseFile.path+".bak").exists()||File(file.baseFile.path+".new").exists())JSONObject(file.openRead().bufferedReader().use{it.readText()}).also{demand(android.util.Base64.decode(it.getString("salt"),2).size==16&&android.util.Base64.decode(it.getString("hash"),2).size==32,"LOCK_STATE_CORRUPT")}else null}catch(e:Exception){error=AppException("LOCK_STATE_CORRUPT");JSONObject().put("corrupt",true)}
 private fun persist(value:JSONObject=config!!){val stream=file.startWrite();try{stream.write(value.toString().toByteArray());file.finishWrite(stream)}catch(e:Exception){file.failWrite(stream);throw AppException("FILE_IO_FAILED")}}
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt'] = r'''package cn.datebook.app.platform

import android.Manifest
import android.app.*
import android.content.*
import android.content.pm.PackageManager
import android.graphics.*
import android.net.Uri
import android.os.Build
import android.provider.CalendarContract
import android.provider.Settings
import android.text.Layout
import android.text.StaticLayout
import android.text.TextPaint
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.room.withTransaction
import androidx.work.*
import androidx.glance.appwidget.updateAll
import cn.datebook.app.DateBookApplication
import cn.datebook.app.MainActivity
import cn.datebook.app.R
import cn.datebook.app.data.RoomStore
import cn.datebook.core.*
import kotlinx.coroutines.*
import java.io.File
import java.time.*
import java.util.concurrent.TimeUnit
import kotlin.math.max

class SystemServices(private val context:Context,private val store:RoomStore,private val dates:DateEngine) {
 private val alarms=requireNotNull(context.getSystemService(AlarmManager::class.java))
 private val manager=requireNotNull(context.getSystemService(NotificationManager::class.java))
 private data class Next(val key:String,val fire:Long,val expires:Long)
 private fun next(e:Event,r:ReminderRule,after:Instant):Next? {
  val zone=if(e.date.allDay)ZoneId.systemDefault()else ZoneId.of(e.date.zoneId)
  val seconds=r.offsetValue.toLong()*when(r.offsetUnit){"days"->86400;"hours"->3600;else->60}
  var day=(if(e.date.allDay)after.atZone(zone).toLocalDate().plusDays(r.offsetValue.toLong())else after.plusSeconds(seconds).atZone(zone).toLocalDate()).coerceAtLeast(LocalDate.of(1900,1,1))
  repeat(3){val occurrence=dates.nextOccurrence(e.dateInput(),day)?:return null;val fire=if(e.date.allDay)occurrence.date.minusDays(r.offsetValue.toLong()).atTime(LocalTime.parse(r.localTime?:"09:00")).atZone(zone).toInstant()else occurrence.instant!!.minusSeconds(seconds)
   if(fire>after){val expiry=if(e.date.allDay)fire.atZone(zone).toLocalDate().plusDays(1).atStartOfDay(zone).toInstant().minusMillis(1)else fire.plusSeconds(900);return Next("${occurrence.date}@${zone.id}",fire.toEpochMilli(),expiry.toEpochMilli())};day=occurrence.date.plusDays(1)};return null
 }
 private fun expiry(e:Event,key:String,fire:Long):Long = if(e.date.allDay)Instant.ofEpochMilli(fire).atZone(ZoneId.of(key.substringAfter('@'))).toLocalDate().plusDays(1).atStartOfDay(ZoneId.of(key.substringAfter('@'))).toInstant().minusMillis(1).toEpochMilli()else fire+900000
 fun notificationAllowed():Boolean = (Build.VERSION.SDK_INT<33||ContextCompat.checkSelfPermission(context,Manifest.permission.POST_NOTIFICATIONS)==PackageManager.PERMISSION_GRANTED)&&NotificationManagerCompat.from(context).areNotificationsEnabled()&&(manager.getNotificationChannel("events")?.importance?:NotificationManager.IMPORTANCE_DEFAULT)!=NotificationManager.IMPORTANCE_NONE
 fun exactAllowed()=Build.VERSION.SDK_INT<31||alarms.canScheduleExactAlarms()
 fun requestNotificationSettings()=Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE,context.packageName)
 fun requestExactSettings()=if(Build.VERSION.SDK_INT>=31)Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,Uri.parse("package:${context.packageName}"))else requestNotificationSettings()
 suspend fun reconcile(){store.awaitReady();store.withDb{db,state,_->
  val sql=db.openHelper.writableDatabase;val now=System.currentTimeMillis();val token=newId()
  db.withTransaction {
   invalidateZones(sql,state);consume(sql,state,now)
   val existing=mutableMapOf<String,Triple<Long,Long,Long>>()
   sql.query("SELECT rule_id,fire_at,rule_version,event_version FROM reminder_queue").use{c->while(c.moveToNext())existing[c.getString(0)]=Triple(c.getLong(1),c.getLong(2),c.getLong(3))}
   val active=state.events.filter{state.lifecycle(it.id)=="active"&&it.goal?.state !in setOf("completed","canceled")}
   val ids=mutableSetOf<String>();active.forEach{e->e.reminders.filter{it.enabled}.forEach{r->ids+=r.id;val old=existing[r.id];if(old==null||old.second!=r.version||old.third!=e.version){sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(r.id));next(e,r,Instant.ofEpochMilli(now))?.let{n->sql.execSQL("INSERT INTO reminder_queue(rule_id,occurrence_key,fire_at,rule_version,event_version,epoch) VALUES(?,?,?,?,?,?)",arrayOf(r.id,n.key,n.fire,r.version,e.version,state.epoch))}}}}
   existing.keys.filter{it !in ids}.forEach{sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(it))}
   sql.execSQL("INSERT OR REPLACE INTO device_epoch(singleton,epoch,plan_token,schedule_revision) VALUES(1,?,?,?)",arrayOf(state.epoch,token,state.revision))
  }
  postTickets(sql,state,now);schedule(sql,state,token)
  manager.activeNotifications.filter { it.tag?.startsWith(state.epoch+":") == false }.forEach { manager.cancel(it.tag,it.id) }
  sql.execSQL("DELETE FROM effect_outbox WHERE kind IN ('replan','widget_refresh') AND epoch=? AND target_revision<=?",arrayOf(state.epoch,state.revision))
 };refreshWidgets();WorkManager.getInstance(context).enqueueUniquePeriodicWork("datebook-maintenance",ExistingPeriodicWorkPolicy.KEEP,PeriodicWorkRequestBuilder<MaintenanceWorker>(6,TimeUnit.HOURS).build())}
 private fun invalidateZones(sql:androidx.sqlite.db.SupportSQLiteDatabase,state:LibraryState):Boolean {
  val invalid=mutableListOf<String>();sql.query("SELECT rule_id,occurrence_key FROM reminder_queue").use{c->while(c.moveToNext()){val e=state.events.firstOrNull{event->event.reminders.any{it.id==c.getString(0)}};if(e?.date?.allDay==true&&c.getString(1).substringAfter('@')!=ZoneId.systemDefault().id)invalid+=c.getString(0)}}
  invalid.forEach{sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(it))};return invalid.isNotEmpty()
 }
 private fun consume(sql:androidx.sqlite.db.SupportSQLiteDatabase,state:LibraryState,now:Long){
  val due=mutableListOf<List<Any>>();sql.query("SELECT rule_id,occurrence_key,fire_at,rule_version,event_version,epoch FROM reminder_queue WHERE fire_at<=?",arrayOf(now)).use{c->while(c.moveToNext())due+=listOf(c.getString(0),c.getString(1),c.getLong(2),c.getLong(3),c.getLong(4),c.getString(5))}
  due.forEach{q->val id=q[0]as String;val e=state.events.firstOrNull{ev->ev.reminders.any{it.id==id}};val r=e?.reminders?.firstOrNull{it.id==id};if(e!=null&&r!=null&&r.enabled&&state.lifecycle(e.id)=="active"&&e.goal?.state !in setOf("completed","canceled")&&r.version==q[3]&&e.version==q[4]&&state.epoch==q[5]){val valid=expiry(e,q[1]as String,q[2]as Long);val tag="${state.epoch}:$id:${r.version}:${q[1]}";sql.execSQL("INSERT OR IGNORE INTO delivery_log(epoch,rule_id,occurrence_key,event_id,rule_version,event_version,fire_at,valid_until,state,notification_tag,attempt_count,next_attempt_at) VALUES(?,?,?,?,?,?,?,?,?,?,0,?)",arrayOf(state.epoch,id,q[1],e.id,r.version,e.version,q[2],valid,if(now<=valid)"pending"else"skipped",tag,now));sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(id));next(e,r,Instant.ofEpochMilli(now))?.let{n->sql.execSQL("INSERT INTO reminder_queue VALUES(?,?,?,?,?,?)",arrayOf(id,n.key,n.fire,r.version,e.version,state.epoch))}}else sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(id))}
 }
 private fun alarm(epoch:String,channel:String,token:String,flags:Int=PendingIntent.FLAG_UPDATE_CURRENT):PendingIntent?=PendingIntent.getBroadcast(context,0,Intent(context,ReminderReceiver::class.java).setData(Uri.parse("daybook://alarm/$epoch/$channel")).putExtra("token",token),flags or PendingIntent.FLAG_IMMUTABLE)
 private fun schedule(sql:androidx.sqlite.db.SupportSQLiteDatabase,state:LibraryState,token:String){
  for(channel in listOf("normal","precise")){val p=alarm(state.epoch,channel,token)!!;alarms.cancel(p);var fire:Long?=null;sql.query("SELECT min(q.fire_at) FROM reminder_queue q JOIN reminder_rule r ON r.id=q.rule_id WHERE q.epoch=? AND r.precision_mode=?",arrayOf(state.epoch,channel)).use{if(it.moveToFirst()&&!it.isNull(0))fire=it.getLong(0)};fire?.let{at->try{if(channel=="precise"&&exactAllowed())alarms.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p)else alarms.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p)}catch(_:SecurityException){alarms.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p)}}}
 }
 suspend fun deliver(epoch:String,token:String){store.awaitReady();var rebuild=false;store.withDb{db,s,_->if(s.epoch==epoch){val sql=db.openHelper.writableDatabase;var valid=false;sql.query("SELECT plan_token FROM device_epoch WHERE singleton=1 AND epoch=?",arrayOf(epoch)).use{valid=it.moveToFirst()&&it.getString(0)==token};if(valid){val nextToken=newId();db.withTransaction{rebuild=invalidateZones(sql,s);if(!rebuild){consume(sql,s,System.currentTimeMillis());sql.execSQL("UPDATE device_epoch SET plan_token=? WHERE singleton=1",arrayOf(nextToken))}};if(!rebuild){postTickets(sql,s,System.currentTimeMillis());schedule(sql,s,nextToken)}}}};if(rebuild)reconcile()}
 private fun postTickets(sql:androidx.sqlite.db.SupportSQLiteDatabase,s:LibraryState,now:Long){
  manager.createNotificationChannel(NotificationChannel("events","重要日子提醒",NotificationManager.IMPORTANCE_DEFAULT))
  val pending=mutableListOf<List<Any>>();sql.query("SELECT epoch,rule_id,occurrence_key,event_id,rule_version,event_version,valid_until,notification_tag,attempt_count FROM delivery_log WHERE state IN ('pending','posting','failed') AND next_attempt_at<=? LIMIT 50",arrayOf(now)).use{c->while(c.moveToNext())pending+=listOf(c.getString(0),c.getString(1),c.getString(2),c.getString(3),c.getLong(4),c.getLong(5),c.getLong(6),c.getString(7),c.getLong(8))}
  pending.forEach{t->val e=s.events.firstOrNull{it.id==t[3]};val r=e?.reminders?.firstOrNull{it.id==t[1]};val where="epoch=? AND rule_id=? AND rule_version=? AND occurrence_key=?";val key=arrayOf(t[0],t[1],t[4],t[2]);if(t[0]!=s.epoch||e==null||r==null||!r.enabled||r.version!=t[4]||e.version!=t[5]||s.lifecycle(e.id)!="active"||e.goal?.state in setOf("completed","canceled")||now>t[6]as Long){sql.execSQL("UPDATE delivery_log SET state='skipped' WHERE $where",key);return@forEach};if(!notificationAllowed()){sql.execSQL("UPDATE delivery_log SET state='failed',last_error_code='NOTIFICATION_DISABLED',next_attempt_at=? WHERE $where",arrayOf(now+900000,*key));return@forEach}
   sql.execSQL("UPDATE delivery_log SET state='posting',attempted_at=?,attempt_count=attempt_count+1 WHERE $where",arrayOf(now,*key));try{val intent=Intent(context,MainActivity::class.java).setData(Uri.parse("daybook://event/${s.epoch}/${e.id}"));val open=PendingIntent.getActivity(context,0,intent,PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT);val notification=NotificationCompat.Builder(context,"events").setSmallIcon(R.drawable.ic_datebook).setContentTitle(if((context.applicationContext as DateBookApplication).graph.lock.enabled)"重要日子提醒"else e.title).setContentText(if((context.applicationContext as DateBookApplication).graph.lock.enabled)"打开应用解锁后查看"else dates.evaluate(e.dateInput()).label).setContentIntent(open).setAutoCancel(true).setOnlyAlertOnce(true).setVisibility(NotificationCompat.VISIBILITY_SECRET).build();manager.notify(t[7]as String,1,notification);sql.execSQL("UPDATE delivery_log SET state='posted',last_error_code=NULL WHERE $where",key)}catch(_:Exception){sql.execSQL("UPDATE delivery_log SET state='failed',last_error_code='NOTIFICATION_POST_FAILED',next_attempt_at=? WHERE $where",arrayOf(now+60000,*key))}}
  sql.execSQL("DELETE FROM delivery_log WHERE fire_at<? AND state IN ('posted','skipped')",arrayOf(now-30L*86400000))
  var retry=false;sql.query("SELECT 1 FROM delivery_log WHERE state IN ('pending','posting','failed') LIMIT 1").use{retry=it.moveToFirst()};if(retry)WorkManager.getInstance(context).enqueueUniqueWork("datebook-delivery-retry",ExistingWorkPolicy.KEEP,OneTimeWorkRequestBuilder<MaintenanceWorker>().setInitialDelay(1,TimeUnit.MINUTES).build())
 }
 suspend fun refreshWidgets(){DateBookWidget().updateAll(context)}
 fun calendarAdd(event:Event):Intent {val p=dates.evaluate(event.dateInput());val occurrence=p.occurrence?:throw AppException("DATE_EXHAUSTED");val start=occurrence.instant?:occurrence.date.atStartOfDay(ZoneId.of("UTC")).toInstant();val end=if(event.date.allDay)start.plusSeconds(86400)else start.plusSeconds(3600);return Intent(Intent.ACTION_INSERT).setData(CalendarContract.Events.CONTENT_URI).putExtra(CalendarContract.Events.TITLE,event.title).putExtra(CalendarContract.Events.DESCRIPTION,event.greeting).putExtra(CalendarContract.EXTRA_EVENT_BEGIN_TIME,start.toEpochMilli()).putExtra(CalendarContract.EXTRA_EVENT_END_TIME,end.toEpochMilli()).putExtra(CalendarContract.Events.ALL_DAY,event.date.allDay)}
 suspend fun calendarImport(from:LocalDate,to:LocalDate):List<Event> = withContext(Dispatchers.IO){demand(ContextCompat.checkSelfPermission(context,Manifest.permission.READ_CALENDAR)==PackageManager.PERMISSION_GRANTED,"CALENDAR_PERMISSION_REQUIRED");demand(to>=from&&to.toEpochDay()-from.toEpochDay()<=366,"CALENDAR_WINDOW_INVALID");val b=store.state.value.books.first{it.builtinKey=="uncategorized"};val uri=CalendarContract.Instances.CONTENT_URI.buildUpon().also{ContentUris.appendId(it,from.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli());ContentUris.appendId(it,to.plusDays(1).atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli())}.build();val out=mutableListOf<Event>();context.contentResolver.query(uri,arrayOf(CalendarContract.Instances.TITLE,CalendarContract.Instances.BEGIN,CalendarContract.Instances.ALL_DAY,CalendarContract.Instances.DESCRIPTION,CalendarContract.Instances.EVENT_TIMEZONE),null,null,CalendarContract.Instances.BEGIN+" ASC")?.use{c->while(c.moveToNext()){demand(out.size<2000,"IMPORT_LIMIT_EXCEEDED");val all=c.getInt(2)!=0;val zone=if(all)ZoneId.of("UTC")else runCatching{ZoneId.of(c.getString(4))}.getOrDefault(ZoneId.systemDefault());val time=Instant.ofEpochMilli(c.getLong(1)).atZone(zone);out+=Event(bookId=b.id,title=c.getString(0).orEmpty().ifBlank{"日历事件"}.also{demand(graphemeCount(it)<=60&&it.toByteArray().size<=4096,"CALENDAR_TEXT_TOO_LONG","title")},greeting=c.getString(3).orEmpty().also{demand(graphemeCount(it)<=2000&&it.toByteArray().size<=65536,"CALENDAR_TEXT_TOO_LONG","greeting")},date=DateSpec(year=time.year,month=time.monthValue,day=time.dayOfMonth,allDay=all,localTime=if(all)null else time.toLocalTime().withSecond(0).withNano(0).toString(),zoneId=if(all)null else zone.id))}};out}
 suspend fun validateBackupAssets(preview:BackupPreview)=withContext(Dispatchers.IO){
  preview.state.assets.forEach { a ->
   val file=File(preview.assetRoot,a.relativePath);val bounds=BitmapFactory.Options().apply{inJustDecodeBounds=true};BitmapFactory.decodeFile(file.path,bounds)
   demand(bounds.outWidth==a.width&&bounds.outHeight==a.height&&bounds.outMimeType==a.mimeType&&bounds.outWidth.toLong()*bounds.outHeight<=40000000,"ASSET_CORRUPT")
   var sample=1;while(max(bounds.outWidth,bounds.outHeight)/sample>2560)sample*=2
   val bitmap=BitmapFactory.decodeFile(file.path,BitmapFactory.Options().apply{inSampleSize=sample})?:throw AppException("ASSET_CORRUPT");bitmap.recycle()
  }
 }
 suspend fun stagePhoto(uri:Uri):Asset=withContext(Dispatchers.IO){
  val temporary=File.createTempFile("photo-",".tmp",context.cacheDir);val encoded=File.createTempFile("photo-",".jpg",context.cacheDir)
  try{
   context.contentResolver.openInputStream(uri)?.use{i->temporary.outputStream().use{o->val b=ByteArray(65536);var total=0L;while(true){val n=i.read(b);if(n<0)break;total+=n;demand(total<=25L*1024*1024,"PHOTO_TOO_LARGE");o.write(b,0,n)}}}?:throw AppException("PHOTO_UNREADABLE")
   val bounds=BitmapFactory.Options().apply{inJustDecodeBounds=true};BitmapFactory.decodeFile(temporary.path,bounds)
   demand(bounds.outWidth>0&&bounds.outHeight>0&&bounds.outWidth.toLong()*bounds.outHeight<=40000000,"PHOTO_DIMENSIONS_INVALID")
   var sample=1;while(max(bounds.outWidth,bounds.outHeight)/sample>2560)sample*=2
   val raw=BitmapFactory.decodeFile(temporary.path,BitmapFactory.Options().apply{inSampleSize=sample})?:throw AppException("PHOTO_DECODE_FAILED")
   val orientation=runCatching{android.media.ExifInterface(temporary.path).getAttributeInt(android.media.ExifInterface.TAG_ORIENTATION,1)}.getOrDefault(1)
   val matrix=Matrix().apply{when(orientation){2->setScale(-1f,1f);3->setRotate(180f);4->{setRotate(180f);postScale(-1f,1f)};5->{setRotate(90f);postScale(-1f,1f)};6->setRotate(90f);7->{setRotate(270f);postScale(-1f,1f)};8->setRotate(270f)}}
   val bitmap=try{if(orientation in 2..8)Bitmap.createBitmap(raw,0,0,raw.width,raw.height,matrix,true)else raw}catch(e:Exception){raw.recycle();throw AppException("PHOTO_DECODE_FAILED")}
   if(bitmap!==raw)raw.recycle()
   try{encoded.outputStream().use{demand(bitmap.compress(Bitmap.CompressFormat.JPEG,90,it),"PHOTO_ENCODE_FAILED")};store.addAsset(encoded,"image/jpeg",bitmap.width,bitmap.height)}finally{bitmap.recycle()}
  }finally{temporary.delete();encoded.delete()}
 }
 suspend fun renderCard(event:Event,includeGreeting:Boolean,ratio:String):List<File> = withContext(Dispatchers.IO){
  val width=1080;val base=when(ratio){"1:1"->1080;"9:16"->1920;else->1440};val pad=80;val textWidth=width-pad*2
  val snapshot=store.leaseSnapshot()
  try{
   val current=snapshot.state.events.firstOrNull{it.id==event.id}?:throw AppException("EVENT_NOT_FOUND")
   demand(current.version==event.version,"PREVIEW_STALE")
   val a=event.appearance
   var photo:Bitmap?=null
   try{
    a.assetId?.let{id->val asset=snapshot.state.assets.firstOrNull{it.id==id}?:throw AppException("ASSET_MISSING");val options=BitmapFactory.Options().apply{inJustDecodeBounds=true};val file=File(snapshot.root,asset.relativePath);BitmapFactory.decodeFile(file.path,options);demand(options.outWidth>0&&options.outHeight>0&&options.outWidth.toLong()*options.outHeight<=40000000,"ASSET_CORRUPT");var sample=1;while(max(options.outWidth,options.outHeight)/sample>2560)sample*=2;photo=BitmapFactory.decodeFile(file.path,BitmapFactory.Options().apply{inSampleSize=sample})?:throw AppException("ASSET_CORRUPT")}
    val palette=when(a.presetKey){"sunset"->intArrayOf(Color.rgb(154,83,64),Color.rgb(65,34,50));"ocean"->intArrayOf(Color.rgb(43,92,131),Color.rgb(15,39,75));"lavender"->intArrayOf(Color.rgb(108,82,138),Color.rgb(48,32,77));else->intArrayOf(Color.rgb(31,76,57),Color.rgb(15,32,28))}
    val background=if(a.backgroundKind=="solid")a.solidArgb else photo?.getPixel(photo!!.width/2,photo!!.height/2)?:palette[0]
    val luminance=(.2126*Color.red(background)+.7152*Color.green(background)+.0722*Color.blue(background))*(if(photo!=null)1-a.dimAmount else 1.0)
    val foreground=when(a.textColorMode){"dark"->Color.rgb(20,30,25);"light"->Color.WHITE;else->if(luminance>150)Color.rgb(20,30,25)else Color.WHITE}
    fun paint(size:Float)=TextPaint(Paint.ANTI_ALIAS_FLAG).apply{color=foreground;textSize=size;typeface=if(a.fontKey=="serif")Typeface.SERIF else Typeface.DEFAULT}
    fun layout(value:String,size:Float)=StaticLayout.Builder.obtain(value,0,value.length,paint(size),textWidth).setIncludePad(false).setLineSpacing(10f,1f).build()
    val title=layout(event.title,54f);val projection=dates.evaluate(event.dateInput());val count=layout(projection.label,80f);val date=layout(projection.occurrence?.date?.toString().orEmpty(),34f)
    val titleTop=80;val countTop=titleTop+title.height+44;val dateTop=countTop+count.height+20
    val headerBottom=dateTop+date.height+60;val height=max(base,headerBottom+180)
    val greeting=if(includeGreeting)event.greeting else "";val body=layout(greeting,40f);val capacity=height-headerBottom-80
    val segments=mutableListOf<Pair<Int,Int>>()
    if(greeting.isNotBlank()){var line=0;while(line<body.lineCount){val start=line;val top=body.getLineTop(start);while(line<body.lineCount&&body.getLineBottom(line)-top<=capacity)line++;demand(line>start,"CARD_LAYOUT_FAILED");segments+=start to line;demand(segments.size<=100,"CARD_LIMIT_EXCEEDED")}}else segments+=0 to 0
    val shares=File(context.cacheDir,"shares").apply{mkdirs()};val output=mutableListOf<File>()
    try{segments.forEachIndexed{page,segment->val bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888)
     try{val canvas=Canvas(bitmap);val backgroundPaint=Paint(Paint.ANTI_ALIAS_FLAG).apply{shader=LinearGradient(0f,0f,width.toFloat(),height.toFloat(),palette,null,Shader.TileMode.CLAMP)}
      canvas.drawRect(0f,0f,width.toFloat(),height.toFloat(),backgroundPaint);if(a.backgroundKind=="solid")canvas.drawColor(a.solidArgb)
      photo?.let{p->val scale=max(width.toFloat()/p.width,height.toFloat()/p.height);val w=p.width*scale;val h=p.height*scale;val left=(width-w)*a.focusX.toFloat();val top=(height-h)*a.focusY.toFloat();canvas.drawBitmap(p,null,RectF(left,top,left+w,top+h),null);canvas.drawColor(Color.argb((a.dimAmount*255).toInt(),0,0,0))}
      val shift=if(greeting.isBlank())(height-headerBottom)/2 else 0
      fun draw(l:StaticLayout,y:Int){canvas.save();canvas.translate(pad.toFloat(),(y+shift).toFloat());l.draw(canvas);canvas.restore()}
      draw(title,titleTop);draw(count,countTop);draw(date,dateTop)
      if(greeting.isNotBlank()){val top=body.getLineTop(segment.first);val bottom=body.getLineBottom(segment.second-1);canvas.save();canvas.clipRect(pad,headerBottom,width-pad,headerBottom+bottom-top);canvas.translate(pad.toFloat(),(headerBottom-top).toFloat());body.draw(canvas);canvas.restore()}
      if(segments.size>1)canvas.drawText("${page+1} / ${segments.size}",width-140f,height-24f,paint(22f))
      val file=File.createTempFile("card-",".png",shares);file.outputStream().use{demand(bitmap.compress(Bitmap.CompressFormat.PNG,100,it),"CARD_WRITE_FAILED")};output+=file
     }finally{bitmap.recycle()}
    };output}catch(e:Exception){output.forEach{it.delete()};throw e}
   }finally{photo?.recycle()}
  }finally{snapshot.close()}
 }
 fun share(files:List<File>):Intent {demand(files.isNotEmpty(),"SHARE_EMPTY");val shares=File(context.cacheDir,"shares").apply{mkdirs()};val safe=files.map{f->demand(f.isFile,"FILE_NOT_FOUND");if(f.canonicalPath.startsWith(shares.canonicalPath+File.separator))f else File.createTempFile("datebook-",".${f.extension.ifBlank{"bin"}}",shares).also{f.copyTo(it,true)}};val uris=ArrayList(safe.map{FileProvider.getUriForFile(context,"${context.packageName}.files",it)});return Intent(if(files.size==1)Intent.ACTION_SEND else Intent.ACTION_SEND_MULTIPLE).setType(if(files.all{it.extension=="png"})"image/png"else"application/octet-stream").addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION).apply{if(files.size==1)putExtra(Intent.EXTRA_STREAM,uris.first())else putParcelableArrayListExtra(Intent.EXTRA_STREAM,uris);clipData=ClipData.newRawUri("DateBook",uris.first()).also{c->uris.drop(1).forEach{c.addItem(ClipData.Item(it))}}}}
}

class ReminderReceiver:BroadcastReceiver(){override fun onReceive(context:Context,intent:Intent){val result=goAsync();val app=context.applicationContext as DateBookApplication;app.graph.scope.launch(Dispatchers.IO){try{val parts=intent.data?.pathSegments.orEmpty();if(parts.size==2)app.graph.systems.deliver(parts[0],intent.getStringExtra("token").orEmpty())}catch(_:Exception){WorkManager.getInstance(context).enqueueUniqueWork("datebook-receiver-retry",ExistingWorkPolicy.KEEP,OneTimeWorkRequestBuilder<MaintenanceWorker>().build())}finally{result.finish()}}}}
class RebuildReceiver:BroadcastReceiver(){override fun onReceive(context:Context,intent:Intent){WorkManager.getInstance(context).enqueueUniqueWork("datebook-rebuild",ExistingWorkPolicy.REPLACE,OneTimeWorkRequestBuilder<MaintenanceWorker>().build())}}
class MaintenanceWorker(context:Context,params:WorkerParameters):CoroutineWorker(context,params){override suspend fun doWork():Result=try{val g=(applicationContext as DateBookApplication).graph;g.store.awaitReady();g.service.purgeExpired();g.systems.reconcile();g.store.gc();Result.success()}catch(_:Exception){Result.retry()}}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt'] = r'''package cn.datebook.app.ui

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import cn.datebook.app.DateBookApplication
import cn.datebook.core.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.*
import java.time.LocalDate
import cn.datebook.app.platform.JobManager

@Serializable data class EditorDraft(val event: Event, val dateText: String, val startDate: String = LocalDate.now().toString(), val tags: String = "")
data class FilePreview(val imported: ImportPreview? = null, val backup: BackupPreview? = null,
 val expectedEpoch: String, val expectedRevision: Long, val createdAt:Long=System.currentTimeMillis()) {
 val state get() = imported?.state ?: backup!!.state
}

class AppViewModel(application: Application) : AndroidViewModel(application) {
 val graph = (application as DateBookApplication).graph
 val library = graph.store.state
 val ready = graph.store.ready
 val startupError = graph.store.startupError
 val prefs = DevicePreferences(application)
 val busy = MutableStateFlow(false)
 val message = MutableStateFlow<String?>(null)
 val outgoing = MutableStateFlow<Intent?>(null)
 val preview = MutableStateFlow<FilePreview?>(null)
 val calendarCandidates = MutableStateFlow<List<Event>>(emptyList())
 val currentJob = MutableStateFlow<String?>(null)
 val json = Json { encodeDefaults = true; ignoreUnknownKeys = false }
 private val pending=java.util.concurrent.ConcurrentLinkedQueue<Pair<String,()->Unit>>()
 fun afterUnlock(action:()->Unit) { if(graph.lock.locked.value){pending+=library.value.epoch to action;message.value="请解锁以继续刚才的文件操作"}else action() }
 fun resumePending() { if(graph.lock.locked.value)return;while(true){val (epoch,action)=pending.poll()?:break;if(epoch==library.value.epoch)action()else message.value="资料库已切换，请重新选择文件"} }

 fun execute(label: String = "已完成", allowLocked: Boolean = false, work: suspend () -> Unit) {
  if (busy.value) return
  busy.value = true
  viewModelScope.launch {
   try {
    withContext(Dispatchers.IO) {
     if (!allowLocked) demand(!graph.lock.locked.value, "LOCK_REQUIRED")
     graph.store.awaitReady(); work()
    }
    message.value = label
   } catch (c: CancellationException) { throw c }
   catch (e: Exception) { message.value = friendly(e) }
   finally { busy.value = false }
  }
 }
 suspend fun updateSystem() {
  try { graph.systems.reconcile(); graph.systems.refreshWidgets() }
  catch (_: Exception) { message.value = "资料已保存；系统提醒或组件暂未更新，可在设置中重试" }
 }
 fun save(draft: EditorDraft, existing: Event?, draftKey: String, done: (String) -> Unit) = execute("已保存") {
  val parts = Regex("(?:(\\d{4})|--)-(\\d{2})-(\\d{2})").matchEntire(draft.dateText)
   ?: throw AppException("DATE_INVALID", "日期，请使用 YYYY-MM-DD；未知出生年使用 ---MM-DD")
  val e = draft.event
  val names = draft.tags.split(',','，').map { it.trim() }.filter { it.isNotEmpty() }.distinct()
  demand(names.size <= 20,"TAG_LIMIT")
  val goal = if (e.kind == "goal") (e.goal ?: GoalDetail(draft.startDate)).copy(startDate = draft.startDate) else null
  val updated = e.copy(date = e.date.copy(year=parts.groupValues[1].toIntOrNull(),month=parts.groupValues[2].toInt(),day=parts.groupValues[3].toInt()),goal=goal,
   reminders=if(existing==null&&e.kind=="birthday"&&e.reminders.isEmpty())listOf(ReminderRule(enabled=false))else e.reminders)
  graph.dates.validate(updated.dateInput())
  val saved = graph.service.saveEventWithTagNames(updated,names, existing?.version)
  prefs.deleteDraft(draftKey); updateSystem()
  withContext(Dispatchers.Main) { done(saved.id) }
 }
 fun deletePreview() { if(busy.value){message.value="任务进行中，请先取消任务";return};preview.value?.backup?.assetRoot?.let(::cleanupTemp);preview.value = null }
 private fun cleanupTemp(directory:File) {
  val cache=getApplication<Application>().cacheDir.canonicalFile
  if(directory.parentFile?.canonicalFile!=cache || !directory.name.matches(Regex("(?:restore|merge)-[0-9a-f-]{36}")))return
  if(!directory.exists())return
  java.nio.file.Files.walkFileTree(directory.toPath(),object:java.nio.file.SimpleFileVisitor<java.nio.file.Path>(){
   override fun visitFile(file:java.nio.file.Path,attrs:java.nio.file.attribute.BasicFileAttributes):java.nio.file.FileVisitResult {java.nio.file.Files.deleteIfExists(file);return java.nio.file.FileVisitResult.CONTINUE}
   override fun postVisitDirectory(dir:java.nio.file.Path,error:IOException?):java.nio.file.FileVisitResult{if(error!=null)throw error;java.nio.file.Files.deleteIfExists(dir);return java.nio.file.FileVisitResult.CONTINUE}
  })
 }
 fun importText(uri: Uri, csv: Boolean) = execute("文件已校验，请确认导入") {
  val bytes = getApplication<Application>().contentResolver.openInputStream(uri)?.use { bounded(it,10*1024*1024) } ?: throw AppException("FILE_IO_FAILED")
  val parsed = if(csv) graph.codec.importCsv(bytes) else graph.codec.importJson(bytes)
  val current=library.value
  preview.value?.backup?.assetRoot?.let(::cleanupTemp)
  preview.value=FilePreview(imported=parsed,expectedEpoch=current.epoch,expectedRevision=current.revision)
 }
 fun readBackup(uri: Uri, password: CharArray) = execute("备份已校验，请确认恢复",allowLocked=true) {
  try {
   val staging=File(getApplication<Application>().cacheDir,"restore-${newId()}").apply { mkdirs() }
   try {
    val backup=getApplication<Application>().contentResolver.openInputStream(uri)?.use { graph.codec.readBackup(it,staging,password.takeIf { it.isNotEmpty() }) } ?: throw AppException("FILE_IO_FAILED")
    graph.systems.validateBackupAssets(backup)
    val current=library.value
    preview.value?.backup?.assetRoot?.let(::cleanupTemp)
    preview.value=FilePreview(backup=backup,expectedEpoch=current.epoch,expectedRevision=current.revision)
   } catch(e:Exception){cleanupTemp(staging);throw e}
  } finally { password.fill('\u0000') }
 }
 fun commitPreview(replace: Boolean, confirmation: String = "") = runJob("import_commit",allowLocked=true) {
  val p=preview.value ?: throw AppException("PREVIEW_STALE")
  demand(System.currentTimeMillis()-p.createdAt in 0..1800000,"PREVIEW_EXPIRED")
  if(graph.lock.locked.value) demand(replace && p.backup != null && confirmation=="替换本机全部数据","LOCK_REQUIRED")
  demand(!replace || p.backup != null && confirmation=="替换本机全部数据","REPLACE_CONFIRM_REQUIRED")
  val current=library.value
  demand(current.epoch==p.expectedEpoch && current.revision==p.expectedRevision,"PREVIEW_STALE")
  if (p.backup != null) {
   val incoming=p.backup
   val candidate=if(replace) incoming.state else graph.codec.merge(current,ImportPreview(incoming.state,incoming.backupId,incoming.fileSha256,"backup"))
   val media=if(replace) incoming.assetRoot else combineMedia(current,incoming)
   try {
   progress("已校验资料，准备切换资料库",1,2)
   committing()
   withContext(NonCancellable) {
     val wasLocked=graph.lock.locked.value
     val installed=graph.store.installFrom(candidate,media,p.expectedRevision,p.expectedEpoch)
     if(replace) { prefs.clearDrafts();pending.clear();if(wasLocked)prefs.replacementPinEpoch(installed.epoch) }
   }
   } finally { if(media!=incoming.assetRoot)cleanupTemp(media) }
  } else {
   demand(!graph.lock.locked.value,"LOCK_REQUIRED")
   committing()
   withContext(NonCancellable) { graph.store.transaction(expectedEpoch=p.expectedEpoch) { s ->
    demand(s.revision==p.expectedRevision,"PREVIEW_STALE")
    Change(graph.codec.merge(s,p.imported!!),Unit)
   } }
  }
  p.backup?.assetRoot?.let(::cleanupTemp)
  preview.value=null; updateSystem();"已导入"
 }
 private suspend fun combineMedia(current:LibraryState,incoming:BackupPreview):File {
  val out=File(getApplication<Application>().cacheDir,"merge-${newId()}").apply { mkdirs() }
  val lease=graph.store.leaseSnapshot()
  try {
   demand(lease.state.epoch==current.epoch&&lease.state.revision==current.revision,"PREVIEW_STALE")
   for(a in current.assets+incoming.state.assets) {
    demand(safeAssetPath(a.relativePath),"FILE_PATH_UNSAFE")
    val source=if(a in current.assets)File(lease.root,a.relativePath)else File(incoming.assetRoot,a.relativePath)
    val target=File(out,a.relativePath)
    if(target.exists()) demand(target.length()==source.length() && sha256(target)==sha256(source),"ASSET_HASH_MISMATCH")
    else { target.parentFile!!.mkdirs(); source.copyTo(target) }
   }
  } catch(e:Exception){cleanupTemp(out);throw e} finally { lease.close() }
  return out
 }
 fun export(uri:Uri,format:String,ids:Set<String>?=null,password:CharArray=charArrayOf(),includeTrash:Boolean=false) = runJob("export_$format",onRejected={password.fill('\u0000')}) {
  try {
   val lease=graph.store.leaseSnapshot()
   try {
    progress("正在生成完整文件",0,2)
    val resolver=getApplication<Application>().contentResolver
    // Generate completely in private staging; cancel/failure cannot emit a plausible half-backup.
    val temp=File(getApplication<Application>().cacheDir,"export-${newId()}.tmp")
    try {
     temp.outputStream().use { out -> when(format) {
      "backup" -> graph.codec.writeBackup(lease.state,lease.root,out,password.takeIf { it.isNotEmpty() },includeTrash)
      "csv" -> out.write(graph.codec.exportCsv(lease.state,ids?:lease.state.events.filter { lease.state.lifecycle(it.id)=="active" }.map { it.id }.toSet()))
      else -> out.write(graph.codec.exportJson(lease.state,ids))
     } }
     progress("正在写入所选位置",1,2)
     committing()
     withContext(NonCancellable) {resolver.openOutputStream(uri,"wt")?.use { out -> temp.inputStream().use { it.copyTo(out) } } ?: throw AppException("FILE_IO_FAILED")}
    } finally { temp.delete() }
   } finally { lease.close() }
  } finally { password.fill('\u0000') }
  "已导出"
 }
 fun shareCard(id:String,includeGreeting:Boolean,ratio:String) = execute("卡片已生成") {
  val files=graph.systems.renderCard(library.value.event(id),includeGreeting,ratio)
  outgoing.value=graph.systems.share(files)
 }
 fun photo(uri:Uri,done:(Asset)->Unit) = execute("图片已保存") { val a=graph.systems.stagePhoto(uri); withContext(Dispatchers.Main) { done(a) } }
 fun calendarRead(from:LocalDate,to:LocalDate) = execute("已读取日历，请选择要复制的事项") { calendarCandidates.value=graph.systems.calendarImport(from,to) }
 fun calendarImport(ids:Set<String>) = execute("日历已复制为本地事件") {
  graph.service.saveEventsBatch(calendarCandidates.value.filter { it.id in ids })
  calendarCandidates.value=emptyList(); updateSystem()
 }
 fun clearAll(confirmation:String) = execute("已清空本机资料",allowLocked=true) {
  demand(confirmation=="清空本机全部数据","REPLACE_CONFIRM_REQUIRED")
  val s=library.value
  graph.store.install(defaultLibrary(),s.revision,s.epoch)
  prefs.clearDrafts();prefs.replacementPinEpoch(null);pending.clear();graph.lock.clearForReplacement(); preview.value?.backup?.assetRoot?.let(::cleanupTemp);preview.value=null; updateSystem(); graph.store.gc()
 }
 fun replacementPin(pin:CharArray) = execute("新的 PIN 已设置",allowLocked=true) {
  try {
   demand(prefs.replacementPinEpoch.first()==library.value.epoch,"LOCK_REQUIRED")
   demand(pin.size in 6..12&&pin.all{it in '0'..'9'},"PIN_INVALID")
   graph.lock.replacePinAfterLibraryReplacement(pin);prefs.replacementPinEpoch(null);updateSystem()
  } finally {pin.fill('\u0000')}
 }
 fun mutate(label:String="已完成",action:suspend ()->Unit) = execute(label) { action(); updateSystem() }
 fun error(e:Exception) { message.value=friendly(e) }
 private fun runJob(type:String,allowLocked:Boolean=false,onRejected:()->Unit={},block:suspend JobManager.JobContext.()->String) {
  if(busy.value){onRejected();message.value="已有任务进行中，请完成或取消后重试";return}
  if(!allowLocked&&graph.lock.locked.value){onRejected();message.value="请先解锁";return}
  busy.value=true
  val id=try{graph.jobs.start(type){graph.store.awaitReady();if(!allowLocked)demand(!graph.lock.locked.value,"LOCK_REQUIRED");block()}}
   catch(e:Exception){busy.value=false;onRejected();message.value=friendly(e);return}
  currentJob.value=id
  viewModelScope.launch {
   val end=graph.jobs.observe(id).first{it.state in setOf("completed","failed","canceled")}
   message.value=when(end.state){"completed"->end.result?:"操作已完成";"canceled"->"任务已取消，本机资料保持不变";else->"操作未完成（${end.error}），已保存的本机资料未被清空"}
   busy.value=false
  }
 }
 override fun onCleared(){ if(!busy.value)runCatching{preview.value?.backup?.assetRoot?.let(::cleanupTemp)};pending.clear();super.onCleared() }

 companion object {
  fun sha256(file:File):String { val d=java.security.MessageDigest.getInstance("SHA-256");file.inputStream().use{input->val bytes=ByteArray(65536);while(true){val n=input.read(bytes);if(n<0)break;d.update(bytes,0,n)}};return d.digest().joinToString(""){"%02x".format(it)} }
  fun bounded(input:InputStream,limit:Int):ByteArray {
   val out=ByteArrayOutputStream(); val buffer=ByteArray(8192)
   while(true) { val n=input.read(buffer); if(n<0)break; demand(out.size()+n<=limit,"FILE_LIMIT_EXCEEDED");out.write(buffer,0,n) }
   return out.toByteArray()
  }
  fun friendly(e:Exception):String {
   val a=e as? AppException ?: return "操作失败，请重试。已保存的资料不会被自动清空。"
   val map=mapOf("VERSION_CONFLICT" to "此事项已更新，请退出编辑后重新打开", "PREVIEW_STALE" to "资料发生变化，请重新选择文件并预览", "PREVIEW_EXPIRED" to "预览已超过 30 分钟，请重新选择文件", "LIBRARY_STALE" to "资料库已切换，请重新打开页面", "TREE_DEPTH_EXCEEDED" to "最多支持三级事件", "TREE_DEPTH_LIMIT" to "最多支持三级事件", "TREE_TOO_DEEP" to "最多支持三级事件", "BOOK_PROTECTED" to "未分类本不能删除", "INPUT_REQUIRED" to "请填写必要内容", "DATE_INVALID" to "日期格式或日期无效", "DATE_RANGE" to "日期超出支持范围", "PIN_INCORRECT" to "PIN 不正确", "PIN_INVALID" to "PIN 必须为 6–12 位数字", "LOCK_REQUIRED" to "请先解锁", "LOCK_RATE_LIMIT" to "尝试过于频繁，请稍后重试", "FILE_PASSWORD_INVALID" to "密码错误或文件已损坏", "FILE_AUTH_FAILED" to "密码错误或文件已损坏", "BACKUP_AUTH_FAILED" to "密码错误或文件已损坏", "FILE_LIMIT_EXCEEDED" to "文件超过安全大小限制", "FILE_SCHEMA_INVALID" to "文件格式不符合 DateBook 协议", "PERMISSION_DENIED" to "系统权限未授予，资料仍保存在本机", "ACTION_FUTURE_DATE" to "行动记录日期不能晚于今天", "REPLACE_CONFIRM_REQUIRED" to "请输入完整确认文字", "TAG_LIMIT" to "最多可设置 20 个标签", "CSV_LOSS_REQUIRES_JSON" to "这些事项包含 CSV 无法无损表达的内容，请改用 JSON 导出", "CALENDAR_TEXT_TOO_LONG" to "所选日历事项文字过长，请先在系统日历调整后重试", "ASSET_CORRUPT" to "背景文件损坏或尺寸信息不一致", "BOOK_NAME_CONFLICT" to "已存在同名日子本", "TAG_NAME_CONFLICT" to "已存在同名标签", "GOAL_RANGE_INVALID" to "目标开始日不能晚于截止日", "TEXT_TOO_LONG" to "文字超过允许长度", "TEXT_REQUIRED" to "请填写必要文字")
   return (map[a.code]?:"未完成操作（${a.code}）")+(a.field?.let { " · $it" }?:"")
  }
 }
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt'] = r'''@file:OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class, androidx.compose.foundation.layout.ExperimentalLayoutApi::class, androidx.compose.foundation.ExperimentalFoundationApi::class, androidx.compose.ui.ExperimentalComposeUiApi::class)
package cn.datebook.app.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.BitmapFactory
import android.os.Build
import android.view.WindowManager
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.AlertDialog as MaterialAlertDialog
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.*
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.focus.focusProperties
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.LocalTextToolbar
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.*
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.compose.*
import cn.datebook.app.platform.JobSnapshot
import cn.datebook.core.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import java.time.*
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@Serializable data object HomeRoute
@Serializable data object BooksRoute
@Serializable data object GoalsRoute
@Serializable data object SettingsRoute
@Serializable data object SearchRoute
@Serializable data object CalendarRoute
@Serializable data object ToolsRoute
@Serializable data class DetailRoute(val id:String)
@Serializable data class EditRoute(val id:String="",val parentId:String="",val bookId:String="",val goal:Boolean=false)
@Serializable data class BookRoute(val id:String)
@Serializable data class LifecycleRoute(val kind:String)
@Serializable data class ShareRoute(val id:String)

private val forest=Color(0xFF214F43)
private val cream=Color(0xFFF7F6F0)
private val lightScheme=lightColorScheme(primary=forest,secondary=Color(0xFFA26B3F),background=cream,surface=cream,surfaceVariant=Color(0xFFE6EBE5))
private val darkScheme=darkColorScheme(primary=Color(0xFF91C7B2),secondary=Color(0xFFE9BA8B),background=Color(0xFF131C18),surface=Color(0xFF131C18))
private val LocalClockTick=compositionLocalOf { 0L }
private val LocalLibraryLocked=compositionLocalOf { false }

/** Dialogs are separate windows: alpha on the underlying screen cannot hide them. */
@Composable private fun AlertDialog(onDismissRequest:()->Unit,confirmButton:@Composable ()->Unit,
 dismissButton:(@Composable ()->Unit)?=null,title:(@Composable ()->Unit)?=null,text:(@Composable ()->Unit)?=null) {
 if(!LocalLibraryLocked.current)MaterialAlertDialog(onDismissRequest=onDismissRequest,confirmButton=confirmButton,dismissButton=dismissButton,title=title,text=text)
}

@Composable fun DateBookRoot(vm:AppViewModel,activity:FragmentActivity,requested:StateFlow<String?>,consume:()->Unit) {
 val theme by vm.prefs.theme.collectAsStateWithLifecycle("system")
 val dark=theme=="dark" || theme=="system"&&isSystemInDarkTheme()
 MaterialTheme(colorScheme=if(dark)darkScheme else lightScheme, typography=Typography()) {
  val ready by vm.ready.collectAsStateWithLifecycle()
  val error by vm.startupError.collectAsStateWithLifecycle()
  val locked by vm.graph.lock.locked.collectAsStateWithLifecycle()
  val busy by vm.busy.collectAsStateWithLifecycle()
  val message by vm.message.collectAsStateWithLifecycle()
  val outgoing by vm.outgoing.collectAsStateWithLifecycle()
  val replacementPinEpoch by vm.prefs.replacementPinEpoch.collectAsStateWithLifecycle(null)
  val library by vm.library.collectAsStateWithLifecycle()
  var recovery by rememberSaveable { mutableStateOf(false) }
  val focus=LocalFocusManager.current;val keyboard=LocalSoftwareKeyboardController.current;val toolbar=LocalTextToolbar.current
  val snack=remember { SnackbarHostState() }
  SideEffect {
   if(vm.graph.lock.enabled) activity.window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
   else activity.window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
  }
  LaunchedEffect(message) { message?.let { snack.showSnackbar(it);vm.message.value=null } }
  LaunchedEffect(outgoing,locked) { if(!locked)outgoing?.let { try { activity.startActivity(it) } catch(e:Exception){vm.error(e)};vm.outgoing.value=null } }
  LaunchedEffect(locked,ready,replacementPinEpoch){if(ready&&!locked&&replacementPinEpoch==null)vm.resumePending()}
  LaunchedEffect(locked){if(locked){focus.clearFocus(true);keyboard?.hide();toolbar.hide()}}
  val tick by produceState(System.currentTimeMillis()) { while(true){delay(30000);value=System.currentTimeMillis()} }
  CompositionLocalProvider(LocalClockTick provides tick) { Surface(Modifier.fillMaxSize()) {
   when {
    error!=null -> Column(Modifier.padding(24.dp).fillMaxSize(),verticalArrangement=Arrangement.Center) { Text("无法安全打开资料库",style=MaterialTheme.typography.headlineSmall);Text("${error!!.code}\n资料未被清空。请保留应用数据并寻求修复；不要卸载应用。可重新启动后重试。");Button(onClick={activity.recreate()}){Text("重试打开")} }
    !ready -> Box(Modifier.fillMaxSize(),contentAlignment=Alignment.Center){CircularProgressIndicator()}
    replacementPinEpoch==library.epoch -> ReplacementPinScreen(vm)
    else -> {
     LaunchedEffect(locked) { if(!locked)recovery=false }
     val state by vm.library.collectAsStateWithLifecycle()
     val nav=rememberNavController()
     val request by requested.collectAsStateWithLifecycle()
     LaunchedEffect(request,state.epoch,locked) { if(!locked)request?.let { ref->val id=ref.substringAfter('/');val epoch=ref.substringBefore('/',"");if((epoch.isBlank()||epoch==state.epoch)&&state.events.any{it.id==id})nav.navigate(DetailRoute(id))else vm.message.value="此事件不存在或链接属于旧资料库";consume() } }
     Box(Modifier.fillMaxSize()) {
     Box(Modifier.fillMaxSize().focusProperties { enter={if(locked)FocusRequester.Cancel else FocusRequester.Default} }.focusGroup().then(if(locked)Modifier.alpha(0f).clearAndSetSemantics{}else Modifier)) {
     CompositionLocalProvider(LocalLibraryLocked provides locked) {
     Scaffold(snackbarHost={SnackbarHost(snack)},bottomBar={ NavigationBar {
      val entry by nav.currentBackStackEntryAsState()
      val tabs=listOf(Triple("日子",Icons.Default.Home,HomeRoute),Triple("日子本",Icons.Default.MenuBook,BooksRoute),Triple("目标",Icons.Default.Flag,GoalsRoute),Triple("设置",Icons.Default.Settings,SettingsRoute))
      tabs.forEachIndexed { i,t->
       val selected=when(i){0->entry?.destination?.hasRoute<HomeRoute>();1->entry?.destination?.hasRoute<BooksRoute>();2->entry?.destination?.hasRoute<GoalsRoute>();else->entry?.destination?.hasRoute<SettingsRoute>()}==true
       NavigationBarItem(selected,onClick={when(i){0->nav.navigate(HomeRoute){popUpTo<HomeRoute>{saveState=true};launchSingleTop=true;restoreState=true};1->nav.navigate(BooksRoute){launchSingleTop=true};2->nav.navigate(GoalsRoute){launchSingleTop=true};else->nav.navigate(SettingsRoute){launchSingleTop=true}}},icon={Icon(t.second,t.first)},label={Text(t.first)})
      }
     } }) { padding ->
      Box(Modifier.padding(padding)) {
       NavHost(nav,HomeRoute) {
        composable<HomeRoute>{HomeScreen(vm,state,nav)}
        composable<BooksRoute>{BooksScreen(vm,state,nav)}
        composable<GoalsRoute>{GoalsScreen(vm,state,nav)}
        composable<SettingsRoute>{SettingsScreen(vm,activity,nav)}
        composable<SearchRoute>{SearchScreen(vm,state,nav)}
        composable<CalendarRoute>{CalendarScreen(vm,state,nav)}
        composable<ToolsRoute>{ToolsScreen(vm,onBack={nav.popBackStack()})}
        composable<DetailRoute>{DetailScreen(vm,state,it.toRoute<DetailRoute>().id,nav)}
        composable<EditRoute>{EditorScreen(vm,state,it.toRoute<EditRoute>(),nav)}
        composable<BookRoute>{BookScreen(vm,state,it.toRoute<BookRoute>().id,nav)}
        composable<LifecycleRoute>{LifecycleScreen(vm,state,it.toRoute<LifecycleRoute>().kind,nav)}
        composable<ShareRoute>{ShareScreen(vm,state,it.toRoute<ShareRoute>().id,nav)}
       }
       if(busy) LinearProgressIndicator(Modifier.fillMaxWidth().align(Alignment.TopCenter))
      }
     }
     }
     }
     if(locked)Surface(onClick={},modifier=Modifier.fillMaxSize()) {
      if(recovery)Scaffold(snackbarHost={SnackbarHost(snack)}) { p->ToolsScreen(vm,Modifier.padding(p),recovery=true,onBack={recovery=false}) }
      else Scaffold(snackbarHost={SnackbarHost(snack)}){p->Box(Modifier.padding(p)){LockScreen(vm,activity){recovery=true}}}
     }
     }
    }
   }
  } }
  BackHandler(locked){if(recovery)recovery=false else activity.moveTaskToBack(true)}
 }
}

@Composable private fun Header(title:String,subtitle:String?=null,back:(()->Unit)?=null,actions:@Composable RowScope.()->Unit={}) {
 Row(Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=14.dp),verticalAlignment=Alignment.CenterVertically) {
  if(back!=null) IconButton(back){Icon(Icons.AutoMirrored.Filled.ArrowBack,"返回")}
  Column(Modifier.weight(1f)){Text(title,fontSize=25.sp,fontWeight=FontWeight.Bold);if(subtitle!=null)Text(subtitle,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)}
  actions()
 }
}
@Composable private fun Section(title:String,content:@Composable ColumnScope.()->Unit) {
 ElevatedCard(Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=7.dp),shape=RoundedCornerShape(20.dp)) {
  Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(10.dp)){Text(title,fontWeight=FontWeight.SemiBold);content()}
 }
}
@Composable private fun Empty(text:String="还没有记录，留一个位置给重要的日子。") { Text(text,Modifier.padding(24.dp),color=MaterialTheme.colorScheme.onSurfaceVariant) }
@Composable private fun Options(label:String,value:String,options:List<Pair<String,String>>,change:(String)->Unit) {
 Column {Text(label,style=MaterialTheme.typography.labelLarge);Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)){options.forEach{(v,t)->FilterChip(value==v,{change(v)},label={Text(t)})}} }
}
@Composable private fun Field(label:String,value:String,change:(String)->Unit,lines:Int=1,modifier:Modifier=Modifier) {
 OutlinedTextField(value,change,label={Text(label)},modifier=modifier.fillMaxWidth(),singleLine=lines==1,minLines=lines)
}
@Composable private fun Toggle(label:String,value:Boolean,change:(Boolean)->Unit,detail:String?=null) {
 Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically) {Column(Modifier.weight(1f)){Text(label);if(detail!=null)Text(detail,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)};Switch(value,change)}
}
@Composable private fun Confirm(title:String,text:String,onDismiss:()->Unit,onConfirm:()->Unit) {
 AlertDialog(onDismissRequest=onDismiss,title={Text(title)},text={Text(text)},confirmButton={TextButton(onConfirm){Text("确认")}},dismissButton={TextButton(onDismiss){Text("取消")}})
}
@Composable private fun EventRow(vm:AppViewModel,s:LibraryState,e:Event,click:()->Unit,selected:Boolean?=null,select:(()->Unit)?=null,extra:@Composable RowScope.()->Unit={}) {
 val tick=LocalClockTick.current
 val p=runCatching{vm.graph.dates.evaluate(e.dateInput())}.getOrNull()
 Card(Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=5.dp).combinedClickable(onClick=click,onLongClick=select?:click),shape=RoundedCornerShape(17.dp),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surfaceContainerLow)) {
  Row(Modifier.padding(15.dp),verticalAlignment=Alignment.CenterVertically) {
   if(selected!=null) Checkbox(selected,{select?.invoke()})
   Column(Modifier.weight(1f)){Text(e.title,fontWeight=FontWeight.SemiBold);Text((s.books.find{it.id==e.bookId}?.name?:"")+if(e.parentId!=null)" · 第 ${depth(s,e.id)} 级"else"",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant);if(e.greeting.isNotBlank())Text(e.greeting,maxLines=1,style=MaterialTheme.typography.bodySmall)}
   Column(horizontalAlignment=Alignment.End){Text(p?.days?.toString()?:"—",fontSize=25.sp,fontWeight=FontWeight.Light,color=MaterialTheme.colorScheme.primary);Text(p?.label?:"日期待检查",style=MaterialTheme.typography.labelSmall)}
   extra()
  }
 }
}
@Composable private fun Hero(vm:AppViewModel,e:Event,onClick:()->Unit) {
 val tick=LocalClockTick.current
 val context=LocalContext.current
 var bitmap by remember(e.appearance.assetId) { mutableStateOf<ImageBitmap?>(null) }
 LaunchedEffect(e.appearance.assetId) { bitmap=withContext(Dispatchers.IO) { runCatching { e.appearance.assetId?.let{id->vm.library.value.assets.find{it.id==id}}?.let{a->
  val opts=BitmapFactory.Options().apply{inJustDecodeBounds=true};val file=vm.graph.store.assetFile(a.relativePath);BitmapFactory.decodeFile(file.path,opts);opts.inSampleSize=maxOf(1,maxOf(opts.outWidth,opts.outHeight)/1600);opts.inJustDecodeBounds=false;BitmapFactory.decodeFile(file.path,opts)?.asImageBitmap() }
 }.getOrNull() } }
 val p=runCatching{vm.graph.dates.evaluate(e.dateInput())}.getOrDefault(DateProjection(null,"日期待填写",null))
 val color=when(e.appearance.presetKey){"sunset"->Color(0xFF8B4F45);"ocean"->Color(0xFF345A79);"lavender"->Color(0xFF66557D);else->forest}
 val base=if(e.appearance.backgroundKind=="solid")Color(e.appearance.solidArgb)else color
 val text=when(e.appearance.textColorMode){"dark"->Color(0xFF18251E);"light"->Color.White;else->if(e.appearance.backgroundKind=="solid"&&base.luminance()>.55)Color(0xFF18251E)else Color.White}
 Card(onClick,Modifier.fillMaxWidth().padding(18.dp),shape=RoundedCornerShape(26.dp)) {
  Box(Modifier.fillMaxWidth().heightIn(min=225.dp).background(Brush.linearGradient(listOf(base,base.copy(alpha=.85f))))) {
   bitmap?.let{Image(it,null,Modifier.matchParentSize(),contentScale=ContentScale.Crop,alignment=BiasAlignment((e.appearance.focusX*2-1).toFloat(),(e.appearance.focusY*2-1).toFloat()))}
   if(bitmap!=null)Box(Modifier.matchParentSize().background(Color.Black.copy(alpha=e.appearance.dimAmount.toFloat())))
   Column(Modifier.padding(24.dp),verticalArrangement=Arrangement.spacedBy(8.dp)) {
    Text(e.title,color=text,fontSize=21.sp,fontWeight=FontWeight.Medium)
    Row(verticalAlignment=Alignment.Bottom){Text(p.days?.toString()?:"—",color=text,fontSize=64.sp,fontWeight=FontWeight.Light);Text(" 天",color=text,modifier=Modifier.padding(bottom=10.dp))}
    Text(p.label+(p.age?.let{" · ${it}岁"}?:""),color=text)
    Text(p.occurrence?.date?.toString()?:"无后续日期",color=text.copy(alpha=.75f),fontSize=12.sp)
   }
  }
 }
}

@Composable private fun HomeScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 val tick=LocalClockTick.current
 val list=vm.graph.service.homeEvents(s,s.home.selectedBookId)
 val hero=vm.graph.service.hero(s,s.home.selectedBookId)
 LazyColumn {
  item { Header("重要的日子",LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy 年 M 月 d 日")),actions={IconButton({nav.navigate(SearchRoute)}){Icon(Icons.Default.Search,"搜索")};IconButton({nav.navigate(CalendarRoute)}){Icon(Icons.Default.CalendarMonth,"日历")};IconButton({nav.navigate(EditRoute())}){Icon(Icons.Default.Add,"新建事件")}}) }
  item { Row(Modifier.padding(horizontal=18.dp).horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)) {
   FilterChip(s.home.selectedBookId==null,{vm.mutate{vm.graph.service.saveHome(s.home.copy(selectedBookId=null))}},label={Text("全部")})
   s.books.sortedBy{it.sortRank}.forEach{b->FilterChip(s.home.selectedBookId==b.id,{vm.mutate{vm.graph.service.saveHome(s.home.copy(selectedBookId=b.id))}},label={Text(b.name)})}
  } }
  if(hero!=null)item { Hero(vm,hero){nav.navigate(DetailRoute(hero.id))} }
  item { Row(Modifier.padding(horizontal=18.dp),verticalAlignment=Alignment.CenterVertically){Text("我的日子",Modifier.weight(1f),fontWeight=FontWeight.Bold);TextButton({vm.mutate{vm.graph.service.saveHome(s.home.copy(sortMode=if(s.home.sortMode=="date")"manual"else"date"))}}){Text(if(s.home.sortMode=="date")"按日期 · 切换手动"else"手动排序 · 切换日期")}} }
  if(list.isEmpty())item { Empty() }
  items(list,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))})}
  item { Spacer(Modifier.height(22.dp)) }
 }
}

@Composable private fun BooksScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var edit by remember{mutableStateOf<Book?>(null)}
 var creating by remember{mutableStateOf(false)}
 var name by remember{mutableStateOf("")}
 var icon by remember{mutableStateOf("book")};var color by remember{mutableIntStateOf(forest.toArgb())};var cover by remember{mutableStateOf<String?>(null)}
 val photo=rememberLauncherForActivityResult(ActivityResultContracts.GetContent()){uri->if(uri!=null)vm.afterUnlock{vm.photo(uri){cover=it.id}}}
 LazyColumn {
  item { Header("日子本","把相似的日子，放在一起。",actions={IconButton({creating=true;name="";icon="book";color=forest.toArgb();cover=null}){Icon(Icons.Default.Add,"创建日子本")}}) }
  items(s.books.sortedBy{it.sortRank},key={it.id}){b->
   ElevatedCard(onClick={nav.navigate(BookRoute(b.id))},Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=7.dp),shape=RoundedCornerShape(21.dp)) {
    Row(Modifier.padding(18.dp),verticalAlignment=Alignment.CenterVertically){Icon(when(b.iconKey){"birthday"->Icons.Default.Cake;"memorial"->Icons.Default.Favorite;"goal"->Icons.Default.Flag;"holiday"->Icons.Default.BeachAccess;else->Icons.Default.MenuBook},null,tint=Color(b.colorArgb));Column(Modifier.weight(1f).padding(start=14.dp)){Text(b.name,fontWeight=FontWeight.SemiBold);Text("${s.events.count{it.bookId==b.id&&s.lifecycle(it.id)=="active"}} 个日子",style=MaterialTheme.typography.bodySmall)};IconButton({reorderBook(vm,s,b,-1)}){Icon(Icons.Default.KeyboardArrowUp,"本子上移")};IconButton({reorderBook(vm,s,b,1)}){Icon(Icons.Default.KeyboardArrowDown,"本子下移")};IconButton({edit=b;name=b.name;icon=b.iconKey;color=b.colorArgb;cover=b.coverAssetId}){Icon(Icons.Default.Edit,"编辑本子")}}
    b.coverAssetId?.let{AssetPreview(vm,it,Modifier.fillMaxWidth().height(110.dp))}
   }
  }
 }
 if(creating||edit!=null)AlertDialog(onDismissRequest={creating=false;edit=null},title={Text(if(creating)"新建日子本"else"修改日子本")},text={Column(Modifier.heightIn(max=450.dp).verticalScroll(rememberScrollState())){Field("名称",name,{name=it});Options("图标",icon,listOf("book" to "书本","birthday" to "生日","memorial" to "纪念","goal" to "目标","holiday" to "假日")){icon=it};Options("颜色",color.toString(),listOf(forest.toArgb().toString() to "森林",0xFF345A79.toInt().toString() to "海蓝",0xFF8B4F45.toInt().toString() to "暖褐")){color=it.toInt()};TextButton({photo.launch("image/*")}){Text(if(cover==null)"选择封面照片"else"更换封面")};if(cover!=null){AssetPreview(vm,cover!!,Modifier.fillMaxWidth().height(100.dp));TextButton({cover=null}){Text("移除封面")}};Text("200 个本子以内；未分类本不能删除。",style=MaterialTheme.typography.bodySmall)}},confirmButton={TextButton({val old=edit;val b=(old?:Book(name=name,sortRank=(s.books.maxOfOrNull{it.sortRank}?:0)+1)).copy(name=name,iconKey=icon,colorArgb=color,coverAssetId=cover);vm.mutate("日子本已保存"){vm.graph.service.saveBook(b,old?.version)};creating=false;edit=null}){Text("保存")}},dismissButton={TextButton({creating=false;edit=null}){Text("取消")}})
}
private fun reorderBook(vm:AppViewModel,s:LibraryState,b:Book,delta:Int) {
 val all=s.books.sortedBy{it.sortRank}.toMutableList();val i=all.indexOfFirst{it.id==b.id};val j=i+delta;if(j !in all.indices)return
 val other=all[j];all[j]=b;all[i]=other;val ranks=all.mapIndexed{index,book->book.id to index.toLong()}.toMap()
 vm.mutate{vm.graph.store.transaction{state->Change(state.copy(books=state.books.map{it.copy(sortRank=ranks.getValue(it.id),version=it.version+1,updatedAt=System.currentTimeMillis())}),Unit)}}
}
@Composable private fun AssetPreview(vm:AppViewModel,id:String,modifier:Modifier) {
 var image by remember(id){mutableStateOf<ImageBitmap?>(null)}
 LaunchedEffect(id){image=withContext(Dispatchers.IO){runCatching{val a=vm.library.value.assets.first{it.id==id};val f=vm.graph.store.assetFile(a.relativePath);val options=BitmapFactory.Options().apply{inSampleSize=4};BitmapFactory.decodeFile(f.path,options)?.asImageBitmap()}.getOrNull()}}
 image?.let{Image(it,null,modifier,contentScale=ContentScale.Crop)}
}

@Composable private fun BookScreen(vm:AppViewModel,s:LibraryState,id:String,nav:NavHostController) {
 val book=s.books.find{it.id==id}
 if(book==null){Empty("日子本已删除");return}
 var selected by rememberSaveable{idState()}
 var query by rememberSaveable{mutableStateOf("")}
 var allLevels by rememberSaveable{mutableStateOf(false)}
 var delete by remember{mutableStateOf(false)}
 var moving by remember{mutableStateOf(false)}
 var tagsDialog by remember{mutableStateOf(false)}
 val found=vm.graph.service.search(s,query,bookId=id).filter{allLevels||it.parentId==null}.let{if(s.home.sortMode=="manual")it.sortedBy{e->e.sortRank}else it}
 LazyColumn {
  item { Header(book.name,"默认只展示本子的根事件",{nav.popBackStack()},actions={IconButton({nav.navigate(EditRoute(bookId=id))}){Icon(Icons.Default.Add,"新建事件")};if(!book.isProtected)IconButton({delete=true}){Icon(Icons.Default.Delete,"删除本子")}}) }
  item { Column(Modifier.padding(horizontal=18.dp)){Field("搜索本子中的日子",query,{query=it});Toggle("显示所有层级（搜索列表）",allLevels,{allLevels=it});Options("排序",s.home.sortMode,listOf("date" to "日期","manual" to "手动")){v->vm.mutate{vm.graph.service.saveHome(s.home.copy(sortMode=v))}}} }
  if(selected.isNotEmpty())item { Section("已选 ${selected.size} 项") {
   FlowRow(horizontalArrangement=Arrangement.spacedBy(6.dp)){TextButton({val ids=selected.toList();vm.mutate{vm.graph.service.setLifecycle(ids,"archive")};selected=emptyList()}){Text("归档")};TextButton({val ids=selected.toList();vm.mutate{vm.graph.service.setLifecycle(ids,"trash")};selected=emptyList()}){Text("移到回收站")};TextButton({moving=true}){Text("移动")};TextButton({tagsDialog=true}){Text("批量标签")};TextButton({selected=found.map{it.id}}){Text("全选")};TextButton({selected=emptyList()}){Text("取消选择")}}
  } }
  if(found.isEmpty())item{Empty()}
  items(found,key={it.id}){e->EventRow(vm,s,e,{if(selected.isNotEmpty())selected=toggleId(selected,e.id)else nav.navigate(DetailRoute(e.id))},selected=if(selected.isNotEmpty())e.id in selected else null,select={selected=toggleId(selected,e.id)}){
   if(s.home.sortMode=="manual") {IconButton({reorder(vm,s,e,-1,found)}){Icon(Icons.Default.KeyboardArrowUp,"上移")};IconButton({reorder(vm,s,e,1,found)}){Icon(Icons.Default.KeyboardArrowDown,"下移")}}
  }}
 }
 if(delete)AlertDialog(onDismissRequest={delete=false},title={Text("删除 ${book.name}？")},text={Text("选择将全部事件移到未分类本，或将全部事件移到回收站；不会立即永久删除。")},confirmButton={TextButton({delete=false;vm.mutate{vm.graph.service.deleteBook(id,true)};nav.popBackStack()}){Text("事件移到回收站")}},dismissButton={Column{TextButton({delete=false;vm.mutate{vm.graph.service.deleteBook(id,false)};nav.popBackStack()}){Text("事件移到未分类")};TextButton({delete=false}){Text("取消")}}})
 if(moving)MoveDialog(s,selected.firstOrNull(),{moving=false}){bookId,parent->val ids=selected.toList();vm.mutate{vm.graph.service.moveSubtrees(ids,bookId,parent)};selected=emptyList();moving=false}
 if(tagsDialog)BatchTagsDialog(vm,s,selected.toList()){tagsDialog=false}
}
@Composable private fun BatchTagsDialog(vm:AppViewModel,s:LibraryState,ids:List<String>,dismiss:()->Unit) {
 var chosen by rememberSaveable{mutableStateOf<List<String>>(emptyList())}
 AlertDialog(onDismissRequest=dismiss,title={Text("替换所选 ${ids.size} 项的标签")},text={Column(Modifier.heightIn(max=400.dp).verticalScroll(rememberScrollState())){Text("确认后以此选择替换原标签；一个也不选会清空所选事件的标签。新标签可先在设置中创建。",style=MaterialTheme.typography.bodySmall);s.tags.forEach{tag->Row(verticalAlignment=Alignment.CenterVertically){Checkbox(tag.id in chosen,{if(tag.id in chosen||chosen.size<20)chosen=toggleId(chosen,tag.id)else vm.message.value="最多 20 个标签"});Text(tag.name)}}}},confirmButton={TextButton({val tags=chosen.toList();vm.mutate{vm.graph.service.setTags(ids,tags)};dismiss()}){Text("确认替换")}},dismissButton={TextButton(dismiss){Text("取消")}})
}
private fun idState()=mutableStateOf<List<String>>(emptyList())
private fun toggleId(ids:List<String>,id:String)=if(id in ids)ids-id else ids+id
private fun reorder(vm:AppViewModel,s:LibraryState,e:Event,delta:Int,list:List<Event>) {
 val siblings=list.filter{it.parentId==e.parentId}.sortedBy{it.sortRank}.toMutableList();val i=siblings.indexOfFirst{it.id==e.id};val j=i+delta;if(j !in siblings.indices)return
 val target=siblings[j];siblings[j]=e;siblings[i]=target
 vm.mutate { vm.graph.store.transaction { state ->
  val ranks=siblings.mapIndexed{index,event->event.id to index.toLong()}.toMap()
  Change(state.copy(events=state.events.map{if(it.id in ranks)it.copy(sortRank=ranks.getValue(it.id),version=it.version+1,updatedAt=System.currentTimeMillis())else it}),Unit)
 } }
}

@Composable private fun SearchScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var query by rememberSaveable{mutableStateOf("")};var scope by rememberSaveable{mutableStateOf("active")};var tag by rememberSaveable{mutableStateOf("")}
 val found=vm.graph.service.search(s,query,scope).filter{tag.isBlank()||tag in it.tagIds}
 LazyColumn {
  item { Header("搜索","标题、寄语、标签和日子本",{nav.popBackStack()}) }
  item { Column(Modifier.padding(horizontal=18.dp)){Field("关键词",query,{query=it});Options("范围",scope,listOf("active" to "使用中","archived" to "已归档","trash" to "回收站","all" to "全部")){scope=it};Options("标签",tag,listOf("" to "所有标签")+s.tags.map{it.id to it.name}){tag=it}} }
  item { Text("${found.size} 个结果",Modifier.padding(18.dp),style=MaterialTheme.typography.labelLarge) }
  items(found,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))})}
 }
}

@Composable private fun GoalsScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var filter by rememberSaveable{mutableStateOf("all")}
 val goals=s.events.filter{it.kind=="goal"&&s.lifecycle(it.id)=="active"&&(filter=="all"||it.goal?.state==filter)}
 LazyColumn {
  item { Header("向目标靠近","记录行动，也看见每一步。",actions={IconButton({nav.navigate(EditRoute(goal=true))}){Icon(Icons.Default.Add,"创建目标")}}) }
  item { Column(Modifier.padding(horizontal=18.dp)){Options("状态",filter,listOf("all" to "全部","not_started" to "未开始","in_progress" to "进行中","completed" to "已完成","canceled" to "已取消")){filter=it}} }
  if(goals.isEmpty())item{Empty("创建目标后，可以在详情中手动添加阶段目标和行动记录。")}
  items(goals,key={it.id}){e->Section(e.title){Text(goalLabel(e.goal!!.state));val rate=vm.graph.service.completionRate(s,e.id);Text(if(rate==null)"尚无参与统计的直属阶段"else"直属阶段 ${rate.first} / ${rate.second} 完成");LinearProgressIndicator(progress={if(rate==null)0f else rate.first.toFloat()/rate.second},modifier=Modifier.fillMaxWidth());TextButton({nav.navigate(DetailRoute(e.id))}){Text("查看目标")}}}
 }
}
private fun goalLabel(s:String)=mapOf("not_started" to "未开始","in_progress" to "进行中","completed" to "已完成","canceled" to "已取消")[s]?:s

@Composable private fun DetailScreen(vm:AppViewModel,s:LibraryState,id:String,nav:NavHostController) {
 val tick=LocalClockTick.current
 val e=s.events.find{it.id==id}
 if(e==null){Column{Header("事件不存在",back={nav.popBackStack()});Empty("可能已被永久删除，或资料库已替换。")};return}
 val level=depth(s,id);val lifecycle=s.lifecycle(id)
 val goal=e.goal;val parentId=e.parentId
 var actionEdit by remember{mutableStateOf<ActionRecord?>(null)};var newAction by remember{mutableStateOf(false)}
 var move by remember{mutableStateOf(false)};var delete by remember{mutableStateOf(false)}
 var sort by rememberSaveable{mutableStateOf("date")};var pages by rememberSaveable(id){mutableIntStateOf(1)}
 val children=remember(s.revision,id,sort,pages,tick){
  val rows=mutableListOf<ChildSummary>();var cursor:String?=null
  repeat(pages){val page=vm.graph.service.directChildren(s,id,sort,cursor);rows+=page.rows;cursor=page.cursor;if(!page.hasMore)return@remember rows to false}
  rows to (cursor!=null)
 }
 val scroll=rememberLazyListState()
 LazyColumn(state=scroll,modifier=Modifier.testTag("detail_list")) {
  item { Header(e.title,"第 $level 级 · ${if(lifecycle=="active")"使用中"else if(lifecycle=="trash")"回收站"else"已归档"}",{nav.popBackStack()},actions={if(lifecycle!="trash")IconButton({nav.navigate(EditRoute(id=id))}){Icon(Icons.Default.Edit,"编辑事件")};IconButton({nav.navigate(ShareRoute(id))}){Icon(Icons.Default.Share,"分享卡片")}}) }
  if(parentId!=null)item{TextButton({nav.navigate(DetailRoute(parentId))}){Text("所属事件：${s.events.find{it.id==parentId}?.title?:"已删除"}")}}
  item { Hero(vm,e){} }
  if(e.greeting.isNotBlank())item { Section("事件寄语"){SelectionContainerCompat(e.greeting)} }
  item { Section("事件信息") {Text("日期：${dateText(e.date)}${if(e.date.calendar=="lunar")"（农历）"else""}");Text("${if(e.countMode=="up")"正数日"else"倒数日"} · ${repeatLabel(e.repeat.frequency)}");if(!e.date.allDay)Text("${e.date.localTime} · ${e.date.zoneId}");if(e.tagIds.isNotEmpty())Text("标签："+e.tagIds.mapNotNull{id2->s.tags.find{it.id==id2}?.name}.joinToString(" / "));Text("提醒："+e.reminders.filter{it.enabled}.joinToString{r->"提前${r.offsetValue}${if(r.offsetUnit=="minutes")"分钟"else"天"} ${r.localTime?:""}"}.ifBlank{"未开启"});Toggle("在首页列表展示",e.homeVisible,{v->vm.mutate{vm.graph.service.saveEvent(e.copy(homeVisible=v),e.version)}});Toggle("置顶",e.pinned,{v->vm.mutate{vm.graph.service.saveEvent(e.copy(pinned=v),e.version)}});TextButton({vm.mutate{vm.graph.service.saveHome(s.home.copy(heroMode="fixed",fixedEventId=id))}}){Text("固定为首页大卡片")}} }
  if(goal!=null)item { Section("目标进度") {
   Text("状态：${goalLabel(goal.state)}")
   if(lifecycle!="trash")FlowRow {(when(goal.state){"not_started"->listOf("in_progress","completed","canceled");"in_progress"->listOf("completed","canceled");else->listOf("in_progress")}).forEach{v->TextButton({vm.mutate{vm.graph.service.setGoalState(id,v)}}){Text(goalLabel(v))}}}
   val rate=vm.graph.service.completionRate(s,id);Text(if(rate==null)"无参与统计的直属阶段"else"直属阶段完成 ${rate.first} / ${rate.second}")
   if(rate!=null)LinearProgressIndicator(progress={rate.first.toFloat()/rate.second},modifier=Modifier.fillMaxWidth())
   Text("时间进度：${(vm.graph.service.timeProgress(s,id)*100).toInt()}%（不是完成率）")
   LinearProgressIndicator(progress={vm.graph.service.timeProgress(s,id).toFloat()},modifier=Modifier.fillMaxWidth())
  } }
  item { Section(if(e.goal!=null)"直属阶段与子事件"else"直属子事件") {
   Text("只显示下一级；点击条目进入它的详情，不在此展开第三级。",style=MaterialTheme.typography.bodySmall)
   Options("排序",sort,listOf("date" to "日期","manual" to "手动")){sort=it;pages=1}
   if(level<3&&lifecycle=="active")Button({nav.navigate(EditRoute(parentId=id,bookId=e.bookId,goal=e.kind=="goal"))}){Text(if(e.kind=="goal")"添加阶段或子事件"else"添加子事件")}
   else Text(if(level==3)"已到第三级，不支持继续新增下级"else"恢复事件后可新增下级",style=MaterialTheme.typography.bodySmall)
  } }
  items(children.first,key={it.event.id}){c->EventRow(vm,s,c.event,{nav.navigate(DetailRoute(c.event.id))}){
   if(sort=="manual"){IconButton({reorder(vm,s,c.event,-1,children.first.map{it.event})}){Icon(Icons.Default.KeyboardArrowUp,"上移")};IconButton({reorder(vm,s,c.event,1,children.first.map{it.event})}){Icon(Icons.Default.KeyboardArrowDown,"下移")}}
  }}
  if(children.second)item{TextButton({pages++},Modifier.fillMaxWidth()){Text("再加载 20 项")}}
  if(e.goal!=null) {
   item { Section("行动记录"){if(lifecycle!="trash")Button({newAction=true}){Text("记录一次行动")};Text("每条独立记录日期、内容与可选用时；不会写成事件寄语。",style=MaterialTheme.typography.bodySmall)} }
   items(s.actions.filter{it.goalEventId==id}.sortedWith(compareByDescending<ActionRecord>{it.date}.thenByDescending{it.createdAt}),key={it.id}){a->Section(a.date+(a.minutes?.let{" · $it 分钟"}?:"")){Text(a.body);Row{if(lifecycle!="trash"){TextButton({actionEdit=a}){Text("编辑")};TextButton({vm.mutate{vm.graph.service.deleteAction(a.id)}}){Text("删除记录")}}}}}
  }
  item { Section("更多操作") {
   FlowRow {if(lifecycle!="trash"){TextButton({vm.mutate{vm.graph.service.copySubtree(id,true)}}){Text("复制含子树")};TextButton({vm.mutate{vm.graph.service.copySubtree(id,false)}}){Text("仅复制当前")};TextButton({move=true}){Text("移动子树")};TextButton({vm.mutate{vm.graph.service.setLifecycle(listOf(id),"archive")}}){Text("归档")};TextButton({delete=true}){Text("移到回收站")};TextButton({try{vm.outgoing.value=vm.graph.systems.calendarAdd(e)}catch(ex:Exception){vm.error(ex)}}){Text("添加到系统日历")}}
    else TextButton({nav.navigate(LifecycleRoute("trash"))}){Text("到回收站恢复或永久删除")}
   }
  } }
 }
 if(delete)Confirm("移到回收站？","当前事件及其全部下级会一并移入。30 天后可被自动清理；此前可恢复。",{delete=false}){delete=false;vm.mutate{vm.graph.service.setLifecycle(listOf(id),"trash")};nav.popBackStack()}
 if(move)MoveDialog(s,id,{move=false}){book,parent->move=false;vm.mutate{vm.graph.service.moveSubtree(id,book,parent)}}
 if(newAction||actionEdit!=null)ActionDialog(vm,id,actionEdit){newAction=false;actionEdit=null}
}
@Composable private fun SelectionContainerCompat(text:String) { androidx.compose.foundation.text.selection.SelectionContainer { Text(text) } }
private fun dateText(d:DateSpec)=(d.year?.toString()?:"--")+"-%02d-%02d".format(d.month,d.day)
private fun repeatLabel(v:String)=mapOf("none" to "不重复","yearly" to "每年","monthly" to "每月","weekly" to "每周","every_n_days" to "每 N 天")[v]?:v

@Composable private fun MoveDialog(s:LibraryState,id:String?,dismiss:()->Unit,confirm:(String,String?)->Unit) {
 var book by remember{mutableStateOf(s.events.find{it.id==id}?.bookId?:s.books.first().id)};var parent by remember{mutableStateOf<String?>(null)}
 val excluded=if(id==null)emptySet()else descendants(s,id)
 AlertDialog(onDismissRequest=dismiss,title={Text("移动事件及其全部下级")},text={Column(Modifier.heightIn(max=450.dp).verticalScroll(rememberScrollState())){
  Text("移动不会改变日期；目标层级超过三级会被拒绝。")
  Options("目标本",book,s.books.map{it.id to it.name}){book=it;parent=null}
  FilterChip(parent==null,{parent=null},label={Text("作为根事件")})
  s.events.filter{it.bookId==book&&it.id !in excluded&&s.lifecycle(it.id)=="active"&&depth(s,it.id)<3}.forEach{e->FilterChip(parent==e.id,{parent=e.id},label={Text("第${depth(s,e.id)}级 · ${e.title}")})}
 }},confirmButton={TextButton({confirm(book,parent)}){Text("移动")}},dismissButton={TextButton(dismiss){Text("取消")}})
}

@Composable private fun ActionDialog(vm:AppViewModel,id:String,existing:ActionRecord?,dismiss:()->Unit) {
 var date by rememberSaveable{mutableStateOf(existing?.date?:LocalDate.now().toString())};var body by rememberSaveable{mutableStateOf(existing?.body?:"")};var minutes by rememberSaveable{mutableStateOf(existing?.minutes?.toString()?:"")}
 AlertDialog(onDismissRequest=dismiss,title={Text(if(existing==null)"记录行动"else"编辑行动")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(8.dp)){Field("行动日期 YYYY-MM-DD",date,{date=it});Field("记录内容（最多 1000 字符）",body,{body=it},4);Field("用时分钟（可留空，0–1440）",minutes,{minutes=it})}},confirmButton={TextButton({val n=if(minutes.isBlank())null else minutes.toIntOrNull();if(minutes.isNotBlank()&&n==null){vm.message.value="用时必须为整数"}else{vm.mutate("行动已记录"){vm.graph.service.saveAction(existing?.copy(date=date,body=body,minutes=n)?:ActionRecord(goalEventId=id,date=date,body=body,minutes=n),existing?.version)};dismiss()}}){Text("保存")}},dismissButton={TextButton(dismiss){Text("取消")}})
}

@Composable private fun EditorScreen(vm:AppViewModel,s:LibraryState,route:EditRoute,nav:NavHostController) {
 val existing=s.events.find{it.id==route.id}
 if(route.id.isNotEmpty()&&existing==null){Empty("事件已不存在，请返回重新选择");return}
 val key=if(existing!=null)existing.id else "new-${route.parentId}-${route.bookId}-${route.goal}"
 val book=route.parentId.takeIf{it.isNotBlank()}?.let{s.event(it).bookId}?:route.bookId.takeIf{b->s.books.any{it.id==b}}?:s.books.firstOrNull{it.builtinKey==if(route.goal)"goal"else"uncategorized"}!!.id
 val base=remember(key){existing?:Event(bookId=book,parentId=route.parentId.takeIf{it.isNotBlank()},title="",kind=if(route.goal)"goal"else"ordinary",date=DateSpec(year=LocalDate.now().year,month=LocalDate.now().monthValue,day=LocalDate.now().dayOfMonth),goal=if(route.goal)GoalDetail(LocalDate.now().toString())else null)}
 var draft by remember(key){mutableStateOf(EditorDraft(base,dateText(base.date),base.goal?.startDate?:LocalDate.now().toString(),base.tagIds.mapNotNull{id->s.tags.find{it.id==id}?.name}.joinToString(",")))}
 var loaded by remember(key){mutableStateOf(false)}
 var askExit by remember{mutableStateOf(false)}
 var conflict by remember{mutableStateOf(false)}
 var parentPicker by remember{mutableStateOf(false)}
 val busy by vm.busy.collectAsStateWithLifecycle()
 val scope=rememberCoroutineScope()
 LaunchedEffect(key){val saved=withContext(Dispatchers.IO){vm.prefs.draft(key)};if(saved!=null)runCatching{vm.json.decodeFromString<EditorDraft>(saved)}.onSuccess{d->if(existing==null||d.event.version==existing.version)draft=d else conflict=true};loaded=true}
 LaunchedEffect(draft,loaded){if(loaded){delay(500);withContext(Dispatchers.IO){vm.prefs.saveDraft(key,vm.json.encodeToString(draft))}}}
 fun setEvent(f:(Event)->Event){draft=draft.copy(event=f(draft.event))}
 fun leave(){scope.launch{withContext(Dispatchers.IO){vm.prefs.saveDraft(key,vm.json.encodeToString(draft))};nav.popBackStack()}}
 BackHandler{askExit=true}
 val e=draft.event
 val photo=rememberLauncherForActivityResult(ActivityResultContracts.GetContent()){uri->if(uri!=null)vm.afterUnlock{vm.photo(uri){a->setEvent{it.copy(appearance=it.appearance.copy(backgroundKind="photo",assetId=a.id))}}}}
 val notification=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){allowed->vm.message.value=if(allowed)"通知权限已开启"else"通知未授权，事件仍可保存"}
 LazyColumn(contentPadding=PaddingValues(bottom=30.dp)) {
  item { Header(if(existing==null)"留住一个日子"else"编辑日子",if(e.parentId==null)"根事件"else"属于：${s.events.find{it.id==e.parentId}?.title}",{askExit=true},actions={TextButton({vm.save(draft,existing,key){id->nav.popBackStack();if(existing==null)nav.navigate(DetailRoute(id))}},enabled=!busy&&loaded){Text("保存",fontWeight=FontWeight.Bold)}}) }
  if(!loaded)item{LinearProgressIndicator(Modifier.fillMaxWidth())}
  item { Section("基本信息") {
   Field("日子名称（最多 60 字符）",e.title,{v->setEvent{it.copy(title=v)}})
   Options("类型",e.kind,listOf("ordinary" to "普通","birthday" to "生日","memorial" to "纪念日","holiday" to "假日","goal" to "目标")){kind->setEvent{old->old.copy(kind=kind,countMode=if(kind in setOf("birthday","goal"))"down"else old.countMode,date=if(kind in setOf("birthday","goal"))old.date.copy(calendar=if(kind=="goal")"gregorian"else old.date.calendar,allDay=true,localTime=null,zoneId=null,leapMonth=if(kind=="goal")false else old.date.leapMonth)else old.date,repeat=if(kind=="birthday")RecurrenceSpec("yearly")else if(kind=="goal")RecurrenceSpec()else old.repeat,goal=if(kind=="goal")old.goal?:GoalDetail(draft.startDate)else null,reminders=if(kind=="birthday"&&old.reminders.isEmpty())listOf(ReminderRule(enabled=true,offsetValue=7),ReminderRule(enabled=true))else old.reminders)}}
   if(existing==null){Options("所属本",e.bookId,s.books.map{it.id to it.name}){v->if(e.parentId==null)setEvent{it.copy(bookId=v)}else vm.message.value="子事件与父事件必须属于同一本"};TextButton({parentPicker=true}){Text(if(e.parentId==null)"作为根事件 · 选择上级"else"更改上级（同本）")}}
   else Text("所属本与上级请在详情的‘移动子树’中更改。",style=MaterialTheme.typography.bodySmall)
   Options("计算方式",e.countMode,if(e.kind in setOf("birthday","goal"))listOf("down" to "倒数")else listOf("down" to "倒数","up" to "正数")){v->setEvent{it.copy(countMode=v,repeat=if(v=="up")RecurrenceSpec()else it.repeat)}}
   if(e.countMode=="up")Toggle("包含开始当天",e.includeStartDay,{v->setEvent{it.copy(includeStartDay=v)}})
   Toggle("在首页列表显示",e.homeVisible,{v->setEvent{it.copy(homeVisible=v)}})
   Toggle("置顶事件",e.pinned,{v->setEvent{it.copy(pinned=v)}})
   Field("标签（英文或中文逗号分隔）",draft.tags,{draft=draft.copy(tags=it)})
  } }
  item { Section("日期与重复") {
   Options("历法",e.date.calendar,if(e.kind=="goal"||!e.date.allDay)listOf("gregorian" to "公历")else listOf("gregorian" to "公历","lunar" to "农历")){v->setEvent{it.copy(date=it.date.copy(calendar=v,leapMonth=false),repeat=if(v=="lunar"&&it.repeat.frequency !in setOf("none","yearly"))RecurrenceSpec()else it.repeat)}}
   Field("日期 YYYY-MM-DD",draft.dateText,{draft=draft.copy(dateText=it)})
   Text(if(e.kind=="birthday")"未知出生年份可用 ---MM-DD，例如 ---10-31；不显示年龄。"else"公历 1900–2100；农历 1901–2099。",style=MaterialTheme.typography.bodySmall)
   if(e.date.calendar=="lunar"){
    Toggle("闰月生日 / 日期",e.date.leapMonth,{v->setEvent{it.copy(date=it.date.copy(leapMonth=v))}})
    Options("当年无闰月",e.date.lunarLeapPolicy,listOf("normal_fallback" to "落到普通月","leap_only" to "仅闰月年份")){v->setEvent{it.copy(date=it.date.copy(lunarLeapPolicy=v))}}
    Options("当月没有三十日",e.date.lunarSmallMonthPolicy,listOf("month_end" to "月末","skip" to "跳过该年")){v->setEvent{it.copy(date=it.date.copy(lunarSmallMonthPolicy=v))}}
   }else Options("2 月 29 日非闰年",e.date.feb29Policy,listOf("feb28" to "2 月 28 日","mar01" to "3 月 1 日")){v->setEvent{it.copy(date=it.date.copy(feb29Policy=v))}}
   if(e.kind !in setOf("birthday","goal")&&e.date.calendar=="gregorian")Toggle("全天事件",e.date.allDay,{v->setEvent{it.copy(date=it.date.copy(allDay=v,localTime=if(v)null else"09:00",zoneId=if(v)null else ZoneId.systemDefault().id),reminders=it.reminders.map{r->r.copy(offsetUnit="days",localTime=if(v)"09:00"else null,version=r.version+1)})}})
   if(!e.date.allDay){Field("当地时间 HH:mm",e.date.localTime.orEmpty(),{v->setEvent{it.copy(date=it.date.copy(localTime=v))}});Field("时区，如 Asia/Shanghai",e.date.zoneId.orEmpty(),{v->setEvent{it.copy(date=it.date.copy(zoneId=v))}});Text("夏令时缺口向后移到有效时间；重复时间取较早偏移。",style=MaterialTheme.typography.bodySmall)}
   val repeats=when{e.kind=="birthday"->listOf("yearly" to "每年");e.kind=="goal"||e.countMode=="up"->listOf("none" to "不重复");e.date.calendar=="lunar"->listOf("none" to "不重复","yearly" to "每年");else->listOf("none" to "不重复","yearly" to "每年","monthly" to "每月","weekly" to "每周","every_n_days" to "每 N 天")}
   Options("重复",e.repeat.frequency,repeats){v->setEvent{it.copy(repeat=it.repeat.copy(frequency=v,intervalDays=if(v=="every_n_days")1 else null,until=if(v=="none")null else it.repeat.until))}}
   if(e.repeat.frequency=="every_n_days")Field("间隔天数 1–365",e.repeat.intervalDays?.toString().orEmpty(),{v->setEvent{it.copy(repeat=it.repeat.copy(intervalDays=v.toIntOrNull()))}})
   if(e.repeat.frequency!="none")Field("重复截止日期（可留空）",e.repeat.until.orEmpty(),{v->setEvent{it.copy(repeat=it.repeat.copy(until=v.takeIf{it.isNotBlank()}))}})
   if(e.kind=="goal"){Field("目标开始日 YYYY-MM-DD",draft.startDate,{draft=draft.copy(startDate=it)});Toggle("作为父目标的参与统计阶段",e.goal?.includeInParent?:true,{v->setEvent{it.copy(goal=(it.goal?:GoalDetail(draft.startDate)).copy(includeInParent=v))}})}
  } }
  item { Section("事件寄语") {Field("写一段想留住的话（可空，最多 2000 字符）",e.greeting,{v->setEvent{it.copy(greeting=v)}},4);Text("只有这一段文字，不生成日记或多条小纸条。",style=MaterialTheme.typography.bodySmall)} }
  item { Section("背景与文字") {
   Options("背景",e.appearance.backgroundKind,listOf("gradient" to "渐变","solid" to "纯色","photo" to "照片")){v->if(v=="photo"&&e.appearance.assetId==null)photo.launch("image/*")else setEvent{it.copy(appearance=it.appearance.copy(backgroundKind=v,assetId=if(v=="photo")it.appearance.assetId else null))}}
   if(e.appearance.backgroundKind=="gradient")Options("主题",e.appearance.presetKey,listOf("forest" to "森林","sunset" to "晚霞","ocean" to "海洋","lavender" to "薰衣草")){v->setEvent{it.copy(appearance=it.appearance.copy(presetKey=v))}}
   if(e.appearance.backgroundKind=="solid")Options("颜色",e.appearance.solidArgb.toString(),listOf(0xFF214F43.toInt().toString() to "森林绿",0xFF345A79.toInt().toString() to "海蓝",0xFFF1E8D5.toInt().toString() to "奶油白",0xFF8B4F45.toInt().toString() to "暖褐")){v->setEvent{it.copy(appearance=it.appearance.copy(solidArgb=v.toInt()))}}
   if(e.appearance.backgroundKind=="photo"){TextButton({photo.launch("image/*")}){Text("选择 / 更换照片")};Text("横向焦点");Slider(e.appearance.focusX.toFloat(),{v->setEvent{it.copy(appearance=it.appearance.copy(focusX=v.toDouble()))}});Text("纵向焦点");Slider(e.appearance.focusY.toFloat(),{v->setEvent{it.copy(appearance=it.appearance.copy(focusY=v.toDouble()))}});Text("遮罩深度");Slider(e.appearance.dimAmount.toFloat(),{v->setEvent{it.copy(appearance=it.appearance.copy(dimAmount=v.toDouble()))}})}
   Options("文字颜色",e.appearance.textColorMode,listOf("auto" to "自动对比度","light" to "浅色","dark" to "深色")){v->setEvent{it.copy(appearance=it.appearance.copy(textColorMode=v))}}
   Hero(vm,e.copy(title=e.title.ifBlank{"你的重要日子"},date=runCatching{val p=draft.dateText.split('-');e.date.copy(year=p[0].toInt(),month=p[1].toInt(),day=p[2].toInt())}.getOrDefault(base.date),repeat=if(e.kind=="birthday")RecurrenceSpec("yearly")else e.repeat)){}
  } }
  item { Section("本机提醒") {
   Text("生日默认提前 7 天和当天 09:00。普通提醒不保证秒级；精准提醒需系统许可。",style=MaterialTheme.typography.bodySmall)
   if(!vm.graph.systems.notificationAllowed())TextButton({if(Build.VERSION.SDK_INT>=33)notification.launch(Manifest.permission.POST_NOTIFICATIONS)else vm.outgoing.value=vm.graph.systems.requestNotificationSettings()}){Text("开启系统通知权限")}
   e.reminders.forEachIndexed{i,r->
    fun change(f:(ReminderRule)->ReminderRule){setEvent{it.copy(reminders=it.reminders.mapIndexed{index,old->if(index==i)f(old).copy(version=old.version+1)else old})}}
    HorizontalDivider();Toggle("提醒 ${i+1}",r.enabled,{v->change{it.copy(enabled=v)}})
    Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){Field("提前数值",r.offsetValue.toString(),{v->change{it.copy(offsetValue=v.toIntOrNull()?:-1)}},modifier=Modifier.weight(1f));TextButton({setEvent{it.copy(reminders=it.reminders.filterIndexed{index,_->index!=i})}}){Text("删除")}}
    if(!e.date.allDay)Options("单位",r.offsetUnit,listOf("days" to "天","hours" to "小时","minutes" to "分钟")){v->change{it.copy(offsetUnit=v)}}
    if(e.date.allDay)Field("提醒时间 HH:mm",r.localTime?:"09:00",{v->change{it.copy(localTime=v)}})
    Options("精度",r.precisionMode,listOf("normal" to "普通","precise" to "精准")){v->change{it.copy(precisionMode=v)}}
   }
   if(e.reminders.size<5)TextButton({setEvent{it.copy(reminders=it.reminders+ReminderRule(enabled=true,localTime=if(it.date.allDay)"09:00"else null))}}){Text("添加提醒（最多 5 条）")}
  } }
  item { Button({vm.save(draft,existing,key){id->nav.popBackStack();if(existing==null)nav.navigate(DetailRoute(id))}},Modifier.fillMaxWidth().padding(18.dp),enabled=!busy&&loaded){Text("保存这个日子")} }
 }
 if(askExit)AlertDialog(onDismissRequest={askExit=false},title={Text("离开编辑？")},text={Text("未保存内容可保留为本机草稿，下次打开同一事件可继续。")},confirmButton={TextButton({askExit=false;leave()}){Text("保留草稿并离开")}},dismissButton={Column{TextButton({askExit=false;scope.launch{vm.prefs.deleteDraft(key);nav.popBackStack()}}){Text("丢弃草稿并离开")};TextButton({askExit=false}){Text("继续编辑")}}})
 if(conflict)Confirm("草稿版本已过期","事件已被其他操作更新。本次已使用最新保存内容；旧草稿不会自动覆盖。",{conflict=false}){conflict=false}
 if(parentPicker)MoveDialog(s,null,{parentPicker=false}){b,parent->val valid=parent==null||depth(s,parent)<3;if(valid){setEvent{it.copy(bookId=b,parentId=parent,homeVisible=parent==null)};parentPicker=false}else vm.message.value="最多支持三级事件"}
}

@Composable private fun LifecycleScreen(vm:AppViewModel,s:LibraryState,kind:String,nav:NavHostController) {
 var purge by remember{mutableStateOf<String?>(null)}
 val events=s.events.filter{s.lifecycle(it.id)==kind}
 LazyColumn {
  item { Header(if(kind=="trash")"回收站"else"已归档",if(kind=="trash")"30 天后可自动清理；永久删除不可恢复"else"不会触发提醒，也不参与首页排序",{nav.popBackStack()}) }
  if(events.isEmpty())item{Empty("这里是空的")}
  items(events,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))}){if(kind=="trash")IconButton({purge=e.id}){Icon(Icons.Default.DeleteForever,"永久删除")}}}
  item { Section("恢复批次") {
   Text("恢复会撤销所选批次的原因；如果仍受到别的归档或回收站批次影响，会继续保持隐藏。",style=MaterialTheme.typography.bodySmall)
   s.causes.filter{it.kind==if(kind=="trash")"trash"else"archive"}.sortedByDescending{it.createdAt}.forEach{c->
    Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text("${c.members.size} 项 · ${Instant.ofEpochMilli(c.createdAt).atZone(ZoneId.systemDefault()).toLocalDate()}");c.purgeAfter?.let{Text("最早清理：${Instant.ofEpochMilli(it).atZone(ZoneId.systemDefault()).toLocalDate()}",style=MaterialTheme.typography.bodySmall)}};TextButton({vm.mutate("已恢复该批次"){vm.graph.service.restoreCause(c.id)}}){Text("恢复")}}
   }
  } }
 }
 if(purge!=null)Confirm("永久删除子树？","此操作会删除当前事件、全部下级及其行动记录，不能撤销。请先确认已有备份。",{purge=null}){val id=purge!!;purge=null;vm.mutate{vm.graph.service.purge(listOf(id));vm.graph.store.gc()}}
}

@Composable private fun CalendarScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var monthText by rememberSaveable{mutableStateOf(YearMonth.now().toString())};var selected by rememberSaveable{mutableStateOf(LocalDate.now().toString())}
 val month=YearMonth.parse(monthText);val monday by vm.prefs.weekMonday.collectAsStateWithLifecycle(true)
 val start=month.atDay(1);val end=month.atEndOfMonth()
 val map=remember(s.revision,monthText){val days=mutableMapOf<LocalDate,MutableList<Event>>();s.events.filter{s.lifecycle(it.id)=="active"}.forEach{e->if(e.countMode=="down")runCatching{vm.graph.dates.occurrences(e.dateInput(),start,end)}.getOrDefault(emptyList()).forEach{days.getOrPut(it.date){mutableListOf()}+=e}};days}
 LazyColumn {
  item { Header("日历","按发生日期展开重复事项",{nav.popBackStack()}) }
  item { Section(monthText) {
   Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){TextButton({monthText=month.minusMonths(1).toString()}){Text("上个月")};TextButton({monthText=YearMonth.now().toString();selected=LocalDate.now().toString()}){Text("今天")};TextButton({monthText=month.plusMonths(1).toString()}){Text("下个月")}}
   Row{(if(monday)listOf("一","二","三","四","五","六","日")else listOf("日","一","二","三","四","五","六")).forEach{Text(it,Modifier.weight(1f),textAlign=androidx.compose.ui.text.style.TextAlign.Center)}}
   val offset=if(monday)start.dayOfWeek.value-1 else start.dayOfWeek.value%7
   val total=((offset+month.lengthOfMonth()+6)/7)*7
   (0 until total step 7).forEach{row->Row{(row until row+7).forEach{i->val day=i-offset+1;if(day !in 1..month.lengthOfMonth())Spacer(Modifier.weight(1f).height(50.dp))else{val date=month.atDay(day);Column(Modifier.weight(1f).height(50.dp).background(if(selected==date.toString())MaterialTheme.colorScheme.primaryContainer else Color.Transparent,RoundedCornerShape(10.dp)).clickable{selected=date.toString()},horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){Text(day.toString());Text(if(map[date].isNullOrEmpty())" "else"•",color=MaterialTheme.colorScheme.primary)}}}}}
  } }
  item{Text(selected,Modifier.padding(18.dp),fontWeight=FontWeight.Bold)}
  val events=map[LocalDate.parse(selected)].orEmpty();if(events.isEmpty())item{Empty("这一天没有倒数事件")}
  items(events,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))})}
 }
}

@Composable private fun ShareScreen(vm:AppViewModel,s:LibraryState,id:String,nav:NavHostController) {
 val e=s.events.find{it.id==id};if(e==null){Empty("事件不存在");return}
 var greeting by rememberSaveable{mutableStateOf(e.greeting.isNotBlank())};var ratio by rememberSaveable{mutableStateOf("3:4")};val busy by vm.busy.collectAsStateWithLifecycle()
 val json=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"json",setOf(id))}}
 val csv=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("text/csv")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"csv",setOf(id))}}
 LazyColumn {
  item { Header("分享这个日子","卡片只包含当前事件，不带子事件和行动记录",{nav.popBackStack()}) }
  item { Hero(vm,e){} }
  item { Section("卡片内容") {
   if(e.greeting.isNotBlank())Toggle("展示事件寄语",greeting,{greeting=it})else Text("寄语为空，导出卡片将突出倒数日期与背景。")
   Options("比例",ratio,listOf("1:1" to "方形","3:4" to "竖版","9:16" to "长图")){ratio=it}
   if(greeting)Text(e.greeting)
   Text("长寄语自动分成多张图，不截断文字。分享前请确认其中没有不想公开的内容。",style=MaterialTheme.typography.bodySmall)
   Button({vm.shareCard(id,greeting,ratio)},enabled=!busy){Text("生成并分享图片")}
  } }
  item { Section("文本分享") {Text("JSON 保留树关系和文字，照片只保留主题回退；CSV 是平面交换，复杂字段会在导入预览中报告。导入的事件是独立副本，不是实时共享。",style=MaterialTheme.typography.bodySmall);Button({json.launch("DateBook-events.json")},enabled=!busy){Text("导出事件及其子树 JSON")};OutlinedButton({csv.launch("DateBook-events.csv")},enabled=!busy){Text("导出当前事件 CSV")}} }
 }
}

@Composable private fun SettingsScreen(vm:AppViewModel,activity:FragmentActivity,nav:NavHostController) {
 val s by vm.library.collectAsStateWithLifecycle()
 val theme by vm.prefs.theme.collectAsStateWithLifecycle("system")
 val monday by vm.prefs.weekMonday.collectAsStateWithLifecycle(true)
 val scope=rememberCoroutineScope()
 var pinDialog by remember{mutableStateOf(false)};var disableLock by remember{mutableStateOf(false)}
 var tagDialog by remember{mutableStateOf(false)}
 var notificationState by remember{mutableStateOf(vm.graph.systems.notificationAllowed())}
 var exactState by remember{mutableStateOf(vm.graph.systems.exactAllowed())}
 val permission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){notificationState=vm.graph.systems.notificationAllowed()}
 val setting=rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()){notificationState=vm.graph.systems.notificationAllowed();exactState=vm.graph.systems.exactAllowed();vm.mutate("已重新检查系统状态"){}}
 LazyColumn {
  item { Header("设置","无需账号，资料只在这部手机。") }
  item { Section("外观与首页") {
   Options("主题",theme,listOf("system" to "跟随系统","light" to "浅色","dark" to "深色")){v->scope.launch{vm.prefs.theme(v)}}
   Toggle("日历一周从周一开始",monday,{v->scope.launch{vm.prefs.weekMonday(v)}})
   Options("首页大卡片",s.home.heroMode,listOf("auto" to "自动最近事件","fixed" to "手动固定")){v->if(v=="fixed"&&s.home.fixedEventId==null)vm.message.value="请在某个事件详情点击‘固定为首页大卡片’"else vm.mutate{vm.graph.service.saveHome(s.home.copy(heroMode=v))}}
   TextButton({tagDialog=true}){Text("管理标签")}
  } }
  item { Section("提醒与系统功能") {
   Text("通知：${if(notificationState)"已允许"else"未允许 / 通知渠道关闭"}")
   Text("精准闹钟：${if(exactState)"可用"else"未允许，将使用普通提醒"}")
   TextButton({if(Build.VERSION.SDK_INT>=33&&!notificationState)permission.launch(Manifest.permission.POST_NOTIFICATIONS)else setting.launch(vm.graph.systems.requestNotificationSettings())}){Text("管理通知权限")}
   TextButton({setting.launch(vm.graph.systems.requestExactSettings())}){Text("管理精准提醒权限")}
   TextButton({vm.mutate("已重新安排提醒并刷新组件") {}}){Text("立即修复提醒 / 刷新组件")}
   Text("桌面长按空白处 → 组件 → 重要的日子，可选择单事件或最近三项。照片、寄语默认不公开；开启应用锁时桌面仅显示安全入口。",style=MaterialTheme.typography.bodySmall)
   Text("关机、强制停止、厂商省电策略可能延迟提醒，普通模式不承诺精确到分钟。没有后台服务器补发消息。",style=MaterialTheme.typography.bodySmall)
  } }
  item { Section("本机隐私") {
   Text("应用锁：${if(vm.graph.lock.enabled)"已开启"else"未开启"}")
   Button({pinDialog=true}){Text(if(vm.graph.lock.enabled)"修改 PIN"else"设置 PIN 与应用锁")}
   if(vm.graph.lock.enabled){OutlinedButton({disableLock=true}){Text("关闭应用锁")};TextButton({vm.graph.lock.lock()}){Text("立即锁定")}}
   Text("这是访问锁，不是数据库加密。没有账号找回 PIN。可使用本机强生物识别，或验证备份后替换全部资料 / 清空本机资料。",style=MaterialTheme.typography.bodySmall)
   Text("本应用不请求网络权限，不部署云数据库，不加入统计、广告或登录 SDK。Android 自动云备份与设备传输备份已排除应用资料；迁移请手动导出。",style=MaterialTheme.typography.bodySmall)
  } }
  item { Section("资料与工具") {
   TextButton({nav.navigate(ToolsRoute)}){Text("导入 / 导出 / 加密备份 / 恢复 / 日期工具")}
   TextButton({nav.navigate(LifecycleRoute("archived"))}){Text("已归档事件")}
   TextButton({nav.navigate(LifecycleRoute("trash"))}){Text("回收站")}
   Text("版本 1.0.0 · ${s.events.size} / 2000 个事件 · ${s.books.size} / 200 个本子",style=MaterialTheme.typography.bodySmall)
   Text("离线农历：lunar-java 1.7.7（MIT），1901–2099。第三方许可见源码中的 THIRD_PARTY_NOTICES.md。",style=MaterialTheme.typography.bodySmall)
  } }
 }
 if(pinDialog)PinDialog(vm,false){pinDialog=false}
 if(disableLock)PinDialog(vm,true){disableLock=false}
 if(tagDialog)TagsDialog(vm,s){tagDialog=false}
}

@Composable private fun PinDialog(vm:AppViewModel,disable:Boolean,dismiss:()->Unit) {
 var pin by remember{mutableStateOf("")};var repeat by remember{mutableStateOf("")};val locked by vm.graph.lock.locked.collectAsStateWithLifecycle()
 AlertDialog(onDismissRequest=dismiss,title={Text(if(disable)"关闭应用锁"else"设置 6–12 位数字 PIN")},text={Column(verticalArrangement=Arrangement.spacedBy(8.dp)){OutlinedTextField(pin,{pin=it},label={Text(if(disable)"当前 PIN"else"新 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword));if(!disable)OutlinedTextField(repeat,{repeat=it},label={Text("重复 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword));Text("没有邮箱或账号找回，请妥善记住。",style=MaterialTheme.typography.bodySmall)}},confirmButton={TextButton({if(!disable&&pin!=repeat)vm.message.value="两次 PIN 不一致"else{val chars=pin.toCharArray();pin="";repeat="";vm.execute("应用锁设置已更新"){try{if(disable)vm.graph.lock.disable(chars)else vm.graph.lock.setPin(chars);vm.graph.systems.refreshWidgets()}finally{chars.fill('\u0000')}};dismiss()}}){Text(if(disable)"验证并关闭"else"保存")}},dismissButton={TextButton({pin="";repeat="";dismiss()}){Text("取消")}})
}

@Composable private fun TagsDialog(vm:AppViewModel,s:LibraryState,dismiss:()->Unit) {
 var value by remember{mutableStateOf("")};var editing by remember{mutableStateOf<Tag?>(null)};var deleting by remember{mutableStateOf<Tag?>(null)}
 AlertDialog(onDismissRequest=dismiss,title={Text("标签管理")},text={Column(Modifier.heightIn(max=460.dp).verticalScroll(rememberScrollState())) {
  Field(if(editing==null)"新标签"else"修改标签",value,{value=it});TextButton({val tag=editing?.copy(name=value)?:Tag(name=value);vm.mutate{vm.graph.service.saveTag(tag)};editing=null;value=""}){Text("保存标签")}
  s.tags.sortedBy{it.name}.forEach{tag->Row(verticalAlignment=Alignment.CenterVertically){Text(tag.name,Modifier.weight(1f));IconButton({editing=tag;value=tag.name}){Icon(Icons.Default.Edit,"修改")};IconButton({deleting=tag}){Icon(Icons.Default.Delete,"删除")}}}
 }},confirmButton={TextButton(dismiss){Text("完成")}})
 if(deleting!=null)Confirm("删除标签？","标签会从所有事件解除，但事件本身不会删除。",{deleting=null}){val id=deleting!!.id;deleting=null;vm.mutate{vm.graph.service.deleteTag(id)}}
}

@Composable private fun LockScreen(vm:AppViewModel,activity:FragmentActivity,recovery:()->Unit) {
 var pin by remember{mutableStateOf("")};var feedback by remember{mutableStateOf("")};var attempts by remember{mutableIntStateOf(0)}
 var waiting by remember{mutableLongStateOf(vm.graph.lock.remainingLockMillis())}
 val scope=rememberCoroutineScope();var working by remember{mutableStateOf(false)}
 LaunchedEffect(attempts){while(true){waiting=vm.graph.lock.remainingLockMillis();if(waiting<=0)break;delay(1000)}}
 Column(Modifier.fillMaxSize().padding(30.dp).verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.Center,horizontalAlignment=Alignment.CenterHorizontally) {
  Icon(Icons.Default.Lock,"应用锁",Modifier.size(48.dp),tint=MaterialTheme.colorScheme.primary);Spacer(Modifier.height(16.dp));Text("把重要的日子留给自己",fontSize=24.sp,fontWeight=FontWeight.SemiBold);Text("请解锁本机资料库",Modifier.padding(vertical=12.dp))
  OutlinedTextField(pin,{pin=it},label={Text("6–12 位 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword),singleLine=true,modifier=Modifier.fillMaxWidth(),enabled=!working&&waiting<=0)
  if(feedback.isNotBlank())Text(feedback,color=MaterialTheme.colorScheme.error)
  if(waiting>0)Text("请 ${((waiting+999)/1000)} 秒后重试")
  Button({working=true;val chars=pin.toCharArray();pin="";scope.launch{try{val ok=withContext(Dispatchers.IO){vm.graph.lock.unlock(chars)};if(!ok){feedback="PIN 不正确或暂时禁止重试";attempts++}}catch(e:Exception){feedback=AppViewModel.friendly(e)}finally{chars.fill('\u0000');working=false}}},Modifier.fillMaxWidth().padding(top=14.dp),enabled=!working&&waiting<=0){Text("解锁")}
  if(vm.graph.lock.error!=null)Text("应用锁验证资料损坏，已安全锁定。只能从备份替换或清空本机资料。",color=MaterialTheme.colorScheme.error)
  val bioAvailable=vm.graph.lock.error==null&&BiometricManager.from(activity).canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)==BiometricManager.BIOMETRIC_SUCCESS
  if(bioAvailable)OutlinedButton({
   val prompt=BiometricPrompt(activity,ContextCompat.getMainExecutor(activity),object:BiometricPrompt.AuthenticationCallback(){override fun onAuthenticationSucceeded(result:BiometricPrompt.AuthenticationResult){super.onAuthenticationSucceeded(result);scope.launch{try{withContext(Dispatchers.IO){vm.graph.lock.biometricUnlock()}}catch(e:Exception){feedback=AppViewModel.friendly(e)}}};override fun onAuthenticationError(code:Int,message:CharSequence){feedback=message.toString()}})
   prompt.authenticate(BiometricPrompt.PromptInfo.Builder().setTitle("解锁重要的日子").setSubtitle("使用本机强生物识别验证身份").setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG).setNegativeButtonText("使用 PIN").build())
  },Modifier.fillMaxWidth()){Text("使用指纹 / 面容验证")}
  TextButton(recovery){Text("忘记 PIN：从备份替换或清空本机资料")}
  Text("没有登录和云端找回；上述恢复会替换或删除当前资料，不会绕过锁展示旧资料。",style=MaterialTheme.typography.bodySmall)
 }
}

@Composable private fun ReplacementPinScreen(vm:AppViewModel) {
 var pin by remember{mutableStateOf("")};var repeat by remember{mutableStateOf("")}
 val busy by vm.busy.collectAsStateWithLifecycle()
 val message by vm.message.collectAsStateWithLifecycle()
 Column(Modifier.fillMaxSize().padding(28.dp),verticalArrangement=Arrangement.Center) {
  Text("资料已安全替换",fontSize=25.sp,fontWeight=FontWeight.Bold)
  Text("请为新的本机资料设置 6–12 位 PIN 后进入。原来的锁不会被用来解锁旧资料。",Modifier.padding(vertical=16.dp))
  OutlinedTextField(pin,{pin=it},label={Text("新 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword),singleLine=true,modifier=Modifier.fillMaxWidth())
  OutlinedTextField(repeat,{repeat=it},label={Text("重复 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword),singleLine=true,modifier=Modifier.fillMaxWidth())
  if(message!=null)Text(message!!,color=MaterialTheme.colorScheme.error)
  Button({if(pin!=repeat)vm.message.value="两次 PIN 不一致"else{val chars=pin.toCharArray();pin="";repeat="";vm.replacementPin(chars)}},enabled=!busy,modifier=Modifier.fillMaxWidth().padding(top=16.dp)){Text("设置 PIN 并进入")}
 }
 BackHandler {vm.message.value="请先完成新 PIN 设置，或关闭应用后再继续"}
}

@Composable private fun ToolsScreen(vm:AppViewModel,modifier:Modifier=Modifier,recovery:Boolean=false,onBack:()->Unit) {
 val s by vm.library.collectAsStateWithLifecycle();val preview by vm.preview.collectAsStateWithLifecycle();val busy by vm.busy.collectAsStateWithLifecycle()
 val candidates by vm.calendarCandidates.collectAsStateWithLifecycle()
 val jobId by vm.currentJob.collectAsStateWithLifecycle()
 var password by remember{mutableStateOf("")};var confirmation by remember{mutableStateOf("")};var clear by remember{mutableStateOf(false)}
 var includeTrash by rememberSaveable{mutableStateOf(false)};var selected by rememberSaveable{mutableStateOf<List<String>>(emptyList())}
 var from by rememberSaveable{mutableStateOf(LocalDate.now().toString())};var to by rememberSaveable{mutableStateOf(LocalDate.now().plusDays(30).toString())}
 val jsonImport=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null)vm.afterUnlock{vm.importText(uri,false)}}
 val csvImport=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null)vm.afterUnlock{vm.importText(uri,true)}}
 val backupImport=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null){val chars=password.toCharArray();password="";vm.readBackup(uri,chars)}}
 val jsonExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"json")}}
 val csvExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("text/csv")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"csv")}}
 val backupExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/octet-stream")){uri->if(uri!=null){val chars=password.toCharArray();password="";vm.afterUnlock{vm.export(uri,"backup",password=chars,includeTrash=includeTrash)}}}
 val readPermission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){allowed->if(allowed)vm.afterUnlock{try{vm.calendarRead(LocalDate.parse(from),LocalDate.parse(to))}catch(e:Exception){vm.error(e)}}else vm.message.value="日历权限未授予，不影响本机倒数事件"}
 LazyColumn(modifier) {
  item { Header(if(recovery)"锁定资料恢复"else"资料与日期工具",if(recovery)"只允许验证备份后替换，或明确清空本机"else"导出是独立副本，不会跨设备同步",onBack) }
  if(!recovery)item { Section("文本交换") {
   Text("JSON 保留选择事件的子树、寄语与目标数据，不含照片、提醒和设备设置；CSV 为平面交换。请先预览再导入。",style=MaterialTheme.typography.bodySmall)
   Row{TextButton({jsonImport.launch(arrayOf("application/json","text/plain","application/octet-stream"))},enabled=!busy){Text("导入 JSON")};TextButton({jsonExport.launch("DateBook-events.json")},enabled=!busy){Text("导出全部 JSON")}}
   Row{TextButton({csvImport.launch(arrayOf("text/*","application/octet-stream"))},enabled=!busy){Text("导入 CSV")};TextButton({csvExport.launch("DateBook-events.csv")},enabled=!busy){Text("导出全部 CSV")}}
  } }
  item { Section("完整备份与迁移") {
   Text("备份包括本子、三级事件、寄语、目标、行动、背景及归档原因。不包括应用锁、设备日历关联、桌面组件或系统任务。请把备份复制到另一处安全位置；卸载应用会丢失本机原始资料。",style=MaterialTheme.typography.bodySmall)
   OutlinedTextField(password,{password=it},label={Text("加密密码（恢复时填原密码）")},visualTransformation=PasswordVisualTransformation(),modifier=Modifier.fillMaxWidth(),singleLine=true)
   Text("密码为空时导出明文完整备份。密码无法找回；建议至少 8 个字符。",style=MaterialTheme.typography.bodySmall)
   if(!recovery){Toggle("备份包含回收站",includeTrash,{includeTrash=it});Button({backupExport.launch("DateBook-${LocalDate.now()}.dbkp")},enabled=!busy){Text("生成完整备份")}}
   OutlinedButton({backupImport.launch(arrayOf("*/*"))},enabled=!busy){Text("选择备份并验证")}
  } }
  if(preview!=null)item { val p=preview!!;Section("导入预览 · 尚未修改本机资料") {
   Text("${p.state.books.size} 个本子 / ${p.state.events.size} 个事件 / ${p.state.actions.size} 条行动 / ${p.state.assets.size} 张背景")
   if(p.backup!=null)Text(if(p.backup.encrypted)"已完成加密认证和完整性校验"else"明文备份，已校验完整性")
   p.imported?.issues?.forEach{issue->Text("第 ${issue.line} 行：${issue.code} · ${issue.message}",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.error)}
   p.state.events.take(20).forEach{Text("${it.title} · ${dateText(it.date)} · 第 ${depth(p.state,it.id)} 级",style=MaterialTheme.typography.bodySmall)}
   if(p.state.events.size>20)Text("另有 ${p.state.events.size-20} 项；导入保留全部，不截断。",style=MaterialTheme.typography.bodySmall)
   Text("合并使用独立 ID 副本；相同来源重复导入会跳过已导入项。新导入事项的提醒默认关闭，不补发过去提醒。",style=MaterialTheme.typography.bodySmall)
   if(!recovery)Button({vm.commitPreview(false)},enabled=!busy){Text("确认合并导入")}
   if(p.backup!=null){Field("替换确认：替换本机全部数据",confirmation,{confirmation=it});Text("替换不可撤销，会切换整座资料库，不会混入设备配置。",color=MaterialTheme.colorScheme.error,style=MaterialTheme.typography.bodySmall);OutlinedButton({vm.commitPreview(true,confirmation);confirmation=""},enabled=!busy&&confirmation=="替换本机全部数据"){Text("确认替换本机全部资料")}}
   TextButton({vm.deletePreview();confirmation=""}){Text("取消预览")}
  } }
  if(!recovery)item { Section("从系统日历复制") {
   Field("开始日期",from,{from=it});Field("结束日期（范围不超过 366 天）",to,{to=it})
   TextButton({val context=vm.getApplication<android.app.Application>();if(ContextCompat.checkSelfPermission(context,Manifest.permission.READ_CALENDAR)==PackageManager.PERMISSION_GRANTED)try{vm.calendarRead(LocalDate.parse(from),LocalDate.parse(to))}catch(e:Exception){vm.error(e)}else readPermission.launch(Manifest.permission.READ_CALENDAR)}){Text("读取并预览系统日历")}
   Text("只读取你选择的日期范围；确认后复制为本地独立事件。不会自动双向同步，也不会删除系统日历事项。",style=MaterialTheme.typography.bodySmall)
   candidates.forEach{e->Row(verticalAlignment=Alignment.CenterVertically){Checkbox(e.id in selected,{selected=toggleId(selected,e.id)});Text(e.title+" · "+dateText(e.date),Modifier.weight(1f))}}
   if(candidates.isNotEmpty()){Row{TextButton({selected=candidates.map{it.id}}){Text("全选")};TextButton({selected=emptyList()}){Text("清空选择")}};Button({vm.calendarImport(selected.toSet());selected=emptyList()},enabled=selected.isNotEmpty()&&!busy){Text("复制所选 ${selected.size} 项")}}
  } }
  if(!recovery)item { DateCalculator(vm) }
  if(jobId!=null)item { JobPanel(vm,jobId!!) }
  if(jobId==null&&vm.graph.jobs.latest().isNotEmpty())item { Section("最近文件任务") {vm.graph.jobs.latest().take(8).forEach{job->TextButton({vm.currentJob.value=job.id}){Text("${job.type} · ${job.stage}")}}} }
  item { Section("危险操作") {
   Text("清空会删除这部手机中的全部事件和背景，并重置应用锁；不会删除你保存在其他位置的备份文件。",style=MaterialTheme.typography.bodySmall)
   TextButton({clear=true}){Text("清空本机全部资料",color=MaterialTheme.colorScheme.error)}
  } }
 }
 if(clear)AlertDialog(onDismissRequest={clear=false},title={Text("清空本机全部资料？")},text={Column{Text("不可撤销。输入下列完整文字以确认：清空本机全部数据");Field("确认文字",confirmation,{confirmation=it})}},confirmButton={TextButton({vm.clearAll(confirmation);confirmation="";clear=false},enabled=confirmation=="清空本机全部数据"){Text("永久清空")}},dismissButton={TextButton({clear=false;confirmation=""}){Text("取消")}})
}

@Composable private fun JobPanel(vm:AppViewModel,id:String) {
 val job by vm.graph.jobs.observe(id).collectAsStateWithLifecycle()
 Section("文件任务") {
  Text(job.stage);if(job.total!=null&&job.total!!>0)LinearProgressIndicator(progress={(job.current?:0L).toFloat()/job.total!!},modifier=Modifier.fillMaxWidth())else if(job.state in setOf("preparing","progress","committing"))LinearProgressIndicator(Modifier.fillMaxWidth())
  if(job.state in setOf("preparing","progress"))TextButton({vm.graph.jobs.cancel(id)}){Text("取消任务")}
  if(job.state=="committing")Text("正在原子提交，暂时不能取消。",style=MaterialTheme.typography.bodySmall)
  job.error?.let{Text(it,color=MaterialTheme.colorScheme.error)}
  if(job.state in setOf("completed","failed","canceled"))TextButton({vm.currentJob.value=null}){Text("关闭任务状态")}
 }
}

@Composable private fun DateCalculator(vm:AppViewModel) {
 var a by rememberSaveable{mutableStateOf(LocalDate.now().toString())};var b by rememberSaveable{mutableStateOf(LocalDate.now().plusDays(100).toString())};var n by rememberSaveable{mutableStateOf("100")};var result by rememberSaveable{mutableStateOf("")}
 Section("日期计算器") {
  Field("起始日期 YYYY-MM-DD",a,{a=it});Field("结束日期 YYYY-MM-DD",b,{b=it});Field("增加 / 减少天数",n,{n=it})
  FlowRow {TextButton({try{result="两个日期相差 ${ChronoUnit.DAYS.between(LocalDate.parse(a),LocalDate.parse(b))} 天（不含起始日）"}catch(e:Exception){result="请检查日期格式"}}){Text("计算相差天数")};TextButton({try{val amount=n.toLong();demand(amount in -73050..73050,"DATE_RANGE");result=LocalDate.parse(a).plusDays(amount).toString()}catch(e:Exception){result="请检查日期和天数范围"}}){Text("计算 N 天后")};TextButton({try{val d=LocalDate.parse(a);val lunar=com.nlf.calendar.Solar.fromYmd(d.year,d.monthValue,d.dayOfMonth).lunar;result="农历 ${lunar.year} 年 ${lunar.monthInChinese}月${lunar.dayInChinese}"}catch(e:Exception){result="请检查公历日期"}}){Text("公历转农历")}}
  if(result.isNotBlank())SelectionContainerCompat(result)
 }
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt


# ============================================================================
# BEGIN FILE: app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt
# ============================================================================
FILES['app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt'] = r'''package cn.datebook.app.ui

import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.*

private val Context.localPreferences by preferencesDataStore("datebook-device")
class DevicePreferences(context: Context) {
 private val data = context.applicationContext.localPreferences
 val theme = data.data.map { it[stringPreferencesKey("theme")] ?: "system" }
 val weekMonday = data.data.map { it[booleanPreferencesKey("week_monday")] ?: true }
 val privatePreview = data.data.map { it[booleanPreferencesKey("private_preview")] ?: false }
 val replacementPinEpoch = data.data.map { it[stringPreferencesKey("replacement_pin_epoch")] }
 suspend fun replacementPinEpoch(value:String?) { data.edit { if(value==null)it.remove(stringPreferencesKey("replacement_pin_epoch"))else it[stringPreferencesKey("replacement_pin_epoch")]=value } }
 suspend fun theme(value: String) { require(value in setOf("system","light","dark")); data.edit { it[stringPreferencesKey("theme")] = value } }
 suspend fun weekMonday(value: Boolean) { data.edit { it[booleanPreferencesKey("week_monday")] = value } }
 suspend fun privatePreview(value: Boolean) { data.edit { it[booleanPreferencesKey("private_preview")] = value } }
 suspend fun saveDraft(key: String, value: String) { require(value.length <= 50000); data.edit { it[stringPreferencesKey("draft_$key")] = value } }
 suspend fun draft(key: String): String? = data.data.first()[stringPreferencesKey("draft_$key")]
 suspend fun deleteDraft(key: String) { data.edit { it.remove(stringPreferencesKey("draft_$key")) } }
 suspend fun clearDrafts() { data.edit { p -> p.asMap().keys.filter { it.name.startsWith("draft_") }.forEach { p.remove(stringPreferencesKey(it.name)) } } }
}
'''
# END FILE: app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt


# ============================================================================
# BEGIN FILE: app/src/main/res/drawable/ic_datebook.xml
# ============================================================================
FILES['app/src/main/res/drawable/ic_datebook.xml'] = r'''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="48dp" android:height="48dp" android:viewportWidth="48" android:viewportHeight="48"><path android:fillColor="#37634B" android:pathData="M8,5L40,5L40,43L8,43Z"/><path android:fillColor="#FFFFFF" android:pathData="M13,13L35,13L35,17L13,17ZM17,23L31,23L31,36L17,36Z"/></vector>
'''
# END FILE: app/src/main/res/drawable/ic_datebook.xml


# ============================================================================
# BEGIN FILE: app/src/main/res/values/strings.xml
# ============================================================================
FILES['app/src/main/res/values/strings.xml'] = r'''<?xml version="1.0" encoding="utf-8"?><resources><string name="app_name">重要的日子</string><string name="widget_description">单个事件或最近的日子，资料仅保存在本机</string></resources>
'''
# END FILE: app/src/main/res/values/strings.xml


# ============================================================================
# BEGIN FILE: app/src/main/res/values/themes.xml
# ============================================================================
FILES['app/src/main/res/values/themes.xml'] = r'''<?xml version="1.0" encoding="utf-8"?><resources><style name="Theme.DateBook" parent="android:style/Theme.Material.Light.NoActionBar"><item name="android:fontFamily">sans</item><item name="android:windowLightStatusBar">true</item><item name="android:colorAccent">#37634B</item><item name="android:windowActionModeOverlay">true</item><item name="android:windowNoTitle">true</item></style></resources>
'''
# END FILE: app/src/main/res/values/themes.xml


# ============================================================================
# BEGIN FILE: app/src/main/res/xml/backup_rules.xml
# ============================================================================
FILES['app/src/main/res/xml/backup_rules.xml'] = r'''<?xml version="1.0" encoding="utf-8"?><full-backup-content><exclude domain="root" path="."/><exclude domain="database" path="."/><exclude domain="sharedpref" path="."/><exclude domain="file" path="."/><exclude domain="external" path="."/></full-backup-content>
'''
# END FILE: app/src/main/res/xml/backup_rules.xml


# ============================================================================
# BEGIN FILE: app/src/main/res/xml/data_extraction_rules.xml
# ============================================================================
FILES['app/src/main/res/xml/data_extraction_rules.xml'] = r'''<?xml version="1.0" encoding="utf-8"?><data-extraction-rules><cloud-backup disableIfNoEncryptionCapabilities="true"><exclude domain="root" path="."/><exclude domain="database" path="."/><exclude domain="sharedpref" path="."/><exclude domain="file" path="."/><exclude domain="external" path="."/></cloud-backup><device-transfer><exclude domain="root" path="."/><exclude domain="database" path="."/><exclude domain="sharedpref" path="."/><exclude domain="file" path="."/><exclude domain="external" path="."/></device-transfer></data-extraction-rules>
'''
# END FILE: app/src/main/res/xml/data_extraction_rules.xml


# ============================================================================
# BEGIN FILE: app/src/main/res/xml/file_paths.xml
# ============================================================================
FILES['app/src/main/res/xml/file_paths.xml'] = r'''<?xml version="1.0" encoding="utf-8"?><paths><cache-path name="shares" path="shares/"/></paths>
'''
# END FILE: app/src/main/res/xml/file_paths.xml


# ============================================================================
# BEGIN FILE: app/src/main/res/xml/widget_info.xml
# ============================================================================
FILES['app/src/main/res/xml/widget_info.xml'] = r'''<?xml version="1.0" encoding="utf-8"?><appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android" android:minWidth="180dp" android:minHeight="100dp" android:targetCellWidth="3" android:targetCellHeight="2" android:updatePeriodMillis="1800000" android:resizeMode="horizontal|vertical" android:widgetCategory="home_screen|keyguard" android:initialLayout="@layout/glance_default_loading_layout" android:configure="cn.datebook.app.platform.WidgetConfigureActivity" android:description="@string/widget_description"/>
'''
# END FILE: app/src/main/res/xml/widget_info.xml


# ============================================================================
# BEGIN FILE: app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt
# ============================================================================
FILES['app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt'] = r'''package cn.datebook.app

import cn.datebook.core.*
import org.junit.Assert.*
import org.junit.Test
import java.time.Clock
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

/**
 * 固定样例来自香港天文台逐日对照表，核验于 2026-10-31。
 * https://www.hko.gov.hk/en/gts/time/calendar/text/files/T2024e.txt
 * https://www.hko.gov.hk/en/gts/time/calendar/text/files/T2025e.txt
 * https://www.hko.gov.hk/en/gts/time/calendar/text/files/T2026e.txt
 * 只测试离线算法输出，不在测试执行时请求网络。
 */
class LunarGoldenTests {
 private val port = LunarAdapter()
 private val zone = ZoneId.of("Asia/Shanghai")
 private fun solar(year: Int, month: Int, day: Int) = port.solar(year, month, day, false, "normal_fallback", "month_end")
 @Test fun newYear2024() { assertEquals(LocalDate.of(2024, 2, 10), solar(2024, 1, 1)) }
 @Test fun newYear2025() { assertEquals(LocalDate.of(2025, 1, 29), solar(2025, 1, 1)) }
 @Test fun newYear2026() { assertEquals(LocalDate.of(2026, 2, 17), solar(2026, 1, 1)) }
 @Test fun midAutumn2024() { assertEquals(LocalDate.of(2024, 9, 17), solar(2024, 8, 15)) }
 @Test fun midAutumn2025() { assertEquals(LocalDate.of(2025, 10, 6), solar(2025, 8, 15)) }
 @Test fun lunarYearUsesNewYearNotJanuaryFirst() {
  assertEquals(2025, port.lunarYear(LocalDate.of(2026, 2, 16)))
  assertEquals(2026, port.lunarYear(LocalDate.of(2026, 2, 17)))
 }
 @Test fun lunarLeapMonth2025DistinguishesNormalAndLeapSix() {
  assertEquals(LocalDate.of(2025, 6, 25), solar(2025, 6, 1))
  assertEquals(LocalDate.of(2025, 7, 25), port.solar(2025, 6, 1, true, "leap_only", "month_end"))
 }
 @Test fun missingLeapMonthCanFallbackOrSkip() {
  assertEquals(solar(2026, 6, 1), port.solar(2026, 6, 1, true, "normal_fallback", "month_end"))
  assertNull(port.solar(2026, 6, 1, true, "leap_only", "month_end"))
 }
 @Test fun smallLunarMonthDoesNotInventThirtiethDay() {
  // 2024 正月为29天：3月9日廿九，3月10日二月初一。
  assertEquals(LocalDate.of(2024, 3, 9), port.solar(2024, 1, 30, false, "normal_fallback", "month_end"))
  assertNull(port.solar(2024, 1, 30, false, "normal_fallback", "skip"))
 }
 @Test fun lunarBirthdayKeepsTodayThenRollsOverNextCivilDay() {
  val clock = Clock.fixed(Instant.parse("2025-10-06T04:00:00Z"), zone)
  val engine = DateEngine(clock, port)
  val input = DateInput(DateSpec(calendar = "lunar", year = 2000, month = 8, day = 15), RecurrenceSpec("yearly"), kind = "birthday")
  assertEquals("今天生日", engine.evaluate(input).label)
  assertEquals(LocalDate.of(2026, 9, 25), engine.evaluate(input, Instant.parse("2025-10-06T16:00:00Z")).occurrence!!.date)
 }
 @Test fun everySupportedLunarYearHasOrderedFirstDays() {
  for (year in 1901..2099) {
   val first = solar(year, 1, 1)!!
   val last = solar(year, 12, 1)!!
   assertTrue(first < last)
   assertEquals(year, port.lunarYear(first))
  }
 }
 @Test fun outOfRangeAndImpossibleMonthReturnNull() {
  assertNull(port.solar(1900, 1, 1, false, "normal_fallback", "month_end"))
  assertNull(port.solar(2100, 1, 1, false, "normal_fallback", "month_end"))
  assertNull(port.solar(2026, 13, 1, false, "normal_fallback", "month_end"))
 }
}
'''
# END FILE: app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt


# ============================================================================
# BEGIN FILE: build.gradle.kts
# ============================================================================
FILES['build.gradle.kts'] = r'''plugins {
 alias(libs.plugins.android.application) apply false
 alias(libs.plugins.kotlin.jvm) apply false
 alias(libs.plugins.kotlin.compose) apply false
 alias(libs.plugins.kotlin.serialization) apply false
 alias(libs.plugins.ksp) apply false
 alias(libs.plugins.room) apply false
}
'''
# END FILE: build.gradle.kts


# ============================================================================
# BEGIN FILE: core/build.gradle.kts
# ============================================================================
FILES['core/build.gradle.kts'] = r'''plugins { alias(libs.plugins.kotlin.jvm); alias(libs.plugins.kotlin.serialization) }
kotlin { jvmToolchain(17) }
dependencies {
 implementation(libs.coroutines.core)
 implementation(libs.serialization.json)
 implementation(libs.lunar)
 testImplementation(libs.junit)
}
'''
# END FILE: core/build.gradle.kts


# ============================================================================
# BEGIN FILE: core/src/main/kotlin/cn/datebook/core/DateBookService.kt
# ============================================================================
FILES['core/src/main/kotlin/cn/datebook/core/DateBookService.kt'] = r'''package cn.datebook.core

import java.text.Normalizer
import java.time.Clock
import java.time.LocalDate
import java.time.temporal.ChronoUnit
import java.util.Locale
import java.util.regex.Pattern

/** 扩展字素簇而非 UTF16 或 code point；Android 的 ICU 正则与 JDK 均支持 \X。 */
fun graphemeCount(value: String): Int {
 val matcher = Pattern.compile("\\X").matcher(value)
 var count = 0
 while (matcher.find()) count++
 return count
}
fun nameKey(value: String): String = Normalizer.normalize(value.trim(), Normalizer.Form.NFC).lowercase(Locale.ROOT)
private fun text(value: String, max: Int, bytes: Int, field: String, allowEmpty: Boolean = false) {
 demand(allowEmpty && value.isEmpty() || value.isNotBlank(), "INPUT_REQUIRED", field)
 demand(!value.any { it == '\u0000' || Character.isSurrogate(it) } || validSurrogates(value), "INPUT_INVALID", field)
 demand(graphemeCount(value) <= max, "INPUT_TOO_LONG", field)
 demand(value.toByteArray(Charsets.UTF_8).size <= bytes, "INPUT_BYTE_LIMIT", field)
}
private fun validSurrogates(s: String): Boolean {
 var i = 0
 while (i < s.length) {
  val c = s[i]
  if (c == '\u0000') return false
  if (Character.isHighSurrogate(c)) { if (i + 1 >= s.length || !Character.isLowSurrogate(s[i + 1])) return false; i++ }
  else if (Character.isLowSurrogate(c)) return false
  i++
 }
 return true
}
private fun idsUnique(values: List<String>, field: String) {
 demand(values.all { it.isNotBlank() && it.length <= 128 } && values.size == values.toSet().size, "INPUT_DUPLICATE", field)
}
fun depth(snapshot: LibraryState, id: String): Int {
 val byId = snapshot.events.associateBy { it.id }; val seen = HashSet<String>()
 var at: String? = id; var result = 0
 while (at != null) {
  demand(seen.add(at), "TREE_CYCLE")
  result++
  at = (byId[at] ?: throw AppException("TREE_PARENT_NOT_FOUND")).parentId
 }
 return result
}
fun descendants(snapshot: LibraryState, id: String): Set<String> {
 snapshot.event(id)
 val out = linkedSetOf(id); val queue = java.util.ArrayDeque<String>(); queue += id
 while (!queue.isEmpty()) {
  val parent = queue.removeFirst()
  snapshot.events.filter { it.parentId == parent }.forEach {
   demand(out.add(it.id), "TREE_CYCLE"); queue += it.id
  }
 }
 return out
}

/** 文件导入、候选库和每次用例提交共用；带 dates 时额外执行离线历法转换验证。 */
object LibraryValidator {
 fun validate(state: LibraryState, dates: DateEngine? = null) {
  demand(state.id.isNotBlank() && state.epoch.isNotBlank() && state.revision >= 0, "LIBRARY_INVALID")
  text(state.name, 40, 2048, "library.name")
  demand(state.books.size in 1..200 && state.events.size <= 2000 && state.actions.size <= 10000 && state.tags.size <= 200, "CAPACITY_LIMIT")
  idsUnique(state.books.map { it.id }, "books.id"); idsUnique(state.events.map { it.id }, "events.id")
  idsUnique(state.actions.map { it.id }, "actions.id"); idsUnique(state.tags.map { it.id }, "tags.id")
  idsUnique(state.assets.map { it.id }, "assets.id"); idsUnique(state.causes.map { it.id }, "causes.id")
  idsUnique(state.imports.map { it.id }, "imports.id")
  demand(state.books.map { nameKey(it.name) }.toSet().size == state.books.size, "BOOK_NAME_CONFLICT")
  val builtin = state.books.mapNotNull { it.builtinKey }
  demand(builtin.toSet().size == builtin.size && builtin.all { it in setOf("birthday", "memorial", "holiday", "goal", "uncategorized") }, "BOOK_BUILTIN_INVALID")
  demand(state.books.count { it.builtinKey == "uncategorized" && it.isProtected } == 1, "BOOK_PROTECTED")
  val bookIds = state.books.map { it.id }.toSet(); val tagIds = state.tags.map { it.id }.toSet(); val assetIds = state.assets.map { it.id }.toSet()
  state.books.forEach { b ->
   text(b.name, 30, 2048, "book.name"); demand(b.version >= 1, "VERSION_INVALID")
   demand(b.isProtected == (b.builtinKey == "uncategorized"), "BOOK_PROTECTED")
   demand(b.coverAssetId == null || b.coverAssetId in assetIds, "ASSET_NOT_FOUND")
  }
  demand(state.tags.map { nameKey(it.name) }.toSet().size == state.tags.size, "TAG_NAME_CONFLICT")
  state.tags.forEach { text(it.name, 30, 2048, "tag.name") }
  val allRuleIds = state.events.flatMap { e -> e.reminders.map { it.id } }; idsUnique(allRuleIds, "reminder.id")
  state.events.forEach { e ->
   text(e.title, 60, 4096, "title"); text(e.greeting, 2000, 65536, "greeting", true)
   demand(e.bookId in bookIds && e.version >= 1, "BOOK_NOT_FOUND")
   demand(e.tagIds.size <= 20, "TAG_LIMIT")
   demand(e.tagIds.size == e.tagIds.toSet().size && e.tagIds.all { it in tagIds }, "TAG_NOT_FOUND")
   if (e.parentId != null) demand((state.events.find { it.id == e.parentId } ?: throw AppException("TREE_PARENT_NOT_FOUND")).bookId == e.bookId, "TREE_BOOK_MISMATCH")
   demand(depth(state, e.id) <= 3, "TREE_DEPTH_EXCEEDED")
   validateDateStructure(e.dateInput())
   dates?.validate(e.dateInput())
   demand(e.appearance.backgroundKind in setOf("gradient", "solid", "photo") && e.appearance.textColorMode in setOf("auto", "light", "dark"), "INPUT_ENUM", "appearance")
   demand(listOf(e.appearance.focusX, e.appearance.focusY, e.appearance.dimAmount).all { it.isFinite() && it in 0.0..1.0 }, "INPUT_RANGE", "appearance")
   demand(if (e.appearance.backgroundKind == "photo") e.appearance.assetId in assetIds else e.appearance.assetId == null, "ASSET_NOT_FOUND")
   demand(e.reminders.size <= 5, "REMINDER_LIMIT")
   e.reminders.forEach { r ->
    demand(r.version >= 1 && r.offsetUnit in setOf("days", "hours", "minutes") && r.offsetValue in 0..525600 && r.precisionMode in setOf("normal", "precise"), "REMINDER_INVALID")
    if (e.date.allDay) demand(r.offsetUnit == "days" && r.localTime != null && Regex("([01][0-9]|2[0-3]):[0-5][0-9]").matches(r.localTime), "REMINDER_INVALID")
    else demand(r.localTime == null, "REMINDER_INVALID")
   }
   demand((e.kind == "goal") == (e.goal != null), "GOAL_INVALID")
   e.goal?.let { g ->
    demand(g.state in setOf("not_started", "in_progress", "completed", "canceled"), "GOAL_STATE_INVALID")
    demand((g.state == "completed") == (g.completedAt != null) && (g.completedAt == null || g.completedAt >= 0 && (dates == null || g.completedAt <= dates.currentInstant().toEpochMilli())), "GOAL_STATE_INVALID")
    val start = parseDate(g.startDate, "goal.startDate")
    val end = LocalDate.of(e.date.year!!, e.date.month, e.date.day)
    demand(start <= end, "GOAL_RANGE_INVALID")
   }
  }
  state.actions.forEach { a ->
   val goal = state.event(a.goalEventId); demand(goal.kind == "goal", "GOAL_INVALID")
   text(a.body, 1000, 32768, "action.body"); val actionDate = parseDate(a.date, "action.date")
   demand(dates == null || actionDate <= dates.currentDate(), "ACTION_FUTURE_DATE")
   demand(a.minutes == null || a.minutes in 0..1440, "INPUT_RANGE", "action.minutes")
   demand(a.version >= 1, "VERSION_INVALID")
  }
  state.assets.forEach { a ->
   demand(Regex("[a-fA-F0-9]{64}").matches(a.sha256) && a.bytes in 1..26214400 && a.width > 0 && a.height > 0 && a.width.toLong() * a.height <= 40000000, "ASSET_INVALID")
   demand(a.mimeType in setOf("image/jpeg", "image/png", "image/webp") && safeAssetPath(a.relativePath), "ASSET_INVALID")
  }
  demand(state.assets.map { it.relativePath }.toSet().size == state.assets.size, "ASSET_INVALID")
  val eventIds = state.events.map { it.id }.toSet()
  val childrenByParent = state.events.groupBy { it.parentId }
  state.causes.forEach { c ->
   demand(c.kind in setOf("archive", "trash") && c.members.isNotEmpty() && c.members.toSet().size == c.members.size && c.members.all { it in eventIds }, "LIFECYCLE_INVALID")
   demand(if (c.kind == "trash") c.purgeAfter != null && c.purgeAfter >= c.createdAt else c.purgeAfter == null, "LIFECYCLE_INVALID")
   demand(c.sourceEventId == null || c.sourceEventId in eventIds, "LIFECYCLE_INVALID")
   // 原因集对子树封闭，防止父隐藏而新后代仍参与首页和提醒。
   val memberSet = c.members.toSet()
   c.members.forEach { member -> demand(childrenByParent[member].orEmpty().all { it.id in memberSet }, "LIFECYCLE_INVALID") }
  }
  demand(state.home.heroMode in setOf("auto", "fixed") && state.home.sortMode in setOf("date", "manual"), "HOME_INVALID")
  demand(state.home.fixedEventId == null || state.home.fixedEventId in eventIds, "HOME_INVALID")
  demand(state.home.heroMode != "fixed" || state.home.fixedEventId in eventIds, "HOME_INVALID")
  demand(state.home.selectedBookId == null || state.home.selectedBookId in bookIds, "HOME_INVALID")
  val imported = HashSet<Pair<String, String>>()
  state.imports.forEach { b ->
   demand(b.sourceExportId.isNotBlank() && b.format in setOf("json", "csv", "backup") && Regex("[a-fA-F0-9]{64}").matches(b.fileSha256), "IMPORT_INVALID")
   b.provenance.forEach { p -> demand(p.sourceRef.isNotBlank() && imported.add(b.sourceExportId to p.sourceRef) && (p.localEventId == null || p.localEventId in eventIds), "IMPORT_DUPLICATE") }
  }
 }
 private fun validateDateStructure(i: DateInput) {
  val d = i.date; val r = i.repeat
  demand(i.kind in setOf("ordinary", "birthday", "memorial", "holiday", "goal") && i.countMode in setOf("down", "up"), "INPUT_ENUM")
  demand(d.calendar in setOf("gregorian", "lunar") && d.month in 1..12 && d.day in 1..31, "DATE_INVALID")
  demand(r.frequency in setOf("none", "yearly", "monthly", "weekly", "every_n_days") && (if (r.frequency == "every_n_days") r.intervalDays != null && r.intervalDays in 1..365 else r.intervalDays == null), "DATE_REPEAT_INVALID")
  demand(d.year != null || i.kind == "birthday" && r.frequency == "yearly", "DATE_YEAR_REQUIRED")
  demand(i.kind != "birthday" || d.allDay && r.frequency == "yearly" && i.countMode == "down", "DATE_KIND_INVALID")
  demand(i.countMode != "up" || r.frequency == "none", "DATE_REPEAT_INVALID")
  demand(i.kind != "goal" || d.calendar == "gregorian" && d.allDay && r.frequency == "none" && i.countMode == "down", "GOAL_DATE_INVALID")
  demand(d.feb29Policy in setOf("feb28", "mar01") && d.lunarLeapPolicy in setOf("normal_fallback", "leap_only") && d.lunarSmallMonthPolicy in setOf("month_end", "skip"), "INPUT_ENUM")
  if (d.allDay) demand(d.localTime == null && d.zoneId == null, "DATE_TIME_INVALID")
  else {
   demand(d.calendar == "gregorian" && d.localTime != null && d.zoneId != null && Regex("([01][0-9]|2[0-3]):[0-5][0-9]").matches(d.localTime), "DATE_TIME_INVALID")
   try { java.time.ZoneId.of(d.zoneId) } catch (e: Exception) { throw AppException("DATE_TIME_INVALID") }
  }
  if (d.calendar == "gregorian") {
   demand(!d.leapMonth && (d.year == null || d.year in 1900..2100), "DATE_RANGE")
   try { LocalDate.of(d.year ?: 2000, d.month, d.day) } catch (e: Exception) { throw AppException("DATE_INVALID") }
  } else demand(d.allDay && d.day <= 30 && (d.year == null || d.year in 1901..2099) && r.frequency in setOf("none", "yearly"), "DATE_RANGE")
  r.until?.let { until ->
   val date = parseDate(until); demand(r.frequency != "none", "DATE_REPEAT_INVALID")
   if (d.year != null && d.calendar == "gregorian") demand(date >= LocalDate.of(d.year, d.month, d.day), "DATE_UNTIL_INVALID")
  }
 }
}

fun safeAssetPath(path: String): Boolean = path.isNotBlank() && path.length <= 240 && !path.startsWith("/") && '\\' !in path && ':' !in path && path.split('/').all { it.isNotBlank() && it != "." && it != ".." && it.none { c -> c.code < 32 } }

class DateBookService(private val repo: LibraryRepository, private val dates: DateEngine, private val clock: Clock) {
 private fun checked(state: LibraryState): LibraryState { LibraryValidator.validate(state, dates); return state }
 private fun version(actual: Long?, expected: Long?) {
  demand(actual == null && expected == null || actual != null && expected == actual, "VERSION_CONFLICT")
 }
 private fun modifiable(s: LibraryState, id: String) { demand(s.lifecycle(id) != "trash", "EVENT_IN_TRASH") }
 suspend fun saveEvent(event: Event, expectedVersion: Long? = null, operationId: String = newId()): Event = repo.transaction(operationId) { s ->
  val change = prepareEvent(s, event, expectedVersion)
  Change(checked(change.state), change.result)
 }
 /** 同一次保存内建立新标签；日期、版本或容量失败时不会遗留半次提交。 */
 suspend fun saveEventWithTagNames(event: Event, tagNames: List<String>, expectedVersion: Long? = null, operationId: String = newId()): Event = repo.transaction(operationId) { s ->
  demand(tagNames.size <= 20, "TAG_LIMIT")
  val names = tagNames.map { it.trim() }.filter { it.isNotEmpty() }.distinctBy(::nameKey)
  var working = s
  val tagIds = names.map { name ->
   working.tags.find { nameKey(it.name) == nameKey(name) }?.id ?: Tag(name = name, createdAt = clock.millis()).also { tag ->
    text(tag.name, 30, 2048, "tag.name"); working = working.copy(tags = working.tags + tag)
   }.id
  }
  val change = prepareEvent(working, event.copy(tagIds = tagIds), expectedVersion)
  Change(checked(change.state), change.result)
 }
 /** 日历选择复制等“全成全败”的新建批次；更新仍用带版本的单项接口。 */
 suspend fun saveEventsBatch(events: List<Event>, operationId: String = newId()): Int = repo.transaction(operationId) { s ->
  demand(events.isNotEmpty(), "INPUT_REQUIRED")
  idsUnique(events.map { it.id }, "events.id")
  demand(events.none { incoming -> s.events.any { it.id == incoming.id } }, "VERSION_CONFLICT")
  var working = s
  val saved = events.map { event -> prepareEvent(working, event, null).let { working = it.state; it.result } }
  Change(checked(working), saved.size)
 }
 private fun prepareEvent(s: LibraryState, event: Event, expectedVersion: Long?): Change<Event> {
  val old = s.events.find { it.id == event.id }; version(old?.version, expectedVersion)
  if (old != null) modifiable(s, old.id)
  if (event.parentId != null) {
   demand(s.events.any { it.id == event.parentId }, "TREE_PARENT_NOT_FOUND"); modifiable(s, event.parentId)
   demand(s.lifecycle(event.parentId) == "active" || old?.parentId == event.parentId, "PARENT_NOT_ACTIVE")
  }
  demand(old == null || event.parentId == old.parentId && event.bookId == old.bookId, "USE_MOVE_SUBTREE")
  if (old?.goal != null && event.goal == null) demand(s.actions.none { it.goalEventId == old.id } && s.events.none { it.parentId == old.id && it.kind == "goal" }, "GOAL_HAS_HISTORY")
  val saved = event.copy(createdAt = old?.createdAt ?: clock.millis(), updatedAt = clock.millis(), version = (old?.version ?: 0) + 1,
   reminders = if (old == null && event.kind == "birthday" && event.reminders.isEmpty()) listOf(ReminderRule(enabled = true, offsetValue = 7), ReminderRule(enabled = true)) else event.reminders)
  val next = s.copy(events = s.events.filterNot { it.id == saved.id } + saved)
  return Change(next, saved)
 }
 suspend fun saveBook(book: Book, expectedVersion: Long? = null): Book = repo.transaction { s ->
  val old = s.books.find { it.id == book.id }; version(old?.version, expectedVersion)
  demand(old == null && book.builtinKey == null || old != null && old.builtinKey == book.builtinKey && old.isProtected == book.isProtected, "BOOK_BUILTIN_INVALID")
  val saved = book.copy(name = book.name.trim(), version = (old?.version ?: 0) + 1, createdAt = old?.createdAt ?: clock.millis(), updatedAt = clock.millis())
  Change(checked(s.copy(books = s.books.filterNot { it.id == saved.id } + saved)), saved)
 }
 suspend fun deleteBook(id: String, trashContents: Boolean) { repo.transaction { s ->
  val book = s.books.find { it.id == id } ?: throw AppException("BOOK_NOT_FOUND")
  demand(!book.isProtected, "BOOK_PROTECTED")
  val unclassified = s.books.first { it.builtinKey == "uncategorized" }.id
  val members = s.events.filter { it.bookId == id }.map { it.id }
  // 本已删除，原因保留成员及自身 ID；不能留下引用已不存在本的外键。
  val cause = if (trashContents && members.isNotEmpty()) LifecycleCause(kind = "trash", createdAt = clock.millis(), purgeAfter = clock.millis() + THIRTY_DAYS, members = members) else null
  val changed = s.copy(books = s.books.filterNot { it.id == id }, events = s.events.map { if (it.bookId == id) it.copy(bookId = unclassified, version = it.version + 1, updatedAt = clock.millis()) else it }, causes = s.causes + listOfNotNull(cause), home = s.home.copy(selectedBookId = s.home.selectedBookId?.takeUnless { it == id }))
  Change(checked(changed), Unit)
 } }
 suspend fun moveSubtree(id: String, destinationBookId: String, destinationParentId: String?) { repo.transaction { s ->
  Change(checked(prepareMove(s, id, destinationBookId, destinationParentId)), Unit)
 } }
 /** 批量移动先剔除被选中祖先覆盖的节点，任一根失败时整批回滚。 */
 suspend fun moveSubtrees(ids: List<String>, destinationBookId: String, destinationParentId: String? = null): Int = repo.transaction { s ->
  val roots = normalizedRoots(s, ids)
  var working = s
  roots.forEach { id -> working = prepareMove(working, id, destinationBookId, destinationParentId) }
  Change(checked(working), roots.size)
 }
 private fun prepareMove(s: LibraryState, id: String, destinationBookId: String, destinationParentId: String?): LibraryState {
  modifiable(s, id); demand(s.books.any { it.id == destinationBookId }, "BOOK_NOT_FOUND")
  val all = descendants(s, id)
  if (destinationParentId != null) {
   val parent = s.event(destinationParentId)
   demand(destinationParentId !in all, "TREE_CYCLE")
   demand(parent.bookId == destinationBookId && s.lifecycle(parent.id) == "active", "TREE_BOOK_MISMATCH")
  }
  val oldAncestors = s.causes.filter { c -> id in c.members && c.sourceEventId != null && c.sourceEventId !in all }.map { it.id }.toSet()
  val nextCauses = s.causes.mapNotNull { c ->
   val members = if (c.id in oldAncestors) c.members.filterNot { it in all } else c.members
   if (members.isEmpty()) null else c.copy(members = members)
  }.map { c -> if (destinationParentId in c.members) c.copy(members = (c.members + all).distinct()) else c }
  val next = s.copy(events = s.events.map { e -> if (e.id in all) e.copy(bookId = destinationBookId, parentId = if (e.id == id) destinationParentId else e.parentId, version = e.version + 1, updatedAt = clock.millis()) else e }, causes = nextCauses)
  return next
 }
 suspend fun copySubtree(id: String, wholeTree: Boolean = true): String = repo.transaction { s ->
  val root = s.event(id); modifiable(s, id)
  val selected = if (wholeTree) descendants(s, id) else setOf(id)
  val ids = selected.associateWith { newId() }
  val events = s.events.filter { it.id in selected }.map { e -> e.copy(id = ids.getValue(e.id), parentId = if (e.id == id) null else ids[e.parentId], pinned = false, homeVisible = e.id == id, createdAt = clock.millis(), updatedAt = clock.millis(), version = 1,
   reminders = e.reminders.map { it.copy(id = newId(), enabled = false, version = 1) }) }
  val actions = s.actions.filter { it.goalEventId in selected }.map { it.copy(id = newId(), goalEventId = ids.getValue(it.goalEventId), version = 1, createdAt = clock.millis(), updatedAt = clock.millis()) }
  Change(checked(s.copy(events = s.events + events, actions = s.actions + actions)), ids.getValue(root.id))
 }
 suspend fun setLifecycle(rootIds: List<String>, action: String): String = repo.transaction { s ->
  demand(action in setOf("archive", "trash") && rootIds.isNotEmpty(), "LIFECYCLE_INVALID")
  val roots = normalizedRoots(s, rootIds)
  val members = roots.flatMap { descendants(s, it) }.distinct()
  if (action == "archive") demand(members.none { s.lifecycle(it) == "trash" }, "EVENT_IN_TRASH")
  val source = roots.singleOrNull()
  val cause = LifecycleCause(kind = action, sourceEventId = source, createdAt = clock.millis(), purgeAfter = if (action == "trash") clock.millis() + THIRTY_DAYS else null, members = members)
  Change(checked(s.copy(causes = s.causes + cause)), cause.id)
 }
 suspend fun restoreCause(causeId: String) { repo.transaction { s ->
  demand(s.causes.any { it.id == causeId }, "CAUSE_NOT_FOUND")
  Change(checked(s.copy(causes = s.causes.filterNot { it.id == causeId })), Unit)
 } }
 suspend fun purge(rootIds: List<String>) { repo.transaction { s ->
  val all = normalizedRoots(s, rootIds).flatMap { descendants(s, it) }.toSet()
  demand(all.isNotEmpty() && all.all { s.lifecycle(it) == "trash" }, "PURGE_NOT_IN_TRASH")
  Change(checked(purged(s, all)), Unit)
 } }
 suspend fun purgeExpired() { repo.transaction { s ->
  val all = s.causes.filter { it.kind == "trash" && it.purgeAfter!! <= clock.millis() }.flatMap { it.members }.toSet()
  Change(checked(purged(s, all)), Unit)
 } }
 private fun purged(s: LibraryState, ids: Set<String>): LibraryState {
  if (ids.isEmpty()) return s
  val causes = s.causes.mapNotNull { c -> val members = c.members.filterNot { it in ids }; if (members.isEmpty()) null else c.copy(members = members, sourceEventId = c.sourceEventId?.takeUnless { it in ids }) }
  return s.copy(events = s.events.filterNot { it.id in ids }, actions = s.actions.filterNot { it.goalEventId in ids }, causes = causes,
   imports = s.imports.map { b -> b.copy(provenance = b.provenance.map { it.copy(localEventId = it.localEventId?.takeUnless { id -> id in ids }) }) },
   home = if (s.home.fixedEventId in ids) s.home.copy(heroMode = "auto", fixedEventId = null) else s.home)
 }
 suspend fun setGoalState(id: String, state: String) { repo.transaction { s ->
  val e = s.event(id); modifiable(s, id); val goal = e.goal ?: throw AppException("GOAL_INVALID")
  demand(state in setOf("not_started", "in_progress", "completed", "canceled"), "GOAL_STATE_INVALID")
  val allowed = when (goal.state) {
   "not_started" -> setOf("not_started", "in_progress", "completed", "canceled")
   "in_progress" -> setOf("in_progress", "completed", "canceled")
   "completed" -> setOf("completed", "in_progress")
   else -> setOf("canceled", "in_progress")
  }
  demand(state in allowed, "GOAL_STATE_TRANSITION")
  val edited = e.copy(goal = goal.copy(state = state, completedAt = if (state == "completed") goal.completedAt ?: clock.millis() else null), version = e.version + 1, updatedAt = clock.millis())
  Change(checked(s.copy(events = s.events.map { if (it.id == id) edited else it })), Unit)
 } }
 suspend fun saveAction(action: ActionRecord, expectedVersion: Long? = null): ActionRecord = repo.transaction { s ->
  val old = s.actions.find { it.id == action.id }; version(old?.version, expectedVersion)
  val goal = s.event(action.goalEventId); modifiable(s, goal.id)
  demand(goal.kind == "goal" && (old == null || old.goalEventId == action.goalEventId), "GOAL_INVALID")
  demand(parseDate(action.date) <= LocalDate.now(clock), "ACTION_FUTURE_DATE")
  val saved = action.copy(version = (old?.version ?: 0) + 1, createdAt = old?.createdAt ?: clock.millis(), updatedAt = clock.millis())
  Change(checked(s.copy(actions = s.actions.filterNot { it.id == saved.id } + saved)), saved)
 }
 suspend fun deleteAction(id: String) { repo.transaction { s ->
  val action = s.actions.find { it.id == id } ?: throw AppException("ACTION_NOT_FOUND"); modifiable(s, action.goalEventId)
  Change(s.copy(actions = s.actions.filterNot { it.id == id }), Unit)
 } }
 suspend fun saveTag(tag: Tag): Tag = repo.transaction { s ->
  val saved = tag.copy(name = tag.name.trim(), createdAt = s.tags.find { it.id == tag.id }?.createdAt ?: clock.millis())
  Change(checked(s.copy(tags = s.tags.filterNot { it.id == tag.id } + saved)), saved)
 }
 suspend fun deleteTag(id: String) { repo.transaction { s ->
  demand(s.tags.any { it.id == id }, "TAG_NOT_FOUND")
  Change(checked(s.copy(tags = s.tags.filterNot { it.id == id }, events = s.events.map { if (id in it.tagIds) it.copy(tagIds = it.tagIds - id, version = it.version + 1, updatedAt = clock.millis()) else it })), Unit)
 } }
 suspend fun setTags(eventIds: List<String>, tagIds: List<String>) { repo.transaction { s ->
  demand(eventIds.isNotEmpty() && eventIds.toSet().size == eventIds.size && tagIds.toSet().size == tagIds.size, "INPUT_DUPLICATE")
  eventIds.forEach { s.event(it); modifiable(s, it) }
  Change(checked(s.copy(events = s.events.map { if (it.id in eventIds) it.copy(tagIds = tagIds, version = it.version + 1, updatedAt = clock.millis()) else it })), Unit)
 } }
 suspend fun saveHome(home: HomeConfig) { repo.transaction { s -> Change(checked(s.copy(home = home)), Unit) } }

 fun search(snapshot: LibraryState, query: String, scope: String = "active", bookId: String? = null): List<Event> {
  demand(scope in setOf("active", "archived", "trash", "all"), "INPUT_ENUM")
  val key = nameKey(query); val books = snapshot.books.associateBy { it.id }; val tags = snapshot.tags.associateBy { it.id }
  return snapshot.events.filter { e -> (scope == "all" || snapshot.lifecycle(e.id) == scope) && (bookId == null || e.bookId == bookId) && (key.isEmpty() || listOf(e.title, e.greeting, books[e.bookId]?.name ?: "").plus(e.tagIds.mapNotNull { tags[it]?.name }).any { nameKey(it).contains(key) }) }.sortedWith(eventComparator(snapshot, "date"))
 }
 fun directChildren(snapshot: LibraryState, parentId: String, sortMode: String = "date", cursor: String? = null, pageSize: Int = 20): ChildPage {
  snapshot.event(parentId); demand(pageSize in 1..100, "INPUT_RANGE", "pageSize")
  demand(sortMode in setOf("date", "manual"), "INPUT_ENUM")
  val signature = "${snapshot.revision}:$parentId:$sortMode:"
  val offset = if (cursor == null) 0 else { demand(cursor.startsWith(signature), "CURSOR_STALE"); cursor.removePrefix(signature).toIntOrNull() ?: throw AppException("CURSOR_INVALID") }
  demand(offset >= 0, "CURSOR_INVALID")
  val children = snapshot.events.filter { it.parentId == parentId && snapshot.lifecycle(it.id) == "active" }.sortedWith(eventComparator(snapshot, sortMode))
  demand(offset <= children.size, "CURSOR_INVALID")
  val selected = children.drop(offset).take(pageSize)
  val more = offset + selected.size < children.size
  return ChildPage(selected.map { e -> ChildSummary(e, depth(snapshot, e.id), snapshot.events.count { it.parentId == e.id && snapshot.lifecycle(it.id) == "active" }, dates.evaluate(e.dateInput())) }, if (more) signature + (offset + selected.size) else null, more, snapshot.revision)
 }
 fun homeEvents(snapshot: LibraryState, bookId: String? = null): List<Event> = snapshot.events.filter { e -> e.homeVisible && snapshot.lifecycle(e.id) == "active" && (bookId == null || e.bookId == bookId) && e.goal?.state !in setOf("completed", "canceled") }.sortedWith(compareByDescending<Event> { it.pinned }.then(eventComparator(snapshot, snapshot.home.sortMode)))
 fun hero(snapshot: LibraryState, bookId: String? = null): Event? {
  if (snapshot.home.heroMode == "fixed") snapshot.events.find { it.id == snapshot.home.fixedEventId && snapshot.lifecycle(it.id) == "active" && it.goal?.state !in setOf("completed", "canceled") }?.let { return it }
  return homeEvents(snapshot, bookId).filter { it.countMode == "down" }.filter { dates.evaluate(it.dateInput()).let { p -> !p.exhausted && (p.occurrence?.instant ?: p.occurrence?.date?.plusDays(1)?.atStartOfDay(clock.zone)?.toInstant())?.let { time -> time >= clock.instant() } == true } }.minWithOrNull(eventComparator(snapshot, "date"))
 }
 fun completionRate(snapshot: LibraryState, id: String): Pair<Int, Int>? {
  demand(snapshot.event(id).goal != null, "GOAL_INVALID")
  val goals = snapshot.events.filter { it.parentId == id && it.goal != null && it.goal.includeInParent && it.goal.state != "canceled" && snapshot.lifecycle(it.id) == "active" }
  return if (goals.isEmpty()) null else goals.count { it.goal!!.state == "completed" } to goals.size
 }
 fun timeProgress(snapshot: LibraryState, id: String): Double {
  val e = snapshot.event(id); val g = e.goal ?: throw AppException("GOAL_INVALID")
  val start = parseDate(g.startDate); val end = LocalDate.of(e.date.year!!, e.date.month, e.date.day); val today = LocalDate.now(clock)
  if (end == start) return if (today >= start) 1.0 else 0.0
  return (ChronoUnit.DAYS.between(start, today).toDouble() / ChronoUnit.DAYS.between(start, end)).coerceIn(0.0, 1.0)
 }
 private fun eventComparator(snapshot: LibraryState, mode: String): Comparator<Event> {
  if (mode == "manual") return compareBy<Event> { it.sortRank }.thenBy { it.createdAt }.thenBy { it.id }
  val projection = snapshot.events.associate { it.id to dates.evaluate(it.dateInput()) }
  return compareBy<Event> { e -> val p = projection.getValue(e.id); when { e.countMode == "up" -> 2; p.exhausted -> 3; p.occurrence?.date?.isBefore(LocalDate.now(clock)) == true -> 3; else -> 0 } }
   .thenBy { projection.getValue(it.id).occurrence?.instant ?: projection.getValue(it.id).occurrence?.date?.atStartOfDay(clock.zone)?.toInstant() ?: java.time.Instant.MAX }
   .thenBy { it.sortRank }.thenBy { it.createdAt }.thenBy { it.id }
 }
 private fun normalizedRoots(s: LibraryState, ids: List<String>): List<String> {
  demand(ids.isNotEmpty(), "INPUT_REQUIRED")
  val unique = ids.toSet(); unique.forEach { s.event(it) }
  return unique.filter { id -> unique.none { other -> other != id && id in descendants(s, other) } }
 }
 companion object { private const val THIRTY_DAYS = 30L * 24 * 60 * 60 * 1000 }
}
'''
# END FILE: core/src/main/kotlin/cn/datebook/core/DateBookService.kt


# ============================================================================
# BEGIN FILE: core/src/main/kotlin/cn/datebook/core/DateEngine.kt
# ============================================================================
FILES['core/src/main/kotlin/cn/datebook/core/DateEngine.kt'] = r'''package cn.datebook.core

import java.time.*
import java.time.temporal.ChronoUnit
import kotlin.math.ceil
import kotlin.math.floor

/** 日期事实与当前时钟的纯投影；不会改写原始锚点或创建年度副本。 */
class DateEngine(private val clock: Clock, private val lunar: LunarPort) {
 fun currentDate(): LocalDate = LocalDate.now(clock)
 fun currentInstant(): Instant = clock.instant()
 fun validate(input: DateInput) {
  val d = input.date; val r = input.repeat
  demand(input.kind in setOf("ordinary", "birthday", "memorial", "holiday", "goal"), "INPUT_ENUM", "kind")
  demand(input.countMode in setOf("up", "down"), "INPUT_ENUM", "countMode")
  demand(d.calendar in setOf("gregorian", "lunar"), "INPUT_ENUM", "date.calendar")
  demand(d.feb29Policy in setOf("feb28", "mar01") && d.lunarLeapPolicy in setOf("normal_fallback", "leap_only") && d.lunarSmallMonthPolicy in setOf("month_end", "skip"), "INPUT_ENUM", "date.policy")
  demand(r.frequency in setOf("none", "yearly", "monthly", "weekly", "every_n_days"), "INPUT_ENUM", "repeat.frequency")
  demand(if (r.frequency == "every_n_days") r.intervalDays != null && r.intervalDays in 1..365 else r.intervalDays == null, "DATE_REPEAT_INVALID", "repeat.intervalDays")
  demand(d.month in 1..12 && d.day in 1..31, "DATE_INVALID", "date")
  demand(d.year != null || input.kind == "birthday" && r.frequency == "yearly", "DATE_YEAR_REQUIRED", "date.year")
  demand(input.kind != "birthday" || d.allDay && r.frequency == "yearly" && input.countMode == "down", "DATE_KIND_INVALID", "kind")
  demand(input.countMode != "up" || r.frequency == "none", "DATE_REPEAT_INVALID", "countMode")
  demand(input.kind != "goal" || d.calendar == "gregorian" && d.allDay && r.frequency == "none" && input.countMode == "down", "GOAL_DATE_INVALID", "date")
  demand(d.feb29Policy.isNotBlank() && d.calendarEngineVersion.length <= 64, "DATE_INVALID", "date")
  if (d.allDay) demand(d.localTime == null && d.zoneId == null, "DATE_TIME_INVALID", "date.localTime")
  else {
   demand(d.calendar == "gregorian" && d.localTime != null && d.zoneId != null, "DATE_TIME_INVALID", "date")
   try { demand(Regex("([01][0-9]|2[0-3]):[0-5][0-9]").matches(d.localTime!!), "DATE_TIME_INVALID"); ZoneId.of(d.zoneId) }
   catch (e: DateTimeException) { throw AppException("DATE_TIME_INVALID", "date") }
  }
  if (d.calendar == "gregorian") {
   demand(!d.leapMonth && (d.year == null || d.year in 1900..2100), "DATE_RANGE", "date.year")
   try { LocalDate.of(d.year ?: 2000, d.month, d.day) } catch (e: DateTimeException) { throw AppException("DATE_INVALID", "date") }
  } else {
   demand(d.allDay && d.day <= 30 && r.frequency in setOf("none", "yearly") && (d.year == null || d.year in 1901..2099), "DATE_RANGE", "date")
   if (d.year != null) demand(lunarDate(d, d.year) != null, "DATE_INVALID", "date")
  }
  if (r.until != null) {
   val until = parseDate(r.until, "repeat.until")
   demand(r.frequency != "none", "DATE_REPEAT_INVALID", "repeat.until")
   if (d.year != null) anchor(input)?.let { demand(!until.isBefore(it), "DATE_UNTIL_INVALID", "repeat.until") }
  }
 }

 fun nextOccurrence(input: DateInput, after: LocalDate, inclusive: Boolean = true): Occurrence? {
  validate(input)
  val start = if (inclusive) after else after.plusDays(1)
  val d = input.date; val r = input.repeat
  val until = r.until?.let { parseDate(it) }
  if (until != null && start > until) return null
  val candidate: LocalDate? = when (r.frequency) {
   "none" -> anchor(input)?.takeIf { it >= start }
   "yearly" -> {
    val first = if (d.calendar == "lunar") maxOf(1901, lunar.lunarYear(start) - 1, d.year ?: 1901) else maxOf(1900, start.year, d.year ?: 1900)
    val last = if (d.calendar == "lunar") 2099 else 2100
    var found: LocalDate? = null
    for (year in first..last) {
     val date = if (d.calendar == "lunar") lunarDate(d, year) else yearlyDate(d, year)
     if (date != null && date >= start && (until == null || date <= until) && (found == null || date < found)) found = date
     if (found != null && (d.calendar != "lunar" || year > first)) break
    }
    found
   }
   "monthly" -> {
    val base = anchor(input)!!
    var month = YearMonth.from(if (start < base) base else start)
    var date = month.atDay(minOf(d.day, month.lengthOfMonth()))
    if (date < start || date < base) { month = month.plusMonths(1); date = month.atDay(minOf(d.day, month.lengthOfMonth())) }
    date.takeIf { it.year <= 2100 }
   }
   else -> {
    val base = anchor(input)!!
    val step = if (r.frequency == "weekly") 7L else r.intervalDays!!.toLong()
    val delta = ChronoUnit.DAYS.between(base, start).coerceAtLeast(0)
    base.plusDays((delta + step - 1) / step * step).takeIf { it.year <= 2100 }
   }
  }
  if (candidate == null || until != null && candidate > until) return null
  return occurrence(input, candidate)
 }

 fun occurrences(input: DateInput, from: LocalDate, to: LocalDate): List<Occurrence> {
  demand(to >= from && ChronoUnit.DAYS.between(from, to) <= 36600, "DATE_WINDOW_INVALID")
  val out = ArrayList<Occurrence>(); var cursor = from
  while (cursor <= to) {
   val next = nextOccurrence(input, cursor) ?: break
   if (next.date > to) break
   out += next
   demand(out.size <= 10000, "DATE_WINDOW_LIMIT")
   cursor = next.date.plusDays(1)
  }
  return out
 }

 fun evaluate(input: DateInput, now: Instant = clock.instant(), zone: ZoneId = clock.zone): DateProjection {
  validate(input)
  val d = input.date
  val effectiveZone = if (d.allDay) zone else ZoneId.of(d.zoneId)
  val today = now.atZone(effectiveZone).toLocalDate()
  val tomorrow = today.plusDays(1).atStartOfDay(effectiveZone).toInstant()
  if (input.countMode == "up") {
   val start = occurrence(input, anchor(input)!!)
   val delta = if (d.allDay) ChronoUnit.DAYS.between(start.date, today) else floor(Duration.between(start.instant, now).seconds / 86400.0).toLong()
   if (delta < 0) {
    val boundary = if (d.allDay) tomorrow else start.instant!!.minusSeconds((-delta - 1) * 86400)
    return DateProjection(-delta, "尚未开始", start, validUntil = minOf(tomorrow, boundary))
   }
   val count = delta + if (input.includeStartDay) 1 else 0
   val boundary = if (d.allDay) tomorrow else start.instant!!.plusSeconds((delta + 1) * 86400)
   return DateProjection(count, "已过 $count 天", start, start.date == today, validUntil = minOf(tomorrow, boundary))
  }
  var next = nextOccurrence(input, today)
  if (next?.instant != null && next.instant!! < now && input.repeat.frequency != "none") next = nextOccurrence(input, today, false)
  if (next == null && input.repeat.frequency != "none") return DateProjection(null, "已无后续日期", null, exhausted = true, validUntil = tomorrow)
  if (next == null) next = occurrence(input, anchor(input)!!)
  val isToday = next.date == today
  val age = if (input.kind == "birthday" && d.year != null) (if (d.calendar == "lunar") lunar.lunarYear(next.date) else next.date.year) - d.year else null
  if (d.allDay) {
   val diff = ChronoUnit.DAYS.between(today, next.date)
   val label = when { diff == 0L -> if (input.kind == "birthday") "今天生日" else "就是今天"; diff > 0 -> "还有 $diff 天"; else -> "已过 ${-diff} 天" }
   return DateProjection(kotlin.math.abs(diff), label, next, isToday, age = age, validUntil = tomorrow)
  }
  val duration = Duration.between(now, next.instant)
  val seconds = duration.seconds.toDouble() + duration.nano / 1_000_000_000.0
  val days = if (seconds > 0) ceil(seconds / 86400.0).toLong() else floor(-seconds / 86400.0).toLong()
  val label = when { seconds > 0 -> "还有 $days 天"; seconds == 0.0 -> "就是现在"; days == 0L -> "已过不足 1 天"; else -> "已过 $days 天" }
  val boundary = if (seconds > 0) next.instant!!.minusSeconds((days - 1) * 86400) else next.instant!!.plusSeconds((days + 1) * 86400)
  return DateProjection(days, label, next, isToday, age = age, validUntil = minOf(tomorrow, boundary))
 }

 private fun anchor(input: DateInput): LocalDate? = input.date.let { d ->
  val year = d.year ?: return null
  if (d.calendar == "lunar") lunarDate(d, year) else LocalDate.of(year, d.month, d.day)
 }
 private fun lunarDate(d: DateSpec, year: Int) = lunar.solar(year, d.month, d.day, d.leapMonth, d.lunarLeapPolicy, d.lunarSmallMonthPolicy)
 private fun yearlyDate(d: DateSpec, year: Int): LocalDate = if (d.month == 2 && d.day == 29 && !Year.isLeap(year.toLong())) {
  if (d.feb29Policy == "mar01") LocalDate.of(year, 3, 1) else LocalDate.of(year, 2, 28)
 } else LocalDate.of(year, d.month, d.day)
 private fun occurrence(input: DateInput, date: LocalDate): Occurrence {
  val d = input.date
  // atZone 默认：DST 缺口向前推移到有效时刻，重叠选较早偏移。
  val instant = if (d.allDay) null else date.atTime(LocalTime.parse(d.localTime)).atZone(ZoneId.of(d.zoneId)).toInstant()
  val fallback = when { d.calendar == "gregorian" && d.month == 2 && d.day == 29 && date.dayOfMonth != 29 -> d.feb29Policy; else -> null }
  return Occurrence(date, instant, fallback)
 }
}

fun parseDate(value: String, field: String? = null): LocalDate = try {
 demand(Regex("[0-9]{4}-[0-9]{2}-[0-9]{2}").matches(value), "DATE_INVALID", field)
 LocalDate.parse(value)
} catch (e: DateTimeException) { throw AppException("DATE_INVALID", field) }
'''
# END FILE: core/src/main/kotlin/cn/datebook/core/DateEngine.kt


# ============================================================================
# BEGIN FILE: core/src/main/kotlin/cn/datebook/core/FileCodec.kt
# ============================================================================
FILES['core/src/main/kotlin/cn/datebook/core/FileCodec.kt'] = r'''package cn.datebook.core

import kotlinx.serialization.json.*
import java.io.*
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.security.SecureRandom
import java.time.Instant
import java.time.LocalDate
import java.util.Base64
import java.util.UUID
import java.util.zip.ZipEntry
import java.util.zip.ZipInputStream
import java.util.zip.ZipOutputStream
import javax.crypto.Cipher
import javax.crypto.Mac
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

data class LineIssue(val line: Int, val code: String, val message: String)
data class ImportPreview(val state: LibraryState, val sourceExportId: String, val fileSha256: String,
 val format: String, val issues: List<LineIssue> = emptyList())
data class BackupPreview(val state: LibraryState, val backupId: String, val assetRoot: File,
 val encrypted: Boolean, val fileSha256: String)
data class BackupReceipt(val backupId: String, val fileSha256: String, val bytes: Long)

/** The public format is deliberately mapped field by field; device state never leaves this boundary. */
class FileCodec(private val dates: DateEngine) {
 private val json = Json { isLenient = false; ignoreUnknownKeys = false; allowSpecialFloatingPointValues = false }
 private val textLimit = 10L * 1024 * 1024
 private val containerLimit = 256L * 1024 * 1024
 private val expandedLimit = 512L * 1024 * 1024
 private fun obj(vararg pairs: Pair<String, JsonElement>) = JsonObject(linkedMapOf(*pairs))
 private fun str(v: String?) = v?.let(::JsonPrimitive) ?: JsonNull
 private fun num(v: Number?) = v?.let(::JsonPrimitive) ?: JsonNull
 private fun bool(v: Boolean) = JsonPrimitive(v)
 private fun arr(v: Iterable<JsonElement>) = JsonArray(v.toList())
 private fun fields(o: JsonObject, required: String, optional: String = ""): JsonObject {
  val req = required.split(' ').filter { it.isNotEmpty() }.toSet()
  val allow = req + optional.split(' ').filter { it.isNotEmpty() }
  demand(o.keys.containsAll(req) && o.keys.all { it in allow }, "FILE_SCHEMA_INVALID")
  return o
 }
 private fun JsonObject.s(k: String): String = (get(k) as? JsonPrimitive)?.let { demand(it.isString,"FILE_SCHEMA_INVALID",k); it.content } ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.ns(k: String): String? = if (get(k) == JsonNull) null else s(k)
 private fun JsonObject.n(k: String): Long = (get(k) as? JsonPrimitive)?.let { demand(!it.isString,"FILE_SCHEMA_INVALID",k); it.longOrNull } ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.i(k: String): Int { val n = n(k); demand(n in Int.MIN_VALUE..Int.MAX_VALUE,"FILE_SCHEMA_INVALID",k); return n.toInt() }
 private fun JsonObject.nn(k: String): Long? = if(get(k)==JsonNull) null else n(k)
 private fun JsonObject.b(k: String): Boolean = (get(k) as? JsonPrimitive)?.let { demand(!it.isString,"FILE_SCHEMA_INVALID",k); it.booleanOrNull } ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.d(k: String, default: Double): Double = get(k)?.let { e -> val p=e as? JsonPrimitive ?: throw AppException("FILE_SCHEMA_INVALID",k); demand(!p.isString,"FILE_SCHEMA_INVALID",k); p.doubleOrNull?.also { demand(it.isFinite(),"FILE_SCHEMA_INVALID",k) } ?: throw AppException("FILE_SCHEMA_INVALID",k) } ?: default
 private fun JsonObject.o(k: String) = get(k) as? JsonObject ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.a(k: String) = get(k) as? JsonArray ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonElement.o() = this as? JsonObject ?: throw AppException("FILE_SCHEMA_INVALID")
 private fun utf8(bytes: ByteArray): String = try { StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString() } catch(e:Exception) { throw AppException("FILE_ENCODING_INVALID") }
 private fun parse(bytes: ByteArray, max: Long = textLimit): JsonObject {
  demand(bytes.size.toLong() <= max,"FILE_LIMIT_EXCEEDED")
  val text=utf8(bytes); rejectDuplicateKeys(text)
  return try { json.parseToJsonElement(text).o() } catch(e:AppException){throw e} catch(e:Exception){throw AppException("FILE_SCHEMA_INVALID")}
 }
 private fun validString(s:String):Boolean {var i=0;while(i<s.length){val c=s[i];if(c=='\u0000')return false;if(Character.isHighSurrogate(c)){if(i+1>=s.length||!Character.isLowSurrogate(s[i+1]))return false;i++}else if(Character.isLowSurrogate(c))return false;i++};return true}
 private fun date(d: DateSpec) = obj("calendar" to str(d.calendar),"year" to num(d.year),"month" to num(d.month),"day" to num(d.day),"leapMonth" to bool(d.leapMonth),"allDay" to bool(d.allDay),"localTime" to str(d.localTime),"zoneId" to str(d.zoneId),"feb29Policy" to str(d.feb29Policy),"lunarLeapPolicy" to str(d.lunarLeapPolicy),"lunarSmallMonthPolicy" to str(d.lunarSmallMonthPolicy),"calendarEngineVersion" to str(d.calendarEngineVersion))
 private fun readDate(o:JsonObject):DateSpec { fields(o,"calendar year month day leapMonth allDay localTime zoneId feb29Policy lunarLeapPolicy lunarSmallMonthPolicy calendarEngineVersion"); return DateSpec(o.s("calendar"),o.nn("year")?.also { demand(it in 1900..2100,"DATE_OUT_OF_RANGE") }?.toInt(),o.i("month"),o.i("day"),o.b("leapMonth"),o.b("allDay"),o.ns("localTime"),o.ns("zoneId"),o.s("feb29Policy"),o.s("lunarLeapPolicy"),o.s("lunarSmallMonthPolicy"),o.s("calendarEngineVersion")) }
 private fun repeat(r:RecurrenceSpec) = obj("frequency" to str(r.frequency),"intervalDays" to num(r.intervalDays),"until" to str(r.until))
 private fun readRepeat(o:JsonObject):RecurrenceSpec { fields(o,"frequency intervalDays until"); return RecurrenceSpec(o.s("frequency"),o.nn("intervalDays")?.also { demand(it in 1..365,"REPEAT_INVALID") }?.toInt(),o.ns("until")) }
 private fun goal(g:GoalDetail?) :JsonElement = g?.let { obj("startDate" to str(it.startDate),"state" to str(it.state),"completedAt" to num(it.completedAt),"includeInParent" to bool(it.includeInParent)) } ?: JsonNull
 private fun readGoal(e:JsonElement?):GoalDetail? { if(e==JsonNull) return null; val o=e?.o()?:throw AppException("FILE_SCHEMA_INVALID"); fields(o,"startDate state completedAt includeInParent"); return GoalDetail(o.s("startDate"),o.s("state"),o.nn("completedAt"),o.b("includeInParent")) }
 private fun appearance(a:Appearance,full:Boolean):JsonObject {
  val base=linkedMapOf<String,JsonElement>("backgroundKind" to str(if(!full&&a.backgroundKind=="photo")"gradient" else a.backgroundKind),"presetKey" to str(a.presetKey),"solidArgb" to num(a.solidArgb),"textColorMode" to str(a.textColorMode),"fontKey" to str(a.fontKey))
  if(full) base.putAll(mapOf("assetRef" to str(a.assetId),"focusX" to num(a.focusX),"focusY" to num(a.focusY),"dimAmount" to num(a.dimAmount)))
  return JsonObject(base)
 }
 private fun readAppearance(o:JsonObject,full:Boolean):Appearance {
  fields(o,"backgroundKind presetKey textColorMode fontKey",if(full)"solidArgb assetRef focusX focusY dimAmount" else "solidArgb")
  val kind=o.s("backgroundKind"); demand(kind in if(full)setOf("gradient","solid","photo")else setOf("gradient","solid"),"FILE_SCHEMA_INVALID")
  if(kind=="photo") demand(listOf("assetRef","focusX","focusY","dimAmount").all { it in o } && o.ns("assetRef")!=null,"ASSET_MISSING")
  return Appearance(kind,if(full&&"assetRef" in o)o.ns("assetRef")else null,o.s("presetKey"),if("solidArgb" in o)o.i("solidArgb")else -13278421,o.d("focusX",.5),o.d("focusY",.5),o.d("dimAmount",.35),o.s("textColorMode"),o.s("fontKey"))
 }
 private fun book(b:Book,full:Boolean):JsonObject { val m=linkedMapOf<String,JsonElement>("ref" to str(b.id),"name" to str(b.name),"builtinKey" to str(b.builtinKey),"iconKey" to str(b.iconKey),"colorArgb" to num(b.colorArgb),"sortRank" to num(b.sortRank)); if(full)m.putAll(mapOf("coverAssetRef" to str(b.coverAssetId),"createdAt" to num(b.createdAt),"updatedAt" to num(b.updatedAt),"version" to num(b.version))); return JsonObject(m) }
 private fun readBook(o:JsonObject,full:Boolean):Book { fields(o,"ref name builtinKey iconKey colorArgb sortRank"+if(full)" coverAssetRef createdAt updatedAt version"else ""); val builtin=o.ns("builtinKey"); demand(builtin==null||builtin in setOf("birthday","memorial","holiday","goal","uncategorized"),"FILE_SCHEMA_INVALID"); return Book(ref(o,"ref"),o.s("name"),builtin,o.s("iconKey"),o.i("colorArgb"),if(full)o.ns("coverAssetRef")else null,o.n("sortRank"),if(full)o.n("createdAt")else 0,if(full)o.n("updatedAt")else 0,if(full)o.n("version")else 1) }
 private fun event(e:Event,full:Boolean,tags:Map<String,Tag>):JsonObject {
  val m=linkedMapOf<String,JsonElement>("ref" to str(e.id),"bookRef" to str(e.bookId),"parentRef" to str(e.parentId),"title" to str(e.title),"kind" to str(e.kind),"countMode" to str(e.countMode),"includeStartDay" to bool(e.includeStartDay),"greeting" to str(e.greeting),"homeVisible" to bool(e.homeVisible),"pinned" to bool(e.pinned),"sortRank" to num(e.sortRank),"date" to date(e.date),"repeat" to repeat(e.repeat),"appearance" to appearance(e.appearance,full),"goal" to goal(e.goal))
  if(full)m.putAll(mapOf("tagRefs" to arr(e.tagIds.map{str(it)}),"createdAt" to num(e.createdAt),"updatedAt" to num(e.updatedAt),"version" to num(e.version),"reminders" to arr(e.reminders.map{r->obj("ref" to str(r.id),"enabled" to bool(r.enabled),"offsetUnit" to str(r.offsetUnit),"offsetValue" to num(r.offsetValue),"localTime" to str(r.localTime),"precisionMode" to str(r.precisionMode),"version" to num(r.version))})))
  else m.putAll(mapOf("tags" to arr(e.tagIds.mapNotNull{tags[it]?.name}.map{str(it)}),"backgroundFallback" to str(if(e.appearance.backgroundKind=="photo")"photo_omitted"else"none")))
  return JsonObject(m)
 }
 private fun readEvent(o:JsonObject,full:Boolean,tagByName:MutableMap<String,Tag>):Event {
  fields(o,"ref bookRef parentRef title kind countMode includeStartDay greeting homeVisible pinned sortRank date repeat appearance goal"+if(full)" tagRefs createdAt updatedAt version reminders" else " tags backgroundFallback")
  val tags=if(full) o.a("tagRefs").map { scalarString(it) } else o.a("tags").map{v->val name=scalarString(v);tagByName.getOrPut(name){Tag(name=name)}.id}
  demand(tags.size<=20&&tags.distinct().size==tags.size,"FILE_SCHEMA_INVALID")
  if(!full)demand(o.s("backgroundFallback")in setOf("none","photo_omitted"),"FILE_SCHEMA_INVALID")
  val rules=if(full)o.a("reminders").map{ e->val r=fields(e.o(),"ref enabled offsetUnit offsetValue localTime precisionMode version");ReminderRule(ref(r,"ref"),r.b("enabled"),r.s("offsetUnit"),r.i("offsetValue"),r.ns("localTime"),r.s("precisionMode"),r.n("version")) }else emptyList()
  return Event(ref(o,"ref"),ref(o,"bookRef"),o.ns("parentRef"),o.s("title"),o.s("kind"),o.s("countMode"),o.b("includeStartDay"),o.s("greeting"),o.b("homeVisible"),o.b("pinned"),o.n("sortRank"),readDate(o.o("date")),readRepeat(o.o("repeat")),readAppearance(o.o("appearance"),full),readGoal(o["goal"]),rules,tags,if(full)o.n("createdAt")else 0,if(full)o.n("updatedAt")else 0,if(full)o.n("version")else 1)
 }
 private fun scalarString(e:JsonElement):String { val p=e as? JsonPrimitive?:throw AppException("FILE_SCHEMA_INVALID"); demand(p.isString,"FILE_SCHEMA_INVALID"); return p.content }
 private fun ref(o:JsonObject,k:String):String = o.s(k).also{ demand(it.isNotEmpty()&&it.length<=128,"FILE_SCHEMA_INVALID",k) }
 private fun check(state:LibraryState) {
  LibraryValidator.validate(state,dates);state.events.forEach { dates.validate(it.dateInput()) }
  val refs=state.books.map{it.id}+state.events.map{it.id}+state.tags.map{it.id}+state.assets.map{it.id}+state.actions.map{it.id}+state.causes.map{it.id}+state.imports.map{it.id}+state.events.flatMap{it.reminders}.map{it.id}
  demand(refs.size==refs.distinct().size&&refs.all{it.isNotEmpty()&&it.length<=128},"FILE_REF_INVALID")
  state.books.forEach{demand(it.iconKey.length<=64,"FILE_SCHEMA_INVALID")}
  state.events.forEach{e->demand(e.appearance.presetKey.length<=64&&e.appearance.fontKey.length<=64&&e.date.calendarEngineVersion.length<=64&&(e.date.zoneId?.length?:0)<=128&&e.tagIds.size<=20,"FILE_SCHEMA_INVALID")}
  state.assets.forEach{a->val extension=when(a.mimeType){"image/jpeg"->"jpg";"image/png"->"png";"image/webp"->"webp";else->throw AppException("ASSET_INVALID")};demand(a.sha256.matches(Regex("[0-9a-f]{64}"))&&a.relativePath=="assets/${a.sha256}.$extension","ASSET_INVALID")}
  demand(state.causes.size<=200000&&state.imports.size<=200000,"FILE_LIMIT_EXCEEDED")
 }
 fun exportJson(state:LibraryState,selectedIds:Set<String>?=null):ByteArray {
  check(state); val selected=state.events.filter{ (selectedIds==null||it.id in selectedIds)&&state.lifecycle(it.id)=="active" }; val ids=selected.map{it.id}.toSet()
  val output=obj("format" to str("countdown_events"),"version" to num(1),"exportId" to str(newId()),"exportedAt" to str(Instant.now().toString()),"books" to arr(state.books.filter{b->selected.any{it.bookId==b.id}}.map{book(it,false)}),"events" to arr(selected.map{event(it.copy(parentId=it.parentId?.takeIf{p->p in ids}),false,state.tags.associateBy{it.id})})).toString().toByteArray()
  demand(output.size.toLong()<=textLimit,"FILE_LIMIT_EXCEEDED"); return output
 }
 fun importJson(bytes:ByteArray):ImportPreview {
  val o=fields(parse(bytes),"format version exportId exportedAt books events"); demand(o.s("format")=="countdown_events"&&o.n("version")==1L,"FILE_VERSION_UNSUPPORTED"); UUID.fromString(o.s("exportId"));Instant.parse(o.s("exportedAt"))
  val tags=linkedMapOf<String,Tag>(); val books=o.a("books").map{readBook(it.o(),false)}.toMutableList();if(books.none{it.builtinKey=="uncategorized"})books+=Book(name=if(books.any{it.name=="未分类"})"未分类 (导入)"else"未分类",builtinKey="uncategorized");val state=LibraryState(books=books,events=o.a("events").map{readEvent(it.o(),false,tags)},tags=tags.values.toList())
  check(state); return ImportPreview(state,o.s("exportId"),sha256(bytes),"json")
 }
 fun exportCsv(state:LibraryState,ids:Set<String>):ByteArray {
  val rows=state.events.filter{it.id in ids}; demand(rows.all{it.date.calendar=="gregorian"&&it.date.allDay&&it.kind!="goal"&&it.parentId==null&&state.events.none{c->c.parentId==it.id}&&it.repeat.frequency in setOf("none","yearly","monthly","weekly")&&it.date.year!=null},"CSV_LOSS_REQUIRES_JSON")
  val header="schema_version,escape_mode,title,date,calendar,type,repeat,message\r\n"
  val result=header+rows.joinToString(""){e->listOf("1","apostrophe_v1",e.title,LocalDate.of(e.date.year!!,e.date.month,e.date.day).toString(),"gregorian",e.kind,e.repeat.frequency,e.greeting).map{escapeFormula(it)}.joinToString(","){csvQuote(it)}+"\r\n"}
  return result.toByteArray().also{demand(it.size.toLong()<=textLimit,"FILE_LIMIT_EXCEEDED")}
 }
 fun importCsv(bytes:ByteArray):ImportPreview {
  demand(bytes.size.toLong()<=textLimit,"FILE_LIMIT_EXCEEDED"); val rows=parseCsv(utf8(bytes).removePrefix("\uFEFF"));demand(rows.isNotEmpty(),"CSV_HEADER_INVALID")
  val current=listOf("schema_version","escape_mode","title","date","calendar","type","repeat","message");val old=current.drop(2);val modern=rows.first().second==current
  demand(modern||rows.first().second==old,"CSV_HEADER_INVALID");if(modern)demand(rows.drop(1).filter{it.second.any(String::isNotEmpty)}.all{it.second.size>=2&&it.second[0]=="1"&&it.second[1]=="apostrophe_v1"},"CSV_ESCAPE_INVALID");val issues=mutableListOf<LineIssue>();val events=mutableListOf<Event>();val b=Book(name="导入的日子",builtinKey="uncategorized")
  rows.drop(1).forEach { (line,values)->if(values.any{it.isNotEmpty()})try { demand(values.size==if(modern)8 else 6,"CSV_COLUMN_INVALID"); if(modern)demand(values[0]=="1"&&values[1]=="apostrophe_v1","CSV_ESCAPE_INVALID");val v=if(modern)values.drop(2).map(::unescapeFormula)else values;demand(v[2]=="gregorian"&&v[3]in setOf("birthday","memorial","holiday","ordinary")&&v[4]in setOf("none","yearly","monthly","weekly"),"CSV_VALUE_INVALID"); val day=LocalDate.parse(v[1]); val e=Event(id="row:$line",bookId=b.id,title=v[0],kind=v[3],greeting=v[5],date=DateSpec(year=day.year,month=day.monthValue,day=day.dayOfMonth),repeat=RecurrenceSpec(v[4]));check(LibraryState(books=listOf(b),events=listOf(e)));events+=e }catch(e:Exception){issues+=LineIssue(line,(e as? AppException)?.code?:"CSV_VALUE_INVALID","第 $line 行无效，未导入")}}
  demand(events.size<=2000,"LIBRARY_LIMIT_EXCEEDED"); return ImportPreview(LibraryState(books=listOf(b),events=events),"csv:${sha256(bytes)}",sha256(bytes),"csv",issues)
 }
 /** Call within repository.transaction and bind confirmation to the original epoch/revision. */
 fun merge(target:LibraryState,preview:ImportPreview,now:Long=System.currentTimeMillis()):LibraryState {
  val source=preview.state;check(source);if(target.imports.any{it.sourceExportId==preview.sourceExportId&&it.fileSha256==preview.fileSha256})return target
  val prior=target.imports.filter{it.sourceExportId==preview.sourceExportId}.flatMap{it.provenance};val seen=prior.map{it.sourceRef}.toSet();val added=source.events.filter{it.id !in seen};if(added.isEmpty()&&source.events.isNotEmpty())return target
  val oldMap=prior.associate{it.sourceRef to it.localEventId};val bookMap=mutableMapOf<String,String>();val books=target.books.toMutableList();val newBooks=mutableMapOf<String,Book>()
  source.books.forEach{b->val builtin=b.builtinKey?.let{k->books.firstOrNull{it.builtinKey==k}};val priorBooks=source.events.filter{it.bookId==b.id}.mapNotNull{oldMap[it.id]}.mapNotNull{id->target.events.firstOrNull{it.id==id}?.bookId}.distinct();val existing=builtin?:priorBooks.singleOrNull()?.let{id->books.firstOrNull{it.id==id}};if(existing!=null)bookMap[b.id]=existing.id else {var name=b.name;var n=2;while(books.any{nameKey(it.name)==nameKey(name)}){val clusters=java.util.regex.Pattern.compile("\\X").matcher(b.name);var count=0;var end=0;while(count<22&&clusters.find()){end=clusters.end();count++};name="${b.name.substring(0,end)} ($n)";n++};val copy=b.copy(id=newId(),name=name,coverAssetId=null,createdAt=now,updatedAt=now,version=1);books+=copy;bookMap[b.id]=copy.id;newBooks[copy.id]=b}}
  val tagMap=mutableMapOf<String,String>();val tags=target.tags.toMutableList();source.tags.forEach{t->val found=tags.firstOrNull{nameKey(it.name)==nameKey(t.name)}; val copy=found?:t.copy(id=newId(),createdAt=now).also{tags+=it};tagMap[t.id]=copy.id}
  val eventMap=added.associate{it.id to newId()}
  val assets=target.assets.toMutableList();val assetMap=source.assets.associate{a->val found=assets.firstOrNull{it.sha256==a.sha256};val copy=found?:a.copy(id=newId()).also{assets+=it};a.id to copy.id}
  val copies=added.map{e->e.copy(id=eventMap.getValue(e.id),bookId=bookMap.getValue(e.bookId),parentId=e.parentId?.let{eventMap[it]?:oldMap[it]},tagIds=e.tagIds.map{tagMap.getValue(it)},appearance=e.appearance.copy(assetId=e.appearance.assetId?.let{assetMap[it]}),reminders=e.reminders.map{it.copy(id=newId(),enabled=false,version=1)},createdAt=now,updatedAt=now,version=1)}
  val actions=source.actions.filter{it.goalEventId in eventMap}.map{it.copy(id=newId(),goalEventId=eventMap.getValue(it.goalEventId),createdAt=now,updatedAt=now,version=1)}
  val causes=source.causes.mapNotNull{c->val members=c.members.mapNotNull{eventMap[it]};if(members.isEmpty())null else c.copy(id=newId(),sourceEventId=c.sourceEventId?.let{eventMap[it]},sourceBookId=c.sourceBookId?.let{bookMap[it]},members=members)}
  val batch=ImportBatch(format=preview.format,sourceExportId=preview.sourceExportId,fileSha256=preview.fileSha256,importedAt=now,provenance=added.map{ImportOrigin(it.id,eventMap[it.id])})
  return target.copy(books=books.map{b->newBooks[b.id]?.let{original->b.copy(coverAssetId=original.coverAssetId?.let{assetMap[it]})}?:b},events=target.events+copies,tags=tags,assets=assets,actions=target.actions+actions,causes=target.causes+causes,imports=target.imports+batch).also(::check)
 }
 private fun snapshot(s:LibraryState):JsonObject = obj("format" to str("daybook_library"),"version" to num(1),"library" to obj("id" to str(s.id),"name" to str(s.name),"contentRevision" to num(s.revision),"createdAt" to num(s.createdAt),"updatedAt" to num(s.updatedAt)),"books" to arr(s.books.map{book(it,true)}),"events" to arr(s.events.map{event(it,true,s.tags.associateBy{t->t.id})}),"assets" to arr(s.assets.map{a->obj("ref" to str(a.id),"sha256" to str(a.sha256),"path" to str(a.relativePath),"mimeType" to str(a.mimeType),"bytes" to num(a.bytes),"width" to num(a.width),"height" to num(a.height),"createdAt" to num(a.createdAt))}),"actions" to arr(s.actions.map{a->obj("ref" to str(a.id),"goalRef" to str(a.goalEventId),"date" to str(a.date),"body" to str(a.body),"minutes" to num(a.minutes),"createdAt" to num(a.createdAt),"updatedAt" to num(a.updatedAt),"version" to num(a.version))}),"tags" to arr(s.tags.map{t->obj("ref" to str(t.id),"name" to str(t.name),"createdAt" to num(t.createdAt))}),"lifecycleCauses" to arr(s.causes.map{c->obj("ref" to str(c.id),"kind" to str(c.kind),"sourceEventRef" to str(c.sourceEventId),"sourceBookRef" to str(c.sourceBookId),"createdAt" to num(c.createdAt),"purgeAfter" to num(c.purgeAfter),"members" to arr(c.members.map{str(it)}))}),"home" to obj("heroMode" to str(s.home.heroMode),"fixedEventRef" to str(s.home.fixedEventId),"sortMode" to str(s.home.sortMode),"selectedBookRef" to str(s.home.selectedBookId)),"importHistory" to arr(s.imports.map{b->obj("batchRef" to str(b.id),"format" to str(when(b.format){"json"->"events_json";"csv"->"events_csv";"backup"->"full_backup";else->throw AppException("IMPORT_INVALID")}),"sourceExportId" to str(b.sourceExportId),"fileSha256" to str(b.fileSha256),"importedAt" to num(b.importedAt),"provenance" to arr(b.provenance.map{p->obj("sourceRef" to str(p.sourceRef),"localEventRef" to str(p.localEventId))}))}))
 private fun readSnapshot(bytes:ByteArray):LibraryState {
  val o=fields(parse(bytes,64L*1024*1024),"format version library books events assets actions tags lifecycleCauses home importHistory");demand(o.s("format")=="daybook_library"&&o.n("version")==1L,"FILE_VERSION_UNSUPPORTED")
  val lib=fields(o.o("library"),"id name contentRevision createdAt updatedAt");UUID.fromString(lib.s("id"));val h=fields(o.o("home"),"heroMode fixedEventRef sortMode selectedBookRef")
  val state=LibraryState(id=lib.s("id"),name=lib.s("name"),revision=lib.n("contentRevision"),createdAt=lib.n("createdAt"),updatedAt=lib.n("updatedAt"),books=o.a("books").map{readBook(it.o(),true)},events=o.a("events").map{readEvent(it.o(),true,linkedMapOf())},tags=o.a("tags").map{v->val t=fields(v.o(),"ref name createdAt");Tag(ref(t,"ref"),t.s("name"),t.n("createdAt"))},assets=o.a("assets").map{v->val a=fields(v.o(),"ref sha256 path mimeType bytes width height createdAt");Asset(ref(a,"ref"),a.s("sha256"),a.s("path"),a.s("mimeType"),a.n("bytes"),a.i("width"),a.i("height"),a.n("createdAt"))},actions=o.a("actions").map{v->val a=fields(v.o(),"ref goalRef date body minutes createdAt updatedAt version");ActionRecord(ref(a,"ref"),ref(a,"goalRef"),a.s("date"),a.s("body"),a.nn("minutes")?.also{demand(it in 0..1440,"FILE_SCHEMA_INVALID")}?.toInt(),a.n("createdAt"),a.n("updatedAt"),a.n("version"))},causes=o.a("lifecycleCauses").map{v->val c=fields(v.o(),"ref kind sourceEventRef sourceBookRef createdAt purgeAfter members");LifecycleCause(ref(c,"ref"),c.s("kind"),c.ns("sourceEventRef"),c.ns("sourceBookRef"),c.n("createdAt"),c.nn("purgeAfter"),c.a("members").map(::scalarString))},home=HomeConfig(h.s("heroMode"),h.ns("fixedEventRef"),h.s("sortMode"),h.ns("selectedBookRef")),imports=o.a("importHistory").map{v->val b=fields(v.o(),"batchRef format sourceExportId fileSha256 importedAt provenance");ImportBatch(ref(b,"batchRef"),when(b.s("format")){"events_json"->"json";"events_csv"->"csv";"full_backup"->"backup";else->throw AppException("FILE_SCHEMA_INVALID")},ref(b,"sourceExportId"),b.s("fileSha256"),b.n("importedAt"),b.a("provenance").map{p->val q=fields(p.o(),"sourceRef localEventRef");ImportOrigin(ref(q,"sourceRef"),q.ns("localEventRef"))})})
  check(state);return state
 }
 fun writeBackup(state:LibraryState,assetRoot:File,out:OutputStream,password:CharArray?,includeTrash:Boolean=false):BackupReceipt {
  check(state);val omitted=state.events.filter{!includeTrash&&state.lifecycle(it.id)=="trash"}.map{it.id}.toSet();val events=state.events.filter{it.id !in omitted};val used=events.mapNotNull{it.appearance.assetId}.toSet()+state.books.mapNotNull{it.coverAssetId};val s=state.copy(events=events,actions=state.actions.filter{it.goalEventId !in omitted},assets=state.assets.filter{it.id in used},causes=state.causes.mapNotNull{c->val members=c.members.filter{it !in omitted};if(members.isEmpty())null else c.copy(members=members,sourceEventId=c.sourceEventId?.takeIf{it !in omitted})},home=state.home.copy(fixedEventId=state.home.fixedEventId?.takeIf{it !in omitted},heroMode=if(state.home.fixedEventId in omitted)"auto"else state.home.heroMode),imports=state.imports.map{b->b.copy(provenance=b.provenance.map{it.copy(localEventId=it.localEventId?.takeIf{id->id !in omitted})})})
  check(s);val temp=File.createTempFile("datebook-payload-",".zip",assetRoot.parentFile?:assetRoot);val backupId=newId()
  try {
   val content=snapshot(s).toString().toByteArray();val files=mutableListOf(obj("path" to str("library.json"),"bytes" to num(content.size),"sha256" to str(sha256(content))))
   s.assets.forEach{a->val f=safeAsset(assetRoot,a.relativePath);demand(f.isFile&&f.length()==a.bytes&&sha256(f)==a.sha256,"ASSET_CORRUPT");files+=obj("path" to str(a.relativePath),"bytes" to num(a.bytes),"sha256" to str(a.sha256))}
   val manifest=obj("format" to str("daybook_manifest"),"version" to num(1),"backupId" to str(backupId),"createdAt" to str(Instant.now().toString()),"contentRevision" to num(s.revision),"snapshotSchemaVersion" to num(1),"counts" to obj("books" to num(s.books.size),"events" to num(s.events.size),"actions" to num(s.actions.size),"assets" to num(s.assets.size)),"files" to arr(files)).toString().toByteArray()
   ZipOutputStream(temp.outputStream().buffered()).apply{setLevel(0)}.use{z->fun entry(path:String,write:()->Unit){z.putNextEntry(ZipEntry(path).apply{time=0});write();z.closeEntry()};entry("manifest.json"){z.write(manifest)};entry("library.json"){z.write(content)};s.assets.forEach{a->entry(a.relativePath){safeAsset(assetRoot,a.relativePath).inputStream().use{it.copyTo(z)}}}}
   demand(temp.length()<containerLimit-8192,"FILE_LIMIT_EXCEEDED");val encrypted=password!=null;val salt=if(encrypted)random(16)else null;val nonce=if(encrypted)random(12)else null;val header=obj("containerVersion" to num(1),"suite" to str(if(encrypted)"pbkdf2-sha256-aes256gcm"else"plain"),"salt" to str(salt?.let{Base64.getEncoder().encodeToString(it)}),"nonce" to str(nonce?.let{Base64.getEncoder().encodeToString(it)}),"iterations" to num(if(encrypted)600000 else null),"payloadFormat" to str("zip")).toString().toByteArray();val prefix=ByteArrayOutputStream().also{b->DataOutputStream(b).apply{write("DAYBOOK1".toByteArray());writeByte(if(encrypted)1 else 0);writeInt(header.size);write(header)}}.toByteArray()
   val digest=MessageDigest.getInstance("SHA-256");var count=0L;val target=object:FilterOutputStream(out){override fun write(b:Int){out.write(b);digest.update(b.toByte());count++};override fun write(b:ByteArray,off:Int,len:Int){out.write(b,off,len);digest.update(b,off,len);count+=len}}
   target.write(prefix);if(encrypted){val key=derive(password!!,salt!!);try{val c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,SecretKeySpec(key,"AES"),GCMParameterSpec(128,nonce));c.updateAAD(prefix);cipherCopy(temp,c,target)}finally{key.fill(0)}}else temp.inputStream().use{it.copyTo(target)};target.flush();return BackupReceipt(backupId,hex(digest.digest()),count)
  } finally {temp.delete()}
 }
 fun readBackup(input:InputStream,staging:File,password:CharArray?):BackupPreview {
  demand(!staging.exists()||staging.listFiles().isNullOrEmpty(),"STAGING_NOT_EMPTY");demand(staging.mkdirs()||staging.isDirectory,"FILE_IO_FAILED");val source=File(staging,"container.tmp");val zip=File(staging,"payload.tmp");var success=false
  try {
   source.outputStream().use{o->copyBounded(input,o,containerLimit)};val digest=sha256(source);var encrypted=false
   DataInputStream(source.inputStream().buffered()).use{d->val magic=ByteArray(8);d.readFully(magic);demand(magic.contentEquals("DAYBOOK1".toByteArray()),"FILE_VERSION_UNSUPPORTED");val suite=d.readUnsignedByte();demand(suite in 0..1,"FILE_VERSION_UNSUPPORTED");encrypted=suite==1;val length=d.readInt();demand(length in 1..4096,"FILE_SCHEMA_INVALID");val hb=ByteArray(length);d.readFully(hb);val h=fields(parse(hb,4096),"containerVersion suite salt nonce iterations payloadFormat");demand(h.n("containerVersion")==1L&&h.s("payloadFormat")=="zip","FILE_VERSION_UNSUPPORTED");val prefix=ByteArrayOutputStream().also{b->DataOutputStream(b).apply{write(magic);writeByte(suite);writeInt(length);write(hb)}}.toByteArray()
    zip.outputStream().use{o->if(encrypted){demand(h.s("suite")=="pbkdf2-sha256-aes256gcm"&&h.nn("iterations")==600000L,"FILE_VERSION_UNSUPPORTED");val salt=decode64(h.s("salt"),16);val nonce=decode64(h.s("nonce"),12);demand(password!=null,"PASSWORD_REQUIRED");val key=derive(password!!,salt);try{val c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.DECRYPT_MODE,SecretKeySpec(key,"AES"),GCMParameterSpec(128,nonce));c.updateAAD(prefix);try{cipherCopy(d,c,o,containerLimit)}catch(e:Exception){throw AppException("BACKUP_AUTH_FAILED")}}finally{key.fill(0)}}else{demand(h.s("suite")=="plain"&&h["salt"]==JsonNull&&h["nonce"]==JsonNull&&h["iterations"]==JsonNull,"FILE_SCHEMA_INVALID");copyBounded(d,o,containerLimit)}}
   }
   val entries=linkedMapOf<String,File>();var total=0L
   ZipInputStream(zip.inputStream().buffered()).use{z->while(true){val e=z.nextEntry?:break;val p=e.name;demand(!e.isDirectory&&p !in entries&&(p=="manifest.json"||p=="library.json"||p.matches(Regex("assets/[0-9a-f]{64}\\.(jpg|png|webp)"))),"BACKUP_PATH_INVALID");demand(entries.size<20000,"FILE_LIMIT_EXCEEDED");val f=File(staging,p);f.parentFile.mkdirs();f.outputStream().use{o->total+=copyBounded(z,o,if(p.startsWith("assets/"))26214400 else 64L*1024*1024)};demand(total<=expandedLimit&&(total<=1024*1024||total<=zip.length()*100),"FILE_LIMIT_EXCEEDED");entries[p]=f;z.closeEntry()}}
   val manifest=fields(parse((entries["manifest.json"]?:throw AppException("BACKUP_MANIFEST_INVALID")).readBytes(),64L*1024*1024),"format version backupId createdAt contentRevision snapshotSchemaVersion counts files");demand(manifest.s("format")=="daybook_manifest"&&manifest.n("version")==1L&&manifest.n("snapshotSchemaVersion")==1L,"FILE_VERSION_UNSUPPORTED");UUID.fromString(manifest.s("backupId"));Instant.parse(manifest.s("createdAt"));val listed=mutableSetOf<String>();manifest.a("files").forEach{v->val f=fields(v.o(),"path bytes sha256");val path=f.s("path");demand(listed.add(path)&&path!="manifest.json","BACKUP_MANIFEST_INVALID");val file=entries[path]?:throw AppException("BACKUP_MANIFEST_INVALID");demand(file.length()==f.n("bytes")&&sha256(file)==f.s("sha256"),"BACKUP_CHECKSUM_INVALID")};demand(listed==entries.keys-"manifest.json","BACKUP_MANIFEST_INVALID")
   val state=readSnapshot((entries["library.json"]?:throw AppException("BACKUP_MANIFEST_INVALID")).readBytes());val counts=fields(manifest.o("counts"),"books events actions assets");demand(counts.n("books")==state.books.size.toLong()&&counts.n("events")==state.events.size.toLong()&&counts.n("actions")==state.actions.size.toLong()&&counts.n("assets")==state.assets.size.toLong()&&manifest.n("contentRevision")==state.revision,"BACKUP_MANIFEST_INVALID")
   demand(entries.keys.filter{it.startsWith("assets/")}.toSet()==state.assets.map{it.relativePath}.toSet(),"BACKUP_MANIFEST_INVALID");state.assets.forEach{a->val f=entries[a.relativePath]?:throw AppException("ASSET_MISSING");demand(f.length()==a.bytes&&sha256(f)==a.sha256&&a.width.toLong()*a.height<=40000000,"ASSET_CORRUPT")};source.delete();zip.delete();entries["manifest.json"]?.delete();entries["library.json"]?.delete();success=true
   return BackupPreview(state.copy(epoch=newId(),events=state.events.map{e->e.copy(reminders=e.reminders.map{it.copy(enabled=false)})}),manifest.s("backupId"),staging,encrypted,digest)
  }catch(e:AppException){throw e}catch(e:Exception){throw AppException("BACKUP_FILE_INVALID")}finally{if(!success)staging.deleteRecursively()}
 }
 private fun decode64(value:String,size:Int):ByteArray = try{Base64.getDecoder().decode(value).also{demand(it.size==size&&Base64.getEncoder().encodeToString(it)==value,"FILE_SCHEMA_INVALID")}}catch(e:AppException){throw e}catch(e:Exception){throw AppException("FILE_SCHEMA_INVALID")}
 private fun safeAsset(root:File,path:String):File {demand(path.matches(Regex("assets/[0-9a-f]{64}\\.(jpg|png|webp)")),"BACKUP_PATH_INVALID");val f=File(root,path);demand(f.canonicalPath.startsWith(root.canonicalPath+File.separator),"BACKUP_PATH_INVALID");return f}
 private fun random(n:Int)=ByteArray(n).also{SecureRandom().nextBytes(it)}
 private fun derive(password:CharArray,salt:ByteArray):ByteArray {
  val chars=String(password);demand(chars.codePointCount(0,chars.length)>=8&&chars.toByteArray().size<=1024,"PASSWORD_INVALID");var i=0;while(i<chars.length){val c=chars[i];if(Character.isHighSurrogate(c)){demand(i+1<chars.length&&Character.isLowSurrogate(chars[i+1]),"PASSWORD_INVALID");i++}else demand(!Character.isLowSurrogate(c),"PASSWORD_INVALID");i++}
  val bytes=chars.toByteArray(StandardCharsets.UTF_8);try{val mac=Mac.getInstance("HmacSHA256");mac.init(SecretKeySpec(bytes,"HmacSHA256"));var u=mac.doFinal(salt+byteArrayOf(0,0,0,1));val result=u.clone();repeat(599999){val next=mac.doFinal(u);u.fill(0);u=next;for(j in result.indices)result[j]=(result[j].toInt() xor u[j].toInt()).toByte()};u.fill(0);return result}finally{bytes.fill(0)}
 }
 private fun cipherCopy(file:File,c:Cipher,out:OutputStream)=file.inputStream().use{cipherCopy(it,c,out,containerLimit)}
 private fun cipherCopy(input:InputStream,c:Cipher,out:OutputStream,max:Long){val buf=ByteArray(65536);var count=0L;while(true){val n=input.read(buf);if(n<0)break;count+=n;demand(count<=max,"FILE_LIMIT_EXCEEDED");c.update(buf,0,n)?.let{out.write(it)}};out.write(c.doFinal());buf.fill(0)}
 private fun copyBounded(input:InputStream,out:OutputStream,max:Long):Long{var total=0L;val b=ByteArray(65536);while(true){val n=input.read(b);if(n<0)break;total+=n;demand(total<=max,"FILE_LIMIT_EXCEEDED");out.write(b,0,n)};return total}
 private fun escapeFormula(s:String)=if(s.firstOrNull()?.let { it in "=+-@\t\r\n'" }==true)"'$s"else s
 private fun unescapeFormula(s:String)=if(s.length>=2&&s[0]=='\''&&s[1]in "=+-@\t\r\n'")s.substring(1)else s
 private fun csvQuote(s:String)="\"${s.replace("\"","\"\"")}\""
 private fun parseCsv(s:String):List<Pair<Int,List<String>>>{val result=mutableListOf<Pair<Int,List<String>>>();val row=mutableListOf<String>();val cell=StringBuilder();var quoted=false;var endedQuote=false;var line=1;var start=1;var i=0;while(i<s.length){val c=s[i];if(quoted){if(c=='"'){if(i+1<s.length&&s[i+1]=='"'){cell.append('"');i++}else{quoted=false;endedQuote=true}}else{cell.append(c);if(c=='\n')line++}}else when(c){'"'->{demand(cell.isEmpty()&&!endedQuote,"CSV_SYNTAX_INVALID");quoted=true};','->{row+=cell.toString();cell.clear();endedQuote=false};'\r','\n'->{if(c=='\r'&&i+1<s.length&&s[i+1]=='\n')i++;row+=cell.toString();result+=start to row.toList();row.clear();cell.clear();endedQuote=false;line++;start=line};else->{demand(!endedQuote,"CSV_SYNTAX_INVALID");cell.append(c)}};i++};demand(!quoted,"CSV_SYNTAX_INVALID");if(cell.isNotEmpty()||row.isNotEmpty()||endedQuote){row+=cell.toString();result+=start to row};return result}
 /** JSON's default parser accepts duplicate keys. Scan structure first with bounded nesting. */
 private fun rejectDuplicateKeys(text:String){var i=0;fun ws(){while(i<text.length&&text[i].isWhitespace())i++};fun string():String{val start=i++;while(i<text.length){val c=text[i++];if(c=='\\'){demand(i<text.length,"FILE_SCHEMA_INVALID");i++}else if(c=='"')return try{json.parseToJsonElement(text.substring(start,i)).jsonPrimitive.content.also{demand(validString(it),"FILE_ENCODING_INVALID")}}catch(e:Exception){throw AppException("FILE_SCHEMA_INVALID")}};throw AppException("FILE_SCHEMA_INVALID")};fun value(depth:Int){demand(depth<=32,"FILE_LIMIT_EXCEEDED");ws();demand(i<text.length,"FILE_SCHEMA_INVALID");when(text[i]){'{'->{i++;ws();val keys=mutableSetOf<String>();if(i<text.length&&text[i]=='}'){i++;return};while(true){ws();demand(i<text.length&&text[i]=='"',"FILE_SCHEMA_INVALID");demand(keys.add(string()),"FILE_DUPLICATE_KEY");ws();demand(i<text.length&&text[i++]==':',"FILE_SCHEMA_INVALID");value(depth+1);ws();demand(i<text.length,"FILE_SCHEMA_INVALID");val c=text[i++];if(c=='}')break;demand(c==',',"FILE_SCHEMA_INVALID")}};'['->{i++;ws();if(i<text.length&&text[i]==']'){i++;return};while(true){value(depth+1);ws();demand(i<text.length,"FILE_SCHEMA_INVALID");val c=text[i++];if(c==']')break;demand(c==',',"FILE_SCHEMA_INVALID")}};'"'->{string()};else->{val start=i;while(i<text.length&&text[i] !in ",]} \t\r\n")i++;demand(i>start,"FILE_SCHEMA_INVALID")}}};value(0);ws();demand(i==text.length,"FILE_SCHEMA_INVALID")}
 companion object {
  fun sha256(bytes:ByteArray)=hex(MessageDigest.getInstance("SHA-256").digest(bytes))
  fun sha256(file:File):String{val d=MessageDigest.getInstance("SHA-256");file.inputStream().use{i->val b=ByteArray(65536);while(true){val n=i.read(b);if(n<0)break;d.update(b,0,n)}};return hex(d.digest())}
  private fun hex(bytes:ByteArray)=bytes.joinToString(""){"%02x".format(it.toInt() and 255)}
 }
}
'''
# END FILE: core/src/main/kotlin/cn/datebook/core/FileCodec.kt


# ============================================================================
# BEGIN FILE: core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt
# ============================================================================
FILES['core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt'] = r'''package cn.datebook.core

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.time.Clock

/** 测试和离线业务验证用仓库；生产由 RoomStore 实现同一契约。 */
class MemoryRepository(seed: LibraryState = defaultLibrary(), private val clock: Clock = Clock.systemUTC()) : LibraryRepository {
 private val mutex = Mutex()
 private val current = MutableStateFlow(seed)
 private val receipts = LinkedHashMap<String, Any?>()
 override val state: StateFlow<LibraryState> = current.asStateFlow()
 init { LibraryValidator.validate(seed) }
 @Suppress("UNCHECKED_CAST")
 override suspend fun <T> transaction(operationId: String, expectedEpoch: String?, block: (LibraryState) -> Change<T>): T = mutex.withLock {
  val old = current.value
  demand(expectedEpoch == null || expectedEpoch == old.epoch, "LIBRARY_STALE")
  demand(operationId.isNotBlank() && operationId.length <= 128, "INPUT_INVALID", "operationId")
  if (receipts.containsKey(operationId)) return@withLock receipts[operationId] as T
  val change = block(old)
  demand(change.state.id == old.id && change.state.epoch == old.epoch && change.state.revision == old.revision, "LIBRARY_IDENTITY_INVALID")
  LibraryValidator.validate(change.state)
  if (change.state != old) current.value = change.state.copy(revision = old.revision + 1, updatedAt = clock.millis())
  receipts[operationId] = change.result
  change.result
 }
 override suspend fun install(candidate: LibraryState, expectedRevision: Long, expectedEpoch: String): LibraryState = mutex.withLock {
  val old = current.value
  demand(old.epoch == expectedEpoch && old.revision == expectedRevision, "PREVIEW_STALE")
  LibraryValidator.validate(candidate)
  val installed = candidate.copy(epoch = newId(), revision = old.revision + 1, updatedAt = clock.millis())
  current.value = installed
  receipts.clear()
  installed
 }
}
'''
# END FILE: core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt


# ============================================================================
# BEGIN FILE: core/src/main/kotlin/cn/datebook/core/Models.kt
# ============================================================================
FILES['core/src/main/kotlin/cn/datebook/core/Models.kt'] = r'''package cn.datebook.core

import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.Serializable
import java.time.Clock
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.util.UUID

fun newId(): String = UUID.randomUUID().toString()

@Serializable data class Book(
 val id: String = newId(), val name: String, val builtinKey: String? = null,
 val iconKey: String = "book", val colorArgb: Int = -13278421,
 val coverAssetId: String? = null, val sortRank: Long = 0,
 val createdAt: Long = 0, val updatedAt: Long = 0, val version: Long = 1,
 val isProtected: Boolean = builtinKey == "uncategorized"
)
@Serializable data class DateSpec(
 val calendar: String = "gregorian", val year: Int? = null, val month: Int = 1,
 val day: Int = 1, val leapMonth: Boolean = false, val allDay: Boolean = true,
 val localTime: String? = null, val zoneId: String? = null,
 val feb29Policy: String = "feb28", val lunarLeapPolicy: String = "normal_fallback",
 val lunarSmallMonthPolicy: String = "month_end", val calendarEngineVersion: String = "lunar-1.7.7"
)
@Serializable data class RecurrenceSpec(val frequency: String = "none", val intervalDays: Int? = null, val until: String? = null)
@Serializable data class Appearance(
 val backgroundKind: String = "gradient", val assetId: String? = null,
 val presetKey: String = "forest", val solidArgb: Int = -13278421,
 val focusX: Double = .5, val focusY: Double = .5, val dimAmount: Double = .35,
 val textColorMode: String = "auto", val fontKey: String = "system"
)
@Serializable data class GoalDetail(
 val startDate: String, val state: String = "not_started", val completedAt: Long? = null,
 val includeInParent: Boolean = true
)
@Serializable data class ReminderRule(
 val id: String = newId(), val enabled: Boolean = false, val offsetUnit: String = "days",
 val offsetValue: Int = 0, val localTime: String? = "09:00",
 val precisionMode: String = "normal", val version: Long = 1
)
@Serializable data class Event(
 val id: String = newId(), val bookId: String, val parentId: String? = null,
 val title: String, val kind: String = "ordinary", val countMode: String = "down",
 val includeStartDay: Boolean = false, val greeting: String = "",
 val homeVisible: Boolean = parentId == null, val pinned: Boolean = false,
 val sortRank: Long = 0, val date: DateSpec, val repeat: RecurrenceSpec = RecurrenceSpec(),
 val appearance: Appearance = Appearance(), val goal: GoalDetail? = null,
 val reminders: List<ReminderRule> = emptyList(), val tagIds: List<String> = emptyList(),
 val createdAt: Long = 0, val updatedAt: Long = 0, val version: Long = 1
)
@Serializable data class ActionRecord(
 val id: String = newId(), val goalEventId: String, val date: String,
 val body: String, val minutes: Int? = null, val createdAt: Long = 0,
 val updatedAt: Long = 0, val version: Long = 1
)
@Serializable data class Tag(val id: String = newId(), val name: String, val createdAt: Long = 0)
@Serializable data class Asset(
 val id: String = newId(), val sha256: String, val relativePath: String,
 val mimeType: String, val bytes: Long, val width: Int, val height: Int, val createdAt: Long = 0
)
@Serializable data class LifecycleCause(
 val id: String = newId(), val kind: String, val sourceEventId: String? = null,
 val sourceBookId: String? = null, val createdAt: Long, val purgeAfter: Long? = null,
 val members: List<String>
)
@Serializable data class HomeConfig(
 val heroMode: String = "auto", val fixedEventId: String? = null,
 val sortMode: String = "date", val selectedBookId: String? = null
)
@Serializable data class ImportOrigin(
 val sourceRef: String, val localEventId: String? = null
)
@Serializable data class ImportBatch(
 val id: String = newId(), val format: String, val sourceExportId: String,
 val fileSha256: String, val importedAt: Long, val provenance: List<ImportOrigin> = emptyList()
)
@Serializable data class LibraryState(
 val id: String = newId(), val name: String = "我的重要日子", val revision: Long = 0,
 val epoch: String = newId(), val createdAt: Long = 0, val updatedAt: Long = 0,
 val books: List<Book> = emptyList(), val events: List<Event> = emptyList(),
 val actions: List<ActionRecord> = emptyList(), val tags: List<Tag> = emptyList(),
 val assets: List<Asset> = emptyList(), val causes: List<LifecycleCause> = emptyList(),
 val home: HomeConfig = HomeConfig(), val imports: List<ImportBatch> = emptyList()
)

data class Change<T>(val state: LibraryState, val result: T)
interface LibraryRepository {
 val state: StateFlow<LibraryState>
 suspend fun <T> transaction(operationId: String = newId(), expectedEpoch: String? = null,
  block: (LibraryState) -> Change<T>): T
 suspend fun install(candidate: LibraryState, expectedRevision: Long, expectedEpoch: String): LibraryState
}

class AppException(val code: String, val field: String? = null, message: String = code) : IllegalArgumentException(message)
fun demand(ok: Boolean, code: String, field: String? = null) { if (!ok) throw AppException(code, field) }

data class DateInput(val date: DateSpec, val repeat: RecurrenceSpec, val countMode: String = "down",
 val includeStartDay: Boolean = false, val kind: String = "ordinary")
fun Event.dateInput() = DateInput(date, repeat, countMode, includeStartDay, kind)
data class Occurrence(val date: LocalDate, val instant: Instant? = null, val fallback: String? = null)
data class DateProjection(
 val days: Long?, val label: String, val occurrence: Occurrence?, val today: Boolean = false,
 val exhausted: Boolean = false, val age: Int? = null, val validUntil: Instant? = null
)
interface LunarPort {
 fun solar(year: Int, month: Int, day: Int, leapMonth: Boolean, leapPolicy: String, smallMonthPolicy: String): LocalDate?
 fun lunarYear(date: LocalDate): Int
}
data class ChildSummary(val event: Event, val depth: Int, val directChildCount: Int, val presentation: DateProjection)
data class ChildPage(val rows: List<ChildSummary>, val cursor: String?, val hasMore: Boolean, val revision: Long)

fun LibraryState.event(id: String): Event = events.firstOrNull { it.id == id } ?: throw AppException("EVENT_NOT_FOUND")
fun LibraryState.lifecycle(id: String): String = when {
 causes.any { it.kind == "trash" && id in it.members } -> "trash"
 causes.any { it.kind == "archive" && id in it.members } -> "archived"
 else -> "active"
}
fun defaultLibrary(now: Long = System.currentTimeMillis()): LibraryState = LibraryState(
 createdAt = now, updatedAt = now, books = listOf("birthday" to "生日本", "memorial" to "纪念日本",
  "holiday" to "假日本", "goal" to "目标本", "uncategorized" to "未分类").mapIndexed { i, p ->
  Book(name = p.second, builtinKey = p.first, iconKey = p.first, sortRank = i.toLong(), createdAt = now, updatedAt = now)
 })
'''
# END FILE: core/src/main/kotlin/cn/datebook/core/Models.kt


# ============================================================================
# BEGIN FILE: core/src/test/kotlin/cn/datebook/core/CoreTests.kt
# ============================================================================
FILES['core/src/test/kotlin/cn/datebook/core/CoreTests.kt'] = r'''package cn.datebook.core

import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test
import java.time.*

class CoreTests {
 private val clock = Clock.fixed(Instant.parse("2026-10-31T04:00:00Z"), ZoneId.of("Asia/Shanghai"))
 private val lunar = object : LunarPort {
  override fun solar(year: Int, month: Int, day: Int, leapMonth: Boolean, leapPolicy: String, smallMonthPolicy: String): LocalDate? {
   if (leapMonth && leapPolicy == "leap_only" && year != 2028) return null
   val max = YearMonth.of(year, month).lengthOfMonth()
   if (day > max && smallMonthPolicy == "skip") return null
   return LocalDate.of(year, month, minOf(day, max))
  }
  override fun lunarYear(date: LocalDate) = date.year
 }
 private val dates = DateEngine(clock, lunar)
 private fun event(book: String, id: String = newId(), parent: String? = null, day: Int = 1): Event = Event(id = id, bookId = book, parentId = parent, title = id, date = DateSpec(year = 2026, month = 12, day = day))
 private fun input(year: Int? = 2026, month: Int = 10, day: Int = 31, frequency: String = "none", kind: String = "ordinary", mode: String = "down", include: Boolean = false) = DateInput(DateSpec(year = year, month = month, day = day), RecurrenceSpec(frequency), mode, include, kind)
 private fun error(code: String, block: () -> Unit) {
  try { block(); fail("Expected $code") } catch (e: AppException) { assertEquals(code, e.code) }
 }
 private suspend fun failure(code: String, block: suspend () -> Unit) {
  try { block(); fail("Expected $code") } catch (e: AppException) { assertEquals(code, e.code) }
 }
 private fun fixture(): Triple<MemoryRepository, DateBookService, String> {
  val repo = MemoryRepository(defaultLibrary(clock.millis()), clock)
  return Triple(repo, DateBookService(repo, dates, clock), repo.state.value.books.first().id)
 }

 @Test fun birthdayTodayAndTomorrowRollover() {
  val i = input(2000, 10, 31, "yearly", "birthday")
  val today = dates.evaluate(i)
  assertEquals("今天生日", today.label); assertEquals(26, today.age); assertEquals(0L, today.days)
  val next = dates.evaluate(i, Instant.parse("2026-10-31T16:00:00Z"))
  assertEquals(LocalDate.of(2027, 10, 31), next.occurrence!!.date); assertEquals(27, next.age)
 }
 @Test fun birthdayWithoutYearHidesAge() { assertNull(dates.evaluate(input(null, frequency = "yearly", kind = "birthday")).age) }
 @Test fun leapBirthdayFeb28() { assertEquals(LocalDate.of(2027, 2, 28), dates.nextOccurrence(input(2000, 2, 29, "yearly", "birthday"), LocalDate.of(2027, 1, 1))!!.date) }
 @Test fun leapBirthdayMarchPolicy() {
  val i = input(2000, 2, 29, "yearly", "birthday"); assertEquals(LocalDate.of(2027, 3, 1), dates.nextOccurrence(i.copy(date = i.date.copy(feb29Policy = "mar01")), LocalDate.of(2027, 1, 1))!!.date)
 }
 @Test fun monthlyDoesNotLoseOriginalAnchor() {
  val values = dates.occurrences(input(2027, 1, 31, "monthly"), LocalDate.of(2027, 1, 1), LocalDate.of(2027, 3, 31))
  assertEquals(listOf("2027-01-31", "2027-02-28", "2027-03-31"), values.map { it.date.toString() })
 }
 @Test fun weeklyAndEveryNDaysAnchored() {
  assertEquals(LocalDate.of(2026, 11, 7), dates.nextOccurrence(input(frequency = "weekly"), LocalDate.of(2026, 11, 1))!!.date)
  val i = input().copy(repeat = RecurrenceSpec("every_n_days", 3))
  assertEquals(LocalDate.of(2026, 11, 3), dates.nextOccurrence(i, LocalDate.of(2026, 11, 1))!!.date)
 }
 @Test fun untilIsInclusive() {
  val i = input(frequency = "weekly").copy(repeat = RecurrenceSpec("weekly", until = "2026-11-07"))
  assertEquals(2, dates.occurrences(i, LocalDate.of(2026, 10, 1), LocalDate.of(2026, 12, 1)).size)
  assertNull(dates.nextOccurrence(i, LocalDate.of(2026, 11, 8)))
 }
 @Test fun repeatExhaustedRetainsProjection() {
  val i = input(2000, 1, 1, "yearly").copy(repeat = RecurrenceSpec("yearly", until = "2025-01-01"))
  assertTrue(dates.evaluate(i).exhausted)
 }
 @Test fun annualDoesNotOccurBeforeAnchor() {
  assertEquals(LocalDate.of(2028, 10, 31), dates.nextOccurrence(input(2028, frequency = "yearly"), LocalDate.of(2026, 1, 1))!!.date)
 }
 @Test fun positiveIncludesStartOnlyWhenRequested() {
  assertEquals(0L, dates.evaluate(input(mode = "up")).days)
  assertEquals(1L, dates.evaluate(input(mode = "up", include = true)).days)
  assertEquals("尚未开始", dates.evaluate(input(2027, mode = "up")).label)
 }
 @Test fun allDayDstCountsCalendarDaysNot24Hours() {
  val i = input(2026, 3, 9)
  val p = dates.evaluate(i, Instant.parse("2026-03-08T05:00:00Z"), ZoneId.of("America/New_York"))
  assertEquals(1L, p.days)
  assertEquals(Instant.parse("2026-03-09T04:00:00Z"), p.validUntil)
 }
 @Test fun timedDstGapMovesForward() {
  val i = input(2026, 3, 8).copy(date = DateSpec(year = 2026, month = 3, day = 8, allDay = false, localTime = "02:30", zoneId = "America/New_York"))
  assertEquals(Instant.parse("2026-03-08T07:30:00Z"), dates.nextOccurrence(i, LocalDate.of(2026, 3, 8))!!.instant)
 }
 @Test fun timedDstOverlapUsesEarlierOffset() {
  val i = input(2026, 11, 1).copy(date = DateSpec(year = 2026, month = 11, day = 1, allDay = false, localTime = "01:30", zoneId = "America/New_York"))
  assertEquals(Instant.parse("2026-11-01T05:30:00Z"), dates.nextOccurrence(i, LocalDate.of(2026, 11, 1))!!.instant)
 }
 @Test fun timedFutureCeilingAndPastFloor() {
  val i = input().copy(date = DateSpec(year = 2026, month = 10, day = 31, allDay = false, localTime = "13:00", zoneId = "Asia/Shanghai"))
  assertEquals(1L, dates.evaluate(i).days)
  assertEquals("已过不足 1 天", dates.evaluate(i, Instant.parse("2026-10-31T05:30:00Z")).label)
  assertEquals("还有 1 天", dates.evaluate(i, Instant.parse("2026-10-31T04:59:59.999999999Z")).label)
 }
 @Test fun timedProjectionExpiresAtNumericBoundaryNotOnlyMidnight() {
  val i = input(2026, 11, 1).copy(date = DateSpec(year = 2026, month = 11, day = 1, allDay = false, localTime = "13:00", zoneId = "Asia/Shanghai"))
  val p = dates.evaluate(i)
  assertEquals(2L, p.days); assertEquals(Instant.parse("2026-10-31T05:00:00Z"), p.validUntil)
 }
 @Test fun leapFebruaryMonthlyAnchorStaysFebruary29() {
  val datesList = dates.occurrences(input(2024, 2, 29, "monthly"), LocalDate.of(2024, 2, 1), LocalDate.of(2024, 4, 30)).map { it.date }
  assertEquals(listOf(LocalDate.of(2024, 2, 29), LocalDate.of(2024, 3, 29), LocalDate.of(2024, 4, 29)), datesList)
 }
 @Test fun dateInvalidCombinationsRejected() {
  error("DATE_INVALID") { dates.validate(input(2026, 2, 31)) }
  error("DATE_REPEAT_INVALID") { dates.validate(input(frequency = "every_n_days")) }
  error("DATE_KIND_INVALID") { dates.validate(input(kind = "birthday")) }
  error("GOAL_DATE_INVALID") { dates.validate(input(frequency = "yearly", kind = "goal")) }
  error("DATE_TIME_INVALID") { dates.validate(input().copy(date = input().date.copy(localTime = "09:00"))) }
 }
 @Test fun lunarPortLeapAndSmallMonthPolicies() {
  val i = input(2026, 2, 30, "yearly").copy(date = DateSpec(calendar = "lunar", year = 2026, month = 2, day = 30, leapMonth = true, lunarLeapPolicy = "leap_only"))
  // 明确 fake 端口样例，不冒充真实农历权威转换测试。
  val next = dates.nextOccurrence(i.copy(date = i.date.copy(year = null), kind = "birthday"), LocalDate.of(2026, 1, 1))
  assertNotNull(next)
 }
 @Test fun occurrenceWindowBounded() { error("DATE_WINDOW_INVALID") { dates.occurrences(input(), LocalDate.of(1900, 1, 1), LocalDate.of(2100, 1, 1)) } }
 @Test fun extendedGraphemesCountFamilyFlagsCombining() {
  assertEquals(1, graphemeCount("👩‍👩‍👧‍👦")); assertEquals(1, graphemeCount("🇨🇳")); assertEquals(1, graphemeCount("e\u0301")); assertEquals(1, graphemeCount("👍🏽"))
 }
 @Test fun sixtyFamilyEmojiAllowedSixtyOneRejected() = runBlocking {
  val (_, service, book) = fixture()
  val saved = service.saveEvent(event(book).copy(title = "👩‍👩‍👧‍👦".repeat(60)))
  assertEquals(60, graphemeCount(saved.title))
  failure("INPUT_TOO_LONG") { service.saveEvent(event(book).copy(title = "👩‍👩‍👧‍👦".repeat(61))) }
 }
 @Test fun whitespaceAndUnsafeSurrogatesRejected() = runBlocking {
  val (_, service, book) = fixture()
  failure("INPUT_REQUIRED") { service.saveEvent(event(book).copy(title = " \n\t")) }
  failure("INPUT_INVALID") { service.saveEvent(event(book).copy(title = "bad\uD800")) }
  failure("INPUT_REQUIRED") { service.saveEvent(event(book).copy(greeting = "  ")) }
 }
 @Test fun byteLimitIsIndependentOfGraphemeLimit() = runBlocking {
  val (_, service, book) = fixture()
  val title = "a" + "\u0301".repeat(3000)
  assertEquals(1, graphemeCount(title))
  failure("INPUT_BYTE_LIMIT") { service.saveEvent(event(book).copy(title = title)) }
 }
 @Test fun normalAndPreciseReminderModesAccepted() = runBlocking {
  val (_, service, book) = fixture()
  val saved = service.saveEvent(event(book).copy(reminders = listOf(ReminderRule(precisionMode = "precise"))))
  assertEquals("precise", saved.reminders.single().precisionMode)
  failure("REMINDER_INVALID") { service.saveEvent(event(book).copy(reminders = listOf(ReminderRule(precisionMode = "exact")))) }
 }
 @Test fun treeDirectChildrenAndThirdLevelRestriction() = runBlocking {
  val (repo, service, book) = fixture()
  val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id)); val leaf = service.saveEvent(event(book, parent = child.id))
  assertEquals(listOf(child.id), service.directChildren(repo.state.value, root.id).rows.map { it.event.id })
  assertEquals(listOf(leaf.id), service.directChildren(repo.state.value, child.id).rows.map { it.event.id })
  assertTrue(service.directChildren(repo.state.value, leaf.id).rows.isEmpty())
  val revision = repo.state.value.revision
  failure("TREE_DEPTH_EXCEEDED") { service.saveEvent(event(book, parent = leaf.id)) }
  assertEquals(revision, repo.state.value.revision)
 }
 @Test fun missingParentCycleAndCrossBookRejected() = runBlocking {
  val (repo, service, book) = fixture()
  failure("TREE_PARENT_NOT_FOUND") { service.saveEvent(event(book, parent = "missing")) }
  val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id))
  failure("TREE_CYCLE") { service.moveSubtree(root.id, book, child.id) }
  val other = repo.state.value.books[1].id
  failure("TREE_BOOK_MISMATCH") { service.saveEvent(event(other, parent = root.id)) }
 }
 @Test fun parentMustExistEvenReverseOrderedLibrary() {
  val s = defaultLibrary(); val book = s.books.first().id
  error("TREE_PARENT_NOT_FOUND") { LibraryValidator.validate(s.copy(events = listOf(event(book, "child", "missing")))) }
 }
 @Test fun updatesRequireExpectedVersionAndOperationIdIsIdempotent() = runBlocking {
  val (repo, service, book) = fixture(); val raw = event(book)
  val saved = service.saveEvent(raw, operationId = "one")
  assertEquals(saved, service.saveEvent(raw, operationId = "one")); assertEquals(1, repo.state.value.events.size)
  failure("VERSION_CONFLICT") { service.saveEvent(saved.copy(title = "edit")) }
  val edited = service.saveEvent(saved.copy(title = "edit"), saved.version)
  assertEquals(2L, edited.version)
 }
 @Test fun bookNameNfcUniqueProtectedCannotDelete() = runBlocking {
  val (repo, service, _) = fixture(); service.saveBook(Book(name = "Café"))
  failure("BOOK_NAME_CONFLICT") { service.saveBook(Book(name = "cafe\u0301")) }
  failure("BOOK_PROTECTED") { service.deleteBook(repo.state.value.books.first { it.isProtected }.id, true) }
 }
 @Test fun deletingBookMovesToUnclassifiedAndCanTrash() = runBlocking {
  val (repo, service, _) = fixture(); val book = service.saveBook(Book(name = "custom")); val root = service.saveEvent(event(book.id)); val child = service.saveEvent(event(book.id, parent = root.id))
  service.deleteBook(book.id, true)
  val s = repo.state.value
  assertEquals(s.books.first { it.isProtected }.id, s.event(root.id).bookId); assertEquals("trash", s.lifecycle(child.id))
  service.restoreCause(s.causes.single().id); assertEquals("active", repo.state.value.lifecycle(child.id))
 }
 @Test fun copyingSubtreeHasNewIdsAndIndependentGreetingAndNoReminder() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book).copy(greeting = "hello", reminders = listOf(ReminderRule(enabled = true))))
  val child = service.saveEvent(event(book, parent = root.id)); val id = service.copySubtree(root.id)
  val copied = repo.state.value.event(id)
  assertNotEquals(root.id, id); assertEquals("hello", copied.greeting); assertFalse(copied.reminders.single().enabled)
  assertNotEquals(child.id, service.directChildren(repo.state.value, id).rows.single().event.id)
 }
 @Test fun moveWholeTreeKeepsDirectParentRelations() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id)); val dest = repo.state.value.books[1].id
  service.moveSubtree(root.id, dest, null)
  assertEquals(dest, repo.state.value.event(child.id).bookId); assertEquals(root.id, repo.state.value.event(child.id).parentId)
 }
 @Test fun overlappingArchiveCausesRestoreIndependently() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id))
  val childCause = service.setLifecycle(listOf(child.id), "archive"); val rootCause = service.setLifecycle(listOf(root.id, child.id), "archive")
  assertEquals(2, repo.state.value.causes.size)
  service.restoreCause(rootCause); assertEquals("active", repo.state.value.lifecycle(root.id)); assertEquals("archived", repo.state.value.lifecycle(child.id))
  service.restoreCause(childCause); assertEquals("active", repo.state.value.lifecycle(child.id))
 }
 @Test fun trashAndPurgeAreExplicitAndFixHome() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book)); service.saveHome(HomeConfig("fixed", root.id))
  failure("PURGE_NOT_IN_TRASH") { service.purge(listOf(root.id)) }
  service.setLifecycle(listOf(root.id), "trash"); failure("EVENT_IN_TRASH") { service.saveEvent(root.copy(title = "edit"), root.version) }
  service.purge(listOf(root.id)); assertTrue(repo.state.value.events.isEmpty()); assertEquals("auto", repo.state.value.home.heroMode)
 }
 @Test fun goalProgressCountsOnlyEligibleDirectGoals() = runBlocking {
  val (repo, service, book) = fixture()
  fun goal(parent: String? = null) = event(book, parent = parent).copy(kind = "goal", goal = GoalDetail("2026-01-01"))
  val root = service.saveEvent(goal()); val complete = service.saveEvent(goal(root.id)); service.saveEvent(goal(root.id)); val canceled = service.saveEvent(goal(root.id)); val archived = service.saveEvent(goal(root.id)); service.saveEvent(event(book, parent = root.id)); service.saveEvent(goal(complete.id))
  service.setGoalState(complete.id, "completed"); service.setGoalState(canceled.id, "canceled"); service.setLifecycle(listOf(archived.id), "archive")
  assertEquals(1 to 2, service.completionRate(repo.state.value, root.id))
  assertEquals("not_started", repo.state.value.event(root.id).goal!!.state)
 }
 @Test fun goalCompletionReopenPreservesActions() = runBlocking {
  val (repo, service, book) = fixture(); val goal = service.saveEvent(event(book).copy(kind = "goal", goal = GoalDetail("2026-01-01")))
  val action = service.saveAction(ActionRecord(goalEventId = goal.id, date = "2026-10-31", body = "practice", minutes = 0))
  service.setGoalState(goal.id, "completed"); assertNotNull(repo.state.value.event(goal.id).goal!!.completedAt)
  service.setGoalState(goal.id, "in_progress"); assertNull(repo.state.value.event(goal.id).goal!!.completedAt); assertEquals(action.id, repo.state.value.actions.single().id)
  failure("GOAL_HAS_HISTORY") { val e = repo.state.value.event(goal.id); service.saveEvent(e.copy(kind = "ordinary", goal = null), e.version) }
 }
 @Test fun actionsFutureInvalidMinutesAndVersionRejected() = runBlocking {
  val (_, service, book) = fixture(); val goal = service.saveEvent(event(book).copy(kind = "goal", goal = GoalDetail("2026-01-01")))
  failure("ACTION_FUTURE_DATE") { service.saveAction(ActionRecord(goalEventId = goal.id, date = "2026-11-01", body = "future")) }
  failure("INPUT_RANGE") { service.saveAction(ActionRecord(goalEventId = goal.id, date = "2026-10-31", body = "long", minutes = 1441)) }
 }
 @Test fun tagsBatchAndSearchCoverBookGreetingAndTag() = runBlocking {
  val (repo, service, book) = fixture(); val event = service.saveEvent(event(book).copy(greeting = "story")); val tag = service.saveTag(Tag(name = "family")); service.setTags(listOf(event.id), listOf(tag.id))
  assertEquals(event.id, service.search(repo.state.value, "FAMILY").single().id)
  assertEquals(event.id, service.search(repo.state.value, "story").single().id)
  service.setLifecycle(listOf(event.id), "archive"); assertTrue(service.search(repo.state.value, "family").isEmpty()); assertEquals(1, service.search(repo.state.value, "family", "archived").size)
 }
 @Test fun directPaginationRevisionRejectsStaleCursor() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book))
  repeat(21) { service.saveEvent(event(book, parent = root.id)) }
  val first = service.directChildren(repo.state.value, root.id); assertEquals(20, first.rows.size); assertTrue(first.hasMore)
  assertEquals(1, service.directChildren(repo.state.value, root.id, cursor = first.cursor).rows.size)
  service.saveEvent(event(book))
  error("CURSOR_STALE") { service.directChildren(repo.state.value, root.id, cursor = first.cursor) }
 }
 @Test fun goalSameDayProgressAvoidsZeroDivision() = runBlocking {
  val (repo, service, book) = fixture(); val e = service.saveEvent(event(book).copy(kind = "goal", date = DateSpec(year = 2026, month = 10, day = 31), goal = GoalDetail("2026-10-31")))
  assertEquals(1.0, service.timeProgress(repo.state.value, e.id), 0.0); assertNull(service.completionRate(repo.state.value, e.id))
 }
 @Test fun restoreCasEpochAndRollback() = runBlocking {
  val (repo, service, book) = fixture(); val before = repo.state.value
  service.saveEvent(event(book))
  failure("PREVIEW_STALE") { repo.install(before, before.revision, before.epoch) }
  val now = repo.state.value; val installed = repo.install(before, now.revision, now.epoch)
  assertNotEquals(now.epoch, installed.epoch)
  failure("LIBRARY_STALE") { repo.transaction("old", now.epoch) { Change(it, Unit) } }
 }
 @Test fun repositoryFailedChangeDoesNotAdvanceOrLoseData() = runBlocking {
  val (repo, _, _) = fixture(); val before = repo.state.value
  failure("CAPACITY_LIMIT") { repo.transaction { Change(it.copy(books = emptyList()), Unit) } }
  assertEquals(before, repo.state.value)
 }
 @Test fun assetPathRejectsTraversalAndAbsolutePaths() {
  assertTrue(safeAssetPath("assets/a.jpg")); listOf("../a", "/tmp/a", "x/../a", "a\\b", "C:a", "a//b").forEach { assertFalse(safeAssetPath(it)) }
 }
 @Test fun reminderBirthdayDefaultsAndLimit() = runBlocking {
  val (_, service, book) = fixture(); val birthday = service.saveEvent(event(book).copy(kind = "birthday", repeat = RecurrenceSpec("yearly")))
  assertEquals(listOf(7, 0), birthday.reminders.map { it.offsetValue }); assertTrue(birthday.reminders.all { it.enabled && it.localTime == "09:00" })
  failure("REMINDER_LIMIT") { service.saveEvent(event(book).copy(reminders = List(6) { ReminderRule() })) }
 }
 @Test fun eventAndNewTagsCommitAtomically() = runBlocking {
  val (repo, service, book) = fixture(); val before = repo.state.value
  failure("DATE_INVALID") { service.saveEventWithTagNames(event(book).copy(date = DateSpec(year = 2026, month = 2, day = 31)), listOf("newtag")) }
  assertEquals(before, repo.state.value)
  val saved = service.saveEventWithTagNames(event(book), listOf("Work", "work"))
  assertEquals(1, saved.tagIds.size); assertEquals(1, repo.state.value.tags.size)
 }
 @Test fun calendarBatchAllOrNothing() = runBlocking {
  val (repo, service, book) = fixture(); val before = repo.state.value
  failure("DATE_INVALID") { service.saveEventsBatch(listOf(event(book), event(book).copy(date = DateSpec(year = 2026, month = 2, day = 31)))) }
  assertEquals(before, repo.state.value)
  val all = service.saveEventsBatch(listOf(event(book), event(book)))
  assertEquals(2, all); assertEquals(1L, repo.state.value.revision)
 }
 @Test fun validatorLimitsTagsForEveryWritePath() = runBlocking {
  val (repo, service, book) = fixture()
  val tags = List(21) { service.saveTag(Tag(name = "tag$it")) }
  val e = service.saveEvent(event(book))
  val before = repo.state.value
  failure("TAG_LIMIT") { service.setTags(listOf(e.id), tags.map { it.id }) }
  assertEquals(before, repo.state.value)
  error("TAG_LIMIT") { LibraryValidator.validate(before.copy(events = listOf(e.copy(tagIds = tags.map { it.id }))), dates) }
 }
 @Test fun batchMoveRejectsInvalidSecondRootAtomically() = runBlocking {
  val (repo, service, book) = fixture()
  val destRoot = service.saveEvent(event(book)); val destChild = service.saveEvent(event(book, parent = destRoot.id))
  val small = service.saveEvent(event(book)); val deep = service.saveEvent(event(book)); service.saveEvent(event(book, parent = deep.id))
  val before = repo.state.value
  failure("TREE_DEPTH_EXCEEDED") { service.moveSubtrees(listOf(small.id, deep.id), book, destChild.id) }
  assertEquals(before, repo.state.value)
  assertNull(repo.state.value.event(small.id).parentId)
 }
 @Test fun batchMoveDeduplicatesSelectedDescendantsAndCommitsOnce() = runBlocking {
  val (repo, service, book) = fixture()
  val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id)); val other = service.saveEvent(event(book))
  val before = repo.state.value.revision; val destination = repo.state.value.books[1].id
  assertEquals(2, service.moveSubtrees(listOf(root.id, child.id, other.id), destination))
  assertEquals(before + 1, repo.state.value.revision)
  assertEquals(root.id, repo.state.value.event(child.id).parentId)
  assertEquals(destination, repo.state.value.event(child.id).bookId)
 }
}
'''
# END FILE: core/src/test/kotlin/cn/datebook/core/CoreTests.kt


# ============================================================================
# BEGIN FILE: core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt
# ============================================================================
FILES['core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt'] = r'''package cn.datebook.core

import org.junit.Assert.*
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.nio.file.Files
import java.time.Clock
import java.time.LocalDate
import java.time.ZoneOffset
import kotlinx.serialization.json.*
import java.nio.ByteBuffer
import javax.crypto.Cipher
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.PBEKeySpec
import javax.crypto.spec.SecretKeySpec
import java.util.Base64
import java.io.DataOutputStream
import java.util.zip.ZipInputStream
import java.util.zip.ZipOutputStream
import java.util.zip.ZipEntry

class FileCodecTests {
 private val dates=DateEngine(Clock.systemUTC(),object:LunarPort{override fun solar(year:Int,month:Int,day:Int,leapMonth:Boolean,leapPolicy:String,smallMonthPolicy:String):LocalDate?=null;override fun lunarYear(date:LocalDate)=date.year})
 private val codec=FileCodec(dates)
 private fun sample():LibraryState {val state=defaultLibrary(1);val b=state.books.first();val root=Event(bookId=b.id,title="一家人的生日",greeting="=不是公式，'原文\n下一行",date=DateSpec(year=2027,month=1,day=3));val child=root.copy(id=newId(),parentId=root.id,title="子日子");val leaf=child.copy(id=newId(),parentId=child.id,title="第三级");return state.copy(events=listOf(root,child,leaf))}
 private fun fails(code:String?=null,block:()->Unit){try{block();fail("Expected failure")}catch(e:AppException){if(code!=null)assertEquals(code,e.code)}}
 @Test fun textRoundTripKeepsThreeLevelsAndGreeting(){val s=sample();val p=codec.importJson(codec.exportJson(s));assertEquals(3,p.state.events.size);assertEquals(s.events.map{it.parentId},p.state.events.map{it.parentId});assertEquals(s.events.first().greeting,p.state.events.first().greeting)}
 @Test fun goalStartStateSurviveText(){val s=sample();val e=s.events.first().copy(kind="goal",goal=GoalDetail("2026-01-01","completed",5),date=DateSpec(year=2027,month=1,day=3));val p=codec.importJson(codec.exportJson(s.copy(events=listOf(e))));assertEquals(e.goal,p.state.events.single().goal)}
 @Test fun photoIsExplicitlyOmittedFromText(){val s=sample();val bytes=codec.exportJson(s);val text=String(bytes).replace("\"backgroundFallback\":\"none\"","\"backgroundFallback\":\"photo_omitted\"");assertEquals("gradient",codec.importJson(text.toByteArray()).state.events.first().appearance.backgroundKind)}
 @Test fun unknownFieldRejected(){val bytes=codec.exportJson(sample());fails("FILE_SCHEMA_INVALID"){codec.importJson(String(bytes).replaceFirst("{","{\"surprise\":1,").toByteArray())}}
 @Test fun duplicateKeyRejected(){val bytes=codec.exportJson(sample());fails("FILE_DUPLICATE_KEY"){codec.importJson(String(bytes).replaceFirst("{","{\"version\":1,").toByteArray())}}
 @Test fun malformedUtf8Rejected(){fails("FILE_ENCODING_INVALID"){codec.importJson(byteArrayOf(0xC3.toByte(),0x28))}}
 @Test fun csvReversibleFormulaAndQuotes(){val s=sample();for(title in listOf("=1+1","'原引号","+标题","@文字","普通,逗号","多行\n标题")){val e=s.events.first().copy(title=title,parentId=null);val x=s.copy(events=listOf(e));val p=codec.importCsv(codec.exportCsv(x,setOf(e.id)));assertTrue(p.issues.toString(),p.issues.isEmpty());assertEquals(title,p.state.events.single().title);assertEquals(e.greeting,p.state.events.single().greeting)}}
 @Test fun legacyCsvDoesNotUnescape(){val bytes="title,date,calendar,type,repeat,message\r\n'=原文,2027-01-01,gregorian,ordinary,none,'=保留\r\n".toByteArray();assertEquals("'=原文",codec.importCsv(bytes).state.events.single().title)}
 @Test fun invalidCsvRowsReportOriginalLine(){val p=codec.importCsv("title,date,calendar,type,repeat,message\n好日子,2027-01-01,gregorian,ordinary,none,好\n坏日子,not-a-date,gregorian,ordinary,none,错\n".toByteArray());assertEquals(1,p.state.events.size);assertEquals(3,p.issues.single().line)}
 @Test fun importDeduplicatesAcrossBatches(){val p=codec.importJson(codec.exportJson(sample()));val one=codec.merge(defaultLibrary(),p);val two=codec.merge(one,p);assertEquals(one,two);assertEquals(3,two.events.size)}
 @Test fun plainBackupRoundTripAndNoDeviceEpoch(){val root=Files.createTempDirectory("datebook-codec-").toFile();try{val s=sample();val bytes=ByteArrayOutputStream();codec.writeBackup(s,root,bytes,null);assertTrue(String(bytes.toByteArray().take(8).toByteArray())=="DAYBOOK1");val p=codec.readBackup(ByteArrayInputStream(bytes.toByteArray()),root.resolve("restored"),null);assertEquals(s.events,p.state.events);assertNotEquals(s.epoch,p.state.epoch);assertFalse(p.encrypted)}finally{root.deleteRecursively()}}
 @Test fun authenticatedBackupRejectsWrongPasswordAndTamper(){val root=Files.createTempDirectory("datebook-auth-").toFile();try{val bytes=ByteArrayOutputStream();val password="中文密码🔑测试é".toCharArray();codec.writeBackup(sample(),root,bytes,password);val p=codec.readBackup(ByteArrayInputStream(bytes.toByteArray()),root.resolve("ok"),password);assertTrue(p.encrypted);fails("BACKUP_AUTH_FAILED"){codec.readBackup(ByteArrayInputStream(bytes.toByteArray()),root.resolve("bad"),"错误密码123456".toCharArray())};val changed=bytes.toByteArray();changed[changed.lastIndex]=(changed.last().toInt()xor 1).toByte();fails("BACKUP_AUTH_FAILED"){codec.readBackup(ByteArrayInputStream(changed),root.resolve("tampered"),password)};assertFalse(root.resolve("bad").exists());assertFalse(root.resolve("tampered").exists())}finally{root.deleteRecursively()}}
 @Test fun selectedSubtreeDoesNotLeakAncestors(){val s=sample();val p=codec.importJson(codec.exportJson(s,s.events.drop(1).map{it.id}.toSet()));assertNull(p.state.events.first().parentId);assertEquals(p.state.events.first().id,p.state.events.last().parentId)}
 @Test fun csvRefusesSilentLossOfHierarchy(){val s=sample();fails("CSV_LOSS_REQUIRES_JSON"){codec.exportCsv(s,setOf(s.events.first().id))}}
 @Test fun unicodePasswordContainerInteroperatesWithIndependentJcaPbkdf2(){val root=Files.createTempDirectory("datebook-vector-").toFile();try{val out=ByteArrayOutputStream();val password="中文密码🔑é测试".toCharArray();codec.writeBackup(sample(),root,out,password);val bytes=out.toByteArray();val length=ByteBuffer.wrap(bytes,9,4).int;val header=Json.parseToJsonElement(String(bytes,13,length)).jsonObject;val salt=Base64.getDecoder().decode(header.getValue("salt").jsonPrimitive.content);val nonce=Base64.getDecoder().decode(header.getValue("nonce").jsonPrimitive.content);val spec=PBEKeySpec(password,salt,600000,256);val key=try{SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).encoded}finally{spec.clearPassword()};try{val cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.DECRYPT_MODE,SecretKeySpec(key,"AES"),GCMParameterSpec(128,nonce));cipher.updateAAD(bytes.copyOfRange(0,13+length));val plain=cipher.doFinal(bytes.copyOfRange(13+length,bytes.size));assertEquals('P'.code,plain[0].toInt());assertEquals('K'.code,plain[1].toInt())}finally{key.fill(0)}}finally{root.deleteRecursively()}}
 @Test fun backupPersistsImportHistoryUsingWireNames(){val root=Files.createTempDirectory("datebook-origin-").toFile();try{val source=codec.importJson(codec.exportJson(sample()));val state=codec.merge(defaultLibrary(),source);val out=ByteArrayOutputStream();codec.writeBackup(state,root,out,null);val restored=codec.readBackup(ByteArrayInputStream(out.toByteArray()),root.resolve("restore"),null);assertEquals("json",restored.state.imports.single().format);assertEquals(state,codec.merge(state,source));assertEquals(state.imports,restored.state.imports)}finally{root.deleteRecursively()}}
 @Test fun csvMixedEscapeModeRejected(){fails("CSV_ESCAPE_INVALID"){codec.importCsv("schema_version,escape_mode,title,date,calendar,type,repeat,message\n1,apostrophe_v1,甲,2027-01-01,gregorian,ordinary,none,\n1,none,乙,2027-01-01,gregorian,ordinary,none,".toByteArray())}}
 private fun plainContainer(entries:Map<String,ByteArray>):ByteArray{val payload=ByteArrayOutputStream();ZipOutputStream(payload).use{z->entries.forEach{(path,bytes)->z.putNextEntry(ZipEntry(path));z.write(bytes);z.closeEntry()}};val header="""{"containerVersion":1,"suite":"plain","salt":null,"nonce":null,"iterations":null,"payloadFormat":"zip"}""".toByteArray();return ByteArrayOutputStream().also{o->DataOutputStream(o).apply{write("DAYBOOK1".toByteArray());writeByte(0);writeInt(header.size);write(header);write(payload.toByteArray())}}.toByteArray()}
 @Test fun backupRejectsPathTraversalWithoutWritingOutsideStaging(){val root=Files.createTempDirectory("datebook-path-").toFile();try{fails("BACKUP_PATH_INVALID"){codec.readBackup(ByteArrayInputStream(plainContainer(mapOf("../escaped.txt" to "bad".toByteArray()))),root.resolve("staging"),null)};assertFalse(root.resolve("escaped.txt").exists());assertFalse(root.resolve("staging").exists())}finally{root.deleteRecursively()}}
 @Test fun checksumMismatchLeavesNoCandidate(){val root=Files.createTempDirectory("datebook-checksum-").toFile();try{val out=ByteArrayOutputStream();codec.writeBackup(sample(),root,out,null);val bytes=out.toByteArray();val h=ByteBuffer.wrap(bytes,9,4).int;val entries=linkedMapOf<String,ByteArray>();ZipInputStream(ByteArrayInputStream(bytes,13+h,bytes.size-13-h)).use{z->while(true){val e=z.nextEntry?:break;entries[e.name]=z.readBytes()}};entries["library.json"]=entries.getValue("library.json")+byteArrayOf(32);fails("BACKUP_CHECKSUM_INVALID"){codec.readBackup(ByteArrayInputStream(plainContainer(entries)),root.resolve("staging"),null)};assertFalse(root.resolve("staging").exists())}finally{root.deleteRecursively()}}
 @Test fun fullBackupKeepsPhotoBytesAndUnusedTags(){val root=Files.createTempDirectory("datebook-photo-").toFile();try{val png=Base64.getDecoder().decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aH7sAAAAASUVORK5CYII=");val hash=FileCodec.sha256(png);val a=Asset(sha256=hash,relativePath="assets/$hash.png",mimeType="image/png",bytes=png.size.toLong(),width=1,height=1);root.resolve(a.relativePath).also{it.parentFile.mkdirs();it.writeBytes(png)};val s=sample();val photo=s.events.first().copy(appearance=Appearance(backgroundKind="photo",assetId=a.id));val source=s.copy(events=listOf(photo),assets=listOf(a),tags=listOf(Tag(name="未使用标签")));val out=ByteArrayOutputStream();codec.writeBackup(source,root,out,null);val p=codec.readBackup(ByteArrayInputStream(out.toByteArray()),root.resolve("staging"),null);assertArrayEquals(png,p.assetRoot.resolve(a.relativePath).readBytes());assertEquals(source.tags,p.state.tags);val text=String(codec.exportJson(source));assertTrue(text.contains("photo_omitted"));assertFalse(text.contains("assetRef"));assertEquals("gradient",codec.importJson(text.toByteArray()).state.events.single().appearance.backgroundKind)}finally{root.deleteRecursively()}}
 @Test fun fullRestorePausesReminderRules(){val root=Files.createTempDirectory("datebook-reminder-").toFile();try{val s=sample();val e=s.events.first().copy(reminders=listOf(ReminderRule(enabled=true)));val out=ByteArrayOutputStream();codec.writeBackup(s.copy(events=listOf(e)),root,out,null);val p=codec.readBackup(ByteArrayInputStream(out.toByteArray()),root.resolve("staging"),null);assertFalse(p.state.events.single().reminders.single().enabled)}finally{root.deleteRecursively()}}
 @Test fun wrongJsonPrimitiveTypeRejected(){val text=String(codec.exportJson(sample())).replaceFirst("\"title\":\"一家人的生日\"","\"title\":true");fails("FILE_SCHEMA_INVALID"){codec.importJson(text.toByteArray())}}
 @Test fun emptyBookAndUnusedTagBackupMergeIsIdempotent(){val s=defaultLibrary();val source=s.copy(books=s.books+Book(name="空的旅行本"),tags=listOf(Tag(name="暂未使用")));val p=ImportPreview(source,newId(),"a".repeat(64),"backup");val first=codec.merge(defaultLibrary(),p);assertTrue(first.books.any{it.name=="空的旅行本"});assertEquals("暂未使用",first.tags.single().name);assertEquals(first,codec.merge(first,p))}
 @Test fun repeatedSourceWithNewChildMapsToPreviouslyImportedBook(){val s=sample();val custom=Book(name="旅行本");val root=s.events.first().copy(bookId=custom.id);val p=codec.importJson(codec.exportJson(s.copy(books=s.books+custom,events=listOf(root))));val first=codec.merge(defaultLibrary(),p);val child=Event(bookId=custom.id,parentId=root.id,title="后来增加的计划",date=DateSpec(year=2028,month=1,day=1));val extended=p.copy(state=p.state.copy(events=p.state.events+child),fileSha256="b".repeat(64));val second=codec.merge(first,extended);val added=second.events.first{it.title==child.title};val parent=second.event(added.parentId!!);assertEquals(parent.bookId,added.bookId);assertEquals(2,second.events.size)}
}
'''
# END FILE: core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt


# ============================================================================
# BEGIN FILE: docs/file_contracts_v1.schema.json
# ============================================================================
FILES['docs/file_contracts_v1.schema.json'] = r'''{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:daybook:contracts:v1",
  "title": "Daybook local file contracts; TD revision 1.1",
  "description": "Four entry points; choose the relevant $defs. Semantic validation in TD is mandatory. No network services. Unknown core fields rejected; future changes require a format version. x-graphemeMax / x-maxUtf8Bytes are enforced by application validators, not by JSON Schema alone.",
  "oneOf": [
    {
      "$ref": "#/$defs/EventsExport"
    },
    {
      "$ref": "#/$defs/Manifest"
    },
    {
      "$ref": "#/$defs/BackupSnapshot"
    },
    {
      "$ref": "#/$defs/ContainerHeader"
    }
  ],
  "$defs": {
    "DateSpec": {
      "type": "object",
      "properties": {
        "calendar": {
          "enum": [
            "gregorian",
            "lunar"
          ]
        },
        "year": {
          "anyOf": [
            {
              "type": "integer",
              "minimum": 1900,
              "maximum": 2100
            },
            {
              "type": "null"
            }
          ]
        },
        "month": {
          "type": "integer",
          "minimum": 1,
          "maximum": 12
        },
        "day": {
          "type": "integer",
          "minimum": 1,
          "maximum": 31
        },
        "leapMonth": {
          "type": "boolean"
        },
        "allDay": {
          "type": "boolean"
        },
        "localTime": {
          "anyOf": [
            {
              "type": "string",
              "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
            },
            {
              "type": "null"
            }
          ]
        },
        "zoneId": {
          "anyOf": [
            {
              "type": "string",
              "maxLength": 128
            },
            {
              "type": "null"
            }
          ]
        },
        "feb29Policy": {
          "enum": [
            "feb28",
            "mar01"
          ]
        },
        "lunarLeapPolicy": {
          "enum": [
            "normal_fallback",
            "leap_only"
          ]
        },
        "lunarSmallMonthPolicy": {
          "enum": [
            "month_end",
            "skip"
          ]
        },
        "calendarEngineVersion": {
          "type": "string",
          "maxLength": 64
        }
      },
      "required": [
        "calendar",
        "year",
        "month",
        "day",
        "leapMonth",
        "allDay",
        "localTime",
        "zoneId",
        "feb29Policy",
        "lunarLeapPolicy",
        "lunarSmallMonthPolicy",
        "calendarEngineVersion"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "allDay": {
                "const": true
              }
            }
          },
          "then": {
            "properties": {
              "localTime": {
                "type": "null"
              },
              "zoneId": {
                "type": "null"
              }
            }
          },
          "else": {
            "properties": {
              "localTime": {
                "type": "string"
              },
              "zoneId": {
                "type": "string",
                "minLength": 1
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "calendar": {
                "const": "gregorian"
              }
            }
          },
          "then": {
            "properties": {
              "leapMonth": {
                "const": false
              }
            }
          },
          "else": {
            "properties": {
              "allDay": {
                "const": true
              }
            }
          }
        }
      ]
    },
    "Recurrence": {
      "type": "object",
      "properties": {
        "frequency": {
          "enum": [
            "none",
            "yearly",
            "monthly",
            "weekly",
            "every_n_days"
          ]
        },
        "intervalDays": {
          "anyOf": [
            {
              "type": "integer",
              "minimum": 1,
              "maximum": 365
            },
            {
              "type": "null"
            }
          ]
        },
        "until": {
          "anyOf": [
            {
              "type": "string",
              "format": "date"
            },
            {
              "type": "null"
            }
          ]
        }
      },
      "required": [
        "frequency",
        "intervalDays",
        "until"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "frequency": {
                "const": "every_n_days"
              }
            }
          },
          "then": {
            "properties": {
              "intervalDays": {
                "type": "integer"
              }
            }
          },
          "else": {
            "properties": {
              "intervalDays": {
                "type": "null"
              }
            }
          }
        }
      ]
    },
    "GoalDetail": {
      "type": "object",
      "properties": {
        "startDate": {
          "type": "string",
          "format": "date"
        },
        "state": {
          "enum": [
            "not_started",
            "in_progress",
            "completed",
            "canceled"
          ]
        },
        "completedAt": {
          "anyOf": [
            {
              "type": "integer",
              "minimum": 0
            },
            {
              "type": "null"
            }
          ]
        },
        "includeInParent": {
          "type": "boolean"
        }
      },
      "required": [
        "startDate",
        "state",
        "completedAt",
        "includeInParent"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "state": {
                "const": "completed"
              }
            }
          },
          "then": {
            "properties": {
              "completedAt": {
                "type": "integer"
              }
            }
          },
          "else": {
            "properties": {
              "completedAt": {
                "type": "null"
              }
            }
          }
        }
      ]
    },
    "TextAppearance": {
      "type": "object",
      "properties": {
        "backgroundKind": {
          "enum": [
            "gradient",
            "solid"
          ]
        },
        "presetKey": {
          "type": "string",
          "maxLength": 64
        },
        "solidArgb": {
          "type": "integer"
        },
        "textColorMode": {
          "enum": [
            "auto",
            "light",
            "dark"
          ]
        },
        "fontKey": {
          "type": "string",
          "maxLength": 64
        }
      },
      "required": [
        "backgroundKind",
        "presetKey",
        "textColorMode",
        "fontKey"
      ],
      "additionalProperties": false
    },
    "FullAppearance": {
      "type": "object",
      "properties": {
        "backgroundKind": {
          "enum": [
            "gradient",
            "solid",
            "photo"
          ]
        },
        "presetKey": {
          "type": "string",
          "maxLength": 64
        },
        "solidArgb": {
          "type": "integer"
        },
        "textColorMode": {
          "enum": [
            "auto",
            "light",
            "dark"
          ]
        },
        "fontKey": {
          "type": "string",
          "maxLength": 64
        },
        "assetRef": {
          "anyOf": [
            {
              "type": "string",
              "minLength": 1,
              "maxLength": 128
            },
            {
              "type": "null"
            }
          ]
        },
        "focusX": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "focusY": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "dimAmount": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      },
      "required": [
        "backgroundKind",
        "presetKey",
        "textColorMode",
        "fontKey"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "backgroundKind": {
                "const": "photo"
              }
            }
          },
          "then": {
            "required": [
              "assetRef",
              "focusX",
              "focusY",
              "dimAmount"
            ],
            "properties": {
              "assetRef": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              }
            }
          }
        }
      ]
    },
    "TextEvent": {
      "type": "object",
      "properties": {
        "ref": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "bookRef": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "parentRef": {
          "anyOf": [
            {
              "type": "string",
              "minLength": 1,
              "maxLength": 128
            },
            {
              "type": "null"
            }
          ]
        },
        "title": {
          "type": "string",
          "x-graphemeMax": 60,
          "x-maxUtf8Bytes": 4096,
          "minLength": 1
        },
        "kind": {
          "enum": [
            "birthday",
            "memorial",
            "holiday",
            "goal",
            "ordinary"
          ]
        },
        "countMode": {
          "enum": [
            "down",
            "up"
          ]
        },
        "includeStartDay": {
          "type": "boolean"
        },
        "greeting": {
          "type": "string",
          "x-graphemeMax": 2000,
          "x-maxUtf8Bytes": 65536
        },
        "homeVisible": {
          "type": "boolean"
        },
        "pinned": {
          "type": "boolean"
        },
        "sortRank": {
          "type": "integer"
        },
        "date": {
          "$ref": "#/$defs/DateSpec"
        },
        "repeat": {
          "$ref": "#/$defs/Recurrence"
        },
        "appearance": {
          "$ref": "#/$defs/TextAppearance"
        },
        "goal": {
          "anyOf": [
            {
              "$ref": "#/$defs/GoalDetail"
            },
            {
              "type": "null"
            }
          ]
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string",
            "x-graphemeMax": 40,
            "x-maxUtf8Bytes": 2048
          },
          "uniqueItems": true,
          "maxItems": 20
        },
        "backgroundFallback": {
          "enum": [
            "none",
            "photo_omitted"
          ]
        }
      },
      "required": [
        "ref",
        "bookRef",
        "parentRef",
        "title",
        "kind",
        "countMode",
        "includeStartDay",
        "greeting",
        "homeVisible",
        "pinned",
        "sortRank",
        "date",
        "repeat",
        "appearance",
        "goal",
        "tags",
        "backgroundFallback"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "kind": {
                "const": "goal"
              }
            }
          },
          "then": {
            "properties": {
              "goal": {
                "$ref": "#/$defs/GoalDetail"
              },
              "repeat": {
                "properties": {
                  "frequency": {
                    "const": "none"
                  }
                }
              },
              "date": {
                "properties": {
                  "year": {
                    "type": "integer"
                  },
                  "calendar": {
                    "const": "gregorian"
                  },
                  "allDay": {
                    "const": true
                  }
                }
              }
            }
          },
          "else": {
            "properties": {
              "goal": {
                "type": "null"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "kind": {
                "const": "birthday"
              }
            }
          },
          "then": {
            "properties": {
              "date": {
                "properties": {
                  "allDay": {
                    "const": true
                  }
                }
              },
              "repeat": {
                "properties": {
                  "frequency": {
                    "const": "yearly"
                  }
                }
              },
              "countMode": {
                "const": "down"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "date": {
                "properties": {
                  "year": {
                    "type": "null"
                  }
                }
              }
            }
          },
          "then": {
            "properties": {
              "kind": {
                "const": "birthday"
              }
            }
          }
        }
      ]
    },
    "FullEvent": {
      "type": "object",
      "properties": {
        "ref": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "bookRef": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "parentRef": {
          "anyOf": [
            {
              "type": "string",
              "minLength": 1,
              "maxLength": 128
            },
            {
              "type": "null"
            }
          ]
        },
        "title": {
          "type": "string",
          "x-graphemeMax": 60,
          "x-maxUtf8Bytes": 4096,
          "minLength": 1
        },
        "kind": {
          "enum": [
            "birthday",
            "memorial",
            "holiday",
            "goal",
            "ordinary"
          ]
        },
        "countMode": {
          "enum": [
            "down",
            "up"
          ]
        },
        "includeStartDay": {
          "type": "boolean"
        },
        "greeting": {
          "type": "string",
          "x-graphemeMax": 2000,
          "x-maxUtf8Bytes": 65536
        },
        "homeVisible": {
          "type": "boolean"
        },
        "pinned": {
          "type": "boolean"
        },
        "sortRank": {
          "type": "integer"
        },
        "date": {
          "$ref": "#/$defs/DateSpec"
        },
        "repeat": {
          "$ref": "#/$defs/Recurrence"
        },
        "appearance": {
          "$ref": "#/$defs/FullAppearance"
        },
        "goal": {
          "anyOf": [
            {
              "$ref": "#/$defs/GoalDetail"
            },
            {
              "type": "null"
            }
          ]
        },
        "createdAt": {
          "type": "integer",
          "minimum": 0
        },
        "updatedAt": {
          "type": "integer",
          "minimum": 0
        },
        "version": {
          "type": "integer",
          "minimum": 1
        },
        "reminders": {
          "type": "array",
          "maxItems": 5,
          "items": {
            "$ref": "#/$defs/ReminderRule"
          }
        },
        "tagRefs": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/Ref"
          },
          "uniqueItems": true,
          "maxItems": 20
        }
      },
      "required": [
        "ref",
        "bookRef",
        "parentRef",
        "title",
        "kind",
        "countMode",
        "includeStartDay",
        "greeting",
        "homeVisible",
        "pinned",
        "sortRank",
        "date",
        "repeat",
        "appearance",
        "goal",
        "tagRefs",
        "createdAt",
        "updatedAt",
        "version",
        "reminders"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "kind": {
                "const": "goal"
              }
            }
          },
          "then": {
            "properties": {
              "goal": {
                "$ref": "#/$defs/GoalDetail"
              },
              "repeat": {
                "properties": {
                  "frequency": {
                    "const": "none"
                  }
                }
              },
              "date": {
                "properties": {
                  "year": {
                    "type": "integer"
                  },
                  "calendar": {
                    "const": "gregorian"
                  },
                  "allDay": {
                    "const": true
                  }
                }
              }
            }
          },
          "else": {
            "properties": {
              "goal": {
                "type": "null"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "kind": {
                "const": "birthday"
              }
            }
          },
          "then": {
            "properties": {
              "date": {
                "properties": {
                  "allDay": {
                    "const": true
                  }
                }
              },
              "repeat": {
                "properties": {
                  "frequency": {
                    "const": "yearly"
                  }
                }
              },
              "countMode": {
                "const": "down"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "date": {
                "properties": {
                  "year": {
                    "type": "null"
                  }
                }
              }
            }
          },
          "then": {
            "properties": {
              "kind": {
                "const": "birthday"
              }
            }
          }
        }
      ]
    },
    "Book": {
      "type": "object",
      "properties": {
        "ref": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "name": {
          "type": "string",
          "x-graphemeMax": 30,
          "x-maxUtf8Bytes": 2048,
          "minLength": 1
        },
        "builtinKey": {
          "anyOf": [
            {
              "enum": [
                "birthday",
                "memorial",
                "holiday",
                "goal",
                "uncategorized"
              ]
            },
            {
              "type": "null"
            }
          ]
        },
        "iconKey": {
          "type": "string",
          "maxLength": 64
        },
        "colorArgb": {
          "type": "integer"
        },
        "sortRank": {
          "type": "integer"
        }
      },
      "required": [
        "ref",
        "name",
        "builtinKey",
        "iconKey",
        "colorArgb",
        "sortRank"
      ],
      "additionalProperties": false
    },
    "FullBook": {
      "type": "object",
      "properties": {
        "ref": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "name": {
          "type": "string",
          "x-graphemeMax": 30,
          "x-maxUtf8Bytes": 2048,
          "minLength": 1
        },
        "builtinKey": {
          "anyOf": [
            {
              "enum": [
                "birthday",
                "memorial",
                "holiday",
                "goal",
                "uncategorized"
              ]
            },
            {
              "type": "null"
            }
          ]
        },
        "iconKey": {
          "type": "string",
          "maxLength": 64
        },
        "colorArgb": {
          "type": "integer"
        },
        "sortRank": {
          "type": "integer"
        },
        "coverAssetRef": {
          "anyOf": [
            {
              "type": "string",
              "minLength": 1,
              "maxLength": 128
            },
            {
              "type": "null"
            }
          ]
        },
        "createdAt": {
          "type": "integer",
          "minimum": 0
        },
        "updatedAt": {
          "type": "integer",
          "minimum": 0
        },
        "version": {
          "type": "integer",
          "minimum": 1
        }
      },
      "required": [
        "ref",
        "name",
        "builtinKey",
        "iconKey",
        "colorArgb",
        "sortRank",
        "coverAssetRef",
        "createdAt",
        "updatedAt",
        "version"
      ],
      "additionalProperties": false
    },
    "ReminderRule": {
      "type": "object",
      "properties": {
        "ref": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "enabled": {
          "type": "boolean"
        },
        "offsetUnit": {
          "enum": [
            "days",
            "hours",
            "minutes"
          ]
        },
        "offsetValue": {
          "type": "integer",
          "minimum": 0,
          "maximum": 525600
        },
        "localTime": {
          "anyOf": [
            {
              "type": "string",
              "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
            },
            {
              "type": "null"
            }
          ]
        },
        "precisionMode": {
          "enum": [
            "normal",
            "precise"
          ]
        },
        "version": {
          "type": "integer",
          "minimum": 1
        }
      },
      "required": [
        "ref",
        "enabled",
        "offsetUnit",
        "offsetValue",
        "localTime",
        "precisionMode",
        "version"
      ],
      "additionalProperties": false
    },
    "EventsExport": {
      "type": "object",
      "properties": {
        "format": {
          "const": "countdown_events"
        },
        "version": {
          "const": 1
        },
        "exportId": {
          "type": "string",
          "format": "uuid"
        },
        "exportedAt": {
          "type": "string",
          "format": "date-time"
        },
        "books": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/Book"
          },
          "maxItems": 200
        },
        "events": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/TextEvent"
          },
          "maxItems": 2000
        }
      },
      "required": [
        "format",
        "version",
        "exportId",
        "exportedAt",
        "books",
        "events"
      ],
      "additionalProperties": false
    },
    "ContainerHeader": {
      "type": "object",
      "properties": {
        "containerVersion": {
          "const": 1
        },
        "suite": {
          "enum": [
            "plain",
            "pbkdf2-sha256-aes256gcm"
          ]
        },
        "salt": {
          "anyOf": [
            {
              "type": "string",
              "contentEncoding": "base64"
            },
            {
              "type": "null"
            }
          ]
        },
        "nonce": {
          "anyOf": [
            {
              "type": "string",
              "contentEncoding": "base64"
            },
            {
              "type": "null"
            }
          ]
        },
        "iterations": {
          "anyOf": [
            {
              "const": 600000
            },
            {
              "type": "null"
            }
          ]
        },
        "payloadFormat": {
          "const": "zip"
        }
      },
      "required": [
        "containerVersion",
        "suite",
        "salt",
        "nonce",
        "iterations",
        "payloadFormat"
      ],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "suite": {
                "const": "plain"
              }
            }
          },
          "then": {
            "properties": {
              "salt": {
                "type": "null"
              },
              "nonce": {
                "type": "null"
              },
              "iterations": {
                "type": "null"
              }
            }
          },
          "else": {
            "properties": {
              "salt": {
                "type": "string",
                "pattern": "^[A-Za-z0-9+/]{22}==$"
              },
              "nonce": {
                "type": "string",
                "pattern": "^[A-Za-z0-9+/]{16}$"
              },
              "iterations": {
                "const": 600000
              }
            }
          }
        }
      ]
    },
    "Manifest": {
      "type": "object",
      "properties": {
        "format": {
          "const": "daybook_manifest"
        },
        "version": {
          "const": 1
        },
        "backupId": {
          "type": "string",
          "format": "uuid"
        },
        "createdAt": {
          "type": "string",
          "format": "date-time"
        },
        "contentRevision": {
          "type": "integer",
          "minimum": 0
        },
        "snapshotSchemaVersion": {
          "const": 1
        },
        "counts": {
          "type": "object",
          "properties": {
            "books": {
              "type": "integer",
              "minimum": 0,
              "maximum": 200
            },
            "events": {
              "type": "integer",
              "minimum": 0,
              "maximum": 2000
            },
            "actions": {
              "type": "integer",
              "minimum": 0,
              "maximum": 10000
            },
            "assets": {
              "type": "integer",
              "minimum": 0,
              "maximum": 19998
            }
          },
          "required": [
            "books",
            "events",
            "actions",
            "assets"
          ],
          "additionalProperties": false
        },
        "files": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "path": {
                "type": "string",
                "pattern": "^(library\\.json|assets/[0-9a-f]{64}\\.(jpg|png|webp))$"
              },
              "bytes": {
                "type": "integer",
                "minimum": 0,
                "maximum": 536870912
              },
              "sha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$"
              }
            },
            "required": [
              "path",
              "bytes",
              "sha256"
            ],
            "additionalProperties": false
          },
          "maxItems": 19999
        }
      },
      "required": [
        "format",
        "version",
        "backupId",
        "createdAt",
        "contentRevision",
        "snapshotSchemaVersion",
        "counts",
        "files"
      ],
      "additionalProperties": false
    },
    "BackupSnapshot": {
      "type": "object",
      "properties": {
        "format": {
          "const": "daybook_library"
        },
        "version": {
          "const": 1
        },
        "library": {
          "type": "object",
          "properties": {
            "id": {
              "type": "string",
              "format": "uuid"
            },
            "name": {
              "type": "string",
              "maxLength": 120
            },
            "contentRevision": {
              "type": "integer",
              "minimum": 0
            },
            "createdAt": {
              "type": "integer",
              "minimum": 0
            },
            "updatedAt": {
              "type": "integer",
              "minimum": 0
            }
          },
          "required": [
            "id",
            "name",
            "contentRevision",
            "createdAt",
            "updatedAt"
          ],
          "additionalProperties": false
        },
        "books": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/FullBook"
          },
          "maxItems": 200
        },
        "events": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/FullEvent"
          },
          "maxItems": 2000
        },
        "assets": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "ref": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "sha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$"
              },
              "path": {
                "type": "string",
                "pattern": "^assets/[0-9a-f]{64}\\.(jpg|png|webp)$"
              },
              "mimeType": {
                "enum": [
                  "image/jpeg",
                  "image/png",
                  "image/webp"
                ]
              },
              "bytes": {
                "type": "integer",
                "minimum": 1,
                "maximum": 26214400
              },
              "width": {
                "type": "integer",
                "minimum": 1
              },
              "height": {
                "type": "integer",
                "minimum": 1
              },
              "createdAt": {
                "type": "integer",
                "minimum": 0
              }
            },
            "required": [
              "ref",
              "sha256",
              "path",
              "mimeType",
              "bytes",
              "width",
              "height",
              "createdAt"
            ],
            "additionalProperties": false
          },
          "maxItems": 19998
        },
        "actions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "ref": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "goalRef": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "date": {
                "type": "string",
                "format": "date"
              },
              "body": {
                "type": "string",
                "x-graphemeMax": 1000,
                "x-maxUtf8Bytes": 32768,
                "minLength": 1
              },
              "minutes": {
                "anyOf": [
                  {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1440
                  },
                  {
                    "type": "null"
                  }
                ]
              },
              "createdAt": {
                "type": "integer",
                "minimum": 0
              },
              "updatedAt": {
                "type": "integer",
                "minimum": 0
              },
              "version": {
                "type": "integer",
                "minimum": 1
              }
            },
            "required": [
              "ref",
              "goalRef",
              "date",
              "body",
              "minutes",
              "createdAt",
              "updatedAt",
              "version"
            ],
            "additionalProperties": false
          },
          "maxItems": 10000
        },
        "lifecycleCauses": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "ref": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "kind": {
                "enum": [
                  "archive",
                  "trash"
                ]
              },
              "sourceEventRef": {
                "anyOf": [
                  {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 128
                  },
                  {
                    "type": "null"
                  }
                ]
              },
              "sourceBookRef": {
                "anyOf": [
                  {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 128
                  },
                  {
                    "type": "null"
                  }
                ]
              },
              "createdAt": {
                "type": "integer",
                "minimum": 0
              },
              "purgeAfter": {
                "anyOf": [
                  {
                    "type": "integer",
                    "minimum": 0
                  },
                  {
                    "type": "null"
                  }
                ]
              },
              "members": {
                "type": "array",
                "items": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 128
                },
                "maxItems": 2000
              }
            },
            "required": [
              "ref",
              "kind",
              "sourceEventRef",
              "sourceBookRef",
              "createdAt",
              "purgeAfter",
              "members"
            ],
            "additionalProperties": false
          },
          "maxItems": 200000
        },
        "home": {
          "type": "object",
          "properties": {
            "heroMode": {
              "enum": [
                "auto",
                "fixed"
              ]
            },
            "fixedEventRef": {
              "anyOf": [
                {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 128
                },
                {
                  "type": "null"
                }
              ]
            },
            "sortMode": {
              "enum": [
                "date",
                "manual"
              ]
            },
            "selectedBookRef": {
              "anyOf": [
                {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 128
                },
                {
                  "type": "null"
                }
              ]
            }
          },
          "required": [
            "heroMode",
            "fixedEventRef",
            "sortMode",
            "selectedBookRef"
          ],
          "additionalProperties": false
        },
        "importHistory": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "batchRef": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "format": {
                "enum": [
                  "events_json",
                  "events_csv",
                  "full_backup"
                ]
              },
              "sourceExportId": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "fileSha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$"
              },
              "importedAt": {
                "type": "integer",
                "minimum": 0
              },
              "provenance": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "sourceRef": {
                      "type": "string",
                      "minLength": 1,
                      "maxLength": 128
                    },
                    "localEventRef": {
                      "anyOf": [
                        {
                          "type": "string",
                          "minLength": 1,
                          "maxLength": 128
                        },
                        {
                          "type": "null"
                        }
                      ]
                    }
                  },
                  "required": [
                    "sourceRef",
                    "localEventRef"
                  ],
                  "additionalProperties": false
                },
                "maxItems": 2000
              }
            },
            "required": [
              "batchRef",
              "format",
              "sourceExportId",
              "fileSha256",
              "importedAt",
              "provenance"
            ],
            "additionalProperties": false
          },
          "maxItems": 200000
        },
        "tags": {
          "type": "array",
          "maxItems": 20000,
          "items": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "ref": {
                "$ref": "#/$defs/Ref"
              },
              "name": {
                "type": "string",
                "minLength": 1,
                "x-graphemeMax": 40,
                "x-maxUtf8Bytes": 2048
              },
              "createdAt": {
                "type": "integer",
                "minimum": 0
              }
            },
            "required": [
              "ref",
              "name",
              "createdAt"
            ]
          }
        }
      },
      "required": [
        "format",
        "version",
        "library",
        "books",
        "events",
        "assets",
        "actions",
        "lifecycleCauses",
        "home",
        "importHistory",
        "tags"
      ],
      "additionalProperties": false
    },
    "Ref": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  }
}
'''
# END FILE: docs/file_contracts_v1.schema.json


# ============================================================================
# BEGIN FILE: gradle.properties
# ============================================================================
FILES['gradle.properties'] = r'''org.gradle.jvmargs=-Xmx3g -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
org.gradle.parallel=true
org.gradle.caching=true
'''
# END FILE: gradle.properties


# ============================================================================
# BEGIN FILE: gradle/libs.versions.toml
# ============================================================================
FILES['gradle/libs.versions.toml'] = r'''[versions]
agp = "9.2.1"
kotlin = "2.2.10"
ksp = "2.3.10"
room = "2.8.5"
compose = "2025.08.01"
activity = "1.10.1"
lifecycle = "2.9.2"
navigation = "2.9.3"
coroutines = "1.10.2"
serialization = "1.9.0"
datastore = "1.1.7"
work = "2.10.3"
glance = "1.1.1"
biometric = "1.1.0"
lunar = "1.7.7"
junit = "4.13.2"

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
room = { id = "androidx.room", version.ref = "room" }

[libraries]
compose-bom = { module = "androidx.compose:compose-bom", version.ref = "compose" }
compose-ui = { module = "androidx.compose.ui:ui" }
compose-tooling = { module = "androidx.compose.ui:ui-tooling" }
compose-preview = { module = "androidx.compose.ui:ui-tooling-preview" }
compose-material3 = { module = "androidx.compose.material3:material3" }
compose-icons = { module = "androidx.compose.material:material-icons-extended" }
activity = { module = "androidx.activity:activity-compose", version.ref = "activity" }
lifecycle-runtime = { module = "androidx.lifecycle:lifecycle-runtime-compose", version.ref = "lifecycle" }
lifecycle-viewmodel = { module = "androidx.lifecycle:lifecycle-viewmodel-compose", version.ref = "lifecycle" }
navigation = { module = "androidx.navigation:navigation-compose", version.ref = "navigation" }
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }
coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
coroutines-android = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-android", version.ref = "coroutines" }
serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "serialization" }
datastore = { module = "androidx.datastore:datastore-preferences", version.ref = "datastore" }
work = { module = "androidx.work:work-runtime-ktx", version.ref = "work" }
glance = { module = "androidx.glance:glance-appwidget", version.ref = "glance" }
biometric = { module = "androidx.biometric:biometric", version.ref = "biometric" }
lunar = { module = "cn.6tail:lunar", version.ref = "lunar" }
junit = { module = "junit:junit", version.ref = "junit" }
'''
# END FILE: gradle/libs.versions.toml


# ============================================================================
# BEGIN FILE: gradle/wrapper/gradle-wrapper.jar
# ============================================================================
BINARY_BASE64['gradle/wrapper/gradle-wrapper.jar'] = (
    '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'
    'AAAAACwACQBvcmcvZ3JhZGxlL2NsaS9QYXJzZWRDb21tYW5kTGluZU9wdGlvbi5jbGFzc1VUBQABAAAAAG1Qy0rDQBQ9Y9TUWt+6'
    'dZGFaGkMotaiIkjBjYWKgtDlNLlNp06SMpMURPRD/AsXUlDwA/wo8bbgzs3lvObcmfn++fgCcIRNgdeXl9vGk9eV4QOlkXfqhT2v'
    '5oVZMlRa5ipL/SSLiHVDmqQlNvvS+mGfwgdbJNY77UltqeYNYz+RQ19NOo67dRnVTzhrGn/ne4XWLNi+9A+YUhqrlMioNGZ1RMby'
    'LtYb+4f7DT+ikfdcghAo32WFCelKaRLYyUwcxEZGmoJQq+BGGktRM0sSmUYt7msPJ1d2MSuwOpAjGWiZxkG7O6AwdzEvMD+SuiAr'
    'sNWa+kWudHBpjHxsKZufceBcpSq/EHB29+4rKGOxDBcVgY1/8i6Wy1hBpYISFhYwhzWB2Sa/F2tMXP5jwYi9KRKTNp4bzLbhMALW'
    'q50xlj6x0rkeY7X6jvU3YJp2eM7A+QVQSwcIEvFZOFEBAACsAQAAUEsDBBQACAgIAAAAIQAAAAAAAAAAAAAAAAAzAAkAb3JnL2dy'
    'YWRsZS9pbnRlcm5hbC9maWxlL1BhdGhUcmF2ZXJzYWxDaGVja2VyLmNsYXNzVVQFAAEAAAAAdVXLdxNVGP/dpjDTNIUS3lJhCAIh'
    'zUMESikPhQAaTQs2QA1U4WZykwydzISZSUtF8C2+cE9X7NgqnpOCPYpLj7px51LP4a/Qo/G70welxEXumfs9ft/vfq/8/O93PwDY'
    'i1sMUzduDPdfixS4PiasYmQgopci8YhuV2uGyT3DthJVuyhI7ghTcFeQssLdhF4R+phbr7qRgRI3XRGP1MqJKq8lDImxr9DHi337'
    'ydbpn/cv1U2TBG6FJ3bTVVhlwxLCMawySceF41Iskvcn9yT7E0UxHrmugjEEc3bd0cVJwxQMCdspp8oOL5oiZViecCxupkqkSp3m'
    'XuWMwyUON9OSnHAUtDN0X+bjPGVyq5w6VbgsdE/BckLN5C6OZIaOnxrJMbDzDCGXl4QEGeJVCrQjmn3sl/Mky4O7nhY9AT8rUxBi'
    'UAz3RLXmTTIEorvOh7ACK4PoQncIKjo6sAxhijqgYg2DqtuWxw3LZdi0OGi6wp2cuFIXli4OSox1WC8xNpBnSsUz9AbX447njhhe'
    'hWFtK8Lk1YNnpddm8hpVodFDfTPDTsmMKogwdLmixh3u2Y6MSYbpEJ7D9g5sww56iiNqJtcpJ+ui6XSLHIQQxS4ZI8aw/JBhGd6R'
    '/6FzLoQ4EkHCTZKpZ8t0S9g5UItILdSSYJ/Hbmn7AsNqX1/3DDN11HH4ZNZwqYx7GcJPOyroo0eWhScLmbbrlucXIRNCPw50Yj8G'
    'GNqjmVkyh4LYh8NUBIN6SWZgER0/XGZOTnRexEvS/eh81Cf0CtKUKhqMIXHVC+EEVnbiOE5SKIsEDGuiizM324iE+Qoy0u5VYuDZ'
    's2laaruQ5SwGZfwheg4vFpekeA5RVvw0XpevGpYHkW1LJlWcpXxTL9GghjAi9V14gwpNGmp9lebe76IQRme75U2GLY+xM6YpytzM'
    'edwTJ67qoia3goKLDOuX0jxWN8yiHDzOsOGsNWbZE5YmS6Mt9NiApkIPouD3AK/VKDhDT7RFZ82B0dNLKEuPijyGgrgkfSNPETzq'
    'lOtVYXmLOJoMyZ3b3Z2a4WqW7Wlck2OucUevGONCI2NnUrMdrUaNo1nUMJQRi3iVbKfKqWwHWrTxhRZpb1WvGq7IXDpBVCVf9ZBu'
    'zg0HteM56hbbTcqQKiaeXCOTrieqCmh5dFIbn3bsmnC8yRCuoTOIt/HOvLXfgFlb53KOb1Clz9IuC2eX6ojKe3i/A+/iA0L07Kw9'
    'IZw0bfLHW26xdcu3fISP5Vs+IdYThlW0J1wVn1Jzp2m10wKh1tDHBnntDC/ILb0yS5t9qF4tCMeX0BZeBoX+cBg2ygVIX210BtFJ'
    'ks9JfAvLESDp37EGVk3hj3tYfRuhWHhtAxun8FssvKmBLVP4KRbe6n88nMG27D3szB/uHr2DFbHuVE8DvYN3saqnO3UHN2Pdo76g'
    'Nx+fRqqBPfnsDPblB3sfgFb2NI48wDGGLF1fZriNjXH6eo3hR+x/gFMMDeRG7jYfxRs4s2Cze96kKz8YPtdAfgoHJM3mn/HwBXlt'
    '/u5/vDWFrXebv8a+nsGl/AwK+Z6L4eI0RANGA5enMUbcq/n276Hks4FYLmz33oc7De+hn5Qv6BxFx7p/EFMRZU3KeUBBF33TCTSx'
    '2b8rOK7QdC/cMXdrR9usFvgLfU3KbkAmnTQbwHwEfEm/zWRP0097u412YADD5PgVlegXKsMj0qmoY3y2NNDIhhCwJnz1Pq7fw4cN'
    '3Ax/RnX5Fqu/AfyiBnzugf8AUEsHCAYNbGgiBQAAVggAAFBLAwQUAAgICAAAACEAAAAAAAAAAAAAAAAAQQAJAG9yZy9ncmFkbGUv'
    'aW50ZXJuYWwvZmlsZS9sb2NraW5nL0V4Y2x1c2l2ZUZpbGVBY2Nlc3NNYW5hZ2VyLmNsYXNzVVQFAAEAAAAAZVHBbtNAEH3bJHWT'
    'xrShpdx9aqO6FqINUYsqoQpOVAiKynm9njjbrNeW146oEP0QfoBzTwgOHDnwUcDYKuLAHmZ33nvzZjT789e37wAO8VDg083Nm+mH'
    'IJZqQTYJjgM1C/YDlWeFNrLSuQ2zPCHGSzIkHTE5ly5Uc1ILV2cuOJ5J42g/KNIwk0WoG4+jeCKTyRPWltO/9bPaGAbcXIaPOCWb'
    'aktUapsyuqTScS/GpwePD6ZhQsvg4xqEwOAir0tFL7QhgZO8TKO0lImhSNuKSitNNGMqMrlasFX0/L0ytdPLtuCZUuTcubQypdJD'
    'V2DzSi5lZCQrX8VXpCoPqwKrT7XV1alAZ3fvcog19AfwMBAYZfI6pjOTO3pda6rMtcDO7svWROdRS8jY0MneJYv/gz3cE+ipJh1i'
    'E/11bGAksPVvCB6XimbLHrYEume8KgH/ouLfOJfF28YEI/R4muasQDTDcXzA2YhvwXdv/AXrt62gjyH8O3pyR2+Mf8Aff8V9gc/o'
    'vrtlsMsiH9v82mGBj5XfHADhMcZgp23V+QNQSwcI2abL5Z0BAAAmAgAAUEsDBBQACAgIAAAAIQAAAAAAAAAAAAAAAAAxAAkAb3Jn'
    'L2dyYWRsZS91dGlsL2ludGVybmFsL1dyYXBwZXJDcmVkZW50aWFscy5jbGFzc1VUBQABAAAAAI1V3XMTVRT/3SbpJmmAfFAqH1WM'
    'SNNN0oh81bZUaW0xJm2QtGCKWjabm3TbzW7YbIodBl79G8Rnpy99qA4EkNHhqc747/ik41jP3aQU2uCQz3vPPef8zvmdc8/+8e8v'
    'vwE4B4vhwf3714bvRouKusKNUnQkqpajiahqVmuartiaaSSrZomT3OI6V+qcDpeUelJd4upKvVGtR0fKil7niWitkqwqtaQmfJwv'
    'XlBKFy6SrjW8Y19u6DoJ6ktK8gxtuVHRDM4tzaiQdJVbdcIi+fDQ2aHhZImvRu95wRj8ebNhqXxa0zlD3LQqqYqllHSeatiantIM'
    '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'
    'xQQt8WUsPFPU9we4nLB5xxUUZBEVDWWcpiCFlbewPpCsswxTCcPxK421T++YYiAfhIrzDEdfbV2Pvcjpi33rSwwz+3O72Qv87eTs'
    '52p9qKGGZdJ6cRQXdBzBUY0EIr3TK/RWGMZIH3PrOh/clJsYJpr0VG7E/Y4IEgSTRFdJqRR5JDl5k1LwRDuSm+wBqSImaLxEszzS'
    'hABTpfbnj3Dw1A6m2Q4OpXYw8zCRfFIm8YL8B0boB77JZ+5/jy9KP+HQb2hntaw1dy9/z5/G7Na3qdt7MPYwn9Xc2712VXmAGvFm'
    'csoPqJRyCvnTOWUPp3ZxJjtfVX5BOafs4twtCvgjxq79jFq79Aj1p/m5+w8wJukHLxL3lgzWvvYrMqX83C4+fkh1zuIk2qhKURK7'
    'hKuJXcV6Yls0SnsAlynpGaT/grzHTEX1GTIqlHR64k/qxScEjlPHjlGZ88TeJJ9ub9Kr1N9QSwcIuFKYZ0sDAAASBQAAUEsDBBQA'
    'CAgIAAAAIQAAAAAAAAAAAAAAAAA0AAkAb3JnL2dyYWRsZS93cmFwcGVyL0Rvd25sb2FkJFByb3h5QXV0aGVudGljYXRvci5jbGFz'
    'c1VUBQABAAAAAI1UW08TQRT+hgJblq0WVLzfFtRt6cUrFFQUi3gBIwE1Nj6Y6e7Qrm536+wWJEZ+iA8++qxGS9TE+KSJP0o8y8W0'
    'hUSadHfmnO+c850z3+zvP1+/A7iIaYY3y8uzuVd6kZvPhWvpo7o5r6d006tUbYcHtuemK54lyC6FI7gvyFnmftosC/O5X6v4+ug8'
    'd3yR0quldIVX03aY41JxiFtDw4SVuc34+ZrjkMEv8/Q52gq3ZLtCSNstkXVBSJ9qkT2XuZDJpS2xoL+OgjGoc15NmmLSdgRDxpOl'
    'bElyyxHZRcmrVSGzE96i63jcGpiR3sul8VpQFm5gmzzwpIJ2hr5nfIFnXRFkW3ydDHF/yQ9EhSIpU2ALn2H39Bq+FthO9h6vXmbo'
    'vGK7djDG0Gu0+BKPGCJG4pEGFZoKBTENUXR1oQO7GQ6WRDDDfX/Rk1ZDaWqTod9ITP/jtT2IKscpw6x4URM+EX6wVKUJGI2BTQ0N'
    'NCEva9iDvSGnfQwDO4lQsJ+hY2b2/uMCw+mdFjmIQ104gMNNZOlMH86StuKNZMlC+KM4FpI6zqA1ehScZOgOBya9wDM9h2HvZrDD'
    '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'
    'YQT+kUOGwFfZlgnZcAMazmIfEyidRmC9Ok7DE9VGDZNqUD2Np9SF6goNr1RXaXi1ulHDm9SIhnerRzV8VD2mngXUE+rnGn9WPS/Q'
    'd5Xvev9s1aJhQIV9N/k+p3GBgt/i+5LGBQp+q2+PxgUKPuIb1bhAwe/13a9xgYI/4NuncYGCP+j7lcYFCv607zmNCxT8Bd9LGhco'
    '+Mu+VzQuUPD/+is0LpC4v9q/QHANicOnTmPZvRx1/8M5BpYZ6HwVs8c49wUMlOuF0/V/V//fZnC4UcAYq/i0BKzhqDCMMdb4aWkM'
    'XEqq1zHXwGVKLR5jr6ianh+JRKZ/Jn6GVsucieQ6TXLczJqfa+CuMVw+LZFLIir01BjKpqcxsFdT/VoMm4HqKa3RSTNrNMam+SbR'
    'OFV28wSdeTJZjcMoWd1bOMyBhntHMETFPeR3qLAKtxmq5TX4SSXOHKfhVoEKEtjSjZbxjbLSDXF5fuMVHDbGDl3GPl0g5Egp3535'
    'VDqwoag3396LxMc4g+NAN+m2cP98+vESDgOXke5aKvZltvjXEFDrUKXWI6j6MUslMdu3FnN8mzDXdx7m+WKo9vWjxncxDvJ3odZ/'
    'Pub741jgd7DQn0DIP6jl+PXY4f8/UEsHCE8sfs/EDAAAshgAAFBLAwQUAAgICAAAACEAAAAAAAAAAAAAAAAALQAJAG9yZy9ncmFk'
    'bGUvd3JhcHBlci9JbnN0YWxsJEluc3RhbGxDaGVjay5jbGFzc1VUBQABAAAAAGWR20oDMRCG/1i1WldrPd14twqeui7iqah4I4iC'
    'IigIXqa70200eyDZ1gvRB/EtvBDBCx/AhxJnqyIiA5mZP9/8Ccn7x+sbgA3MCDw+PJw37tymDG4oCd0dN2i5dTdI40xpmas08eI0'
    'JNYNaZKWeLMtrRe0Kbixndi6Oy2pLdXdLPJimXmq8Nhsbslwa5tZ0/iZb3W0ZsG2pbfGLSWRSoiMSiJWu2Qsn8V6Y3V9teGF1HXv'
    'hyAEKhdpxwR0qDQJLKQm8iMjQ03+rZFZRsY/TmwutZ7/zgfFxcroFxi/ll3pa5lE/lnzmoK8jEH2+xo/SmP2GzvpMSr1C/9dFlpS'
    '6Y6hU7JWRkxMnPy6XOTFbZka3FOJyvcF5hb/GvyHly4FSotLlw4cjFVQRtXBEIaHMYCagwpGimpSoP+AXwk1bsr8M31cMcVVrWA4'
    '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'
    'Qn0kDcT2emwkbewMPUri7tLintATJKVLUtbGPht5G0/asGyM2Th0Gjf3XcLRlPcypFS/pz0ZeiY+gRdj43j5yjlKLYKN+BaH0Y2t'
    'zjiAx51xD0acUcVBZzyE4874Ev2LkUE8n1vQcI3EBgmNEj1WmITD/2ABsRgp80WGvcQtsOASTqT62mPRcbwes/GujZPnaDx5hfRm'
    'k/Z80nGNBsGukegRzJ8QNj+mKXo7lQzuRhMaaOyMnsfC0Ckbn19FIBo6xbzEz1mRKy0s3tIoEk71ekKnkt5oMvRlO2U9jq+vELLB'
    'ceMBa4EQ/TRBPkUyNNJToeQoXIrcRwVzbDsRCkQTje6OoaumpN1B2iKsUHRx6PSWCXwf3StAEzj3wyROeJrt7CbXU7EO9lfC2mXs'
    '71OxjYRtcrCPlLAFkhtpvEfQ0U5spNZ6r6Jpofds7CoaY2eXnEQjm0pLH20Eh5XYVFZa4AleI4Nep6THRKL/kFjOeglFyhxWGuD5'
    'D1BLBwjxMGK5oQYAAEQNAABQSwECFAAUAAgICAAAACEAsLejHukNAAC+JwAAEAAJAAAAAAAAAAAAAAAAAAAATUVUQS1JTkYvTElD'
    'RU5TRVVUBQABAAAAAFBLAQIUABQACAgIAAAAIQBqz8talQAAALkAAAAUAAkAAAAAAAAAAAAAADAOAABNRVRBLUlORi9NQU5JRkVT'
    'VC5NRlVUBQABAAAAAFBLAQIUABQACAgIAAAAIQDg+kxEIgEAAHABAAAxAAkAAAAAAAAAAAAAABAPAABvcmcvZ3JhZGxlL2NsaS9D'
    'b21tYW5kTGluZUFyZ3VtZW50RXhjZXB0aW9uLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhAGGshe2OAgAA2wMAACYACQAA'
    'AAAAAAAAAAAAmhAAAG9yZy9ncmFkbGUvY2xpL0NvbW1hbmRMaW5lT3B0aW9uLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAh'
    'ANZLIUpbAgAAtgQAADMACQAAAAAAAAAAAAAAhRMAAG9yZy9ncmFkbGUvY2xpL0NvbW1hbmRMaW5lUGFyc2VyJEFmdGVyT3B0aW9u'
    'cy5jbGFzc1VUBQABAAAAAFBLAQIUABQACAgIAAAAIQARMJNEUgMAAJMHAAA8AAkAAAAAAAAAAAAAAEoWAABvcmcvZ3JhZGxlL2Ns'
    'aS9Db21tYW5kTGluZVBhcnNlciRCZWZvcmVGaXJzdFN1YkNvbW1hbmQuY2xhc3NVVAUAAQAAAABQSwECFAAUAAgICAAAACEApv7c'
    'D18HAAA6DwAAPQAJAAAAAAAAAAAAAAAPGgAAb3JnL2dyYWRsZS9jbGkvQ29tbWFuZExpbmVQYXJzZXIkS25vd25PcHRpb25QYXJz'
    'ZXJTdGF0ZS5jbGFzc1VUBQABAAAAAFBLAQIUABQACAgIAAAAIQBrgzSgTAIAAJcEAAA8AAkAAAAAAAAAAAAAAOIhAABvcmcvZ3Jh'
    'ZGxlL2NsaS9Db21tYW5kTGluZVBhcnNlciRNaXNzaW5nT3B0aW9uQXJnU3RhdGUuY2xhc3NVVAUAAQAAAABQSwECFAAUAAgICAAA'
    'ACEARYZ1xtYCAABKBQAAPQAJAAAAAAAAAAAAAAChJAAAb3JnL2dyYWRsZS9jbGkvQ29tbWFuZExpbmVQYXJzZXIkT3B0aW9uQXdh'
    'cmVQYXJzZXJTdGF0ZS5jbGFzc1VUBQABAAAAAFBLAQIUABQACAgIAAAAIQD1WGfyogEAAH0CAAA4AAkAAAAAAAAAAAAAAOsnAABv'
    'cmcvZ3JhZGxlL2NsaS9Db21tYW5kTGluZVBhcnNlciRPcHRpb25QYXJzZXJTdGF0ZS5jbGFzc1VUBQABAAAAAFBLAQIUABQACAgI'
    'AAAAIQC0fWhNIgIAAGYDAAAzAAkAAAAAAAAAAAAAAPwpAABvcmcvZ3JhZGxlL2NsaS9Db21tYW5kTGluZVBhcnNlciRPcHRpb25T'
    'dHJpbmcuY2xhc3NVVAUAAQAAAABQSwECFAAUAAgICAAAACEAmahlkqwBAADOAgAAMgAJAAAAAAAAAAAAAACILAAAb3JnL2dyYWRs'
    'ZS9jbGkvQ29tbWFuZExpbmVQYXJzZXIkUGFyc2VyU3RhdGUuY2xhc3NVVAUAAQAAAABQSwECFAAUAAgICAAAACEAjwiKR3MCAADH'
    'BAAAPwAJAAAAAAAAAAAAAACdLgAAb3JnL2dyYWRsZS9jbGkvQ29tbWFuZExpbmVQYXJzZXIkVW5rbm93bk9wdGlvblBhcnNlclN0'
    'YXRlLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhAOQRgy/rBAAA0ggAACYACQAAAAAAAAAAAAAAhjEAAG9yZy9ncmFkbGUv'
    'Y2xpL0NvbW1hbmRMaW5lUGFyc2VyLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhABhNjBCDBAAAUggAACYACQAAAAAAAAAA'
    'AAAAzjYAAG9yZy9ncmFkbGUvY2xpL1BhcnNlZENvbW1hbmRMaW5lLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhABLxWThR'
    'AQAArAEAACwACQAAAAAAAAAAAAAArjsAAG9yZy9ncmFkbGUvY2xpL1BhcnNlZENvbW1hbmRMaW5lT3B0aW9uLmNsYXNzVVQFAAEA'
    'AAAAUEsBAhQAFAAICAgAAAAhAAYNbGgiBQAAVggAADMACQAAAAAAAAAAAAAAYj0AAG9yZy9ncmFkbGUvaW50ZXJuYWwvZmlsZS9Q'
    'YXRoVHJhdmVyc2FsQ2hlY2tlci5jbGFzc1VUBQABAAAAAFBLAQIUABQACAgIAAAAIQDZpsvlnQEAACYCAABBAAkAAAAAAAAAAAAA'
    'AO5CAABvcmcvZ3JhZGxlL2ludGVybmFsL2ZpbGUvbG9ja2luZy9FeGNsdXNpdmVGaWxlQWNjZXNzTWFuYWdlci5jbGFzc1VUBQAB'
    'AAAAAFBLAQIUABQACAgIAAAAIQBKCT6T2wQAAOoIAAAxAAkAAAAAAAAAAAAAAANFAABvcmcvZ3JhZGxlL3V0aWwvaW50ZXJuYWwv'
    'V3JhcHBlckNyZWRlbnRpYWxzLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhANenErjaAQAAxwIAAD4ACQAAAAAAAAAAAAAA'
    'RkoAAG9yZy9ncmFkbGUvdXRpbC9pbnRlcm5hbC9XcmFwcGVyRGlzdHJpYnV0aW9uVXJsQ29udmVydGVyLmNsYXNzVVQFAAEAAAAA'
    'UEsBAhQAFAAICAgAAAAhAMk3EZmPAQAAHgIAAC8ACQAAAAAAAAAAAAAAlUwAAG9yZy9ncmFkbGUvd3JhcHBlci9Cb290c3RyYXBN'
    'YWluU3RhcnRlciQxLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhALhSmGdLAwAAEgUAAEEACQAAAAAAAAAAAAAAik4AAG9y'
    'Zy9ncmFkbGUvd3JhcHBlci9Eb3dubG9hZCREZWZhdWx0RG93bmxvYWRQcm9ncmVzc0xpc3RlbmVyLmNsYXNzVVQFAAEAAAAAUEsB'
    'AhQAFAAICAgAAAAhAOQLi38GAwAAQQUAADQACQAAAAAAAAAAAAAATVIAAG9yZy9ncmFkbGUvd3JhcHBlci9Eb3dubG9hZCRQcm94'
    'eUF1dGhlbnRpY2F0b3IuY2xhc3NVVAUAAQAAAABQSwECFAAUAAgICAAAACEAM6wND1ALAAAdFgAAIQAJAAAAAAAAAAAAAAC+VQAA'
    'b3JnL2dyYWRsZS93cmFwcGVyL0Rvd25sb2FkLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhAK2rZ0rZAQAAsgIAAC0ACQAA'
    'AAAAAAAAAAAAZmEAAG9yZy9ncmFkbGUvd3JhcHBlci9HcmFkbGVVc2VySG9tZUxvb2t1cC5jbGFzc1VUBQABAAAAAFBLAQIUABQA'
    'CAgIAAAAIQBB/e93+AAAACwBAAAxAAkAAAAAAAAAAAAAAKNjAABvcmcvZ3JhZGxlL3dyYXBwZXIvR3JhZGxlV3JhcHBlck1haW4k'
    'QWN0aW9uLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhAExnGE2CGAAA7TIAACoACQAAAAAAAAAAAAAAA2UAAG9yZy9ncmFk'
    'bGUvd3JhcHBlci9HcmFkbGVXcmFwcGVyTWFpbi5jbGFzc1VUBQABAAAAAFBLAQIUABQACAgIAAAAIQBPLH7PxAwAALIYAAAiAAkA'
    'AAAAAAAAAAAAAOZ9AABvcmcvZ3JhZGxlL3dyYXBwZXIvSW5zdGFsbCQxLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhAJQK'
    'w5RqAQAA5wEAAC0ACQAAAAAAAAAAAAAAA4sAAG9yZy9ncmFkbGUvd3JhcHBlci9JbnN0YWxsJEluc3RhbGxDaGVjay5jbGFzc1VU'
    'BQABAAAAAFBLAQIUABQACAgIAAAAIQCOJXStDREAAM4gAAAgAAkAAAAAAAAAAAAAANGMAABvcmcvZ3JhZGxlL3dyYXBwZXIvSW5z'
    'dGFsbC5jbGFzc1VUBQABAAAAAFBLAQIUABQACAgIAAAAIQAyJAvjWwIAAFoEAAAfAAkAAAAAAAAAAAAAADWeAABvcmcvZ3JhZGxl'
    'L3dyYXBwZXIvTG9nZ2VyLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhACOKqc0jAQAAagEAACYACQAAAAAAAAAAAAAA5qAA'
    'AG9yZy9ncmFkbGUvd3JhcHBlci9QYXRoQXNzZW1ibGVyLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhADBmz+YyBAAAZgcA'
    'AC4ACQAAAAAAAAAAAAAAZqIAAG9yZy9ncmFkbGUvd3JhcHBlci9Qcm9wZXJ0aWVzRmlsZUhhbmRsZXIuY2xhc3NVVAUAAQAAAABQ'
    'SwECFAAUAAgICAAAACEAt0UBU+8CAABQBgAALQAJAAAAAAAAAAAAAAD9pgAAb3JnL2dyYWRsZS93cmFwcGVyL1dyYXBwZXJDb25m'
    'aWd1cmF0aW9uLmNsYXNzVVQFAAEAAAAAUEsBAhQAFAAICAgAAAAhAPEwYrmhBgAARA0AACgACQAAAAAAAAAAAAAAUKoAAG9yZy9n'
    'cmFkbGUvd3JhcHBlci9XcmFwcGVyRXhlY3V0b3IuY2xhc3NVVAUAAQAAAABQSwUGAAAAACMAIwDgDQAAULEAAAAA'
)
# END FILE: gradle/wrapper/gradle-wrapper.jar


# ============================================================================
# BEGIN FILE: gradle/wrapper/gradle-wrapper.properties
# ============================================================================
FILES['gradle/wrapper/gradle-wrapper.properties'] = r'''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionSha256Sum=2ab2958f2a1e51120c326cad6f385153bb11ee93b3c216c5fccebfdfbb7ec6cb
distributionUrl=https\://services.gradle.org/distributions/gradle-9.4.1-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
'''
# END FILE: gradle/wrapper/gradle-wrapper.properties


# ============================================================================
# BEGIN FILE: gradlew
# ============================================================================
FILES['gradlew'] = r'''#!/bin/sh

#
# Copyright © 2015 the original authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
#

##############################################################################
#
#   Gradle start up script for POSIX generated by Gradle.
#
#   Important for running:
#
#   (1) You need a POSIX-compliant shell to run this script. If your /bin/sh is
#       noncompliant, but you have some other compliant shell such as ksh or
#       bash, then to run this script, type that shell name before the whole
#       command line, like:
#
#           ksh Gradle
#
#       Busybox and similar reduced shells will NOT work, because this script
#       requires all of these POSIX shell features:
#         * functions;
#         * expansions «$var», «${var}», «${var:-default}», «${var+SET}»,
#           «${var#prefix}», «${var%suffix}», and «$( cmd )»;
#         * compound commands having a testable exit status, especially «case»;
#         * various built-in commands including «command», «set», and «ulimit».
#
#   Important for patching:
#
#   (2) This script targets any POSIX shell, so it avoids extensions provided
#       by Bash, Ksh, etc; in particular arrays are avoided.
#
#       The "traditional" practice of packing multiple parameters into a
#       space-separated string is a well documented source of bugs and security
#       problems, so this is (mostly) avoided, by progressively accumulating
#       options in "$@", and eventually passing that to Java.
#
#       Where the inherited environment variables (DEFAULT_JVM_OPTS, JAVA_OPTS,
#       and GRADLE_OPTS) rely on word-splitting, this is performed explicitly;
#       see the in-line comments for details.
#
#       There are tweaks for specific operating systems such as AIX, CygWin,
#       Darwin, MinGW, and NonStop.
#
#   (3) This script is generated from the Groovy template
#       https://github.com/gradle/gradle/blob/2d6327017519d23b96af35865dc997fcb544fb40/platforms/jvm/plugins-application/src/main/resources/org/gradle/api/internal/plugins/unixStartScript.txt
#       within the Gradle project.
#
#       You can find Gradle at https://github.com/gradle/gradle/.
#
##############################################################################

# Attempt to set APP_HOME

# Resolve links: $0 may be a link
app_path=$0

# Need this for daisy-chained symlinks.
while
    APP_HOME=${app_path%"${app_path##*/}"}  # leaves a trailing /; empty if no leading path
    [ -h "$app_path" ]
do
    ls=$( ls -ld "$app_path" )
    link=${ls#*' -> '}
    case $link in             #(
      /*)   app_path=$link ;; #(
      *)    app_path=$APP_HOME$link ;;
    esac
done

# This is normally unused
# shellcheck disable=SC2034
APP_BASE_NAME=${0##*/}
# Discard cd standard output in case $CDPATH is set (https://github.com/gradle/gradle/issues/25036)
APP_HOME=$( cd -P "${APP_HOME:-./}" > /dev/null && printf '%s\n' "$PWD" ) || exit

# Use the maximum available, or set MAX_FD != -1 to use that value.
MAX_FD=maximum

warn () {
    echo "$*"
} >&2

die () {
    echo
    echo "$*"
    echo
    exit 1
} >&2

# OS specific support (must be 'true' or 'false').
cygwin=false
msys=false
darwin=false
nonstop=false
case "$( uname )" in                #(
  CYGWIN* )         cygwin=true  ;; #(
  Darwin* )         darwin=true  ;; #(
  MSYS* | MINGW* )  msys=true    ;; #(
  NONSTOP* )        nonstop=true ;;
esac



# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD=$JAVA_HOME/jre/sh/java
    else
        JAVACMD=$JAVA_HOME/bin/java
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD=java
    if ! command -v java >/dev/null 2>&1
    then
        die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
fi

# Increase the maximum file descriptors if we can.
if ! "$cygwin" && ! "$darwin" && ! "$nonstop" ; then
    case $MAX_FD in #(
      max*)
        # In POSIX sh, ulimit -H is undefined. That's why the result is checked to see if it worked.
        # shellcheck disable=SC2039,SC3045
        MAX_FD=$( ulimit -H -n ) ||
            warn "Could not query maximum file descriptor limit"
    esac
    case $MAX_FD in  #(
      '' | soft) :;; #(
      *)
        # In POSIX sh, ulimit -n is undefined. That's why the result is checked to see if it worked.
        # shellcheck disable=SC2039,SC3045
        ulimit -n "$MAX_FD" ||
            warn "Could not set maximum file descriptor limit to $MAX_FD"
    esac
fi

# Collect all arguments for the java command, stacking in reverse order:
#   * args from the command line
#   * the main class name
#   * -classpath
#   * -D...appname settings
#   * --module-path (only if needed)
#   * DEFAULT_JVM_OPTS, JAVA_OPTS, and GRADLE_OPTS environment variables.

# For Cygwin or MSYS, switch paths to Windows format before running java
if "$cygwin" || "$msys" ; then
    APP_HOME=$( cygpath --path --mixed "$APP_HOME" )

    JAVACMD=$( cygpath --unix "$JAVACMD" )

    # Now convert the arguments - kludge to limit ourselves to /bin/sh
    for arg do
        if
            case $arg in                                #(
              -*)   false ;;                            # don't mess with options #(
              /?*)  t=${arg#/} t=/${t%%/*}              # looks like a POSIX filepath
                    [ -e "$t" ] ;;                      #(
              *)    false ;;
            esac
        then
            arg=$( cygpath --path --ignore --mixed "$arg" )
        fi
        # Roll the args list around exactly as many times as the number of
        # args, so each arg winds up back in the position where it started, but
        # possibly modified.
        #
        # NB: a `for` loop captures its iteration list before it begins, so
        # changing the positional parameters here affects neither the number of
        # iterations, nor the values presented in `arg`.
        shift                   # remove old arg
        set -- "$@" "$arg"      # push replacement arg
    done
fi


# Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
DEFAULT_JVM_OPTS='"-Xmx64m" "-Xms64m"'

# Collect all arguments for the java command:
#   * DEFAULT_JVM_OPTS, JAVA_OPTS, and optsEnvironmentVar are not allowed to contain shell fragments,
#     and any embedded shellness will be escaped.
#   * For example: A user cannot expect ${Hostname} to be expanded, as it is an environment variable and will be
#     treated as '${Hostname}' itself on the command line.

set -- \
        "-Dorg.gradle.appname=$APP_BASE_NAME" \
        -jar "$APP_HOME/gradle/wrapper/gradle-wrapper.jar" \
        "$@"

# Stop when "xargs" is not available.
if ! command -v xargs >/dev/null 2>&1
then
    die "xargs is not available"
fi

# Use "xargs" to parse quoted args.
#
# With -n1 it outputs one arg per line, with the quotes and backslashes removed.
#
# In Bash we could simply go:
#
#   readarray ARGS < <( xargs -n1 <<<"$var" ) &&
#   set -- "${ARGS[@]}" "$@"
#
# but POSIX shell has neither arrays nor command substitution, so instead we
# post-process each arg (as a line of input to sed) to backslash-escape any
# character that might be a shell metacharacter, then use eval to reverse
# that process (while maintaining the separation between arguments), and wrap
# the whole thing up as a single "set" statement.
#
# This will of course break if any of these variables contains a newline or
# an unmatched quote.
#

eval "set -- $(
        printf '%s\n' "$DEFAULT_JVM_OPTS $JAVA_OPTS $GRADLE_OPTS" |
        xargs -n1 |
        sed ' s~[^-[:alnum:]+,./:=@_]~\\&~g; ' |
        tr '\n' ' '
    )" '"$@"'

exec "$JAVACMD" "$@"
'''
# END FILE: gradlew


# ============================================================================
# BEGIN FILE: gradlew.bat
# ============================================================================
FILES['gradlew.bat'] = '@rem\r\n@rem Copyright 2015 the original author or authors.\r\n@rem\r\n@rem Licensed under the Apache License, Version 2.0 (the "License");\r\n@rem you may not use this file except in compliance with the License.\r\n@rem You may obtain a copy of the License at\r\n@rem\r\n@rem      https://www.apache.org/licenses/LICENSE-2.0\r\n@rem\r\n@rem Unless required by applicable law or agreed to in writing, software\r\n@rem distributed under the License is distributed on an "AS IS" BASIS,\r\n@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\r\n@rem See the License for the specific language governing permissions and\r\n@rem limitations under the License.\r\n@rem\r\n@rem SPDX-License-Identifier: Apache-2.0\r\n@rem\r\n\r\n@if "%DEBUG%"=="" @echo off\r\n@rem ##########################################################################\r\n@rem\r\n@rem  Gradle startup script for Windows\r\n@rem\r\n@rem ##########################################################################\r\n\r\n@rem Set local scope for the variables with windows NT shell\r\nif "%OS%"=="Windows_NT" setlocal\r\n\r\nset DIRNAME=%~dp0\r\nif "%DIRNAME%"=="" set DIRNAME=.\r\n@rem This is normally unused\r\nset APP_BASE_NAME=%~n0\r\nset APP_HOME=%DIRNAME%\r\n\r\n@rem Resolve any "." and ".." in APP_HOME to make it shorter.\r\nfor %%i in ("%APP_HOME%") do set APP_HOME=%%~fi\r\n\r\n@rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.\r\nset DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"\r\n\r\n@rem Find java.exe\r\nif defined JAVA_HOME goto findJavaFromJavaHome\r\n\r\nset JAVA_EXE=java.exe\r\n%JAVA_EXE% -version >NUL 2>&1\r\nif %ERRORLEVEL% equ 0 goto execute\r\n\r\necho. 1>&2\r\necho ERROR: JAVA_HOME is not set and no \'java\' command could be found in your PATH. 1>&2\r\necho. 1>&2\r\necho Please set the JAVA_HOME variable in your environment to match the 1>&2\r\necho location of your Java installation. 1>&2\r\n\r\ngoto fail\r\n\r\n:findJavaFromJavaHome\r\nset JAVA_HOME=%JAVA_HOME:"=%\r\nset JAVA_EXE=%JAVA_HOME%/bin/java.exe\r\n\r\nif exist "%JAVA_EXE%" goto execute\r\n\r\necho. 1>&2\r\necho ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME% 1>&2\r\necho. 1>&2\r\necho Please set the JAVA_HOME variable in your environment to match the 1>&2\r\necho location of your Java installation. 1>&2\r\n\r\ngoto fail\r\n\r\n:execute\r\n@rem Setup the command line\r\n\r\n\r\n\r\n@rem Execute Gradle\r\n"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% "-Dorg.gradle.appname=%APP_BASE_NAME%" -jar "%APP_HOME%\\gradle\\wrapper\\gradle-wrapper.jar" %*\r\n\r\n:end\r\n@rem End local scope for the variables with windows NT shell\r\nif %ERRORLEVEL% equ 0 goto mainEnd\r\n\r\n:fail\r\nrem Set variable GRADLE_EXIT_CONSOLE if you need the _script_ return code instead of\r\nrem the _cmd.exe /c_ return code!\r\nset EXIT_CODE=%ERRORLEVEL%\r\nif %EXIT_CODE% equ 0 set EXIT_CODE=1\r\nif not ""=="%GRADLE_EXIT_CONSOLE%" exit %EXIT_CODE%\r\nexit /b %EXIT_CODE%\r\n\r\n:mainEnd\r\nif "%OS%"=="Windows_NT" endlocal\r\n\r\n:omega\r\n'
# END FILE: gradlew.bat


# ============================================================================
# BEGIN FILE: licenses/gradle-APACHE-2.0.txt
# ============================================================================
FILES['licenses/gradle-APACHE-2.0.txt'] = r'''
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS


==============================================================================
Licenses for included components:

------------------------------------------------------------------------------
Eclipse Public License 1.0
https://opensource.org/licenses/EPL-1.0

junit:junit
org.sonatype.aether:aether-api
org.sonatype.aether:aether-connector-wagon
org.sonatype.aether:aether-impl
org.sonatype.aether:aether-spi
org.sonatype.aether:aether-util

------------------------------------------------------------------------------
3-Clause BSD
https://opensource.org/licenses/BSD-3-Clause

com.google.code.findbugs:jsr305

org.hamcrest:hamcrest
BSD 3-Clause License

Copyright (c) 2000-2024, www.hamcrest.org

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

com.esotericsoftware.kryo:kryo
com.esotericsoftware.minlog:minlog
Copyright (c) 2008-2018, Nathan Sweet All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of Esoteric Software nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

org.ow2.asm:asm
org.ow2.asm:asm-analysis
org.ow2.asm:asm-commons
org.ow2.asm:asm-tree
org.ow2.asm:asm-util
ASM: a very small and fast Java bytecode manipulation framework
 Copyright (c) 2000-2011 INRIA, France Telecom
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. Neither the name of the copyright holders nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 THE POSSIBILITY OF SUCH DAMAGE.

------------------------------------------------------------------------------
MIT

com.googlecode.plist:dd-plist
dd-plist - An open source library to parse and generate property lists
Copyright (C) 2016 Daniel Dreibrodt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

org.bouncycastle:bcpg-jdk15on
org.bouncycastle:bcprov-jdk15on
Copyright (c) 2000 - 2019 The Legion of the Bouncy Castle Inc. (https://www.bouncycastle.org)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

org.slf4j:jcl-over-slf4j
org.slf4j:jul-to-slf4j
org.slf4j:log4j-over-slf4j
org.slf4j:slf4j-api
Copyright (c) 2004-2022 QOS.ch Sarl (Switzerland)
All rights reserved.

Permission is hereby granted, free  of charge, to any person obtaining
a  copy  of this  software  and  associated  documentation files  (the
"Software"), to  deal in  the Software without  restriction, including
without limitation  the rights to  use, copy, modify,  merge, publish,
distribute,  sublicense, and/or sell  copies of  the Software,  and to
permit persons to whom the Software  is furnished to do so, subject to
the following conditions:

The  above  copyright  notice  and  this permission  notice  shall  be
included in all copies or substantial portions of the Software.

THE  SOFTWARE IS  PROVIDED  "AS  IS", WITHOUT  WARRANTY  OF ANY  KIND,
EXPRESS OR  IMPLIED, INCLUDING  BUT NOT LIMITED  TO THE  WARRANTIES OF
MERCHANTABILITY,    FITNESS    FOR    A   PARTICULAR    PURPOSE    AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE,  ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


------------------------------------------------------------------------------
CDDL
https://opensource.org/licenses/CDDL-1.0

com.sun.xml.bind:jaxb-impl

------------------------------------------------------------------------------
LGPL 2.1
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html

org.samba.jcifs:jcifs

org.jetbrains.intellij.deps:trove4j

------------------------------------------------------------------------------
License for the GNU Trove library included by the Kotlin embeddable compiler
------------------------------------------------------------------------------
The source code for GNU Trove is licensed under the Lesser GNU Public License (LGPL).

    Copyright (c) 2001, Eric D. Friedman All Rights Reserved. This library is free software; you can redistribute it and/or modify it under
    the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or
    (at your option) any later version. This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
    even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
    You should have received a copy of the GNU Lesser General Public License along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


Two classes (HashFunctions and PrimeFinder) included in Trove are licensed under the following terms:

    Copyright (c) 1999 CERN - European Organization for Nuclear Research. Permission to use, copy, modify, distribute and sell this software
    and its documentation for any purpose is hereby granted without fee, provided that the above copyright notice appear in all copies and
    that both that copyright notice and this permission notice appear in supporting documentation. CERN makes no representations about the
    suitability of this software for any purpose. It is provided "as is" without expressed or implied warranty.

The source code of modified GNU Trove library is available at
    https://github.com/JetBrains/intellij-deps-trove4j (with trove4j_changes.txt describing the changes)

------------------------------------------------------------------------------
Eclipse Distribution License 1.0
https://www.eclipse.org/org/documents/edl-v10.php

org.eclipse.jgit:org.eclipse.jgit

------------------------------------------------------------------------------
BSD-style

com.jcraft:jzlib
com.github.mwiede:jsch

Copyright (c) 2002-2015 Atsuhiko Yamanaka, JCraft,Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

  3. The names of the authors may not be used to endorse or promote products
     derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL JCRAFT,
INC. OR ANY CONTRIBUTORS TO THIS SOFTWARE BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

------------------------------------------------------------------------------
Eclipse Public License 2.0
https://www.eclipse.org/legal/epl-2.0/

org.junit.platform:junit-platform-launcher

------------------------------------------------------------------------------
Mozilla Public License 2.0
https://www.mozilla.org/en-US/MPL/2.0/

org.mozilla:rhino
'''
# END FILE: licenses/gradle-APACHE-2.0.txt


# ============================================================================
# BEGIN FILE: settings.gradle.kts
# ============================================================================
FILES['settings.gradle.kts'] = r'''pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "DateBook"
include(":core", ":app")
'''
# END FILE: settings.gradle.kts


# ============================================================================
# BEGIN FILE: tools/host_test.sh
# ============================================================================
FILES['tools/host_test.sh'] = r'''#!/bin/sh
# Pure JVM tests only. Does not install/accept Android SDK or claim device coverage.
set -eu
DATEBOOK_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DATEBOOK_OUT="$DATEBOOK_ROOT/host-test-results"
DATEBOOK_DEPS="${DATEBOOK_TEST_DEPS:-$DATEBOOK_OUT/deps}"
DATEBOOK_KOTLINC="${KOTLINC:-$(command -v kotlinc || true)}"
if [ -z "$DATEBOOK_KOTLINC" ]; then
 echo '需要 Kotlin 2.2.10 CLI 和 JDK17+，或在 Android Studio 配置 SDK 后运行 ./gradlew :core:test :app:testDebugUnitTest。' >&2
 exit 2
fi
DATEBOOK_KOTLIN_LIB="${KOTLIN_LIB:-$(CDPATH= cd -- "$(dirname -- "$DATEBOOK_KOTLINC")/../lib" && pwd)}"
mkdir -p "$DATEBOOK_OUT" "$DATEBOOK_DEPS"
download() {
 if [ ! -f "$DATEBOOK_DEPS/$1.jar" ]; then curl -fL --retry 2 "https://repo.maven.apache.org/maven2/$2" -o "$DATEBOOK_DEPS/$1.jar"; fi
}
download coroutines org/jetbrains/kotlinx/kotlinx-coroutines-core-jvm/1.10.2/kotlinx-coroutines-core-jvm-1.10.2.jar
download serialization-core org/jetbrains/kotlinx/kotlinx-serialization-core-jvm/1.9.0/kotlinx-serialization-core-jvm-1.9.0.jar
download serialization-json org/jetbrains/kotlinx/kotlinx-serialization-json-jvm/1.9.0/kotlinx-serialization-json-jvm-1.9.0.jar
download lunar cn/6tail/lunar/1.7.7/lunar-1.7.7.jar
download junit junit/junit/4.13.2/junit-4.13.2.jar
download hamcrest org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar
DATEBOOK_CP="$DATEBOOK_DEPS/coroutines.jar:$DATEBOOK_DEPS/serialization-core.jar:$DATEBOOK_DEPS/serialization-json.jar:$DATEBOOK_DEPS/lunar.jar:$DATEBOOK_DEPS/junit.jar:$DATEBOOK_DEPS/hamcrest.jar"
"$DATEBOOK_KOTLINC" -jvm-target 17 -Xplugin="$DATEBOOK_KOTLIN_LIB/kotlinx-serialization-compiler-plugin.jar" -classpath "$DATEBOOK_CP" \
 "$DATEBOOK_ROOT"/core/src/main/kotlin/cn/datebook/core/*.kt \
 "$DATEBOOK_ROOT"/core/src/test/kotlin/cn/datebook/core/*.kt \
 "$DATEBOOK_ROOT/app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt" \
 "$DATEBOOK_ROOT/app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt" \
 -d "$DATEBOOK_OUT/host-tests.jar"
if [ -n "${JAVA_HOME:-}" ]; then DATEBOOK_JAVA="$JAVA_HOME/bin/java"; else DATEBOOK_JAVA=java; fi
"$DATEBOOK_JAVA" -cp "$DATEBOOK_OUT/host-tests.jar:$DATEBOOK_CP:$DATEBOOK_KOTLIN_LIB/kotlin-stdlib.jar" org.junit.runner.JUnitCore \
 cn.datebook.core.CoreTests cn.datebook.core.FileCodecTests cn.datebook.app.LunarGoldenTests
'''
# END FILE: tools/host_test.sh


# ============================================================================
# BEGIN FILE: tools/verify_bundle.py
# ============================================================================
FILES['tools/verify_bundle.py'] = r'''#!/usr/bin/env python3
"""Verify the trusted generated delivery, extraction fidelity and fail-closed extraction."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile

source=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'DateBook_AllInOne.py'
spec=importlib.util.spec_from_file_location('datebook_trusted_delivery',source)
bundle=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
checks=0
def denied(action):
 global checks
 try:action()
 except (ValueError,OSError):checks+=1;return
 raise AssertionError('Unsafe action was accepted')

payloads=bundle._payloads()
with tempfile.TemporaryDirectory(prefix='datebook-delivery-test-') as scratch:
 target=Path(scratch)/'DateBook'
 bundle.extract(target)
 for name,data in payloads.items():
  assert (target/name).read_bytes()==data,name
  checks+=1
 marker=target/'README.md';original=marker.read_bytes()
 denied(lambda:bundle.extract(target))
 assert marker.read_bytes()==original;checks+=1
 for path in ('../escape','/absolute','a\\b','a//b','a/./b','a/../b','C:/path',''):
  denied(lambda p=path:bundle._safe_path(p))
 # A malicious path added to otherwise matching metadata must fail before mkdir.
 bundle.FILES['../escape']='no'
 bundle.SHA256['../escape']=hashlib.sha256(b'no').hexdigest()
 denied(lambda:bundle.extract(Path(scratch)/'Unsafe'))
 assert not (Path(scratch)/'Unsafe').exists();checks+=1
 del bundle.FILES['../escape'];del bundle.SHA256['../escape']
 key='README.md';text=bundle.FILES[key];bundle.FILES[key]=text+'tamper'
 denied(bundle._payloads);bundle.FILES[key]=text
 assert hashlib.sha256(payloads['gradle/wrapper/gradle-wrapper.jar']).hexdigest()=='55243ef57851f12b070ad14f7f5bb8302daceeebc5bce5ece5fa6edb23e1145c';checks+=1
 bundle._payloads();checks+=1
print(f'PASS: {checks} bundle extraction/integrity/overwrite/path checks; {len(payloads)} files compared byte-for-byte.')
'''
# END FILE: tools/verify_bundle.py


# ============================================================================
# BEGIN FILE: tools/verify_delivery.py
# ============================================================================
FILES['tools/verify_delivery.py'] = r'''#!/usr/bin/env python3
"""Source/config/actual Room DDL checks. No Android execution is implied."""
import json
from pathlib import Path
import re
import sqlite3
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
checks=0
def check(ok, explanation):
 global checks
 assert ok,explanation
 checks+=1

required=['settings.gradle.kts','app/build.gradle.kts','core/build.gradle.kts','gradlew','gradlew.bat','gradle/wrapper/gradle-wrapper.jar','gradle/wrapper/gradle-wrapper.properties','docs/TEST_PLAN.md','docs/TEST_REPORT.md','README.md']
for name in required:check((ROOT/name).is_file(),'Missing '+name)
manifest=ET.parse(ROOT/'app/src/main/AndroidManifest.xml').getroot()
ns='{http://schemas.android.com/apk/res/android}'
permissions={p.get(ns+'name') for p in manifest.findall('uses-permission')}
check('android.permission.INTERNET' not in permissions,'No network permission')
check('android.permission.GET_ACCOUNTS' not in permissions,'No account permission')
check('android.permission.WRITE_CALENDAR' not in permissions,'Calendar writes use explicit system UI')
check(manifest.find('application').get(ns+'allowBackup')=='false','Automatic Android backup disabled')
paths=ET.parse(ROOT/'app/src/main/res/xml/file_paths.xml').getroot()
check(len(paths)==1 and paths[0].tag=='cache-path' and paths[0].get('path')=='shares/','Only scoped share cache exposed')
catalog=(ROOT/'gradle/libs.versions.toml').read_text()
check('ksp = "2.3.10"' in catalog,'AGP9-compatible KSP')
check('android.disallowKotlinSourceSets=false' not in (ROOT/'gradle.properties').read_text(),'Do not bypass source set guard')
check('org.jetbrains.kotlin.android' not in (ROOT/'app/build.gradle.kts').read_text(),'AGP built-in Kotlin')
for file in (ROOT/'app/src/main').rglob('*.xml'):ET.parse(file);checks+=1
for file in [*(ROOT/'core/src').rglob('*.kt'),*(ROOT/'app/src').rglob('*.kt')]:
 check(not re.search(r'\bTODO\s*\(|\bNotImplementedError\b|throw UnsupportedOperationException',file.read_text()),'Unimplemented placeholder '+str(file))

# Actual schema exported by Room KSP, not a hand-maintained duplicate.
schema=json.loads((ROOT/'app/schemas/cn.datebook.app.data.DateBookDatabase/1.json').read_text())['database']
check(len(schema['entities'])==25,'25 normalized tables')
db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON')
for entity in schema['entities']:
 table=entity['tableName'];db.execute(entity['createSql'].replace('${TABLE_NAME}',table))
 for index in entity.get('indices',[]):db.execute(index['createSql'].replace('${TABLE_NAME}',table))
guard=(ROOT/'app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt').read_text()
statements=re.findall(r'"""([\s\S]*?)"""',guard)
for statement in statements:db.executescript(statement)
check(db.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0]==42,'42 installed guards')
normalize=lambda s:re.sub(r'\s+',' ',s.replace(' IF NOT EXISTS','').strip().rstrip(';'))
for statement in statements:
 name=re.search(r'CREATE (?:TRIGGER|VIEW) IF NOT EXISTS (\w+)',statement).group(1)
 actual=db.execute('SELECT sql FROM sqlite_master WHERE name=?',(name,)).fetchone()[0]
 check(normalize(actual)==normalize(statement),'Guard body mismatch '+name)
db.execute("INSERT INTO library(id,name,created_at,updated_at) VALUES('l','n',0,0)")
db.execute("INSERT INTO book(id,library_id,name,name_key,created_at,updated_at) VALUES('b','l','b','b',0,0)")
def insert(identifier,parent=None):db.execute("INSERT INTO event(id,book_id,parent_id,title,kind,count_mode,created_at,updated_at) VALUES(?,'b',?,?,'ordinary','down',0,0)",(identifier,parent,identifier))
def reject(action,diagnostic):
 try:action()
 except sqlite3.DatabaseError as e:check(diagnostic in str(e),diagnostic+' / '+str(e));return
 raise AssertionError('Incorrectly accepted '+diagnostic)
reject(lambda:insert('x','missing'),'TREE_PARENT_NOT_FOUND')
insert('a');insert('b','a');insert('c','b')
reject(lambda:insert('d','c'),'TREE_DEPTH_EXCEEDED')
reject(lambda:db.execute("UPDATE event SET parent_id='c' WHERE id='a'"),'TREE_CYCLE')
reject(lambda:db.execute("UPDATE event SET id='x' WHERE id='a'"),'EVENT_ID_IMMUTABLE')
reject(lambda:db.execute("INSERT INTO recurrence VALUES('a','every_n_days',NULL,NULL)"),'CHECK_recurrence')
reject(lambda:db.execute("UPDATE event SET title=? WHERE id='a'",('x'*4097,)),'CHECK_event')
db.execute("UPDATE event SET title=? WHERE id='a'",('👨‍👩‍👧‍👦'*60,));checks+=1
reject(lambda:db.execute("INSERT INTO appearance(event_id,background_kind) VALUES('a','photo')"),'CHECK_appearance')
reject(lambda:db.execute("INSERT INTO event_date(event_id,calendar_type,anchor_month,anchor_day,all_day) VALUES('a','lunar',1,1,0)"),'CHECK_event_date')
check(not db.execute('PRAGMA foreign_key_check').fetchall(),'Foreign key integrity')
source=(ROOT/'app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt').read_text()
prepared=0
for sql in re.findall(r'sql\.(?:query|execSQL)\("((?:[^"\\]|\\.)*)"',source):
 sql=sql.replace('$where','epoch=? AND rule_id=? AND rule_version=? AND occurrence_key=?')
 if '$' in sql:continue
 db.execute('EXPLAIN '+sql,[None]*sql.count('?'));prepared+=1
check(prepared>=24,'Prepare platform SQL against actual Room schema')
print(f'PASS: {checks} source/config/SQLite checks; {prepared} platform SQL statements prepared.')
print('NOT RUN by this script: Android build, UI/device execution, notifications, performance and security audit.')
'''
# END FILE: tools/verify_delivery.py

PROJECT_TREE = r'''DateBook/
  .gitignore
  README.md
  THIRD_PARTY_NOTICES.md
  app/build.gradle.kts
  app/proguard-rules.pro
  app/schemas/cn.datebook.app.data.DateBookDatabase/1.json
  app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt
  app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt
  app/src/main/AndroidManifest.xml
  app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt
  app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt
  app/src/main/kotlin/cn/datebook/app/MainActivity.kt
  app/src/main/kotlin/cn/datebook/app/data/Entities.kt
  app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt
  app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt
  app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt
  app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt
  app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt
  app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt
  app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt
  app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt
  app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt
  app/src/main/res/drawable/ic_datebook.xml
  app/src/main/res/values/strings.xml
  app/src/main/res/values/themes.xml
  app/src/main/res/xml/backup_rules.xml
  app/src/main/res/xml/data_extraction_rules.xml
  app/src/main/res/xml/file_paths.xml
  app/src/main/res/xml/widget_info.xml
  app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt
  build.gradle.kts
  core/build.gradle.kts
  core/src/main/kotlin/cn/datebook/core/DateBookService.kt
  core/src/main/kotlin/cn/datebook/core/DateEngine.kt
  core/src/main/kotlin/cn/datebook/core/FileCodec.kt
  core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt
  core/src/main/kotlin/cn/datebook/core/Models.kt
  core/src/test/kotlin/cn/datebook/core/CoreTests.kt
  core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt
  docs/ADR.md
  docs/ERROR_CODES.md
  docs/IMPLEMENTATION_CONTRACT.md
  docs/TEST_PLAN.md
  docs/TEST_REPORT.md
  docs/file_contracts_v1.schema.json
  gradle.properties
  gradle/libs.versions.toml
  gradle/wrapper/gradle-wrapper.jar  [binary, Base64 below]
  gradle/wrapper/gradle-wrapper.properties
  gradlew
  gradlew.bat
  licenses/gradle-APACHE-2.0.txt
  plan/datebook-initial.md
  settings.gradle.kts
  tools/host_test.sh
  tools/verify_bundle.py
  tools/verify_delivery.py'''
SHA256 = {
  ".gitignore": "48457c9f6e04e0cf72cc6d4066a03bd40c1cb7a9cafcc403f4755ca23c1cc738",
  "README.md": "3a09be60a7fa26ff2dcf369eb604cb82dc1e214c6d692a511857be01d6eeb23f",
  "THIRD_PARTY_NOTICES.md": "82984c7b731fee4fe291875c7c3d5f8e3ed0214ded865de4e6e6dabc7e4e7645",
  "app/build.gradle.kts": "d9c0bcabbe621fc65504ee4d287e6fcaf6dc8fdb79525bd64c0083d73cedd44c",
  "app/proguard-rules.pro": "9b10be3cc65133de7a5761cb5db80db034d57c44e9af615734e5cdd3c1fb06c5",
  "app/schemas/cn.datebook.app.data.DateBookDatabase/1.json": "0d188b0829280669e76feb0aecac3b7ef35507d4edb4f07526848abd28208103",
  "app/src/androidTest/kotlin/cn/datebook/app/DatabaseTests.kt": "29d9b1647a26543c4ed41b901b6f53e7d72c0c2dc430b377c1cf10ea3afaad93",
  "app/src/androidTest/kotlin/cn/datebook/app/UiTests.kt": "83b784b118955a7c576e32bbddd027aa2d5e8caeb45bfe5dc4aa4f9342c73972",
  "app/src/main/AndroidManifest.xml": "d025880ffa8eb91ef74df616ef1bd2eccb0950b32027863bde37a02c0d0811a9",
  "app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt": "aeba3c13ec856650862f269e1a3438b232debccf3e51fda0729fe8eb19e36e06",
  "app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt": "d02236498a5ed4fd2d0e08ac7f81ef6f4bda9dffa893c7ed00a2ab104ff953f7",
  "app/src/main/kotlin/cn/datebook/app/MainActivity.kt": "4aeb3de0a453cdca9826fedeafc49762650ea6b83ba2bb7006a4466dd92123fe",
  "app/src/main/kotlin/cn/datebook/app/data/Entities.kt": "658b7a2509e01ec093f5d20ca0d1c3fb81c486894e83d5d39f2c1d0735013084",
  "app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt": "96cb912e11ea96373d972ff675143f9bcfd4e84c20c36310d528f8e6c73cdb44",
  "app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt": "c4703bbcdb806daa14ceb763424bbb535ab3fc94a0f9d7c71dab4de4c6d4db76",
  "app/src/main/kotlin/cn/datebook/app/platform/DateBookWidget.kt": "03f5c3b96de0fc27fec79a3689671b23c939c5f078a598279958601681a612a8",
  "app/src/main/kotlin/cn/datebook/app/platform/JobManager.kt": "7dbb3014f288c7cc651d489b3bcd06eede1a91d32b9940e32ec57eadb57edc8f",
  "app/src/main/kotlin/cn/datebook/app/platform/LockManager.kt": "13350f472f10a2499cf06d08c6c565278bb85aadb95d403cea469a7867c633c6",
  "app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt": "89e96f5491f0cc959830ccec89ce545d212a2bf2629cab3aac15b8ffe52b8b9f",
  "app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt": "215b3d1e5f5c96874f9a549509e3af1018b36e7a9fd0815bfdbf190036897c08",
  "app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt": "b361f7b4ff18f9c41201167699393e3855a86ff08f93193a5c463062d8144a81",
  "app/src/main/kotlin/cn/datebook/app/ui/DevicePreferences.kt": "f44eaf0a9962947bd6b3a6f45057594d47523870305cfff6d30b2f2631300f17",
  "app/src/main/res/drawable/ic_datebook.xml": "266b8271f5b807f18a89a112badf417d0e670eac22b61ccc88d5cd866330edfd",
  "app/src/main/res/values/strings.xml": "0d3c8abbe8c6b89ae137ae06981b3066bf787fee56149efa257bf8eda8c2fdff",
  "app/src/main/res/values/themes.xml": "2df02cd0a4886006cbb72712b7b6950a1502bb95ce4a8ce65e0c11def213c1ba",
  "app/src/main/res/xml/backup_rules.xml": "cbaefee51a97336361e2807bed05c75f042b44696a2a4186e5689a8459f25f1b",
  "app/src/main/res/xml/data_extraction_rules.xml": "4d075204d4c72f5a342f8ff9f837a37d1ac171cc5f872514da4ea3979e3e4249",
  "app/src/main/res/xml/file_paths.xml": "f019f916888d38584f7aaa232a3ed566357a7567fc2f0204018f1c9f7ad9735e",
  "app/src/main/res/xml/widget_info.xml": "77823b10690935cbc26c8c8bf5fbba7efd833274372aa80f573798166dbc6ab0",
  "app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt": "62238f06134adaaa4b1cb3e26a7507a870f63747b226641ab713572cad3bcdeb",
  "build.gradle.kts": "798c9586e15271dbc847c4d2729fd24f430e0e2ba8a59b9785d366ac6d2b0e86",
  "core/build.gradle.kts": "821e1dbf16ede555c1cc36b9fa7c2eed7a026a088e9cc1e0b1da1a9275a55c65",
  "core/src/main/kotlin/cn/datebook/core/DateBookService.kt": "358c10c71b04fcb055b131f696eb1d00ac959e1249ef3bfc969119a0ef33b97a",
  "core/src/main/kotlin/cn/datebook/core/DateEngine.kt": "bcd7e16fa02e9f3937ae524c4feab6295066aa0f5a74a682ac4b56af2c23af04",
  "core/src/main/kotlin/cn/datebook/core/FileCodec.kt": "ba281d2c1116eb98cfb1dc04df3b0c3a2a29b66436f6a4d45bdd03fb2a86afcf",
  "core/src/main/kotlin/cn/datebook/core/MemoryRepository.kt": "6563fa42835c529ec2bb6530c5cdac44040885ba515ea1a6c4168c9b00d114c9",
  "core/src/main/kotlin/cn/datebook/core/Models.kt": "e2cf8d68317ac6e971836db60411881fdaa0517f8fec4f31fea510db49bdd44c",
  "core/src/test/kotlin/cn/datebook/core/CoreTests.kt": "96777ca19320c9704a96f0409563e59cdcd57152ca1c3b731129bd53f9be7dfe",
  "core/src/test/kotlin/cn/datebook/core/FileCodecTests.kt": "fd6fc090259b0ef1223b0f707f55b5e9b3b4859144d96ae01a639bf09722d371",
  "docs/ADR.md": "d6c67b51b3748d653f30795e8a01c6f8df5fcf19b5743468ab0bff04e1bf7553",
  "docs/ERROR_CODES.md": "1255f4f08f11af918daba7ba1b5b10ac83b9e486544df9b5b4e2585221cd6f8f",
  "docs/IMPLEMENTATION_CONTRACT.md": "5e9fc9f4e46fde7696f73d6035cc1ccf1b113ab3fc394eceed3714a2d8a222ca",
  "docs/TEST_PLAN.md": "0affdfcc8e63219b42a726d50dbd0c5144598118a2e4c175d28a90dba6895161",
  "docs/TEST_REPORT.md": "28c97f47688288fbde66203f51603f07c46020ad9fb1ad1cb169164e3d60c6ed",
  "docs/file_contracts_v1.schema.json": "55d806be7b35f030d97405b55c88ceacaf8cfc432655a26fb1b4ed0b81d81cda",
  "gradle.properties": "a886559b125ecbd23fe4ec2fc2ce390c35e9f4fb52b3d7f1098720a6c12d3205",
  "gradle/libs.versions.toml": "213a4cae083979fa66963be282622194e504a75728af3b41823d4db239cac660",
  "gradle/wrapper/gradle-wrapper.jar": "55243ef57851f12b070ad14f7f5bb8302daceeebc5bce5ece5fa6edb23e1145c",
  "gradle/wrapper/gradle-wrapper.properties": "032a71c92fc7f3c1cadf8880f0554b71aa6beb411f97ac253aa93932cb3784d5",
  "gradlew": "aed171fb114f82e6eaea4970a245a200e0582a7dcc8ec0891ca41b6e4a62b754",
  "gradlew.bat": "fedad02c18e266ec094995a5751b7fe1eb6e74f66bf75db64fae2e50eb22c234",
  "licenses/gradle-APACHE-2.0.txt": "cf234c4188d773406f640bf89be680d9288f40ff96901c70d643fcea96ad46df",
  "plan/datebook-initial.md": "9eba8eacb68a418aef008d043499ff53e022f6081d1bec63059326d5bb2a3628",
  "settings.gradle.kts": "aac02d1228ba4a8b4bef35a512daf084c9c789f2113322635fcc518310c019ed",
  "tools/host_test.sh": "388298301643293cd6e0dce9707d5432548c1188a5ef186e4ceb2a8d45947e2f",
  "tools/verify_bundle.py": "bb1207a397985296cc0e7427e1202e2928cd38d3ae9cc9de17c7879fff63615b",
  "tools/verify_delivery.py": "81728932605c417faa70a1137c4f3b200c357963cc26a9b8c488a1b71330f6ae"
}

def _safe_path(value):
    path=PurePosixPath(value)
    if not value or path.is_absolute() or "\\" in value or ":" in value or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("Unsafe project path: "+value)
    return path

def _payloads():
    content={name:text.encode("utf-8") for name,text in FILES.items()}
    for name,value in BINARY_BASE64.items():
        if name in content:raise ValueError("Duplicate path: "+name)
        content[name]=base64.b64decode(value,validate=True)
    for name,data in content.items():
        _safe_path(name)
        if hashlib.sha256(data).hexdigest()!=SHA256.get(name):raise ValueError("Checksum mismatch: "+name)
    if content.keys()!=SHA256.keys():raise ValueError("Manifest entries do not match payloads")
    return content

def verify():
    payloads=_payloads()
    digest=hashlib.sha256("\n".join(name+" "+SHA256[name] for name in sorted(SHA256)).encode()).hexdigest()
    print(f"PASS: {len(payloads)} files / {sum(map(len,payloads.values())):,} source bytes; SHA256 checked.")
    print("Manifest SHA256: "+digest)
    print("This verifies delivery integrity, not Android build/device acceptance.")

def extract(destination):
    payloads=_payloads()  # All paths and hashes validated before creating anything.
    target=Path(destination).expanduser().absolute()
    if target.exists() or target.is_symlink():raise FileExistsError("Refusing to overwrite existing destination: "+str(target))
    target.mkdir(parents=True,exist_ok=False)
    for name,data in payloads.items():
        file=target.joinpath(*_safe_path(name).parts)
        file.parent.mkdir(parents=True,exist_ok=True)
        with file.open("xb") as stream:stream.write(data)
        if name=="gradlew" or name.startswith("tools/") and file.suffix in (".sh",".py"):file.chmod(0o755)
    print(f"Extracted {len(payloads)} files into {target}")
    print("Next: read README.md, configure Android Studio/JDK17/API37 and run the documented build/tests.")
    print("No existing files were overwritten; no SDK license was accepted; no network request was made.")

def main():
    parser=argparse.ArgumentParser(description="DateBook 单文件源码：阅读、校验、还原。默认不写任何文件。")
    actions=parser.add_mutually_exclusive_group()
    actions.add_argument("--verify",action="store_true",help="校验所有内嵌文件SHA256")
    actions.add_argument("--list",action="store_true",help="列出完整项目结构")
    actions.add_argument("--plan",action="store_true",help="显示开发与测试详细规划")
    actions.add_argument("--read",metavar="PROJECT_PATH",help="输出某个明文源码文件")
    actions.add_argument("--extract",metavar="NEW_DIRECTORY",help="还原到一个不存在的新目录，拒绝覆盖")
    args=parser.parse_args()
    try:
        if args.extract:extract(args.extract)
        elif args.list:print(PROJECT_TREE)
        elif args.plan:print(FILES["docs/TEST_PLAN.md"]+"\n\n"+FILES["plan/datebook-initial.md"])
        elif args.read:
            _safe_path(args.read)
            if args.read not in FILES:raise ValueError("Not a text source file: "+args.read)
            print(FILES[args.read],end="")
        else:verify()
    except (ValueError,OSError,KeyError) as error:
        parser.exit(2,"Error: "+str(error)+"\n")

if __name__=="__main__":main()
