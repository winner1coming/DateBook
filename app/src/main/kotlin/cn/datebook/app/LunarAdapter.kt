package cn.datebook.app

import cn.datebook.core.LunarPort
import com.nlf.calendar.Lunar
import com.nlf.calendar.LunarYear
import com.nlf.calendar.Solar
import java.time.LocalDate

/** Pinned offline engine; never consults device ICU or the network. */
class LunarAdapter : LunarPort {
 override fun solar(year: Int, month: Int, day: Int, leapMonth: Boolean, leapPolicy: String, smallMonthPolicy: String): LocalDate? {
  if (year !in 1901..2099 || month !in 1..12 || day !in 1..30) return null
  val lunarYear = LunarYear.fromYear(year)
  var target = lunarYear.getMonth(if (leapMonth) -month else month)
  if (target == null && leapMonth && leapPolicy == "normal_fallback") target = lunarYear.getMonth(month)
  target ?: return null
  if (day > target.dayCount && smallMonthPolicy == "skip") return null
  val solar = Lunar.fromYmd(year, target.month, minOf(day, target.dayCount)).solar
  return LocalDate.of(solar.year, solar.month, solar.day)
 }
 override fun lunarYear(date: LocalDate): Int = Solar.fromYmd(date.year, date.monthValue, date.dayOfMonth).lunar.year
}
