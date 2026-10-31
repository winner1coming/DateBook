# 错误码目录

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
