# 交付测试报告

日期：2026-10-31 至 2026-11-01。结论：源码与测试实现交付；**未完成 Android 安装 / 真机验收，不是已可上架的发布包**。

## 2026-11-01 工程目录化复验

本次复验针对从历史总文件还原的正常Git工程，不新增业务能力、不重新声称产品全量完成。

| 实际执行 | 结果 |
|---|---|
| `sh tools/host_test.sh`（配置Kotlin CLI、JVM与已有依赖） | 85项JUnit通过：49核心、24文件、12真实农历；编译器运行于已有JBR25，目标字节码17 |
| `python3 tools/verify_delivery.py` | 105项源码/配置/SQLite检查通过，24条系统SQL预编译通过 |
| `python3 tools/verify_repository.py --check-baseline` | 目录、Markdown链接、Word原件哈希、54张原文表格及10处TD插图、Wrapper、CI静态约束通过；业务源码/构建文件/资源/schema与历史快照字节一致 |
| `python3 tools/verify_bundle.py` | 72项历史封装完整性/防覆盖/路径检查通过，57个历史文件提取后字节一致；这不是当前工程必须再次提取的要求 |
| Gradle9.4.1 `--offline --no-daemon tasks --all` | 在当前工程成功，app/core、KSP、AndroidTest、lint和打包任务注册；初次受沙箱文件锁通信限制，获准后离线重试成功；未构建APK |
| 工作流YAML | Ruby YAML解析语法通过；GitHub是否实际执行成功以对应提交Actions记录为准 |
| `python3 tools/check_android_sdk.py` | 如实退出1：本机未配置SDK；没有下载SDK、接受许可或运行安装/仪器化测试 |

原件Word未修改；Markdown阅读版保留表格与图片。旧文件中已有的少量末尾空行及官方Windows Wrapper的CRLF保持原样；默认Git空白检查会报告这些历史格式问题，不宣称该项零警告。业务之外的新文档、检查工具及CI为本轮新增。产品差异已列入[实现状态](../development/IMPLEMENTATION_STATUS.md)，后续先完成[开发与验收计划](../development/DEVELOPMENT_PLAN.md)的M1–M5再考虑发布。

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

当前已目录化，无需再提取总文件：直接打开仓库根目录，按README做正式构建，再执行TEST_PLAN矩阵。所有P0/P1阻断发布。访问锁不是数据库加密；正常提醒不能承诺系统准时；外部DocumentProvider写入不能承诺断电原子性；系统强停后没有服务器补发。后续实际构建/设备差异若出现问题，必须修复并重跑，而不是把本报告改成“全部已通过”。

正式Spec门禁标为不适用：本项目来源为TD/PRD文档，没有`spec/_settings.md`或code baseline；本次用计划验证、需求覆盖矩阵和上述编译/测试，不伪造Full Spec的通过记录。
