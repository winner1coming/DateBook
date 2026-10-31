package cn.datebook.core

import java.time.*
import java.time.temporal.ChronoUnit
import kotlin.math.ceil
import kotlin.math.floor

/** 日期事实与当前时钟的纯投影；不会改写原始锚点或创建年度副本。 */
class DateEngine(private val clock: Clock, private val lunar: LunarPort) {
 fun currentDate(): LocalDate = LocalDate.now(clock)
 fun currentInstant(): Instant = clock.instant()
 fun validate(input: DateInput) {
  val d = input.date; val r = input.repeat
  demand(input.kind in setOf("ordinary", "birthday", "memorial", "holiday", "goal"), "INPUT_ENUM", "kind")
  demand(input.countMode in setOf("up", "down"), "INPUT_ENUM", "countMode")
  demand(d.calendar in setOf("gregorian", "lunar"), "INPUT_ENUM", "date.calendar")
  demand(d.feb29Policy in setOf("feb28", "mar01") && d.lunarLeapPolicy in setOf("normal_fallback", "leap_only") && d.lunarSmallMonthPolicy in setOf("month_end", "skip"), "INPUT_ENUM", "date.policy")
  demand(r.frequency in setOf("none", "yearly", "monthly", "weekly", "every_n_days"), "INPUT_ENUM", "repeat.frequency")
  demand(if (r.frequency == "every_n_days") r.intervalDays != null && r.intervalDays in 1..365 else r.intervalDays == null, "DATE_REPEAT_INVALID", "repeat.intervalDays")
  demand(d.month in 1..12 && d.day in 1..31, "DATE_INVALID", "date")
  demand(d.year != null || input.kind == "birthday" && r.frequency == "yearly", "DATE_YEAR_REQUIRED", "date.year")
  demand(input.kind != "birthday" || d.allDay && r.frequency == "yearly" && input.countMode == "down", "DATE_KIND_INVALID", "kind")
  demand(input.countMode != "up" || r.frequency == "none", "DATE_REPEAT_INVALID", "countMode")
  demand(input.kind != "goal" || d.calendar == "gregorian" && d.allDay && r.frequency == "none" && input.countMode == "down", "GOAL_DATE_INVALID", "date")
  demand(d.feb29Policy.isNotBlank() && d.calendarEngineVersion.length <= 64, "DATE_INVALID", "date")
  if (d.allDay) demand(d.localTime == null && d.zoneId == null, "DATE_TIME_INVALID", "date.localTime")
  else {
   demand(d.calendar == "gregorian" && d.localTime != null && d.zoneId != null, "DATE_TIME_INVALID", "date")
   try { demand(Regex("([01][0-9]|2[0-3]):[0-5][0-9]").matches(d.localTime!!), "DATE_TIME_INVALID"); ZoneId.of(d.zoneId) }
   catch (e: DateTimeException) { throw AppException("DATE_TIME_INVALID", "date") }
  }
  if (d.calendar == "gregorian") {
   demand(!d.leapMonth && (d.year == null || d.year in 1900..2100), "DATE_RANGE", "date.year")
   try { LocalDate.of(d.year ?: 2000, d.month, d.day) } catch (e: DateTimeException) { throw AppException("DATE_INVALID", "date") }
  } else {
   demand(d.allDay && d.day <= 30 && r.frequency in setOf("none", "yearly") && (d.year == null || d.year in 1901..2099), "DATE_RANGE", "date")
   if (d.year != null) demand(lunarDate(d, d.year) != null, "DATE_INVALID", "date")
  }
  if (r.until != null) {
   val until = parseDate(r.until, "repeat.until")
   demand(r.frequency != "none", "DATE_REPEAT_INVALID", "repeat.until")
   if (d.year != null) anchor(input)?.let { demand(!until.isBefore(it), "DATE_UNTIL_INVALID", "repeat.until") }
  }
 }

 fun nextOccurrence(input: DateInput, after: LocalDate, inclusive: Boolean = true): Occurrence? {
  validate(input)
  val start = if (inclusive) after else after.plusDays(1)
  val d = input.date; val r = input.repeat
  val until = r.until?.let { parseDate(it) }
  if (until != null && start > until) return null
  val candidate: LocalDate? = when (r.frequency) {
   "none" -> anchor(input)?.takeIf { it >= start }
   "yearly" -> {
    val first = if (d.calendar == "lunar") maxOf(1901, lunar.lunarYear(start) - 1, d.year ?: 1901) else maxOf(1900, start.year, d.year ?: 1900)
    val last = if (d.calendar == "lunar") 2099 else 2100
    var found: LocalDate? = null
    for (year in first..last) {
     val date = if (d.calendar == "lunar") lunarDate(d, year) else yearlyDate(d, year)
     if (date != null && date >= start && (until == null || date <= until) && (found == null || date < found)) found = date
     if (found != null && (d.calendar != "lunar" || year > first)) break
    }
    found
   }
   "monthly" -> {
    val base = anchor(input)!!
    var month = YearMonth.from(if (start < base) base else start)
    var date = month.atDay(minOf(d.day, month.lengthOfMonth()))
    if (date < start || date < base) { month = month.plusMonths(1); date = month.atDay(minOf(d.day, month.lengthOfMonth())) }
    date.takeIf { it.year <= 2100 }
   }
   else -> {
    val base = anchor(input)!!
    val step = if (r.frequency == "weekly") 7L else r.intervalDays!!.toLong()
    val delta = ChronoUnit.DAYS.between(base, start).coerceAtLeast(0)
    base.plusDays((delta + step - 1) / step * step).takeIf { it.year <= 2100 }
   }
  }
  if (candidate == null || until != null && candidate > until) return null
  return occurrence(input, candidate)
 }

