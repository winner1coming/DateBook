package cn.datebook.app.data

import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase

/** CHECK-equivalent guards run on BOTH fresh create and every open/migration. */
object SchemaGuards : RoomDatabase.Callback() {
 override fun onCreate(db: SupportSQLiteDatabase) { install(db) }
 override fun onOpen(db: SupportSQLiteDatabase) { install(db); verify(db) }
 fun install(db: SupportSQLiteDatabase) {
  db.execSQL("PRAGMA foreign_keys=ON")
  for (statement in statements) db.execSQL(statement)
 }
 fun verify(db: SupportSQLiteDatabase) {
  db.query("PRAGMA foreign_key_check").use { check(!it.moveToFirst()) { "DB_FOREIGN_KEY_CHECK_FAILED" } }
  db.query("SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'guard_%'").use {
   check(it.moveToFirst() && it.getInt(0) == 36) { "DB_GUARDS_MISSING" }
  }
  for (statement in statements) {
   val name = Regex("CREATE (?:TRIGGER|VIEW) IF NOT EXISTS (\\w+)").find(statement)!!.groupValues[1]
   db.query("SELECT sql FROM sqlite_master WHERE name=?", arrayOf(name)).use {
    check(it.moveToFirst() && normalize(it.getString(0)) == normalize(statement)) { "DB_GUARD_CHANGED:$name" }
   }
  }
 }
 private fun normalize(sql: String) = sql.replace(" IF NOT EXISTS", "").trim().trimEnd(';').replace(Regex("\\s+"), " ")
 private val statements = listOf(
  """CREATE VIEW IF NOT EXISTS event_lifecycle AS
 SELECT e.id,
 CASE WHEN EXISTS(SELECT 1 FROM lifecycle_member m JOIN lifecycle_cause c ON c.id=m.cause_id WHERE m.event_id=e.id AND c.kind='trash') THEN 'trash'
 WHEN EXISTS(SELECT 1 FROM lifecycle_member m JOIN lifecycle_cause c ON c.id=m.cause_id WHERE m.event_id=e.id AND c.kind='archive') THEN 'archived'
 ELSE 'active' END AS lifecycle FROM event e;""",
  """CREATE TRIGGER IF NOT EXISTS protect_default_book_delete BEFORE DELETE ON book
 WHEN OLD.is_protected = 1
 BEGIN SELECT RAISE(ABORT,'BOOK_PROTECTED'); END;""",
  """CREATE TRIGGER IF NOT EXISTS tree_depth_insert BEFORE INSERT ON event WHEN NEW.parent_id IS NOT NULL
BEGIN
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM event WHERE id=NEW.parent_id)
  THEN RAISE(ABORT,'TREE_PARENT_NOT_FOUND') END;
 SELECT CASE WHEN (
  WITH RECURSIVE ancestors(id,parent_id) AS (
   SELECT id,parent_id FROM event WHERE id=NEW.parent_id
   UNION SELECT e.id,e.parent_id FROM event e JOIN ancestors a ON e.id=a.parent_id
  ) SELECT count(*) FROM ancestors
 ) >= 3 THEN RAISE(ABORT,'TREE_DEPTH_EXCEEDED') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS tree_move_guard BEFORE UPDATE OF parent_id ON event WHEN NEW.parent_id IS NOT NULL
BEGIN
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM event WHERE id=NEW.parent_id)
  THEN RAISE(ABORT,'TREE_PARENT_NOT_FOUND') END;
 SELECT CASE WHEN EXISTS (
  WITH RECURSIVE descendants(id) AS (
   SELECT OLD.id UNION SELECT e.id FROM event e JOIN descendants d ON e.parent_id=d.id
  ) SELECT 1 FROM descendants WHERE id=NEW.parent_id
 ) THEN RAISE(ABORT,'TREE_CYCLE') END;
 SELECT CASE WHEN (
  WITH RECURSIVE ancestors(id,parent_id) AS (
   SELECT id,parent_id FROM event WHERE id=NEW.parent_id
   UNION SELECT e.id,e.parent_id FROM event e JOIN ancestors a ON e.id=a.parent_id
  ), descendants(id,rel) AS (
   SELECT OLD.id,0 UNION ALL SELECT e.id,d.rel+1 FROM event e JOIN descendants d ON e.parent_id=d.id
  ) SELECT (SELECT count(*) FROM ancestors)+1+(SELECT max(rel) FROM descendants)
 ) > 3 THEN RAISE(ABORT,'TREE_DEPTH_EXCEEDED') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS event_id_immutable BEFORE UPDATE OF id ON event
 WHEN NEW.id <> OLD.id
 BEGIN SELECT RAISE(ABORT,'EVENT_ID_IMMUTABLE'); END;""",
  """CREATE TRIGGER IF NOT EXISTS reminder_limit BEFORE INSERT ON reminder_rule
 WHEN (SELECT count(*) FROM reminder_rule WHERE event_id=NEW.event_id)>=5
 BEGIN SELECT RAISE(ABORT,'REMINDER_LIMIT'); END;""",
  """CREATE TRIGGER IF NOT EXISTS reminder_limit_update BEFORE UPDATE OF event_id ON reminder_rule
 WHEN NEW.event_id<>OLD.event_id AND (SELECT count(*) FROM reminder_rule WHERE event_id=NEW.event_id)>=5
 BEGIN SELECT RAISE(ABORT,'REMINDER_LIMIT'); END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_library_insert BEFORE INSERT ON library
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_library_0') END;
 SELECT CASE WHEN NOT (NEW.content_revision >= 0) THEN RAISE(ABORT,'CHECK_library_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_library_update BEFORE UPDATE ON library
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_library_0') END;
 SELECT CASE WHEN NOT (NEW.content_revision >= 0) THEN RAISE(ABORT,'CHECK_library_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_asset_insert BEFORE INSERT ON asset
BEGIN
 SELECT CASE WHEN NOT (NEW.mime_type IN ('image/jpeg','image/png','image/webp')) THEN RAISE(ABORT,'CHECK_asset_0') END;
 SELECT CASE WHEN NOT (NEW.byte_size >= 0) THEN RAISE(ABORT,'CHECK_asset_1') END;
 SELECT CASE WHEN NOT (NEW.width > 0) THEN RAISE(ABORT,'CHECK_asset_2') END;
 SELECT CASE WHEN NOT (NEW.height > 0) THEN RAISE(ABORT,'CHECK_asset_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_asset_update BEFORE UPDATE ON asset
BEGIN
 SELECT CASE WHEN NOT (NEW.mime_type IN ('image/jpeg','image/png','image/webp')) THEN RAISE(ABORT,'CHECK_asset_0') END;
 SELECT CASE WHEN NOT (NEW.byte_size >= 0) THEN RAISE(ABORT,'CHECK_asset_1') END;
 SELECT CASE WHEN NOT (NEW.width > 0) THEN RAISE(ABORT,'CHECK_asset_2') END;
 SELECT CASE WHEN NOT (NEW.height > 0) THEN RAISE(ABORT,'CHECK_asset_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_book_insert BEFORE INSERT ON book
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.name AS BLOB)) BETWEEN 1 AND 2048) THEN RAISE(ABORT,'CHECK_book_0') END;
 SELECT CASE WHEN NOT (NEW.builtin_key IS NULL OR NEW.builtin_key IN ('birthday','memorial','holiday','goal','uncategorized')) THEN RAISE(ABORT,'CHECK_book_1') END;
 SELECT CASE WHEN NOT (NEW.is_protected IN (0,1)) THEN RAISE(ABORT,'CHECK_book_2') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_book_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_book_update BEFORE UPDATE ON book
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.name AS BLOB)) BETWEEN 1 AND 2048) THEN RAISE(ABORT,'CHECK_book_0') END;
 SELECT CASE WHEN NOT (NEW.builtin_key IS NULL OR NEW.builtin_key IN ('birthday','memorial','holiday','goal','uncategorized')) THEN RAISE(ABORT,'CHECK_book_1') END;
 SELECT CASE WHEN NOT (NEW.is_protected IN (0,1)) THEN RAISE(ABORT,'CHECK_book_2') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_book_3') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_insert BEFORE INSERT ON event
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.title AS BLOB)) BETWEEN 1 AND 4096) THEN RAISE(ABORT,'CHECK_event_0') END;
 SELECT CASE WHEN NOT (NEW.kind IN ('birthday','memorial','holiday','goal','ordinary')) THEN RAISE(ABORT,'CHECK_event_1') END;
 SELECT CASE WHEN NOT (NEW.count_mode IN ('down','up')) THEN RAISE(ABORT,'CHECK_event_2') END;
 SELECT CASE WHEN NOT (NEW.include_start_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_3') END;
 SELECT CASE WHEN NOT (length(CAST(NEW.greeting AS BLOB)) <= 65536) THEN RAISE(ABORT,'CHECK_event_4') END;
 SELECT CASE WHEN NOT (NEW.home_visible IN (0,1)) THEN RAISE(ABORT,'CHECK_event_5') END;
 SELECT CASE WHEN NOT (NEW.pinned IN (0,1)) THEN RAISE(ABORT,'CHECK_event_6') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_event_7') END;
 SELECT CASE WHEN NOT (NEW.parent_id IS NULL OR NEW.parent_id <> NEW.id) THEN RAISE(ABORT,'CHECK_event_8') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_update BEFORE UPDATE ON event
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.title AS BLOB)) BETWEEN 1 AND 4096) THEN RAISE(ABORT,'CHECK_event_0') END;
 SELECT CASE WHEN NOT (NEW.kind IN ('birthday','memorial','holiday','goal','ordinary')) THEN RAISE(ABORT,'CHECK_event_1') END;
 SELECT CASE WHEN NOT (NEW.count_mode IN ('down','up')) THEN RAISE(ABORT,'CHECK_event_2') END;
 SELECT CASE WHEN NOT (NEW.include_start_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_3') END;
 SELECT CASE WHEN NOT (length(CAST(NEW.greeting AS BLOB)) <= 65536) THEN RAISE(ABORT,'CHECK_event_4') END;
 SELECT CASE WHEN NOT (NEW.home_visible IN (0,1)) THEN RAISE(ABORT,'CHECK_event_5') END;
 SELECT CASE WHEN NOT (NEW.pinned IN (0,1)) THEN RAISE(ABORT,'CHECK_event_6') END;
 SELECT CASE WHEN NOT (NEW.version > 0) THEN RAISE(ABORT,'CHECK_event_7') END;
 SELECT CASE WHEN NOT (NEW.parent_id IS NULL OR NEW.parent_id <> NEW.id) THEN RAISE(ABORT,'CHECK_event_8') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_date_insert BEFORE INSERT ON event_date
BEGIN
 SELECT CASE WHEN NOT (NEW.calendar_type IN ('gregorian','lunar')) THEN RAISE(ABORT,'CHECK_event_date_0') END;
 SELECT CASE WHEN NOT (NEW.anchor_year IS NULL OR NEW.anchor_year BETWEEN 1900 AND 2100) THEN RAISE(ABORT,'CHECK_event_date_1') END;
 SELECT CASE WHEN NOT (NEW.anchor_month BETWEEN 1 AND 12) THEN RAISE(ABORT,'CHECK_event_date_2') END;
 SELECT CASE WHEN NOT (NEW.anchor_day BETWEEN 1 AND 31) THEN RAISE(ABORT,'CHECK_event_date_3') END;
 SELECT CASE WHEN NOT (NEW.is_leap_month IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_4') END;
 SELECT CASE WHEN NOT (NEW.all_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_5') END;
 SELECT CASE WHEN NOT (NEW.feb29_policy IN ('feb28','mar01')) THEN RAISE(ABORT,'CHECK_event_date_6') END;
 SELECT CASE WHEN NOT (NEW.lunar_leap_policy IN ('normal_fallback','leap_only')) THEN RAISE(ABORT,'CHECK_event_date_7') END;
 SELECT CASE WHEN NOT (NEW.lunar_small_month_policy IN ('month_end','skip')) THEN RAISE(ABORT,'CHECK_event_date_8') END;
 SELECT CASE WHEN NOT ((NEW.all_day=1 AND NEW.local_time IS NULL AND NEW.zone_id IS NULL) OR
       (NEW.all_day=0 AND NEW.local_time IS NOT NULL AND NEW.zone_id IS NOT NULL)) THEN RAISE(ABORT,'CHECK_event_date_9') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='lunar' OR NEW.is_leap_month=0) THEN RAISE(ABORT,'CHECK_event_date_10') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='gregorian' OR NEW.all_day=1) THEN RAISE(ABORT,'CHECK_event_date_11') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_event_date_update BEFORE UPDATE ON event_date
BEGIN
 SELECT CASE WHEN NOT (NEW.calendar_type IN ('gregorian','lunar')) THEN RAISE(ABORT,'CHECK_event_date_0') END;
 SELECT CASE WHEN NOT (NEW.anchor_year IS NULL OR NEW.anchor_year BETWEEN 1900 AND 2100) THEN RAISE(ABORT,'CHECK_event_date_1') END;
 SELECT CASE WHEN NOT (NEW.anchor_month BETWEEN 1 AND 12) THEN RAISE(ABORT,'CHECK_event_date_2') END;
 SELECT CASE WHEN NOT (NEW.anchor_day BETWEEN 1 AND 31) THEN RAISE(ABORT,'CHECK_event_date_3') END;
 SELECT CASE WHEN NOT (NEW.is_leap_month IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_4') END;
 SELECT CASE WHEN NOT (NEW.all_day IN (0,1)) THEN RAISE(ABORT,'CHECK_event_date_5') END;
 SELECT CASE WHEN NOT (NEW.feb29_policy IN ('feb28','mar01')) THEN RAISE(ABORT,'CHECK_event_date_6') END;
 SELECT CASE WHEN NOT (NEW.lunar_leap_policy IN ('normal_fallback','leap_only')) THEN RAISE(ABORT,'CHECK_event_date_7') END;
 SELECT CASE WHEN NOT (NEW.lunar_small_month_policy IN ('month_end','skip')) THEN RAISE(ABORT,'CHECK_event_date_8') END;
 SELECT CASE WHEN NOT ((NEW.all_day=1 AND NEW.local_time IS NULL AND NEW.zone_id IS NULL) OR
       (NEW.all_day=0 AND NEW.local_time IS NOT NULL AND NEW.zone_id IS NOT NULL)) THEN RAISE(ABORT,'CHECK_event_date_9') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='lunar' OR NEW.is_leap_month=0) THEN RAISE(ABORT,'CHECK_event_date_10') END;
 SELECT CASE WHEN NOT (NEW.calendar_type='gregorian' OR NEW.all_day=1) THEN RAISE(ABORT,'CHECK_event_date_11') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_recurrence_insert BEFORE INSERT ON recurrence
BEGIN
 SELECT CASE WHEN NOT (NEW.frequency IN ('none','yearly','monthly','weekly','every_n_days')) THEN RAISE(ABORT,'CHECK_recurrence_0') END;
 SELECT CASE WHEN NOT ((NEW.frequency='every_n_days' AND NEW.interval_days IS NOT NULL AND NEW.interval_days BETWEEN 1 AND 365) OR
       (NEW.frequency<>'every_n_days' AND NEW.interval_days IS NULL)) THEN RAISE(ABORT,'CHECK_recurrence_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_recurrence_update BEFORE UPDATE ON recurrence
BEGIN
 SELECT CASE WHEN NOT (NEW.frequency IN ('none','yearly','monthly','weekly','every_n_days')) THEN RAISE(ABORT,'CHECK_recurrence_0') END;
 SELECT CASE WHEN NOT ((NEW.frequency='every_n_days' AND NEW.interval_days IS NOT NULL AND NEW.interval_days BETWEEN 1 AND 365) OR
       (NEW.frequency<>'every_n_days' AND NEW.interval_days IS NULL)) THEN RAISE(ABORT,'CHECK_recurrence_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_appearance_insert BEFORE INSERT ON appearance
BEGIN
 SELECT CASE WHEN NOT (NEW.background_kind IN ('gradient','solid','photo')) THEN RAISE(ABORT,'CHECK_appearance_0') END;
 SELECT CASE WHEN NOT (NEW.focus_x BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_1') END;
 SELECT CASE WHEN NOT (NEW.focus_y BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_2') END;
 SELECT CASE WHEN NOT (NEW.dim_amount BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_3') END;
 SELECT CASE WHEN NOT (NEW.text_color_mode IN ('auto','light','dark')) THEN RAISE(ABORT,'CHECK_appearance_4') END;
 SELECT CASE WHEN NOT (NEW.background_kind<>'photo' OR NEW.asset_id IS NOT NULL) THEN RAISE(ABORT,'CHECK_appearance_5') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_appearance_update BEFORE UPDATE ON appearance
BEGIN
 SELECT CASE WHEN NOT (NEW.background_kind IN ('gradient','solid','photo')) THEN RAISE(ABORT,'CHECK_appearance_0') END;
 SELECT CASE WHEN NOT (NEW.focus_x BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_1') END;
 SELECT CASE WHEN NOT (NEW.focus_y BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_2') END;
 SELECT CASE WHEN NOT (NEW.dim_amount BETWEEN 0 AND 1) THEN RAISE(ABORT,'CHECK_appearance_3') END;
 SELECT CASE WHEN NOT (NEW.text_color_mode IN ('auto','light','dark')) THEN RAISE(ABORT,'CHECK_appearance_4') END;
 SELECT CASE WHEN NOT (NEW.background_kind<>'photo' OR NEW.asset_id IS NOT NULL) THEN RAISE(ABORT,'CHECK_appearance_5') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_goal_detail_insert BEFORE INSERT ON goal_detail
BEGIN
 SELECT CASE WHEN NOT (NEW.state IN ('not_started','in_progress','completed','canceled')) THEN RAISE(ABORT,'CHECK_goal_detail_0') END;
 SELECT CASE WHEN NOT (NEW.include_in_parent IN (0,1)) THEN RAISE(ABORT,'CHECK_goal_detail_1') END;
 SELECT CASE WHEN NOT ((NEW.state='completed' AND NEW.completed_at IS NOT NULL) OR
       (NEW.state<>'completed' AND NEW.completed_at IS NULL)) THEN RAISE(ABORT,'CHECK_goal_detail_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_goal_detail_update BEFORE UPDATE ON goal_detail
BEGIN
 SELECT CASE WHEN NOT (NEW.state IN ('not_started','in_progress','completed','canceled')) THEN RAISE(ABORT,'CHECK_goal_detail_0') END;
 SELECT CASE WHEN NOT (NEW.include_in_parent IN (0,1)) THEN RAISE(ABORT,'CHECK_goal_detail_1') END;
 SELECT CASE WHEN NOT ((NEW.state='completed' AND NEW.completed_at IS NOT NULL) OR
       (NEW.state<>'completed' AND NEW.completed_at IS NULL)) THEN RAISE(ABORT,'CHECK_goal_detail_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_action_record_insert BEFORE INSERT ON action_record
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.body AS BLOB)) BETWEEN 1 AND 32768) THEN RAISE(ABORT,'CHECK_action_record_0') END;
 SELECT CASE WHEN NOT (NEW.minutes BETWEEN 0 AND 1440) THEN RAISE(ABORT,'CHECK_action_record_1') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_action_record_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_action_record_update BEFORE UPDATE ON action_record
BEGIN
 SELECT CASE WHEN NOT (length(CAST(NEW.body AS BLOB)) BETWEEN 1 AND 32768) THEN RAISE(ABORT,'CHECK_action_record_0') END;
 SELECT CASE WHEN NOT (NEW.minutes BETWEEN 0 AND 1440) THEN RAISE(ABORT,'CHECK_action_record_1') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_action_record_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_lifecycle_cause_insert BEFORE INSERT ON lifecycle_cause
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('archive','trash')) THEN RAISE(ABORT,'CHECK_lifecycle_cause_0') END;
 SELECT CASE WHEN NOT ((NEW.kind='trash' AND NEW.purge_after IS NOT NULL) OR(NEW.kind='archive' AND NEW.purge_after IS NULL)) THEN RAISE(ABORT,'CHECK_lifecycle_cause_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_lifecycle_cause_update BEFORE UPDATE ON lifecycle_cause
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('archive','trash')) THEN RAISE(ABORT,'CHECK_lifecycle_cause_0') END;
 SELECT CASE WHEN NOT ((NEW.kind='trash' AND NEW.purge_after IS NOT NULL) OR(NEW.kind='archive' AND NEW.purge_after IS NULL)) THEN RAISE(ABORT,'CHECK_lifecycle_cause_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_reminder_rule_insert BEFORE INSERT ON reminder_rule
BEGIN
 SELECT CASE WHEN NOT (NEW.enabled IN (0,1)) THEN RAISE(ABORT,'CHECK_reminder_rule_0') END;
 SELECT CASE WHEN NOT (NEW.offset_unit IN ('days','hours','minutes')) THEN RAISE(ABORT,'CHECK_reminder_rule_1') END;
 SELECT CASE WHEN NOT (NEW.offset_value BETWEEN 0 AND 525600) THEN RAISE(ABORT,'CHECK_reminder_rule_2') END;
 SELECT CASE WHEN NOT (NEW.precision_mode IN ('normal','precise')) THEN RAISE(ABORT,'CHECK_reminder_rule_3') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_reminder_rule_4') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_reminder_rule_update BEFORE UPDATE ON reminder_rule
BEGIN
 SELECT CASE WHEN NOT (NEW.enabled IN (0,1)) THEN RAISE(ABORT,'CHECK_reminder_rule_0') END;
 SELECT CASE WHEN NOT (NEW.offset_unit IN ('days','hours','minutes')) THEN RAISE(ABORT,'CHECK_reminder_rule_1') END;
 SELECT CASE WHEN NOT (NEW.offset_value BETWEEN 0 AND 525600) THEN RAISE(ABORT,'CHECK_reminder_rule_2') END;
 SELECT CASE WHEN NOT (NEW.precision_mode IN ('normal','precise')) THEN RAISE(ABORT,'CHECK_reminder_rule_3') END;
 SELECT CASE WHEN NOT (NEW.version>0) THEN RAISE(ABORT,'CHECK_reminder_rule_4') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_home_config_insert BEFORE INSERT ON home_config
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_home_config_0') END;
 SELECT CASE WHEN NOT (NEW.hero_mode IN ('auto','fixed')) THEN RAISE(ABORT,'CHECK_home_config_1') END;
 SELECT CASE WHEN NOT (NEW.sort_mode IN ('date','manual')) THEN RAISE(ABORT,'CHECK_home_config_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_home_config_update BEFORE UPDATE ON home_config
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_home_config_0') END;
 SELECT CASE WHEN NOT (NEW.hero_mode IN ('auto','fixed')) THEN RAISE(ABORT,'CHECK_home_config_1') END;
 SELECT CASE WHEN NOT (NEW.sort_mode IN ('date','manual')) THEN RAISE(ABORT,'CHECK_home_config_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_import_batch_insert BEFORE INSERT ON import_batch
BEGIN
 SELECT CASE WHEN NOT (NEW.format IN ('events_json','events_csv','full_backup')) THEN RAISE(ABORT,'CHECK_import_batch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_import_batch_update BEFORE UPDATE ON import_batch
BEGIN
 SELECT CASE WHEN NOT (NEW.format IN ('events_json','events_csv','full_backup')) THEN RAISE(ABORT,'CHECK_import_batch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_epoch_insert BEFORE INSERT ON device_epoch
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_device_epoch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_epoch_update BEFORE UPDATE ON device_epoch
BEGIN
 SELECT CASE WHEN NOT (NEW.singleton=1) THEN RAISE(ABORT,'CHECK_device_epoch_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_delivery_log_insert BEFORE INSERT ON delivery_log
BEGIN
 SELECT CASE WHEN NOT (NEW.valid_until >= NEW.fire_at) THEN RAISE(ABORT,'CHECK_delivery_log_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('pending','posting','posted','skipped','failed')) THEN RAISE(ABORT,'CHECK_delivery_log_1') END;
 SELECT CASE WHEN NOT (NEW.attempt_count >= 0) THEN RAISE(ABORT,'CHECK_delivery_log_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_delivery_log_update BEFORE UPDATE ON delivery_log
BEGIN
 SELECT CASE WHEN NOT (NEW.valid_until >= NEW.fire_at) THEN RAISE(ABORT,'CHECK_delivery_log_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('pending','posting','posted','skipped','failed')) THEN RAISE(ABORT,'CHECK_delivery_log_1') END;
 SELECT CASE WHEN NOT (NEW.attempt_count >= 0) THEN RAISE(ABORT,'CHECK_delivery_log_2') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_binding_insert BEFORE INSERT ON device_binding
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('calendar','widget')) THEN RAISE(ABORT,'CHECK_device_binding_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('active','unknown','conflict','invalid')) THEN RAISE(ABORT,'CHECK_device_binding_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_device_binding_update BEFORE UPDATE ON device_binding
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('calendar','widget')) THEN RAISE(ABORT,'CHECK_device_binding_0') END;
 SELECT CASE WHEN NOT (NEW.state IN ('active','unknown','conflict','invalid')) THEN RAISE(ABORT,'CHECK_device_binding_1') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_effect_outbox_insert BEFORE INSERT ON effect_outbox
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('replan','widget_refresh','media_gc','calendar_review')) THEN RAISE(ABORT,'CHECK_effect_outbox_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_effect_outbox_update BEFORE UPDATE ON effect_outbox
BEGIN
 SELECT CASE WHEN NOT (NEW.kind IN ('replan','widget_refresh','media_gc','calendar_review')) THEN RAISE(ABORT,'CHECK_effect_outbox_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_backup_receipt_insert BEFORE INSERT ON backup_receipt
BEGIN
 SELECT CASE WHEN NOT (NEW.encrypted IN (0,1)) THEN RAISE(ABORT,'CHECK_backup_receipt_0') END;
END;""",
  """CREATE TRIGGER IF NOT EXISTS guard_backup_receipt_update BEFORE UPDATE ON backup_receipt
BEGIN
 SELECT CASE WHEN NOT (NEW.encrypted IN (0,1)) THEN RAISE(ABORT,'CHECK_backup_receipt_0') END;
END;"""
 )
}

