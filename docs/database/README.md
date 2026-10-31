# 数据库设计与迁移

[schema_design_v1.1.sql](schema_design_v1.1.sql) 是 TD 阶段的逻辑设计附件，用于理解约束，不要拿它覆盖 Room 数据库或当作当前安装脚本。

生产源码在 [Entities.kt](../../app/src/main/kotlin/cn/datebook/app/data/Entities.kt)、[SchemaGuards.kt](../../app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt) 和 [RoomStore.kt](../../app/src/main/kotlin/cn/datebook/app/data/RoomStore.kt)。实际 Room/KSP 导出结构在 [版本1 schema](../../app/schemas/cn.datebook.app.data.DateBookDatabase/1.json)，含25张规范化表；额外42个触发器由 SchemaGuards 安装。

后续修改表结构必须增加数据库版本、显式 Migration 和迁移测试，提交更新后的 Room schema；禁止使用 destructive migration 或捕获打开异常后重建空库。媒体租约、epoch、revision、幂等凭据和副作用 outbox 的行为不能因整理表结构而丢失。

`python3 tools/verify_delivery.py` 会使用实际导出 schema 在主机 SQLite 上执行关系/触发器检查；这不能替代 Android SQLite 和 Room 的设备迁移测试。
