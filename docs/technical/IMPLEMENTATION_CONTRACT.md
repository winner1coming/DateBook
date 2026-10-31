# DateBook 实施契约

依据 TD v1.1，所有讲解中文，Kotlin 标识符英文。主交付是 Android 应用，core 为纯 JVM 支持模块，不是服务端。2026-11-01 起改为正常 Android 工程目录交付：app/core 是维护入口，docs 分类保存产品、技术、开发与测试资料；原单文件保留在 archive 中，仅用于历史核对，不用于覆盖后续源码。下文接口与实现分工保留原开发契约背景，当前状态以实现状态和测试报告为准。

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
