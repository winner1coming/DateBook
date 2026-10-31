package cn.datebook.app

import cn.datebook.core.*
import org.junit.Assert.*
import org.junit.Test
import java.time.Clock
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

/**
 * 固定样例来自香港天文台逐日对照表，核验于 2026-10-31。
 * https://www.hko.gov.hk/en/gts/time/calendar/text/files/T2024e.txt
 * https://www.hko.gov.hk/en/gts/time/calendar/text/files/T2025e.txt
 * https://www.hko.gov.hk/en/gts/time/calendar/text/files/T2026e.txt
 * 只测试离线算法输出，不在测试执行时请求网络。
 */
class LunarGoldenTests {
 private val port = LunarAdapter()
 private val zone = ZoneId.of("Asia/Shanghai")
 private fun solar(year: Int, month: Int, day: Int) = port.solar(year, month, day, false, "normal_fallback", "month_end")
 @Test fun newYear2024() { assertEquals(LocalDate.of(2024, 2, 10), solar(2024, 1, 1)) }
 @Test fun newYear2025() { assertEquals(LocalDate.of(2025, 1, 29), solar(2025, 1, 1)) }
 @Test fun newYear2026() { assertEquals(LocalDate.of(2026, 2, 17), solar(2026, 1, 1)) }
 @Test fun midAutumn2024() { assertEquals(LocalDate.of(2024, 9, 17), solar(2024, 8, 15)) }
 @Test fun midAutumn2025() { assertEquals(LocalDate.of(2025, 10, 6), solar(2025, 8, 15)) }
 @Test fun lunarYearUsesNewYearNotJanuaryFirst() {
  assertEquals(2025, port.lunarYear(LocalDate.of(2026, 2, 16)))
  assertEquals(2026, port.lunarYear(LocalDate.of(2026, 2, 17)))
 }
 @Test fun lunarLeapMonth2025DistinguishesNormalAndLeapSix() {
  assertEquals(LocalDate.of(2025, 6, 25), solar(2025, 6, 1))
  assertEquals(LocalDate.of(2025, 7, 25), port.solar(2025, 6, 1, true, "leap_only", "month_end"))
 }
 @Test fun missingLeapMonthCanFallbackOrSkip() {
  assertEquals(solar(2026, 6, 1), port.solar(2026, 6, 1, true, "normal_fallback", "month_end"))
  assertNull(port.solar(2026, 6, 1, true, "leap_only", "month_end"))
 }
 @Test fun smallLunarMonthDoesNotInventThirtiethDay() {
  // 2024 正月为29天：3月9日廿九，3月10日二月初一。
  assertEquals(LocalDate.of(2024, 3, 9), port.solar(2024, 1, 30, false, "normal_fallback", "month_end"))
  assertNull(port.solar(2024, 1, 30, false, "normal_fallback", "skip"))
 }
 @Test fun lunarBirthdayKeepsTodayThenRollsOverNextCivilDay() {
  val clock = Clock.fixed(Instant.parse("2025-10-06T04:00:00Z"), zone)
  val engine = DateEngine(clock, port)
  val input = DateInput(DateSpec(calendar = "lunar", year = 2000, month = 8, day = 15), RecurrenceSpec("yearly"), kind = "birthday")
  assertEquals("今天生日", engine.evaluate(input).label)
  assertEquals(LocalDate.of(2026, 9, 25), engine.evaluate(input, Instant.parse("2025-10-06T16:00:00Z")).occurrence!!.date)
 }
 @Test fun everySupportedLunarYearHasOrderedFirstDays() {
  for (year in 1901..2099) {
   val first = solar(year, 1, 1)!!
   val last = solar(year, 12, 1)!!
   assertTrue(first < last)
   assertEquals(year, port.lunarYear(first))
  }
 }
 @Test fun outOfRangeAndImpossibleMonthReturnNull() {
  assertNull(port.solar(1900, 1, 1, false, "normal_fallback", "month_end"))
  assertNull(port.solar(2100, 1, 1, false, "normal_fallback", "month_end"))
  assertNull(port.solar(2026, 13, 1, false, "normal_fallback", "month_end"))
 }
}
