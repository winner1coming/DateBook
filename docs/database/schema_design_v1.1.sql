-- Android countdown TD schema design revision 1.1; initial app DB version remains 1
-- Design artifact, not a Room-generated schema or an applied migration.
-- SQLite checks relational invariants; Domain validates full dates, text graphemes,
-- recurrence compatibility, lifecycle rules and capacity before each transaction.
PRAGMA foreign_keys = ON;

CREATE TABLE library (
 id TEXT PRIMARY KEY NOT NULL,
 singleton INTEGER NOT NULL DEFAULT 1 UNIQUE CHECK(singleton=1),
 name TEXT NOT NULL,
 content_revision INTEGER NOT NULL DEFAULT 0 CHECK(content_revision >= 0),
 created_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL
);
CREATE TABLE asset (
 id TEXT PRIMARY KEY NOT NULL,
 sha256 TEXT NOT NULL UNIQUE,
 relative_path TEXT NOT NULL UNIQUE,
 mime_type TEXT NOT NULL CHECK(mime_type IN ('image/jpeg','image/png','image/webp')),
 byte_size INTEGER NOT NULL CHECK(byte_size >= 0),
 width INTEGER NOT NULL CHECK(width > 0),
 height INTEGER NOT NULL CHECK(height > 0),
 created_at INTEGER NOT NULL
);
CREATE TABLE book (
 id TEXT PRIMARY KEY NOT NULL,
 library_id TEXT NOT NULL REFERENCES library(id) ON DELETE RESTRICT,
 name TEXT NOT NULL CHECK(length(CAST(name AS BLOB)) BETWEEN 1 AND 2048),
 name_key TEXT NOT NULL UNIQUE,
 builtin_key TEXT UNIQUE CHECK(builtin_key IS NULL OR builtin_key IN ('birthday','memorial','holiday','goal','uncategorized')),
 is_protected INTEGER NOT NULL DEFAULT 0 CHECK(is_protected IN (0,1)),
 icon_key TEXT NOT NULL DEFAULT 'book',
 color_argb INTEGER NOT NULL DEFAULT -13278421,
 cover_asset_id TEXT REFERENCES asset(id) ON DELETE RESTRICT,
 sort_rank INTEGER NOT NULL DEFAULT 0,
 created_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL,
 version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TRIGGER protect_default_book_delete BEFORE DELETE ON book
 WHEN OLD.is_protected = 1
 BEGIN SELECT RAISE(ABORT,'BOOK_PROTECTED'); END;

CREATE TABLE event (
 id TEXT PRIMARY KEY NOT NULL,
 book_id TEXT NOT NULL REFERENCES book(id) ON DELETE RESTRICT,
 parent_id TEXT,
 title TEXT NOT NULL CHECK(length(CAST(title AS BLOB)) BETWEEN 1 AND 4096),
 kind TEXT NOT NULL CHECK(kind IN ('birthday','memorial','holiday','goal','ordinary')),
 count_mode TEXT NOT NULL CHECK(count_mode IN ('down','up')),
 include_start_day INTEGER NOT NULL DEFAULT 0 CHECK(include_start_day IN (0,1)),
 greeting TEXT NOT NULL DEFAULT '' CHECK(length(CAST(greeting AS BLOB)) <= 65536),
 home_visible INTEGER NOT NULL DEFAULT 1 CHECK(home_visible IN (0,1)),
 pinned INTEGER NOT NULL DEFAULT 0 CHECK(pinned IN (0,1)),
 sort_rank INTEGER NOT NULL DEFAULT 0,
 created_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL,
 version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
 UNIQUE(id,book_id),
 CHECK(parent_id IS NULL OR parent_id <> id),
 FOREIGN KEY(parent_id,book_id) REFERENCES event(id,book_id)
  ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX event_by_parent ON event(parent_id,sort_rank,id);
CREATE INDEX event_by_book ON event(book_id,sort_rank,id);
CREATE INDEX event_by_home ON event(home_visible,pinned,updated_at);

CREATE TRIGGER tree_depth_insert BEFORE INSERT ON event WHEN NEW.parent_id IS NOT NULL
BEGIN
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM event WHERE id=NEW.parent_id)
  THEN RAISE(ABORT,'TREE_PARENT_NOT_FOUND') END;
 SELECT CASE WHEN (
  WITH RECURSIVE ancestors(id,parent_id) AS (
   SELECT id,parent_id FROM event WHERE id=NEW.parent_id
   UNION SELECT e.id,e.parent_id FROM event e JOIN ancestors a ON e.id=a.parent_id
  ) SELECT count(*) FROM ancestors
 ) >= 3 THEN RAISE(ABORT,'TREE_DEPTH_EXCEEDED') END;
END;
CREATE TRIGGER tree_move_guard BEFORE UPDATE OF parent_id ON event WHEN NEW.parent_id IS NOT NULL
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
END;

CREATE TRIGGER event_id_immutable BEFORE UPDATE OF id ON event
 WHEN NEW.id <> OLD.id
 BEGIN SELECT RAISE(ABORT,'EVENT_ID_IMMUTABLE'); END;

CREATE TABLE event_date (
 event_id TEXT PRIMARY KEY NOT NULL REFERENCES event(id) ON DELETE CASCADE,
 calendar_type TEXT NOT NULL CHECK(calendar_type IN ('gregorian','lunar')),
 anchor_year INTEGER CHECK(anchor_year IS NULL OR anchor_year BETWEEN 1900 AND 2100),
 anchor_month INTEGER NOT NULL CHECK(anchor_month BETWEEN 1 AND 12),
 anchor_day INTEGER NOT NULL CHECK(anchor_day BETWEEN 1 AND 31),
 is_leap_month INTEGER NOT NULL DEFAULT 0 CHECK(is_leap_month IN (0,1)),
 all_day INTEGER NOT NULL DEFAULT 1 CHECK(all_day IN (0,1)),
 local_time TEXT,
 zone_id TEXT,
 feb29_policy TEXT NOT NULL DEFAULT 'feb28' CHECK(feb29_policy IN ('feb28','mar01')),
 lunar_leap_policy TEXT NOT NULL DEFAULT 'normal_fallback' CHECK(lunar_leap_policy IN ('normal_fallback','leap_only')),
 lunar_small_month_policy TEXT NOT NULL DEFAULT 'month_end' CHECK(lunar_small_month_policy IN ('month_end','skip')),
 calendar_engine_version TEXT NOT NULL DEFAULT 'calendar-v1',
 CHECK((all_day=1 AND local_time IS NULL AND zone_id IS NULL) OR
       (all_day=0 AND local_time IS NOT NULL AND zone_id IS NOT NULL)),
 CHECK(calendar_type='lunar' OR is_leap_month=0),
 CHECK(calendar_type='gregorian' OR all_day=1)
);
CREATE TABLE recurrence (
 event_id TEXT PRIMARY KEY NOT NULL REFERENCES event(id) ON DELETE CASCADE,
 frequency TEXT NOT NULL CHECK(frequency IN ('none','yearly','monthly','weekly','every_n_days')),
 interval_days INTEGER,
 until_iso TEXT,
 CHECK((frequency='every_n_days' AND interval_days IS NOT NULL AND interval_days BETWEEN 1 AND 365) OR
       (frequency<>'every_n_days' AND interval_days IS NULL))
);
CREATE TABLE appearance (
 event_id TEXT PRIMARY KEY NOT NULL REFERENCES event(id) ON DELETE CASCADE,
 background_kind TEXT NOT NULL DEFAULT 'gradient' CHECK(background_kind IN ('gradient','solid','photo')),
 asset_id TEXT REFERENCES asset(id) ON DELETE RESTRICT,
 preset_key TEXT NOT NULL DEFAULT 'forest',
 focus_x REAL NOT NULL DEFAULT 0.5 CHECK(focus_x BETWEEN 0 AND 1),
 focus_y REAL NOT NULL DEFAULT 0.5 CHECK(focus_y BETWEEN 0 AND 1),
 dim_amount REAL NOT NULL DEFAULT 0.35 CHECK(dim_amount BETWEEN 0 AND 1),
 text_color_mode TEXT NOT NULL DEFAULT 'auto' CHECK(text_color_mode IN ('auto','light','dark')),
 font_key TEXT NOT NULL DEFAULT 'system',
 CHECK(background_kind<>'photo' OR asset_id IS NOT NULL)
);
CREATE TABLE goal_detail (
 event_id TEXT PRIMARY KEY NOT NULL REFERENCES event(id) ON DELETE CASCADE,
 start_iso TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('not_started','in_progress','completed','canceled')),
 completed_at INTEGER,
 include_in_parent INTEGER NOT NULL DEFAULT 1 CHECK(include_in_parent IN (0,1)),
 CHECK((state='completed' AND completed_at IS NOT NULL) OR
       (state<>'completed' AND completed_at IS NULL))
);
CREATE TABLE action_record (
 id TEXT PRIMARY KEY NOT NULL,
 goal_event_id TEXT NOT NULL REFERENCES goal_detail(event_id) ON DELETE CASCADE,
 action_date_iso TEXT NOT NULL,
 body TEXT NOT NULL CHECK(length(CAST(body AS BLOB)) BETWEEN 1 AND 32768),
 minutes INTEGER CHECK(minutes BETWEEN 0 AND 1440),
 created_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL,
 version INTEGER NOT NULL DEFAULT 1 CHECK(version>0)
);
CREATE INDEX actions_by_goal_date ON action_record(goal_event_id,action_date_iso DESC,id);

