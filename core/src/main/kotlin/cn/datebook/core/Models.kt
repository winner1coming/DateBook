package cn.datebook.core

import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.Serializable
import java.time.Clock
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.util.UUID

fun newId(): String = UUID.randomUUID().toString()

@Serializable data class Book(
 val id: String = newId(), val name: String, val builtinKey: String? = null,
 val iconKey: String = "book", val colorArgb: Int = -13278421,
 val coverAssetId: String? = null, val sortRank: Long = 0,
 val createdAt: Long = 0, val updatedAt: Long = 0, val version: Long = 1,
 val isProtected: Boolean = builtinKey == "uncategorized"
)
@Serializable data class DateSpec(
 val calendar: String = "gregorian", val year: Int? = null, val month: Int = 1,
 val day: Int = 1, val leapMonth: Boolean = false, val allDay: Boolean = true,
 val localTime: String? = null, val zoneId: String? = null,
 val feb29Policy: String = "feb28", val lunarLeapPolicy: String = "normal_fallback",
 val lunarSmallMonthPolicy: String = "month_end", val calendarEngineVersion: String = "lunar-1.7.7"
)
@Serializable data class RecurrenceSpec(val frequency: String = "none", val intervalDays: Int? = null, val until: String? = null)
@Serializable data class Appearance(
 val backgroundKind: String = "gradient", val assetId: String? = null,
 val presetKey: String = "forest", val solidArgb: Int = -13278421,
 val focusX: Double = .5, val focusY: Double = .5, val dimAmount: Double = .35,
 val textColorMode: String = "auto", val fontKey: String = "system"
)
@Serializable data class GoalDetail(
 val startDate: String, val state: String = "not_started", val completedAt: Long? = null,
 val includeInParent: Boolean = true
)
@Serializable data class ReminderRule(
 val id: String = newId(), val enabled: Boolean = false, val offsetUnit: String = "days",
 val offsetValue: Int = 0, val localTime: String? = "09:00",
 val precisionMode: String = "normal", val version: Long = 1
)
@Serializable data class Event(
 val id: String = newId(), val bookId: String, val parentId: String? = null,
 val title: String, val kind: String = "ordinary", val countMode: String = "down",
 val includeStartDay: Boolean = false, val greeting: String = "",
 val homeVisible: Boolean = parentId == null, val pinned: Boolean = false,
 val sortRank: Long = 0, val date: DateSpec, val repeat: RecurrenceSpec = RecurrenceSpec(),
 val appearance: Appearance = Appearance(), val goal: GoalDetail? = null,
 val reminders: List<ReminderRule> = emptyList(), val tagIds: List<String> = emptyList(),
 val createdAt: Long = 0, val updatedAt: Long = 0, val version: Long = 1
)
@Serializable data class ActionRecord(
 val id: String = newId(), val goalEventId: String, val date: String,
 val body: String, val minutes: Int? = null, val createdAt: Long = 0,
 val updatedAt: Long = 0, val version: Long = 1
)
@Serializable data class Tag(val id: String = newId(), val name: String, val createdAt: Long = 0)
@Serializable data class Asset(
 val id: String = newId(), val sha256: String, val relativePath: String,
 val mimeType: String, val bytes: Long, val width: Int, val height: Int, val createdAt: Long = 0
)
@Serializable data class LifecycleCause(
 val id: String = newId(), val kind: String, val sourceEventId: String? = null,
 val sourceBookId: String? = null, val createdAt: Long, val purgeAfter: Long? = null,
 val members: List<String>
)
@Serializable data class HomeConfig(
 val heroMode: String = "auto", val fixedEventId: String? = null,
 val sortMode: String = "date", val selectedBookId: String? = null
)
@Serializable data class ImportOrigin(
 val sourceRef: String, val localEventId: String? = null
)
@Serializable data class ImportBatch(
 val id: String = newId(), val format: String, val sourceExportId: String,
 val fileSha256: String, val importedAt: Long, val provenance: List<ImportOrigin> = emptyList()
)
@Serializable data class LibraryState(
 val id: String = newId(), val name: String = "我的重要日子", val revision: Long = 0,
 val epoch: String = newId(), val createdAt: Long = 0, val updatedAt: Long = 0,
 val books: List<Book> = emptyList(), val events: List<Event> = emptyList(),
 val actions: List<ActionRecord> = emptyList(), val tags: List<Tag> = emptyList(),
 val assets: List<Asset> = emptyList(), val causes: List<LifecycleCause> = emptyList(),
 val home: HomeConfig = HomeConfig(), val imports: List<ImportBatch> = emptyList()
)

data class Change<T>(val state: LibraryState, val result: T)
interface LibraryRepository {
 val state: StateFlow<LibraryState>
 suspend fun <T> transaction(operationId: String = newId(), expectedEpoch: String? = null,
  block: (LibraryState) -> Change<T>): T
 suspend fun install(candidate: LibraryState, expectedRevision: Long, expectedEpoch: String): LibraryState
}

class AppException(val code: String, val field: String? = null, message: String = code) : IllegalArgumentException(message)
fun demand(ok: Boolean, code: String, field: String? = null) { if (!ok) throw AppException(code, field) }

data class DateInput(val date: DateSpec, val repeat: RecurrenceSpec, val countMode: String = "down",
 val includeStartDay: Boolean = false, val kind: String = "ordinary")
fun Event.dateInput() = DateInput(date, repeat, countMode, includeStartDay, kind)
data class Occurrence(val date: LocalDate, val instant: Instant? = null, val fallback: String? = null)
data class DateProjection(
 val days: Long?, val label: String, val occurrence: Occurrence?, val today: Boolean = false,
 val exhausted: Boolean = false, val age: Int? = null, val validUntil: Instant? = null
)
interface LunarPort {
 fun solar(year: Int, month: Int, day: Int, leapMonth: Boolean, leapPolicy: String, smallMonthPolicy: String): LocalDate?
 fun lunarYear(date: LocalDate): Int
}
data class ChildSummary(val event: Event, val depth: Int, val directChildCount: Int, val presentation: DateProjection)
data class ChildPage(val rows: List<ChildSummary>, val cursor: String?, val hasMore: Boolean, val revision: Long)

fun LibraryState.event(id: String): Event = events.firstOrNull { it.id == id } ?: throw AppException("EVENT_NOT_FOUND")
fun LibraryState.lifecycle(id: String): String = when {
 causes.any { it.kind == "trash" && id in it.members } -> "trash"
 causes.any { it.kind == "archive" && id in it.members } -> "archived"
 else -> "active"
}
fun defaultLibrary(now: Long = System.currentTimeMillis()): LibraryState = LibraryState(
 createdAt = now, updatedAt = now, books = listOf("birthday" to "生日本", "memorial" to "纪念日本",
  "holiday" to "假日本", "goal" to "目标本", "uncategorized" to "未分类").mapIndexed { i, p ->
  Book(name = p.second, builtinKey = p.first, iconKey = p.first, sortRank = i.toLong(), createdAt = now, updatedAt = now)
 })
