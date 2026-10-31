package cn.datebook.app.ui

import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.*

private val Context.localPreferences by preferencesDataStore("datebook-device")
class DevicePreferences(context: Context) {
 private val data = context.applicationContext.localPreferences
 val theme = data.data.map { it[stringPreferencesKey("theme")] ?: "system" }
 val weekMonday = data.data.map { it[booleanPreferencesKey("week_monday")] ?: true }
 val privatePreview = data.data.map { it[booleanPreferencesKey("private_preview")] ?: false }
 val replacementPinEpoch = data.data.map { it[stringPreferencesKey("replacement_pin_epoch")] }
 suspend fun replacementPinEpoch(value:String?) { data.edit { if(value==null)it.remove(stringPreferencesKey("replacement_pin_epoch"))else it[stringPreferencesKey("replacement_pin_epoch")]=value } }
 suspend fun theme(value: String) { require(value in setOf("system","light","dark")); data.edit { it[stringPreferencesKey("theme")] = value } }
 suspend fun weekMonday(value: Boolean) { data.edit { it[booleanPreferencesKey("week_monday")] = value } }
 suspend fun privatePreview(value: Boolean) { data.edit { it[booleanPreferencesKey("private_preview")] = value } }
 suspend fun saveDraft(key: String, value: String) { require(value.length <= 50000); data.edit { it[stringPreferencesKey("draft_$key")] = value } }
 suspend fun draft(key: String): String? = data.data.first()[stringPreferencesKey("draft_$key")]
 suspend fun deleteDraft(key: String) { data.edit { it.remove(stringPreferencesKey("draft_$key")) } }
 suspend fun clearDrafts() { data.edit { p -> p.asMap().keys.filter { it.name.startsWith("draft_") }.forEach { p.remove(stringPreferencesKey(it.name)) } } }
}