-- Lifecycle is a set of operation causes, not a single overwritten flag.
CREATE TABLE lifecycle_cause (
 id TEXT PRIMARY KEY NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('archive','trash')),
 source_event_id TEXT REFERENCES event(id) ON DELETE SET NULL,
 source_book_id TEXT REFERENCES book(id) ON DELETE SET NULL,
 created_at INTEGER NOT NULL,
 purge_after INTEGER,
 CHECK((kind='trash' AND purge_after IS NOT NULL) OR(kind='archive' AND purge_after IS NULL))
);
CREATE TABLE lifecycle_member (
 cause_id TEXT NOT NULL REFERENCES lifecycle_cause(id) ON DELETE CASCADE,
 event_id TEXT NOT NULL REFERENCES event(id) ON DELETE CASCADE,
 PRIMARY KEY(cause_id,event_id)
);
CREATE INDEX lifecycle_by_event ON lifecycle_member(event_id,cause_id);
CREATE VIEW event_lifecycle AS
 SELECT e.id,
 CASE WHEN EXISTS(SELECT 1 FROM lifecycle_member m JOIN lifecycle_cause c ON c.id=m.cause_id WHERE m.event_id=e.id AND c.kind='trash') THEN 'trash'
 WHEN EXISTS(SELECT 1 FROM lifecycle_member m JOIN lifecycle_cause c ON c.id=m.cause_id WHERE m.event_id=e.id AND c.kind='archive') THEN 'archived'
 ELSE 'active' END AS lifecycle FROM event e;