 fun occurrences(input: DateInput, from: LocalDate, to: LocalDate): List<Occurrence> {
  demand(to >= from && ChronoUnit.DAYS.between(from, to) <= 36600, "DATE_WINDOW_INVALID")
  val out = ArrayList<Occurrence>(); var cursor = from
  while (cursor <= to) {
   val next = nextOccurrence(input, cursor) ?: break
   if (next.date > to) break
   out += next
   demand(out.size <= 10000, "DATE_WINDOW_LIMIT")
   cursor = next.date.plusDays(1)
  }
  return out
 }

 fun evaluate(input: DateInput, now: Instant = clock.instant(), zone: ZoneId = clock.zone): DateProjection {
  validate(input)
  val d = input.date
  val effectiveZone = if (d.allDay) zone else ZoneId.of(d.zoneId)
  val today = now.atZone(effectiveZone).toLocalDate()
  val tomorrow = today.plusDays(1).atStartOfDay(effectiveZone).toInstant()
  if (input.countMode == "up") {
   val start = occurrence(input, anchor(input)!!)
   val delta = if (d.allDay) ChronoUnit.DAYS.between(start.date, today) else floor(Duration.between(start.instant, now).seconds / 86400.0).toLong()
   if (delta < 0) {
    val boundary = if (d.allDay) tomorrow else start.instant!!.minusSeconds((-delta - 1) * 86400)
    return DateProjection(-delta, "尚未开始", start, validUntil = minOf(tomorrow, boundary))
   }
   val count = delta + if (input.includeStartDay) 1 else 0
   val boundary = if (d.allDay) tomorrow else start.instant!!.plusSeconds((delta + 1) * 86400)
   return DateProjection(count, "已过 $count 天", start, start.date == today, validUntil = minOf(tomorrow, boundary))
  }
  var next = nextOccurrence(input, today)
  if (next?.instant != null && next.instant!! < now && input.repeat.frequency != "none") next = nextOccurrence(input, today, false)
  if (next == null && input.repeat.frequency != "none") return DateProjection(null, "已无后续日期", null, exhausted = true, validUntil = tomorrow)
  if (next == null) next = occurrence(input, anchor(input)!!)
  val isToday = next.date == today
  val age = if (input.kind == "birthday" && d.year != null) (if (d.calendar == "lunar") lunar.lunarYear(next.date) else next.date.year) - d.year else null
  if (d.allDay) {
   val diff = ChronoUnit.DAYS.between(today, next.date)
   val label = when { diff == 0L -> if (input.kind == "birthday") "今天生日" else "就是今天"; diff > 0 -> "还有 $diff 天"; else -> "已过 ${-diff} 天" }
   return DateProjection(kotlin.math.abs(diff), label, next, isToday, age = age, validUntil = tomorrow)
  }
  val duration = Duration.between(now, next.instant)
  val seconds = duration.seconds.toDouble() + duration.nano / 1_000_000_000.0
  val days = if (seconds > 0) ceil(seconds / 86400.0).toLong() else floor(-seconds / 86400.0).toLong()
  val label = when { seconds > 0 -> "还有 $days 天"; seconds == 0.0 -> "就是现在"; days == 0L -> "已过不足 1 天"; else -> "已过 $days 天" }
  val boundary = if (seconds > 0) next.instant!!.minusSeconds((days - 1) * 86400) else next.instant!!.plusSeconds((days + 1) * 86400)
  return DateProjection(days, label, next, isToday, age = age, validUntil = minOf(tomorrow, boundary))
 }

 private fun anchor(input: DateInput): LocalDate? = input.date.let { d ->
  val year = d.year ?: return null
  if (d.calendar == "lunar") lunarDate(d, year) else LocalDate.of(year, d.month, d.day)
 }
 private fun lunarDate(d: DateSpec, year: Int) = lunar.solar(year, d.month, d.day, d.leapMonth, d.lunarLeapPolicy, d.lunarSmallMonthPolicy)
 private fun yearlyDate(d: DateSpec, year: Int): LocalDate = if (d.month == 2 && d.day == 29 && !Year.isLeap(year.toLong())) {
  if (d.feb29Policy == "mar01") LocalDate.of(year, 3, 1) else LocalDate.of(year, 2, 28)
 } else LocalDate.of(year, d.month, d.day)
 private fun occurrence(input: DateInput, date: LocalDate): Occurrence {
  val d = input.date
  // atZone 默认：DST 缺口向前推移到有效时刻，重叠选较早偏移。
  val instant = if (d.allDay) null else date.atTime(LocalTime.parse(d.localTime)).atZone(ZoneId.of(d.zoneId)).toInstant()
  val fallback = when { d.calendar == "gregorian" && d.month == 2 && d.day == 29 && date.dayOfMonth != 29 -> d.feb29Policy; else -> null }
  return Occurrence(date, instant, fallback)
 }
}

fun parseDate(value: String, field: String? = null): LocalDate = try {
 demand(Regex("[0-9]{4}-[0-9]{2}-[0-9]{2}").matches(value), "DATE_INVALID", field)
 LocalDate.parse(value)
} catch (e: DateTimeException) { throw AppException("DATE_INVALID", field) }
