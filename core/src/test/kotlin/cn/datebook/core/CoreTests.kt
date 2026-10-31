package cn.datebook.core

import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test
import java.time.*

class CoreTests {
 private val clock = Clock.fixed(Instant.parse("2026-10-31T04:00:00Z"), ZoneId.of("Asia/Shanghai"))
 private val lunar = object : LunarPort {
  override fun solar(year: Int, month: Int, day: Int, leapMonth: Boolean, leapPolicy: String, smallMonthPolicy: String): LocalDate? {
   if (leapMonth && leapPolicy == "leap_only" && year != 2028) return null
   val max = YearMonth.of(year, month).lengthOfMonth()
   if (day > max && smallMonthPolicy == "skip") return null
   return LocalDate.of(year, month, minOf(day, max))
  }
  override fun lunarYear(date: LocalDate) = date.year
 }
 private val dates = DateEngine(clock, lunar)
 private fun event(book: String, id: String = newId(), parent: String? = null, day: Int = 1): Event = Event(id = id, bookId = book, parentId = parent, title = id, date = DateSpec(year = 2026, month = 12, day = day))
 private fun input(year: Int? = 2026, month: Int = 10, day: Int = 31, frequency: String = "none", kind: String = "ordinary", mode: String = "down", include: Boolean = false) = DateInput(DateSpec(year = year, month = month, day = day), RecurrenceSpec(frequency), mode, include, kind)
 private fun error(code: String, block: () -> Unit) {
  try { block(); fail("Expected $code") } catch (e: AppException) { assertEquals(code, e.code) }
 }
 private suspend fun failure(code: String, block: suspend () -> Unit) {
  try { block(); fail("Expected $code") } catch (e: AppException) { assertEquals(code, e.code) }
 }
 private fun fixture(): Triple<MemoryRepository, DateBookService, String> {
  val repo = MemoryRepository(defaultLibrary(clock.millis()), clock)
  return Triple(repo, DateBookService(repo, dates, clock), repo.state.value.books.first().id)
 }

