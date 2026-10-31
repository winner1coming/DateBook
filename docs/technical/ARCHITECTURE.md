# 当前源码架构

本文件描述实际落在仓库的实现，不替代[原始 TD](TD.md)。项目为单进程 Android App，两个 Gradle 模块；没有服务器、HTTP API、账号或网络数据库。

```text
Compose 页面与类型安全导航
        ↓
AppViewModel → DateBookService → LibraryRepository
                 ↓                  ↓
             DateEngine          RoomStore
                 ↓                  ↓
           LunarAdapter      规范化 SQLite 与媒体代次

AppGraph → SystemServices / LockManager / JobManager
                 ↓
AlarmManager / WorkManager / Glance / Calendar / SAF
```

## 代码入口

| 文件/包 | 实际职责 |
|---|---|
| [DateBookApplication](../../app/src/main/kotlin/cn/datebook/app/DateBookApplication.kt) | 初始化 AppGraph、启动维护和精确范围的暂存清理 |
| [MainActivity](../../app/src/main/kotlin/cn/datebook/app/MainActivity.kt) | Compose 宿主、外部事件入口与后台锁定 |
| [AppViewModel](../../app/src/main/kotlin/cn/datebook/app/ui/AppViewModel.kt) | 用例接线、操作状态、预览/提交、权限选择器续行与文件任务 |
| [DateBookUi](../../app/src/main/kotlin/cn/datebook/app/ui/DateBookUi.kt) | 首页、本、目标、详情/编辑、设置、恢复与导航 |
| [Models](../../core/src/main/kotlin/cn/datebook/core/Models.kt) | 共享值对象与仓库契约 |
| [DateEngine](../../core/src/main/kotlin/cn/datebook/core/DateEngine.kt) | Clock 驱动的日期投影、循环、边界与 DST |
| [DateBookService](../../core/src/main/kotlin/cn/datebook/core/DateBookService.kt) | 校验、原子写入、三级树、目标和生命周期 |
| [FileCodec](../../core/src/main/kotlin/cn/datebook/core/FileCodec.kt) | 严格文件协议、CSV、认证备份与导入来源映射 |
| [data](../../app/src/main/kotlin/cn/datebook/app/data/) | 25表、42守卫、事务/幂等、CAS切库、媒体快照租约 |
| [platform](../../app/src/main/kotlin/cn/datebook/app/platform/) | 提醒票据、日历、卡片、组件、锁与持久任务 |

core 不依赖 Android 或 app。UI 不直接持有跨代 Room 连接；业务输入和关系校验在服务层，持久化事务在仓库。长 IO 通过媒体租约读取快照，不长时间持有资料库门锁。

## 重要约束

每次替换资料库变更 epoch；实体更新使用版本，预览提交使用 epoch/revision CAS。通知队列推进与投递票据同事务，OS 通知在提交后发布，不能声称绝对 exactly-once。三级关系在领域与数据库双层保护。

应用锁使用本机 PIN 验证及强生物识别，备份密码独立；锁不声称数据库加密。恢复先认证/校验再切库，锁定恢复后新 PIN 验证资料原子替换。界面遮罩、单独对话框、焦点和系统选择器续行都需真机安全验收。

实际依赖为构造器注入而非 Hilt，物理上为 core/app 两模块而非 TD 中的更多模块；已记录在 [ADR](../decisions/ADR.md)。版本固定在 [libs.versions.toml](../../gradle/libs.versions.toml)，不使用 `latest` 或动态版本。
