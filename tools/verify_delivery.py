#!/usr/bin/env python3
"""Source/config/actual Room DDL checks. No Android execution is implied."""
import json
from pathlib import Path
import re
import sqlite3
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
checks=0
def check(ok, explanation):
 global checks
 assert ok,explanation
 checks+=1

required=['settings.gradle.kts','app/build.gradle.kts','core/build.gradle.kts','gradlew','gradlew.bat','gradle/wrapper/gradle-wrapper.jar','gradle/wrapper/gradle-wrapper.properties','docs/testing/TEST_PLAN.md','docs/testing/TEST_REPORT.md','README.md']
for name in required:check((ROOT/name).is_file(),'Missing '+name)
manifest=ET.parse(ROOT/'app/src/main/AndroidManifest.xml').getroot()
ns='{http://schemas.android.com/apk/res/android}'
permissions={p.get(ns+'name') for p in manifest.findall('uses-permission')}
check('android.permission.INTERNET' not in permissions,'No network permission')
check('android.permission.GET_ACCOUNTS' not in permissions,'No account permission')
check('android.permission.WRITE_CALENDAR' not in permissions,'Calendar writes use explicit system UI')
check(manifest.find('application').get(ns+'allowBackup')=='false','Automatic Android backup disabled')
paths=ET.parse(ROOT/'app/src/main/res/xml/file_paths.xml').getroot()
check(len(paths)==1 and paths[0].tag=='cache-path' and paths[0].get('path')=='shares/','Only scoped share cache exposed')
catalog=(ROOT/'gradle/libs.versions.toml').read_text()
check('ksp = "2.3.10"' in catalog,'AGP9-compatible KSP')
check('android.disallowKotlinSourceSets=false' not in (ROOT/'gradle.properties').read_text(),'Do not bypass source set guard')
check('org.jetbrains.kotlin.android' not in (ROOT/'app/build.gradle.kts').read_text(),'AGP built-in Kotlin')
for file in (ROOT/'app/src/main').rglob('*.xml'):ET.parse(file);checks+=1
for file in [*(ROOT/'core/src').rglob('*.kt'),*(ROOT/'app/src').rglob('*.kt')]:
 check(not re.search(r'\bTODO\s*\(|\bNotImplementedError\b|throw UnsupportedOperationException',file.read_text()),'Unimplemented placeholder '+str(file))

# Actual schema exported by Room KSP, not a hand-maintained duplicate.
schema=json.loads((ROOT/'app/schemas/cn.datebook.app.data.DateBookDatabase/1.json').read_text())['database']
check(len(schema['entities'])==25,'25 normalized tables')
db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON')
for entity in schema['entities']:
 table=entity['tableName'];db.execute(entity['createSql'].replace('${TABLE_NAME}',table))
 for index in entity.get('indices',[]):db.execute(index['createSql'].replace('${TABLE_NAME}',table))
guard=(ROOT/'app/src/main/kotlin/cn/datebook/app/data/SchemaGuards.kt').read_text()
statements=re.findall(r'"""([\s\S]*?)"""',guard)
for statement in statements:db.executescript(statement)
check(db.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0]==42,'42 installed guards')
normalize=lambda s:re.sub(r'\s+',' ',s.replace(' IF NOT EXISTS','').strip().rstrip(';'))
for statement in statements:
 name=re.search(r'CREATE (?:TRIGGER|VIEW) IF NOT EXISTS (\w+)',statement).group(1)
 actual=db.execute('SELECT sql FROM sqlite_master WHERE name=?',(name,)).fetchone()[0]
 check(normalize(actual)==normalize(statement),'Guard body mismatch '+name)
db.execute("INSERT INTO library(id,name,created_at,updated_at) VALUES('l','n',0,0)")
db.execute("INSERT INTO book(id,library_id,name,name_key,created_at,updated_at) VALUES('b','l','b','b',0,0)")
def insert(identifier,parent=None):db.execute("INSERT INTO event(id,book_id,parent_id,title,kind,count_mode,created_at,updated_at) VALUES(?,'b',?,?,'ordinary','down',0,0)",(identifier,parent,identifier))
def reject(action,diagnostic):
 try:action()
 except sqlite3.DatabaseError as e:check(diagnostic in str(e),diagnostic+' / '+str(e));return
 raise AssertionError('Incorrectly accepted '+diagnostic)
reject(lambda:insert('x','missing'),'TREE_PARENT_NOT_FOUND')
insert('a');insert('b','a');insert('c','b')
reject(lambda:insert('d','c'),'TREE_DEPTH_EXCEEDED')
reject(lambda:db.execute("UPDATE event SET parent_id='c' WHERE id='a'"),'TREE_CYCLE')
reject(lambda:db.execute("UPDATE event SET id='x' WHERE id='a'"),'EVENT_ID_IMMUTABLE')
reject(lambda:db.execute("INSERT INTO recurrence VALUES('a','every_n_days',NULL,NULL)"),'CHECK_recurrence')
reject(lambda:db.execute("UPDATE event SET title=? WHERE id='a'",('x'*4097,)),'CHECK_event')
db.execute("UPDATE event SET title=? WHERE id='a'",('👨‍👩‍👧‍👦'*60,));checks+=1
reject(lambda:db.execute("INSERT INTO appearance(event_id,background_kind) VALUES('a','photo')"),'CHECK_appearance')
reject(lambda:db.execute("INSERT INTO event_date(event_id,calendar_type,anchor_month,anchor_day,all_day) VALUES('a','lunar',1,1,0)"),'CHECK_event_date')
check(not db.execute('PRAGMA foreign_key_check').fetchall(),'Foreign key integrity')
source=(ROOT/'app/src/main/kotlin/cn/datebook/app/platform/SystemServices.kt').read_text()
prepared=0
for sql in re.findall(r'sql\.(?:query|execSQL)\("((?:[^"\\]|\\.)*)"',source):
 sql=sql.replace('$where','epoch=? AND rule_id=? AND rule_version=? AND occurrence_key=?')
 if '$' in sql:continue
 db.execute('EXPLAIN '+sql,[None]*sql.count('?'));prepared+=1
check(prepared>=24,'Prepare platform SQL against actual Room schema')
print(f'PASS: {checks} source/config/SQLite checks; {prepared} platform SQL statements prepared.')
print('NOT RUN by this script: Android build, UI/device execution, notifications, performance and security audit.')
