# 架构决策与开发基线

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
16. **正常仓库交付（2026-11-01）**：按用户要求将已交付总文件还原为 app/core 工程，产品、技术、开发、测试资料分类放入 docs。原始Word保持字节一致，提供带原图的Markdown阅读版；原总文件移到archive并保留Git历史。业务代码不因本次整理改变。迁移字节核对是一次性门禁，默认CI检查不冻结后续业务修改。CI配置不等于构建已通过，待补功能和未实测项单独列出。

## 官方技术依据

- https://developer.android.com/build/releases/agp-9-2-0-release-notes
- https://developer.android.com/jetpack/androidx/releases/room
- https://developer.android.com/develop/ui/compose/bom
- https://developer.android.com/develop/background-work/services/alarms/schedule
- https://developer.android.com/develop/ui/views/appwidgets/glance
- https://github.com/6tail/lunar-java/tree/v1.7.7

本交付不包含待用户审批才能实现的服务端依赖。后续若增加实时共享、账号或云备份，需要另立架构与隐私方案，不悄悄改变本地承诺。