CREATE TABLE tag (
 id TEXT PRIMARY KEY NOT NULL,
 name TEXT NOT NULL,
 name_key TEXT NOT NULL UNIQUE,
 created_at INTEGER NOT NULL
);
CREATE TABLE event_tag (
 event_id TEXT NOT NULL REFERENCES event(id) ON DELETE CASCADE,
 tag_id TEXT NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
 PRIMARY KEY(event_id,tag_id)
);
CREATE TABLE reminder_rule (
 id TEXT PRIMARY KEY NOT NULL,
 event_id TEXT NOT NULL REFERENCES event(id) ON DELETE CASCADE,
 enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0,1)),
 offset_unit TEXT NOT NULL CHECK(offset_unit IN ('days','hours','minutes')),
 offset_value INTEGER NOT NULL CHECK(offset_value BETWEEN 0 AND 525600),
 local_time TEXT,
 precision_mode TEXT NOT NULL DEFAULT 'normal' CHECK(precision_mode IN ('normal','precise')),
 version INTEGER NOT NULL DEFAULT 1 CHECK(version>0)
);
CREATE INDEX reminder_by_event ON reminder_rule(event_id,enabled);
CREATE TRIGGER reminder_limit BEFORE INSERT ON reminder_rule
 WHEN (SELECT count(*) FROM reminder_rule WHERE event_id=NEW.event_id)>=5
 BEGIN SELECT RAISE(ABORT,'REMINDER_LIMIT'); END;
CREATE TRIGGER reminder_limit_update BEFORE UPDATE OF event_id ON reminder_rule
 WHEN NEW.event_id<>OLD.event_id AND (SELECT count(*) FROM reminder_rule WHERE event_id=NEW.event_id)>=5
 BEGIN SELECT RAISE(ABORT,'REMINDER_LIMIT'); END;

CREATE TABLE home_config (
 singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 hero_mode TEXT NOT NULL DEFAULT 'auto' CHECK(hero_mode IN ('auto','fixed')),
 fixed_event_id TEXT REFERENCES event(id) ON DELETE SET NULL,
 sort_mode TEXT NOT NULL DEFAULT 'date' CHECK(sort_mode IN ('date','manual')),
 selected_book_id TEXT REFERENCES book(id) ON DELETE SET NULL
);
CREATE TABLE import_batch (
 id TEXT PRIMARY KEY NOT NULL,
 format TEXT NOT NULL CHECK(format IN ('events_json','events_csv','full_backup')),
 source_export_id TEXT NOT NULL,
 file_sha256 TEXT NOT NULL UNIQUE,
 imported_at INTEGER NOT NULL,
 UNIQUE(id,source_export_id)
);
CREATE TABLE import_provenance (
 batch_id TEXT NOT NULL REFERENCES import_batch(id) ON DELETE CASCADE,
 source_export_id TEXT NOT NULL,
 source_ref TEXT NOT NULL,
 local_event_id TEXT REFERENCES event(id) ON DELETE SET NULL,
 PRIMARY KEY(batch_id,source_ref),
 UNIQUE(source_export_id,source_ref),
 FOREIGN KEY(batch_id,source_export_id) REFERENCES import_batch(id,source_export_id) ON DELETE CASCADE
);

