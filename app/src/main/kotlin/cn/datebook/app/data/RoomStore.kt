package cn.datebook.app.data

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
