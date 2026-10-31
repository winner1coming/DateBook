package cn.datebook.app.data

import android.database.Cursor
import androidx.room.*
import androidx.sqlite.db.SupportSQLiteQuery

// Normalized facts; device-only rows are deliberately not part of LibraryState backups.

@Entity(tableName = "library", primaryKeys = ["id"], indices = [
 Index(value = ["singleton"], unique = true)])
data class DbLibrary(
 val id: String,
 @ColumnInfo(defaultValue = "1") val singleton: Long,
 val name: String,
 @ColumnInfo(defaultValue = "0") val content_revision: Long,
 val created_at: Long,
 val updated_at: Long
)

@Entity(tableName = "asset", primaryKeys = ["id"], indices = [
 Index(value = ["sha256"], unique = true),
 Index(value = ["relative_path"], unique = true)])
data class DbAsset(
 val id: String,
 val sha256: String,
 val relative_path: String,
 val mime_type: String,
 val byte_size: Long,
 val width: Long,
 val height: Long,
 val created_at: Long
)

@Entity(tableName = "book", primaryKeys = ["id"], indices = [
 Index(value = ["name_key"], unique = true),
 Index(value = ["builtin_key"], unique = true),
 Index(value = ["library_id"], unique = false),
 Index(value = ["cover_asset_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbLibrary::class, parentColumns = ["id"], childColumns = ["library_id"], onDelete = ForeignKey.RESTRICT, deferred = false),
 ForeignKey(entity = DbAsset::class, parentColumns = ["id"], childColumns = ["cover_asset_id"], onDelete = ForeignKey.RESTRICT, deferred = false)])
data class DbBook(
 val id: String,
 val library_id: String,
 val name: String,
 val name_key: String,
 val builtin_key: String?,
 @ColumnInfo(defaultValue = "0") val is_protected: Long,
 @ColumnInfo(defaultValue = "'book'") val icon_key: String,
 @ColumnInfo(defaultValue = "-13278421") val color_argb: Long,
 val cover_asset_id: String?,
 @ColumnInfo(defaultValue = "0") val sort_rank: Long,
 val created_at: Long,
 val updated_at: Long,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "event", primaryKeys = ["id"], indices = [
 Index(value = ["id", "book_id"], unique = true),
 Index(value = ["parent_id", "sort_rank", "id"], unique = false, name = "event_by_parent"),
 Index(value = ["book_id", "sort_rank", "id"], unique = false, name = "event_by_book"),
 Index(value = ["home_visible", "pinned", "updated_at"], unique = false, name = "event_by_home"),
 Index(value = ["parent_id", "book_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbBook::class, parentColumns = ["id"], childColumns = ["book_id"], onDelete = ForeignKey.RESTRICT, deferred = false),
 ForeignKey(entity = DbEvent::class, parentColumns = ["id", "book_id"], childColumns = ["parent_id", "book_id"], onDelete = ForeignKey.NO_ACTION, deferred = true)])
data class DbEvent(
 val id: String,
 val book_id: String,
 val parent_id: String?,
 val title: String,
 val kind: String,
 val count_mode: String,
 @ColumnInfo(defaultValue = "0") val include_start_day: Long,
 @ColumnInfo(defaultValue = "''") val greeting: String,
 @ColumnInfo(defaultValue = "1") val home_visible: Long,
 @ColumnInfo(defaultValue = "0") val pinned: Long,
 @ColumnInfo(defaultValue = "0") val sort_rank: Long,
 val created_at: Long,
 val updated_at: Long,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "event_date", primaryKeys = ["event_id"], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbEventDate(
 val event_id: String,
 val calendar_type: String,
 val anchor_year: Long?,
 val anchor_month: Long,
 val anchor_day: Long,
 @ColumnInfo(defaultValue = "0") val is_leap_month: Long,
 @ColumnInfo(defaultValue = "1") val all_day: Long,
 val local_time: String?,
 val zone_id: String?,
 @ColumnInfo(defaultValue = "'feb28'") val feb29_policy: String,
 @ColumnInfo(defaultValue = "'normal_fallback'") val lunar_leap_policy: String,
 @ColumnInfo(defaultValue = "'month_end'") val lunar_small_month_policy: String,
 @ColumnInfo(defaultValue = "'calendar-v1'") val calendar_engine_version: String
)

@Entity(tableName = "recurrence", primaryKeys = ["event_id"], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbRecurrence(
 val event_id: String,
 val frequency: String,
 val interval_days: Long?,
 val until_iso: String?
)

@Entity(tableName = "appearance", primaryKeys = ["event_id"], indices = [
 Index(value = ["asset_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbAsset::class, parentColumns = ["id"], childColumns = ["asset_id"], onDelete = ForeignKey.RESTRICT, deferred = false)])
data class DbAppearance(
 val event_id: String,
 @ColumnInfo(defaultValue = "'gradient'") val background_kind: String,
 val asset_id: String?,
 @ColumnInfo(defaultValue = "'forest'") val preset_key: String,
 @ColumnInfo(defaultValue = "-13278421") val solid_argb: Long,
 @ColumnInfo(defaultValue = "0.5") val focus_x: Double,
 @ColumnInfo(defaultValue = "0.5") val focus_y: Double,
 @ColumnInfo(defaultValue = "0.35") val dim_amount: Double,
 @ColumnInfo(defaultValue = "'auto'") val text_color_mode: String,
 @ColumnInfo(defaultValue = "'system'") val font_key: String
)

@Entity(tableName = "goal_detail", primaryKeys = ["event_id"], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbGoalDetail(
 val event_id: String,
 val start_iso: String,
 val state: String,
 val completed_at: Long?,
 @ColumnInfo(defaultValue = "1") val include_in_parent: Long
)

@Entity(tableName = "action_record", primaryKeys = ["id"], indices = [
 Index(value = ["goal_event_id", "action_date_iso", "id"], unique = false, name = "actions_by_goal_date")], foreignKeys = [
 ForeignKey(entity = DbGoalDetail::class, parentColumns = ["event_id"], childColumns = ["goal_event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbActionRecord(
 val id: String,
 val goal_event_id: String,
 val action_date_iso: String,
 val body: String,
 val minutes: Long?,
 val created_at: Long,
 val updated_at: Long,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "lifecycle_cause", primaryKeys = ["id"], indices = [
 Index(value = ["source_event_id"], unique = false),
 Index(value = ["source_book_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["source_event_id"], onDelete = ForeignKey.SET_NULL, deferred = false),
 ForeignKey(entity = DbBook::class, parentColumns = ["id"], childColumns = ["source_book_id"], onDelete = ForeignKey.SET_NULL, deferred = false)])
data class DbLifecycleCause(
 val id: String,
 val kind: String,
 val source_event_id: String?,
 val source_book_id: String?,
 val created_at: Long,
 val purge_after: Long?
)

@Entity(tableName = "lifecycle_member", primaryKeys = ["cause_id", "event_id"], indices = [
 Index(value = ["event_id", "cause_id"], unique = false, name = "lifecycle_by_event")], foreignKeys = [
 ForeignKey(entity = DbLifecycleCause::class, parentColumns = ["id"], childColumns = ["cause_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbLifecycleMember(
 val cause_id: String,
 val event_id: String
)

@Entity(tableName = "tag", primaryKeys = ["id"], indices = [
 Index(value = ["name_key"], unique = true)])
data class DbTag(
 val id: String,
 val name: String,
 val name_key: String,
 val created_at: Long
)

@Entity(tableName = "event_tag", primaryKeys = ["event_id", "tag_id"], indices = [
 Index(value = ["tag_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbTag::class, parentColumns = ["id"], childColumns = ["tag_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbEventTag(
 val event_id: String,
 val tag_id: String
)

@Entity(tableName = "reminder_rule", primaryKeys = ["id"], indices = [
 Index(value = ["event_id", "enabled"], unique = false, name = "reminder_by_event")], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbReminderRule(
 val id: String,
 val event_id: String,
 @ColumnInfo(defaultValue = "0") val enabled: Long,
 val offset_unit: String,
 val offset_value: Long,
 val local_time: String?,
 @ColumnInfo(defaultValue = "'normal'") val precision_mode: String,
 @ColumnInfo(defaultValue = "1") val version: Long
)

@Entity(tableName = "home_config", primaryKeys = ["singleton"], indices = [
 Index(value = ["fixed_event_id"], unique = false),
 Index(value = ["selected_book_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["fixed_event_id"], onDelete = ForeignKey.SET_NULL, deferred = false),
 ForeignKey(entity = DbBook::class, parentColumns = ["id"], childColumns = ["selected_book_id"], onDelete = ForeignKey.SET_NULL, deferred = false)])
data class DbHomeConfig(
 val singleton: Long,
 @ColumnInfo(defaultValue = "'auto'") val hero_mode: String,
 val fixed_event_id: String?,
 @ColumnInfo(defaultValue = "'date'") val sort_mode: String,
 val selected_book_id: String?
)

@Entity(tableName = "import_batch", primaryKeys = ["id"], indices = [
 Index(value = ["file_sha256"], unique = true),
 Index(value = ["id", "source_export_id"], unique = true)])
data class DbImportBatch(
 val id: String,
 val format: String,
 val source_export_id: String,
 val file_sha256: String,
 val imported_at: Long
)

@Entity(tableName = "import_provenance", primaryKeys = ["batch_id", "source_ref"], indices = [
 Index(value = ["source_export_id", "source_ref"], unique = true),
 Index(value = ["local_event_id"], unique = false),
 Index(value = ["batch_id", "source_export_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbImportBatch::class, parentColumns = ["id"], childColumns = ["batch_id"], onDelete = ForeignKey.CASCADE, deferred = false),
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["local_event_id"], onDelete = ForeignKey.SET_NULL, deferred = false),
 ForeignKey(entity = DbImportBatch::class, parentColumns = ["id", "source_export_id"], childColumns = ["batch_id", "source_export_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbImportProvenance(
 val batch_id: String,
 val source_export_id: String,
 val source_ref: String,
 val local_event_id: String?
)

@Entity(tableName = "device_epoch", primaryKeys = ["singleton"])
data class DbDeviceEpoch(
 val singleton: Long,
 val epoch: String,
 val plan_token: String,
 @ColumnInfo(defaultValue = "0") val schedule_revision: Long
)

@Entity(tableName = "reminder_queue", primaryKeys = ["rule_id"], indices = [
 Index(value = ["fire_at", "rule_id"], unique = false, name = "reminder_by_fire")], foreignKeys = [
 ForeignKey(entity = DbReminderRule::class, parentColumns = ["id"], childColumns = ["rule_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbReminderQueue(
 val rule_id: String,
 val occurrence_key: String,
 val fire_at: Long,
 val rule_version: Long,
 val event_version: Long,
 val epoch: String
)

@Entity(tableName = "delivery_log", primaryKeys = ["epoch", "rule_id", "rule_version", "occurrence_key"], indices = [
 Index(value = ["state", "next_attempt_at"], unique = false, name = "delivery_by_state_retry")])
data class DbDeliveryLog(
 val epoch: String,
 val rule_id: String,
 val occurrence_key: String,
 val event_id: String,
 val rule_version: Long,
 val event_version: Long,
 val fire_at: Long,
 val valid_until: Long,
 val state: String,
 val notification_tag: String,
 val attempted_at: Long?,
 @ColumnInfo(defaultValue = "0") val attempt_count: Long,
 val next_attempt_at: Long,
 val last_error_code: String?
)

@Entity(tableName = "device_binding", primaryKeys = ["id"], indices = [
 Index(value = ["kind", "external_id"], unique = true),
 Index(value = ["event_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbEvent::class, parentColumns = ["id"], childColumns = ["event_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbDeviceBinding(
 val id: String,
 val event_id: String?,
 val kind: String,
 val external_id: String,
 val calendar_id: String?,
 val last_written_hash: String?,
 @ColumnInfo(defaultValue = "'[]'") val coverage_json: String,
 val epoch: String,
 val state: String
)

@Entity(tableName = "effect_outbox", primaryKeys = ["id"], indices = [
 Index(value = ["kind", "scope_id", "target_revision", "epoch"], unique = true)])
data class DbEffectOutbox(
 val id: String,
 val kind: String,
 @ColumnInfo(defaultValue = "'library'") val scope_id: String,
 val target_revision: Long,
 val epoch: String,
 @ColumnInfo(defaultValue = "0") val attempts: Long,
 val next_attempt_at: Long,
 val created_at: Long
)

@Entity(tableName = "backup_receipt", primaryKeys = ["id"])
data class DbBackupReceipt(
 val id: String,
 val snapshot_revision: Long,
 val backup_id: String,
 val completed_at: Long,
 val encrypted: Long,
 val file_sha256: String
)

@Entity(tableName = "asset_lease", primaryKeys = ["job_id", "asset_id"], indices = [
 Index(value = ["expires_at"], unique = false, name = "lease_by_expiry"),
 Index(value = ["asset_id"], unique = false)], foreignKeys = [
 ForeignKey(entity = DbAsset::class, parentColumns = ["id"], childColumns = ["asset_id"], onDelete = ForeignKey.CASCADE, deferred = false)])
data class DbAssetLease(
 val job_id: String,
 val asset_id: String,
 val expires_at: Long
)

@Entity(tableName = "command_receipt", primaryKeys = ["operation_id"])
data class DbCommandReceipt(
 val operation_id: String,
 val command_hash: String,
 val epoch: String,
 val entity_id: String,
 val entity_version: Long,
 val content_revision: Long,
 val committed_at: Long,
 @ColumnInfo(defaultValue = "'unit'") val result_type: String,
 @ColumnInfo(defaultValue = "'null'") val result_json: String
)

@Dao interface DeviceDao {
 @RawQuery fun query(query: SupportSQLiteQuery): Cursor
}
@Database(entities = [DbLibrary::class, DbAsset::class, DbBook::class, DbEvent::class, DbEventDate::class, DbRecurrence::class, DbAppearance::class, DbGoalDetail::class, DbActionRecord::class, DbLifecycleCause::class, DbLifecycleMember::class, DbTag::class, DbEventTag::class, DbReminderRule::class, DbHomeConfig::class, DbImportBatch::class, DbImportProvenance::class, DbDeviceEpoch::class, DbReminderQueue::class, DbDeliveryLog::class, DbDeviceBinding::class, DbEffectOutbox::class, DbBackupReceipt::class, DbAssetLease::class, DbCommandReceipt::class], version = 1, exportSchema = true)
abstract class DateBookDatabase : RoomDatabase() {
 abstract fun dao(): DeviceDao
}

