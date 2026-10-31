package cn.datebook.app.ui

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
