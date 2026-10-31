package cn.datebook.app

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
