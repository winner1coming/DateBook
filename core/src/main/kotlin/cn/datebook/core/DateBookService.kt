package cn.datebook.core

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