-- Device-only tables must be excluded from logical full backups and regenerated.
CREATE TABLE device_epoch (
 singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 epoch TEXT NOT NULL,
 plan_token TEXT NOT NULL,
 schedule_revision INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE reminder_queue (
 rule_id TEXT PRIMARY KEY NOT NULL REFERENCES reminder_rule(id) ON DELETE CASCADE,
 occurrence_key TEXT NOT NULL,
 fire_at INTEGER NOT NULL,
 rule_version INTEGER NOT NULL,
 event_version INTEGER NOT NULL,
 epoch TEXT NOT NULL
);
CREATE INDEX reminder_by_fire ON reminder_queue(fire_at,rule_id);
CREATE TABLE delivery_log (
 epoch TEXT NOT NULL,
 rule_id TEXT NOT NULL,
 occurrence_key TEXT NOT NULL,
 event_id TEXT NOT NULL,
 rule_version INTEGER NOT NULL,
 event_version INTEGER NOT NULL,
 fire_at INTEGER NOT NULL,
 valid_until INTEGER NOT NULL CHECK(valid_until >= fire_at),
 state TEXT NOT NULL CHECK(state IN ('pending','posting','posted','skipped','failed')),
 notification_tag TEXT NOT NULL,
 attempted_at INTEGER,
 attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count >= 0),
 next_attempt_at INTEGER NOT NULL,
 last_error_code TEXT,
 PRIMARY KEY(epoch,rule_id,rule_version,occurrence_key)
);
CREATE INDEX delivery_by_state_retry ON delivery_log(state,next_attempt_at);
CREATE TABLE device_binding (
 id TEXT PRIMARY KEY NOT NULL,
 event_id TEXT REFERENCES event(id) ON DELETE CASCADE,
 kind TEXT NOT NULL CHECK(kind IN ('calendar','widget')),
 external_id TEXT NOT NULL,
 calendar_id TEXT,
 last_written_hash TEXT,
 coverage_json TEXT NOT NULL DEFAULT '[]',
 epoch TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('active','unknown','conflict','invalid')),
 UNIQUE(kind,external_id)
);
CREATE TABLE effect_outbox (
 id TEXT PRIMARY KEY NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('replan','widget_refresh','media_gc','calendar_review')),
 scope_id TEXT NOT NULL DEFAULT 'library',
 target_revision INTEGER NOT NULL,
 epoch TEXT NOT NULL,
 attempts INTEGER NOT NULL DEFAULT 0,
 next_attempt_at INTEGER NOT NULL,
 created_at INTEGER NOT NULL,
 UNIQUE(kind,scope_id,target_revision,epoch)
);
CREATE TABLE backup_receipt (
 id TEXT PRIMARY KEY NOT NULL,
 snapshot_revision INTEGER NOT NULL,
 backup_id TEXT NOT NULL,
 completed_at INTEGER NOT NULL,
 encrypted INTEGER NOT NULL CHECK(encrypted IN (0,1)),
 file_sha256 TEXT NOT NULL
);
CREATE TABLE asset_lease (
 job_id TEXT NOT NULL,
 asset_id TEXT NOT NULL REFERENCES asset(id) ON DELETE CASCADE,
 expires_at INTEGER NOT NULL,
 PRIMARY KEY(job_id,asset_id)
);
CREATE INDEX lease_by_expiry ON asset_lease(expires_at);
CREATE TABLE command_receipt (
 operation_id TEXT PRIMARY KEY NOT NULL,
 command_hash TEXT NOT NULL,
 epoch TEXT NOT NULL,
 entity_id TEXT NOT NULL,
 entity_version INTEGER NOT NULL,
 content_revision INTEGER NOT NULL,
 committed_at INTEGER NOT NULL
);
-- App lock verifiers, device preferences and current-generation pointer are outside
-- the logical library snapshot; no account/user/session table exists.

-- Insert/import parents before children. Deferred same-book FK is only for atomic
-- whole-subtree book moves; parent existence is checked immediately by triggers.
-- SQL byte caps are independent of Domain Unicode grapheme limits; never truncate.
-- Room tables/FKs/indexes must match this contract. Any CHECK not expressible by
-- Entity annotations must have equivalent INSERT/UPDATE validation triggers.
-- Fresh-create and migration paths must both install and verify every guard.