 @Test fun birthdayTodayAndTomorrowRollover() {
  val i = input(2000, 10, 31, "yearly", "birthday")
  val today = dates.evaluate(i)
  assertEquals("今天生日", today.label); assertEquals(26, today.age); assertEquals(0L, today.days)
  val next = dates.evaluate(i, Instant.parse("2026-10-31T16:00:00Z"))
  assertEquals(LocalDate.of(2027, 10, 31), next.occurrence!!.date); assertEquals(27, next.age)
 }
 @Test fun birthdayWithoutYearHidesAge() { assertNull(dates.evaluate(input(null, frequency = "yearly", kind = "birthday")).age) }
 @Test fun leapBirthdayFeb28() { assertEquals(LocalDate.of(2027, 2, 28), dates.nextOccurrence(input(2000, 2, 29, "yearly", "birthday"), LocalDate.of(2027, 1, 1))!!.date) }
 @Test fun leapBirthdayMarchPolicy() {
  val i = input(2000, 2, 29, "yearly", "birthday"); assertEquals(LocalDate.of(2027, 3, 1), dates.nextOccurrence(i.copy(date = i.date.copy(feb29Policy = "mar01")), LocalDate.of(2027, 1, 1))!!.date)
 }
 @Test fun monthlyDoesNotLoseOriginalAnchor() {
  val values = dates.occurrences(input(2027, 1, 31, "monthly"), LocalDate.of(2027, 1, 1), LocalDate.of(2027, 3, 31))
  assertEquals(listOf("2027-01-31", "2027-02-28", "2027-03-31"), values.map { it.date.toString() })
 }
 @Test fun weeklyAndEveryNDaysAnchored() {
  assertEquals(LocalDate.of(2026, 11, 7), dates.nextOccurrence(input(frequency = "weekly"), LocalDate.of(2026, 11, 1))!!.date)
  val i = input().copy(repeat = RecurrenceSpec("every_n_days", 3))
  assertEquals(LocalDate.of(2026, 11, 3), dates.nextOccurrence(i, LocalDate.of(2026, 11, 1))!!.date)
 }
 @Test fun untilIsInclusive() {
  val i = input(frequency = "weekly").copy(repeat = RecurrenceSpec("weekly", until = "2026-11-07"))
  assertEquals(2, dates.occurrences(i, LocalDate.of(2026, 10, 1), LocalDate.of(2026, 12, 1)).size)
  assertNull(dates.nextOccurrence(i, LocalDate.of(2026, 11, 8)))
 }
 @Test fun repeatExhaustedRetainsProjection() {
  val i = input(2000, 1, 1, "yearly").copy(repeat = RecurrenceSpec("yearly", until = "2025-01-01"))
  assertTrue(dates.evaluate(i).exhausted)
 }
 @Test fun annualDoesNotOccurBeforeAnchor() {
  assertEquals(LocalDate.of(2028, 10, 31), dates.nextOccurrence(input(2028, frequency = "yearly"), LocalDate.of(2026, 1, 1))!!.date)
 }
 @Test fun positiveIncludesStartOnlyWhenRequested() {
  assertEquals(0L, dates.evaluate(input(mode = "up")).days)
  assertEquals(1L, dates.evaluate(input(mode = "up", include = true)).days)
  assertEquals("尚未开始", dates.evaluate(input(2027, mode = "up")).label)
 }
 @Test fun allDayDstCountsCalendarDaysNot24Hours() {
  val i = input(2026, 3, 9)
  val p = dates.evaluate(i, Instant.parse("2026-03-08T05:00:00Z"), ZoneId.of("America/New_York"))
  assertEquals(1L, p.days)
  assertEquals(Instant.parse("2026-03-09T04:00:00Z"), p.validUntil)
 }
 @Test fun timedDstGapMovesForward() {
  val i = input(2026, 3, 8).copy(date = DateSpec(year = 2026, month = 3, day = 8, allDay = false, localTime = "02:30", zoneId = "America/New_York"))
  assertEquals(Instant.parse("2026-03-08T07:30:00Z"), dates.nextOccurrence(i, LocalDate.of(2026, 3, 8))!!.instant)
 }
 @Test fun timedDstOverlapUsesEarlierOffset() {
  val i = input(2026, 11, 1).copy(date = DateSpec(year = 2026, month = 11, day = 1, allDay = false, localTime = "01:30", zoneId = "America/New_York"))
  assertEquals(Instant.parse("2026-11-01T05:30:00Z"), dates.nextOccurrence(i, LocalDate.of(2026, 11, 1))!!.instant)
 }
 @Test fun timedFutureCeilingAndPastFloor() {
  val i = input().copy(date = DateSpec(year = 2026, month = 10, day = 31, allDay = false, localTime = "13:00", zoneId = "Asia/Shanghai"))
  assertEquals(1L, dates.evaluate(i).days)
  assertEquals("已过不足 1 天", dates.evaluate(i, Instant.parse("2026-10-31T05:30:00Z")).label)
  assertEquals("还有 1 天", dates.evaluate(i, Instant.parse("2026-10-31T04:59:59.999999999Z")).label)
 }
 @Test fun timedProjectionExpiresAtNumericBoundaryNotOnlyMidnight() {
  val i = input(2026, 11, 1).copy(date = DateSpec(year = 2026, month = 11, day = 1, allDay = false, localTime = "13:00", zoneId = "Asia/Shanghai"))
  val p = dates.evaluate(i)
  assertEquals(2L, p.days); assertEquals(Instant.parse("2026-10-31T05:00:00Z"), p.validUntil)
 }
 @Test fun leapFebruaryMonthlyAnchorStaysFebruary29() {
  val datesList = dates.occurrences(input(2024, 2, 29, "monthly"), LocalDate.of(2024, 2, 1), LocalDate.of(2024, 4, 30)).map { it.date }
  assertEquals(listOf(LocalDate.of(2024, 2, 29), LocalDate.of(2024, 3, 29), LocalDate.of(2024, 4, 29)), datesList)
 }
 @Test fun dateInvalidCombinationsRejected() {
  error("DATE_INVALID") { dates.validate(input(2026, 2, 31)) }
  error("DATE_REPEAT_INVALID") { dates.validate(input(frequency = "every_n_days")) }
  error("DATE_KIND_INVALID") { dates.validate(input(kind = "birthday")) }
  error("GOAL_DATE_INVALID") { dates.validate(input(frequency = "yearly", kind = "goal")) }
  error("DATE_TIME_INVALID") { dates.validate(input().copy(date = input().date.copy(localTime = "09:00"))) }
 }
 @Test fun lunarPortLeapAndSmallMonthPolicies() {
  val i = input(2026, 2, 30, "yearly").copy(date = DateSpec(calendar = "lunar", year = 2026, month = 2, day = 30, leapMonth = true, lunarLeapPolicy = "leap_only"))
  // 明确 fake 端口样例，不冒充真实农历权威转换测试。
  val next = dates.nextOccurrence(i.copy(date = i.date.copy(year = null), kind = "birthday"), LocalDate.of(2026, 1, 1))
  assertNotNull(next)
 }
 @Test fun occurrenceWindowBounded() { error("DATE_WINDOW_INVALID") { dates.occurrences(input(), LocalDate.of(1900, 1, 1), LocalDate.of(2100, 1, 1)) } }
 @Test fun extendedGraphemesCountFamilyFlagsCombining() {
  assertEquals(1, graphemeCount("👩‍👩‍👧‍👦")); assertEquals(1, graphemeCount("🇨🇳")); assertEquals(1, graphemeCount("e\u0301")); assertEquals(1, graphemeCount("👍🏽"))
 }
 @Test fun sixtyFamilyEmojiAllowedSixtyOneRejected() = runBlocking {
  val (_, service, book) = fixture()
  val saved = service.saveEvent(event(book).copy(title = "👩‍👩‍👧‍👦".repeat(60)))
  assertEquals(60, graphemeCount(saved.title))
  failure("INPUT_TOO_LONG") { service.saveEvent(event(book).copy(title = "👩‍👩‍👧‍👦".repeat(61))) }
 }
 @Test fun whitespaceAndUnsafeSurrogatesRejected() = runBlocking {
  val (_, service, book) = fixture()
  failure("INPUT_REQUIRED") { service.saveEvent(event(book).copy(title = " \n\t")) }
  failure("INPUT_INVALID") { service.saveEvent(event(book).copy(title = "bad\uD800")) }
  failure("INPUT_REQUIRED") { service.saveEvent(event(book).copy(greeting = "  ")) }
 }
 @Test fun byteLimitIsIndependentOfGraphemeLimit() = runBlocking {
  val (_, service, book) = fixture()
  val title = "a" + "\u0301".repeat(3000)
  assertEquals(1, graphemeCount(title))
  failure("INPUT_BYTE_LIMIT") { service.saveEvent(event(book).copy(title = title)) }
 }
 @Test fun normalAndPreciseReminderModesAccepted() = runBlocking {
  val (_, service, book) = fixture()
  val saved = service.saveEvent(event(book).copy(reminders = listOf(ReminderRule(precisionMode = "precise"))))
  assertEquals("precise", saved.reminders.single().precisionMode)
  failure("REMINDER_INVALID") { service.saveEvent(event(book).copy(reminders = listOf(ReminderRule(precisionMode = "exact")))) }
 }
 @Test fun treeDirectChildrenAndThirdLevelRestriction() = runBlocking {
  val (repo, service, book) = fixture()
  val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id)); val leaf = service.saveEvent(event(book, parent = child.id))
  assertEquals(listOf(child.id), service.directChildren(repo.state.value, root.id).rows.map { it.event.id })
  assertEquals(listOf(leaf.id), service.directChildren(repo.state.value, child.id).rows.map { it.event.id })
  assertTrue(service.directChildren(repo.state.value, leaf.id).rows.isEmpty())
  val revision = repo.state.value.revision
  failure("TREE_DEPTH_EXCEEDED") { service.saveEvent(event(book, parent = leaf.id)) }
  assertEquals(revision, repo.state.value.revision)
 }
 @Test fun missingParentCycleAndCrossBookRejected() = runBlocking {
  val (repo, service, book) = fixture()
  failure("TREE_PARENT_NOT_FOUND") { service.saveEvent(event(book, parent = "missing")) }
  val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id))
  failure("TREE_CYCLE") { service.moveSubtree(root.id, book, child.id) }
  val other = repo.state.value.books[1].id
  failure("TREE_BOOK_MISMATCH") { service.saveEvent(event(other, parent = root.id)) }
 }
 @Test fun parentMustExistEvenReverseOrderedLibrary() {
  val s = defaultLibrary(); val book = s.books.first().id
  error("TREE_PARENT_NOT_FOUND") { LibraryValidator.validate(s.copy(events = listOf(event(book, "child", "missing")))) }
 }
 @Test fun updatesRequireExpectedVersionAndOperationIdIsIdempotent() = runBlocking {
  val (repo, service, book) = fixture(); val raw = event(book)
  val saved = service.saveEvent(raw, operationId = "one")
  assertEquals(saved, service.saveEvent(raw, operationId = "one")); assertEquals(1, repo.state.value.events.size)
  failure("VERSION_CONFLICT") { service.saveEvent(saved.copy(title = "edit")) }
  val edited = service.saveEvent(saved.copy(title = "edit"), saved.version)
  assertEquals(2L, edited.version)
 }
 @Test fun bookNameNfcUniqueProtectedCannotDelete() = runBlocking {
  val (repo, service, _) = fixture(); service.saveBook(Book(name = "Café"))
  failure("BOOK_NAME_CONFLICT") { service.saveBook(Book(name = "cafe\u0301")) }
  failure("BOOK_PROTECTED") { service.deleteBook(repo.state.value.books.first { it.isProtected }.id, true) }
 }
 @Test fun deletingBookMovesToUnclassifiedAndCanTrash() = runBlocking {
  val (repo, service, _) = fixture(); val book = service.saveBook(Book(name = "custom")); val root = service.saveEvent(event(book.id)); val child = service.saveEvent(event(book.id, parent = root.id))
  service.deleteBook(book.id, true)
  val s = repo.state.value
  assertEquals(s.books.first { it.isProtected }.id, s.event(root.id).bookId); assertEquals("trash", s.lifecycle(child.id))
  service.restoreCause(s.causes.single().id); assertEquals("active", repo.state.value.lifecycle(child.id))
 }
 @Test fun copyingSubtreeHasNewIdsAndIndependentGreetingAndNoReminder() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book).copy(greeting = "hello", reminders = listOf(ReminderRule(enabled = true))))
  val child = service.saveEvent(event(book, parent = root.id)); val id = service.copySubtree(root.id)
  val copied = repo.state.value.event(id)
  assertNotEquals(root.id, id); assertEquals("hello", copied.greeting); assertFalse(copied.reminders.single().enabled)
  assertNotEquals(child.id, service.directChildren(repo.state.value, id).rows.single().event.id)
 }
 @Test fun moveWholeTreeKeepsDirectParentRelations() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id)); val dest = repo.state.value.books[1].id
  service.moveSubtree(root.id, dest, null)
  assertEquals(dest, repo.state.value.event(child.id).bookId); assertEquals(root.id, repo.state.value.event(child.id).parentId)
 }
 @Test fun overlappingArchiveCausesRestoreIndependently() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id))
  val childCause = service.setLifecycle(listOf(child.id), "archive"); val rootCause = service.setLifecycle(listOf(root.id, child.id), "archive")
  assertEquals(2, repo.state.value.causes.size)
  service.restoreCause(rootCause); assertEquals("active", repo.state.value.lifecycle(root.id)); assertEquals("archived", repo.state.value.lifecycle(child.id))
  service.restoreCause(childCause); assertEquals("active", repo.state.value.lifecycle(child.id))
 }
 @Test fun trashAndPurgeAreExplicitAndFixHome() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book)); service.saveHome(HomeConfig("fixed", root.id))
  failure("PURGE_NOT_IN_TRASH") { service.purge(listOf(root.id)) }
  service.setLifecycle(listOf(root.id), "trash"); failure("EVENT_IN_TRASH") { service.saveEvent(root.copy(title = "edit"), root.version) }
  service.purge(listOf(root.id)); assertTrue(repo.state.value.events.isEmpty()); assertEquals("auto", repo.state.value.home.heroMode)
 }
 @Test fun goalProgressCountsOnlyEligibleDirectGoals() = runBlocking {
  val (repo, service, book) = fixture()
  fun goal(parent: String? = null) = event(book, parent = parent).copy(kind = "goal", goal = GoalDetail("2026-01-01"))
  val root = service.saveEvent(goal()); val complete = service.saveEvent(goal(root.id)); service.saveEvent(goal(root.id)); val canceled = service.saveEvent(goal(root.id)); val archived = service.saveEvent(goal(root.id)); service.saveEvent(event(book, parent = root.id)); service.saveEvent(goal(complete.id))
  service.setGoalState(complete.id, "completed"); service.setGoalState(canceled.id, "canceled"); service.setLifecycle(listOf(archived.id), "archive")
  assertEquals(1 to 2, service.completionRate(repo.state.value, root.id))
  assertEquals("not_started", repo.state.value.event(root.id).goal!!.state)
 }
 @Test fun goalCompletionReopenPreservesActions() = runBlocking {
  val (repo, service, book) = fixture(); val goal = service.saveEvent(event(book).copy(kind = "goal", goal = GoalDetail("2026-01-01")))
  val action = service.saveAction(ActionRecord(goalEventId = goal.id, date = "2026-10-31", body = "practice", minutes = 0))
  service.setGoalState(goal.id, "completed"); assertNotNull(repo.state.value.event(goal.id).goal!!.completedAt)
  service.setGoalState(goal.id, "in_progress"); assertNull(repo.state.value.event(goal.id).goal!!.completedAt); assertEquals(action.id, repo.state.value.actions.single().id)
  failure("GOAL_HAS_HISTORY") { val e = repo.state.value.event(goal.id); service.saveEvent(e.copy(kind = "ordinary", goal = null), e.version) }
 }
 @Test fun actionsFutureInvalidMinutesAndVersionRejected() = runBlocking {
  val (_, service, book) = fixture(); val goal = service.saveEvent(event(book).copy(kind = "goal", goal = GoalDetail("2026-01-01")))
  failure("ACTION_FUTURE_DATE") { service.saveAction(ActionRecord(goalEventId = goal.id, date = "2026-11-01", body = "future")) }
  failure("INPUT_RANGE") { service.saveAction(ActionRecord(goalEventId = goal.id, date = "2026-10-31", body = "long", minutes = 1441)) }
 }
 @Test fun tagsBatchAndSearchCoverBookGreetingAndTag() = runBlocking {
  val (repo, service, book) = fixture(); val event = service.saveEvent(event(book).copy(greeting = "story")); val tag = service.saveTag(Tag(name = "family")); service.setTags(listOf(event.id), listOf(tag.id))
  assertEquals(event.id, service.search(repo.state.value, "FAMILY").single().id)
  assertEquals(event.id, service.search(repo.state.value, "story").single().id)
  service.setLifecycle(listOf(event.id), "archive"); assertTrue(service.search(repo.state.value, "family").isEmpty()); assertEquals(1, service.search(repo.state.value, "family", "archived").size)
 }
 @Test fun directPaginationRevisionRejectsStaleCursor() = runBlocking {
  val (repo, service, book) = fixture(); val root = service.saveEvent(event(book))
  repeat(21) { service.saveEvent(event(book, parent = root.id)) }
  val first = service.directChildren(repo.state.value, root.id); assertEquals(20, first.rows.size); assertTrue(first.hasMore)
  assertEquals(1, service.directChildren(repo.state.value, root.id, cursor = first.cursor).rows.size)
  service.saveEvent(event(book))
  error("CURSOR_STALE") { service.directChildren(repo.state.value, root.id, cursor = first.cursor) }
 }
 @Test fun goalSameDayProgressAvoidsZeroDivision() = runBlocking {
  val (repo, service, book) = fixture(); val e = service.saveEvent(event(book).copy(kind = "goal", date = DateSpec(year = 2026, month = 10, day = 31), goal = GoalDetail("2026-10-31")))
  assertEquals(1.0, service.timeProgress(repo.state.value, e.id), 0.0); assertNull(service.completionRate(repo.state.value, e.id))
 }
 @Test fun restoreCasEpochAndRollback() = runBlocking {
  val (repo, service, book) = fixture(); val before = repo.state.value
  service.saveEvent(event(book))
  failure("PREVIEW_STALE") { repo.install(before, before.revision, before.epoch) }
  val now = repo.state.value; val installed = repo.install(before, now.revision, now.epoch)
  assertNotEquals(now.epoch, installed.epoch)
  failure("LIBRARY_STALE") { repo.transaction("old", now.epoch) { Change(it, Unit) } }
 }
 @Test fun repositoryFailedChangeDoesNotAdvanceOrLoseData() = runBlocking {
  val (repo, _, _) = fixture(); val before = repo.state.value
  failure("CAPACITY_LIMIT") { repo.transaction { Change(it.copy(books = emptyList()), Unit) } }
  assertEquals(before, repo.state.value)
 }
 @Test fun assetPathRejectsTraversalAndAbsolutePaths() {
  assertTrue(safeAssetPath("assets/a.jpg")); listOf("../a", "/tmp/a", "x/../a", "a\\b", "C:a", "a//b").forEach { assertFalse(safeAssetPath(it)) }
 }
 @Test fun reminderBirthdayDefaultsAndLimit() = runBlocking {
  val (_, service, book) = fixture(); val birthday = service.saveEvent(event(book).copy(kind = "birthday", repeat = RecurrenceSpec("yearly")))
  assertEquals(listOf(7, 0), birthday.reminders.map { it.offsetValue }); assertTrue(birthday.reminders.all { it.enabled && it.localTime == "09:00" })
  failure("REMINDER_LIMIT") { service.saveEvent(event(book).copy(reminders = List(6) { ReminderRule() })) }
 }
 @Test fun eventAndNewTagsCommitAtomically() = runBlocking {
  val (repo, service, book) = fixture(); val before = repo.state.value
  failure("DATE_INVALID") { service.saveEventWithTagNames(event(book).copy(date = DateSpec(year = 2026, month = 2, day = 31)), listOf("newtag")) }
  assertEquals(before, repo.state.value)
  val saved = service.saveEventWithTagNames(event(book), listOf("Work", "work"))
  assertEquals(1, saved.tagIds.size); assertEquals(1, repo.state.value.tags.size)
 }
 @Test fun calendarBatchAllOrNothing() = runBlocking {
  val (repo, service, book) = fixture(); val before = repo.state.value
  failure("DATE_INVALID") { service.saveEventsBatch(listOf(event(book), event(book).copy(date = DateSpec(year = 2026, month = 2, day = 31)))) }
  assertEquals(before, repo.state.value)
  val all = service.saveEventsBatch(listOf(event(book), event(book)))
  assertEquals(2, all); assertEquals(1L, repo.state.value.revision)
 }
 @Test fun validatorLimitsTagsForEveryWritePath() = runBlocking {
  val (repo, service, book) = fixture()
  val tags = List(21) { service.saveTag(Tag(name = "tag$it")) }
  val e = service.saveEvent(event(book))
  val before = repo.state.value
  failure("TAG_LIMIT") { service.setTags(listOf(e.id), tags.map { it.id }) }
  assertEquals(before, repo.state.value)
  error("TAG_LIMIT") { LibraryValidator.validate(before.copy(events = listOf(e.copy(tagIds = tags.map { it.id }))), dates) }
 }
 @Test fun batchMoveRejectsInvalidSecondRootAtomically() = runBlocking {
  val (repo, service, book) = fixture()
  val destRoot = service.saveEvent(event(book)); val destChild = service.saveEvent(event(book, parent = destRoot.id))
  val small = service.saveEvent(event(book)); val deep = service.saveEvent(event(book)); service.saveEvent(event(book, parent = deep.id))
  val before = repo.state.value
  failure("TREE_DEPTH_EXCEEDED") { service.moveSubtrees(listOf(small.id, deep.id), book, destChild.id) }
  assertEquals(before, repo.state.value)
  assertNull(repo.state.value.event(small.id).parentId)
 }
 @Test fun batchMoveDeduplicatesSelectedDescendantsAndCommitsOnce() = runBlocking {
  val (repo, service, book) = fixture()
  val root = service.saveEvent(event(book)); val child = service.saveEvent(event(book, parent = root.id)); val other = service.saveEvent(event(book))
  val before = repo.state.value.revision; val destination = repo.state.value.books[1].id
  assertEquals(2, service.moveSubtrees(listOf(root.id, child.id, other.id), destination))
  assertEquals(before + 1, repo.state.value.revision)
  assertEquals(root.id, repo.state.value.event(child.id).parentId)
  assertEquals(destination, repo.state.value.event(child.id).bookId)
 }
}
