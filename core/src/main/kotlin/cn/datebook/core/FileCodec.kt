package cn.datebook.core

import kotlinx.serialization.json.*
import java.io.*
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.security.SecureRandom
import java.time.Instant
import java.time.LocalDate
import java.util.Base64
import java.util.UUID
import java.util.zip.ZipEntry
import java.util.zip.ZipInputStream
import java.util.zip.ZipOutputStream
import javax.crypto.Cipher
import javax.crypto.Mac
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

data class LineIssue(val line: Int, val code: String, val message: String)
data class ImportPreview(val state: LibraryState, val sourceExportId: String, val fileSha256: String,
 val format: String, val issues: List<LineIssue> = emptyList())
data class BackupPreview(val state: LibraryState, val backupId: String, val assetRoot: File,
 val encrypted: Boolean, val fileSha256: String)
data class BackupReceipt(val backupId: String, val fileSha256: String, val bytes: Long)

/** The public format is deliberately mapped field by field; device state never leaves this boundary. */
class FileCodec(private val dates: DateEngine) {
 private val json = Json { isLenient = false; ignoreUnknownKeys = false; allowSpecialFloatingPointValues = false }
 private val textLimit = 10L * 1024 * 1024
 private val containerLimit = 256L * 1024 * 1024
 private val expandedLimit = 512L * 1024 * 1024
 private fun obj(vararg pairs: Pair<String, JsonElement>) = JsonObject(linkedMapOf(*pairs))
 private fun str(v: String?) = v?.let(::JsonPrimitive) ?: JsonNull
 private fun num(v: Number?) = v?.let(::JsonPrimitive) ?: JsonNull
 private fun bool(v: Boolean) = JsonPrimitive(v)
 private fun arr(v: Iterable<JsonElement>) = JsonArray(v.toList())
 private fun fields(o: JsonObject, required: String, optional: String = ""): JsonObject {
  val req = required.split(' ').filter { it.isNotEmpty() }.toSet()
  val allow = req + optional.split(' ').filter { it.isNotEmpty() }
  demand(o.keys.containsAll(req) && o.keys.all { it in allow }, "FILE_SCHEMA_INVALID")
  return o
 }
 private fun JsonObject.s(k: String): String = (get(k) as? JsonPrimitive)?.let { demand(it.isString,"FILE_SCHEMA_INVALID",k); it.content } ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.ns(k: String): String? = if (get(k) == JsonNull) null else s(k)
 private fun JsonObject.n(k: String): Long = (get(k) as? JsonPrimitive)?.let { demand(!it.isString,"FILE_SCHEMA_INVALID",k); it.longOrNull } ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.i(k: String): Int { val n = n(k); demand(n in Int.MIN_VALUE..Int.MAX_VALUE,"FILE_SCHEMA_INVALID",k); return n.toInt() }
 private fun JsonObject.nn(k: String): Long? = if(get(k)==JsonNull) null else n(k)
 private fun JsonObject.b(k: String): Boolean = (get(k) as? JsonPrimitive)?.let { demand(!it.isString,"FILE_SCHEMA_INVALID",k); it.booleanOrNull } ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.d(k: String, default: Double): Double = get(k)?.let { e -> val p=e as? JsonPrimitive ?: throw AppException("FILE_SCHEMA_INVALID",k); demand(!p.isString,"FILE_SCHEMA_INVALID",k); p.doubleOrNull?.also { demand(it.isFinite(),"FILE_SCHEMA_INVALID",k) } ?: throw AppException("FILE_SCHEMA_INVALID",k) } ?: default
 private fun JsonObject.o(k: String) = get(k) as? JsonObject ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonObject.a(k: String) = get(k) as? JsonArray ?: throw AppException("FILE_SCHEMA_INVALID",k)
 private fun JsonElement.o() = this as? JsonObject ?: throw AppException("FILE_SCHEMA_INVALID")
 private fun utf8(bytes: ByteArray): String = try { StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString() } catch(e:Exception) { throw AppException("FILE_ENCODING_INVALID") }
 private fun parse(bytes: ByteArray, max: Long = textLimit): JsonObject {
  demand(bytes.size.toLong() <= max,"FILE_LIMIT_EXCEEDED")
  val text=utf8(bytes); rejectDuplicateKeys(text)
  return try { json.parseToJsonElement(text).o() } catch(e:AppException){throw e} catch(e:Exception){throw AppException("FILE_SCHEMA_INVALID")}
 }
 private fun validString(s:String):Boolean {var i=0;while(i<s.length){val c=s[i];if(c=='\u0000')return false;if(Character.isHighSurrogate(c)){if(i+1>=s.length||!Character.isLowSurrogate(s[i+1]))return false;i++}else if(Character.isLowSurrogate(c))return false;i++};return true}
 private fun date(d: DateSpec) = obj("calendar" to str(d.calendar),"year" to num(d.year),"month" to num(d.month),"day" to num(d.day),"leapMonth" to bool(d.leapMonth),"allDay" to bool(d.allDay),"localTime" to str(d.localTime),"zoneId" to str(d.zoneId),"feb29Policy" to str(d.feb29Policy),"lunarLeapPolicy" to str(d.lunarLeapPolicy),"lunarSmallMonthPolicy" to str(d.lunarSmallMonthPolicy),"calendarEngineVersion" to str(d.calendarEngineVersion))
 private fun readDate(o:JsonObject):DateSpec { fields(o,"calendar year month day leapMonth allDay localTime zoneId feb29Policy lunarLeapPolicy lunarSmallMonthPolicy calendarEngineVersion"); return DateSpec(o.s("calendar"),o.nn("year")?.also { demand(it in 1900..2100,"DATE_OUT_OF_RANGE") }?.toInt(),o.i("month"),o.i("day"),o.b("leapMonth"),o.b("allDay"),o.ns("localTime"),o.ns("zoneId"),o.s("feb29Policy"),o.s("lunarLeapPolicy"),o.s("lunarSmallMonthPolicy"),o.s("calendarEngineVersion")) }
 private fun repeat(r:RecurrenceSpec) = obj("frequency" to str(r.frequency),"intervalDays" to num(r.intervalDays),"until" to str(r.until))
 private fun readRepeat(o:JsonObject):RecurrenceSpec { fields(o,"frequency intervalDays until"); return RecurrenceSpec(o.s("frequency"),o.nn("intervalDays")?.also { demand(it in 1..365,"REPEAT_INVALID") }?.toInt(),o.ns("until")) }
 private fun goal(g:GoalDetail?) :JsonElement = g?.let { obj("startDate" to str(it.startDate),"state" to str(it.state),"completedAt" to num(it.completedAt),"includeInParent" to bool(it.includeInParent)) } ?: JsonNull
 private fun readGoal(e:JsonElement?):GoalDetail? { if(e==JsonNull) return null; val o=e?.o()?:throw AppException("FILE_SCHEMA_INVALID"); fields(o,"startDate state completedAt includeInParent"); return GoalDetail(o.s("startDate"),o.s("state"),o.nn("completedAt"),o.b("includeInParent")) }
 private fun appearance(a:Appearance,full:Boolean):JsonObject {
  val base=linkedMapOf<String,JsonElement>("backgroundKind" to str(if(!full&&a.backgroundKind=="photo")"gradient" else a.backgroundKind),"presetKey" to str(a.presetKey),"solidArgb" to num(a.solidArgb),"textColorMode" to str(a.textColorMode),"fontKey" to str(a.fontKey))
  if(full) base.putAll(mapOf("assetRef" to str(a.assetId),"focusX" to num(a.focusX),"focusY" to num(a.focusY),"dimAmount" to num(a.dimAmount)))
  return JsonObject(base)
 }
 private fun readAppearance(o:JsonObject,full:Boolean):Appearance {
  fields(o,"backgroundKind presetKey textColorMode fontKey",if(full)"solidArgb assetRef focusX focusY dimAmount" else "solidArgb")
  val kind=o.s("backgroundKind"); demand(kind in if(full)setOf("gradient","solid","photo")else setOf("gradient","solid"),"FILE_SCHEMA_INVALID")
  if(kind=="photo") demand(listOf("assetRef","focusX","focusY","dimAmount").all { it in o } && o.ns("assetRef")!=null,"ASSET_MISSING")
  return Appearance(kind,if(full&&"assetRef" in o)o.ns("assetRef")else null,o.s("presetKey"),if("solidArgb" in o)o.i("solidArgb")else -13278421,o.d("focusX",.5),o.d("focusY",.5),o.d("dimAmount",.35),o.s("textColorMode"),o.s("fontKey"))
 }
 private fun book(b:Book,full:Boolean):JsonObject { val m=linkedMapOf<String,JsonElement>("ref" to str(b.id),"name" to str(b.name),"builtinKey" to str(b.builtinKey),"iconKey" to str(b.iconKey),"colorArgb" to num(b.colorArgb),"sortRank" to num(b.sortRank)); if(full)m.putAll(mapOf("coverAssetRef" to str(b.coverAssetId),"createdAt" to num(b.createdAt),"updatedAt" to num(b.updatedAt),"version" to num(b.version))); return JsonObject(m) }
 private fun readBook(o:JsonObject,full:Boolean):Book { fields(o,"ref name builtinKey iconKey colorArgb sortRank"+if(full)" coverAssetRef createdAt updatedAt version"else ""); val builtin=o.ns("builtinKey"); demand(builtin==null||builtin in setOf("birthday","memorial","holiday","goal","uncategorized"),"FILE_SCHEMA_INVALID"); return Book(ref(o,"ref"),o.s("name"),builtin,o.s("iconKey"),o.i("colorArgb"),if(full)o.ns("coverAssetRef")else null,o.n("sortRank"),if(full)o.n("createdAt")else 0,if(full)o.n("updatedAt")else 0,if(full)o.n("version")else 1) }
 private fun event(e:Event,full:Boolean,tags:Map<String,Tag>):JsonObject {
  val m=linkedMapOf<String,JsonElement>("ref" to str(e.id),"bookRef" to str(e.bookId),"parentRef" to str(e.parentId),"title" to str(e.title),"kind" to str(e.kind),"countMode" to str(e.countMode),"includeStartDay" to bool(e.includeStartDay),"greeting" to str(e.greeting),"homeVisible" to bool(e.homeVisible),"pinned" to bool(e.pinned),"sortRank" to num(e.sortRank),"date" to date(e.date),"repeat" to repeat(e.repeat),"appearance" to appearance(e.appearance,full),"goal" to goal(e.goal))
  if(full)m.putAll(mapOf("tagRefs" to arr(e.tagIds.map{str(it)}),"createdAt" to num(e.createdAt),"updatedAt" to num(e.updatedAt),"version" to num(e.version),"reminders" to arr(e.reminders.map{r->obj("ref" to str(r.id),"enabled" to bool(r.enabled),"offsetUnit" to str(r.offsetUnit),"offsetValue" to num(r.offsetValue),"localTime" to str(r.localTime),"precisionMode" to str(r.precisionMode),"version" to num(r.version))})))
  else m.putAll(mapOf("tags" to arr(e.tagIds.mapNotNull{tags[it]?.name}.map{str(it)}),"backgroundFallback" to str(if(e.appearance.backgroundKind=="photo")"photo_omitted"else"none")))
  return JsonObject(m)
 }
 private fun readEvent(o:JsonObject,full:Boolean,tagByName:MutableMap<String,Tag>):Event {
  fields(o,"ref bookRef parentRef title kind countMode includeStartDay greeting homeVisible pinned sortRank date repeat appearance goal"+if(full)" tagRefs createdAt updatedAt version reminders" else " tags backgroundFallback")
  val tags=if(full) o.a("tagRefs").map { scalarString(it) } else o.a("tags").map{v->val name=scalarString(v);tagByName.getOrPut(name){Tag(name=name)}.id}
  demand(tags.size<=20&&tags.distinct().size==tags.size,"FILE_SCHEMA_INVALID")
  if(!full)demand(o.s("backgroundFallback")in setOf("none","photo_omitted"),"FILE_SCHEMA_INVALID")
  val rules=if(full)o.a("reminders").map{ e->val r=fields(e.o(),"ref enabled offsetUnit offsetValue localTime precisionMode version");ReminderRule(ref(r,"ref"),r.b("enabled"),r.s("offsetUnit"),r.i("offsetValue"),r.ns("localTime"),r.s("precisionMode"),r.n("version")) }else emptyList()
  return Event(ref(o,"ref"),ref(o,"bookRef"),o.ns("parentRef"),o.s("title"),o.s("kind"),o.s("countMode"),o.b("includeStartDay"),o.s("greeting"),o.b("homeVisible"),o.b("pinned"),o.n("sortRank"),readDate(o.o("date")),readRepeat(o.o("repeat")),readAppearance(o.o("appearance"),full),readGoal(o["goal"]),rules,tags,if(full)o.n("createdAt")else 0,if(full)o.n("updatedAt")else 0,if(full)o.n("version")else 1)
 }
 private fun scalarString(e:JsonElement):String { val p=e as? JsonPrimitive?:throw AppException("FILE_SCHEMA_INVALID"); demand(p.isString,"FILE_SCHEMA_INVALID"); return p.content }
 private fun ref(o:JsonObject,k:String):String = o.s(k).also{ demand(it.isNotEmpty()&&it.length<=128,"FILE_SCHEMA_INVALID",k) }
 private fun check(state:LibraryState) {
  LibraryValidator.validate(state,dates);state.events.forEach { dates.validate(it.dateInput()) }
  val refs=state.books.map{it.id}+state.events.map{it.id}+state.tags.map{it.id}+state.assets.map{it.id}+state.actions.map{it.id}+state.causes.map{it.id}+state.imports.map{it.id}+state.events.flatMap{it.reminders}.map{it.id}
  demand(refs.size==refs.distinct().size&&refs.all{it.isNotEmpty()&&it.length<=128},"FILE_REF_INVALID")
  state.books.forEach{demand(it.iconKey.length<=64,"FILE_SCHEMA_INVALID")}
  state.events.forEach{e->demand(e.appearance.presetKey.length<=64&&e.appearance.fontKey.length<=64&&e.date.calendarEngineVersion.length<=64&&(e.date.zoneId?.length?:0)<=128&&e.tagIds.size<=20,"FILE_SCHEMA_INVALID")}
  state.assets.forEach{a->val extension=when(a.mimeType){"image/jpeg"->"jpg";"image/png"->"png";"image/webp"->"webp";else->throw AppException("ASSET_INVALID")};demand(a.sha256.matches(Regex("[0-9a-f]{64}"))&&a.relativePath=="assets/${a.sha256}.$extension","ASSET_INVALID")}
  demand(state.causes.size<=200000&&state.imports.size<=200000,"FILE_LIMIT_EXCEEDED")
 }
 fun exportJson(state:LibraryState,selectedIds:Set<String>?=null):ByteArray {
  check(state); val selected=state.events.filter{ (selectedIds==null||it.id in selectedIds)&&state.lifecycle(it.id)=="active" }; val ids=selected.map{it.id}.toSet()
  val output=obj("format" to str("countdown_events"),"version" to num(1),"exportId" to str(newId()),"exportedAt" to str(Instant.now().toString()),"books" to arr(state.books.filter{b->selected.any{it.bookId==b.id}}.map{book(it,false)}),"events" to arr(selected.map{event(it.copy(parentId=it.parentId?.takeIf{p->p in ids}),false,state.tags.associateBy{it.id})})).toString().toByteArray()
  demand(output.size.toLong()<=textLimit,"FILE_LIMIT_EXCEEDED"); return output
 }
 fun importJson(bytes:ByteArray):ImportPreview {
  val o=fields(parse(bytes),"format version exportId exportedAt books events"); demand(o.s("format")=="countdown_events"&&o.n("version")==1L,"FILE_VERSION_UNSUPPORTED"); UUID.fromString(o.s("exportId"));Instant.parse(o.s("exportedAt"))
  val tags=linkedMapOf<String,Tag>(); val books=o.a("books").map{readBook(it.o(),false)}.toMutableList();if(books.none{it.builtinKey=="uncategorized"})books+=Book(name=if(books.any{it.name=="未分类"})"未分类 (导入)"else"未分类",builtinKey="uncategorized");val state=LibraryState(books=books,events=o.a("events").map{readEvent(it.o(),false,tags)},tags=tags.values.toList())
  check(state); return ImportPreview(state,o.s("exportId"),sha256(bytes),"json")
 }
 fun exportCsv(state:LibraryState,ids:Set<String>):ByteArray {
  val rows=state.events.filter{it.id in ids}; demand(rows.all{it.date.calendar=="gregorian"&&it.date.allDay&&it.kind!="goal"&&it.parentId==null&&state.events.none{c->c.parentId==it.id}&&it.repeat.frequency in setOf("none","yearly","monthly","weekly")&&it.date.year!=null},"CSV_LOSS_REQUIRES_JSON")
  val header="schema_version,escape_mode,title,date,calendar,type,repeat,message\r\n"
  val result=header+rows.joinToString(""){e->listOf("1","apostrophe_v1",e.title,LocalDate.of(e.date.year!!,e.date.month,e.date.day).toString(),"gregorian",e.kind,e.repeat.frequency,e.greeting).map{escapeFormula(it)}.joinToString(","){csvQuote(it)}+"\r\n"}
  return result.toByteArray().also{demand(it.size.toLong()<=textLimit,"FILE_LIMIT_EXCEEDED")}
 }
 fun importCsv(bytes:ByteArray):ImportPreview {
  demand(bytes.size.toLong()<=textLimit,"FILE_LIMIT_EXCEEDED"); val rows=parseCsv(utf8(bytes).removePrefix("\uFEFF"));demand(rows.isNotEmpty(),"CSV_HEADER_INVALID")
  val current=listOf("schema_version","escape_mode","title","date","calendar","type","repeat","message");val old=current.drop(2);val modern=rows.first().second==current
  demand(modern||rows.first().second==old,"CSV_HEADER_INVALID");if(modern)demand(rows.drop(1).filter{it.second.any(String::isNotEmpty)}.all{it.second.size>=2&&it.second[0]=="1"&&it.second[1]=="apostrophe_v1"},"CSV_ESCAPE_INVALID");val issues=mutableListOf<LineIssue>();val events=mutableListOf<Event>();val b=Book(name="导入的日子",builtinKey="uncategorized")
  rows.drop(1).forEach { (line,values)->if(values.any{it.isNotEmpty()})try { demand(values.size==if(modern)8 else 6,"CSV_COLUMN_INVALID"); if(modern)demand(values[0]=="1"&&values[1]=="apostrophe_v1","CSV_ESCAPE_INVALID");val v=if(modern)values.drop(2).map(::unescapeFormula)else values;demand(v[2]=="gregorian"&&v[3]in setOf("birthday","memorial","holiday","ordinary")&&v[4]in setOf("none","yearly","monthly","weekly"),"CSV_VALUE_INVALID"); val day=LocalDate.parse(v[1]); val e=Event(id="row:$line",bookId=b.id,title=v[0],kind=v[3],greeting=v[5],date=DateSpec(year=day.year,month=day.monthValue,day=day.dayOfMonth),repeat=RecurrenceSpec(v[4]));check(LibraryState(books=listOf(b),events=listOf(e)));events+=e }catch(e:Exception){issues+=LineIssue(line,(e as? AppException)?.code?:"CSV_VALUE_INVALID","第 $line 行无效，未导入")}}
  demand(events.size<=2000,"LIBRARY_LIMIT_EXCEEDED"); return ImportPreview(LibraryState(books=listOf(b),events=events),"csv:${sha256(bytes)}",sha256(bytes),"csv",issues)
 }
 /** Call within repository.transaction and bind confirmation to the original epoch/revision. */
 fun merge(target:LibraryState,preview:ImportPreview,now:Long=System.currentTimeMillis()):LibraryState {
  val source=preview.state;check(source);if(target.imports.any{it.sourceExportId==preview.sourceExportId&&it.fileSha256==preview.fileSha256})return target
  val prior=target.imports.filter{it.sourceExportId==preview.sourceExportId}.flatMap{it.provenance};val seen=prior.map{it.sourceRef}.toSet();val added=source.events.filter{it.id !in seen};if(added.isEmpty()&&source.events.isNotEmpty())return target
  val oldMap=prior.associate{it.sourceRef to it.localEventId};val bookMap=mutableMapOf<String,String>();val books=target.books.toMutableList();val newBooks=mutableMapOf<String,Book>()
  source.books.forEach{b->val builtin=b.builtinKey?.let{k->books.firstOrNull{it.builtinKey==k}};val priorBooks=source.events.filter{it.bookId==b.id}.mapNotNull{oldMap[it.id]}.mapNotNull{id->target.events.firstOrNull{it.id==id}?.bookId}.distinct();val existing=builtin?:priorBooks.singleOrNull()?.let{id->books.firstOrNull{it.id==id}};if(existing!=null)bookMap[b.id]=existing.id else {var name=b.name;var n=2;while(books.any{nameKey(it.name)==nameKey(name)}){val clusters=java.util.regex.Pattern.compile("\\X").matcher(b.name);var count=0;var end=0;while(count<22&&clusters.find()){end=clusters.end();count++};name="${b.name.substring(0,end)} ($n)";n++};val copy=b.copy(id=newId(),name=name,coverAssetId=null,createdAt=now,updatedAt=now,version=1);books+=copy;bookMap[b.id]=copy.id;newBooks[copy.id]=b}}
  val tagMap=mutableMapOf<String,String>();val tags=target.tags.toMutableList();source.tags.forEach{t->val found=tags.firstOrNull{nameKey(it.name)==nameKey(t.name)}; val copy=found?:t.copy(id=newId(),createdAt=now).also{tags+=it};tagMap[t.id]=copy.id}
  val eventMap=added.associate{it.id to newId()}
  val assets=target.assets.toMutableList();val assetMap=source.assets.associate{a->val found=assets.firstOrNull{it.sha256==a.sha256};val copy=found?:a.copy(id=newId()).also{assets+=it};a.id to copy.id}
  val copies=added.map{e->e.copy(id=eventMap.getValue(e.id),bookId=bookMap.getValue(e.bookId),parentId=e.parentId?.let{eventMap[it]?:oldMap[it]},tagIds=e.tagIds.map{tagMap.getValue(it)},appearance=e.appearance.copy(assetId=e.appearance.assetId?.let{assetMap[it]}),reminders=e.reminders.map{it.copy(id=newId(),enabled=false,version=1)},createdAt=now,updatedAt=now,version=1)}
  val actions=source.actions.filter{it.goalEventId in eventMap}.map{it.copy(id=newId(),goalEventId=eventMap.getValue(it.goalEventId),createdAt=now,updatedAt=now,version=1)}
  val causes=source.causes.mapNotNull{c->val members=c.members.mapNotNull{eventMap[it]};if(members.isEmpty())null else c.copy(id=newId(),sourceEventId=c.sourceEventId?.let{eventMap[it]},sourceBookId=c.sourceBookId?.let{bookMap[it]},members=members)}
  val batch=ImportBatch(format=preview.format,sourceExportId=preview.sourceExportId,fileSha256=preview.fileSha256,importedAt=now,provenance=added.map{ImportOrigin(it.id,eventMap[it.id])})
  return target.copy(books=books.map{b->newBooks[b.id]?.let{original->b.copy(coverAssetId=original.coverAssetId?.let{assetMap[it]})}?:b},events=target.events+copies,tags=tags,assets=assets,actions=target.actions+actions,causes=target.causes+causes,imports=target.imports+batch).also(::check)
 }
 private fun snapshot(s:LibraryState):JsonObject = obj("format" to str("daybook_library"),"version" to num(1),"library" to obj("id" to str(s.id),"name" to str(s.name),"contentRevision" to num(s.revision),"createdAt" to num(s.createdAt),"updatedAt" to num(s.updatedAt)),"books" to arr(s.books.map{book(it,true)}),"events" to arr(s.events.map{event(it,true,s.tags.associateBy{t->t.id})}),"assets" to arr(s.assets.map{a->obj("ref" to str(a.id),"sha256" to str(a.sha256),"path" to str(a.relativePath),"mimeType" to str(a.mimeType),"bytes" to num(a.bytes),"width" to num(a.width),"height" to num(a.height),"createdAt" to num(a.createdAt))}),"actions" to arr(s.actions.map{a->obj("ref" to str(a.id),"goalRef" to str(a.goalEventId),"date" to str(a.date),"body" to str(a.body),"minutes" to num(a.minutes),"createdAt" to num(a.createdAt),"updatedAt" to num(a.updatedAt),"version" to num(a.version))}),"tags" to arr(s.tags.map{t->obj("ref" to str(t.id),"name" to str(t.name),"createdAt" to num(t.createdAt))}),"lifecycleCauses" to arr(s.causes.map{c->obj("ref" to str(c.id),"kind" to str(c.kind),"sourceEventRef" to str(c.sourceEventId),"sourceBookRef" to str(c.sourceBookId),"createdAt" to num(c.createdAt),"purgeAfter" to num(c.purgeAfter),"members" to arr(c.members.map{str(it)}))}),"home" to obj("heroMode" to str(s.home.heroMode),"fixedEventRef" to str(s.home.fixedEventId),"sortMode" to str(s.home.sortMode),"selectedBookRef" to str(s.home.selectedBookId)),"importHistory" to arr(s.imports.map{b->obj("batchRef" to str(b.id),"format" to str(when(b.format){"json"->"events_json";"csv"->"events_csv";"backup"->"full_backup";else->throw AppException("IMPORT_INVALID")}),"sourceExportId" to str(b.sourceExportId),"fileSha256" to str(b.fileSha256),"importedAt" to num(b.importedAt),"provenance" to arr(b.provenance.map{p->obj("sourceRef" to str(p.sourceRef),"localEventRef" to str(p.localEventId))}))}))
 private fun readSnapshot(bytes:ByteArray):LibraryState {
  val o=fields(parse(bytes,64L*1024*1024),"format version library books events assets actions tags lifecycleCauses home importHistory");demand(o.s("format")=="daybook_library"&&o.n("version")==1L,"FILE_VERSION_UNSUPPORTED")
  val lib=fields(o.o("library"),"id name contentRevision createdAt updatedAt");UUID.fromString(lib.s("id"));val h=fields(o.o("home"),"heroMode fixedEventRef sortMode selectedBookRef")
  val state=LibraryState(id=lib.s("id"),name=lib.s("name"),revision=lib.n("contentRevision"),createdAt=lib.n("createdAt"),updatedAt=lib.n("updatedAt"),books=o.a("books").map{readBook(it.o(),true)},events=o.a("events").map{readEvent(it.o(),true,linkedMapOf())},tags=o.a("tags").map{v->val t=fields(v.o(),"ref name createdAt");Tag(ref(t,"ref"),t.s("name"),t.n("createdAt"))},assets=o.a("assets").map{v->val a=fields(v.o(),"ref sha256 path mimeType bytes width height createdAt");Asset(ref(a,"ref"),a.s("sha256"),a.s("path"),a.s("mimeType"),a.n("bytes"),a.i("width"),a.i("height"),a.n("createdAt"))},actions=o.a("actions").map{v->val a=fields(v.o(),"ref goalRef date body minutes createdAt updatedAt version");ActionRecord(ref(a,"ref"),ref(a,"goalRef"),a.s("date"),a.s("body"),a.nn("minutes")?.also{demand(it in 0..1440,"FILE_SCHEMA_INVALID")}?.toInt(),a.n("createdAt"),a.n("updatedAt"),a.n("version"))},causes=o.a("lifecycleCauses").map{v->val c=fields(v.o(),"ref kind sourceEventRef sourceBookRef createdAt purgeAfter members");LifecycleCause(ref(c,"ref"),c.s("kind"),c.ns("sourceEventRef"),c.ns("sourceBookRef"),c.n("createdAt"),c.nn("purgeAfter"),c.a("members").map(::scalarString))},home=HomeConfig(h.s("heroMode"),h.ns("fixedEventRef"),h.s("sortMode"),h.ns("selectedBookRef")),imports=o.a("importHistory").map{v->val b=fields(v.o(),"batchRef format sourceExportId fileSha256 importedAt provenance");ImportBatch(ref(b,"batchRef"),when(b.s("format")){"events_json"->"json";"events_csv"->"csv";"full_backup"->"backup";else->throw AppException("FILE_SCHEMA_INVALID")},ref(b,"sourceExportId"),b.s("fileSha256"),b.n("importedAt"),b.a("provenance").map{p->val q=fields(p.o(),"sourceRef localEventRef");ImportOrigin(ref(q,"sourceRef"),q.ns("localEventRef"))})})
  check(state);return state
 }
 fun writeBackup(state:LibraryState,assetRoot:File,out:OutputStream,password:CharArray?,includeTrash:Boolean=false):BackupReceipt {
  check(state);val omitted=state.events.filter{!includeTrash&&state.lifecycle(it.id)=="trash"}.map{it.id}.toSet();val events=state.events.filter{it.id !in omitted};val used=events.mapNotNull{it.appearance.assetId}.toSet()+state.books.mapNotNull{it.coverAssetId};val s=state.copy(events=events,actions=state.actions.filter{it.goalEventId !in omitted},assets=state.assets.filter{it.id in used},causes=state.causes.mapNotNull{c->val members=c.members.filter{it !in omitted};if(members.isEmpty())null else c.copy(members=members,sourceEventId=c.sourceEventId?.takeIf{it !in omitted})},home=state.home.copy(fixedEventId=state.home.fixedEventId?.takeIf{it !in omitted},heroMode=if(state.home.fixedEventId in omitted)"auto"else state.home.heroMode),imports=state.imports.map{b->b.copy(provenance=b.provenance.map{it.copy(localEventId=it.localEventId?.takeIf{id->id !in omitted})})})
  check(s);val temp=File.createTempFile("datebook-payload-",".zip",assetRoot.parentFile?:assetRoot);val backupId=newId()
  try {
   val content=snapshot(s).toString().toByteArray();val files=mutableListOf(obj("path" to str("library.json"),"bytes" to num(content.size),"sha256" to str(sha256(content))))
   s.assets.forEach{a->val f=safeAsset(assetRoot,a.relativePath);demand(f.isFile&&f.length()==a.bytes&&sha256(f)==a.sha256,"ASSET_CORRUPT");files+=obj("path" to str(a.relativePath),"bytes" to num(a.bytes),"sha256" to str(a.sha256))}
   val manifest=obj("format" to str("daybook_manifest"),"version" to num(1),"backupId" to str(backupId),"createdAt" to str(Instant.now().toString()),"contentRevision" to num(s.revision),"snapshotSchemaVersion" to num(1),"counts" to obj("books" to num(s.books.size),"events" to num(s.events.size),"actions" to num(s.actions.size),"assets" to num(s.assets.size)),"files" to arr(files)).toString().toByteArray()
   ZipOutputStream(temp.outputStream().buffered()).apply{setLevel(0)}.use{z->fun entry(path:String,write:()->Unit){z.putNextEntry(ZipEntry(path).apply{time=0});write();z.closeEntry()};entry("manifest.json"){z.write(manifest)};entry("library.json"){z.write(content)};s.assets.forEach{a->entry(a.relativePath){safeAsset(assetRoot,a.relativePath).inputStream().use{it.copyTo(z)}}}}
   demand(temp.length()<containerLimit-8192,"FILE_LIMIT_EXCEEDED");val encrypted=password!=null;val salt=if(encrypted)random(16)else null;val nonce=if(encrypted)random(12)else null;val header=obj("containerVersion" to num(1),"suite" to str(if(encrypted)"pbkdf2-sha256-aes256gcm"else"plain"),"salt" to str(salt?.let{Base64.getEncoder().encodeToString(it)}),"nonce" to str(nonce?.let{Base64.getEncoder().encodeToString(it)}),"iterations" to num(if(encrypted)600000 else null),"payloadFormat" to str("zip")).toString().toByteArray();val prefix=ByteArrayOutputStream().also{b->DataOutputStream(b).apply{write("DAYBOOK1".toByteArray());writeByte(if(encrypted)1 else 0);writeInt(header.size);write(header)}}.toByteArray()
   val digest=MessageDigest.getInstance("SHA-256");var count=0L;val target=object:FilterOutputStream(out){override fun write(b:Int){out.write(b);digest.update(b.toByte());count++};override fun write(b:ByteArray,off:Int,len:Int){out.write(b,off,len);digest.update(b,off,len);count+=len}}
   target.write(prefix);if(encrypted){val key=derive(password!!,salt!!);try{val c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,SecretKeySpec(key,"AES"),GCMParameterSpec(128,nonce));c.updateAAD(prefix);cipherCopy(temp,c,target)}finally{key.fill(0)}}else temp.inputStream().use{it.copyTo(target)};target.flush();return BackupReceipt(backupId,hex(digest.digest()),count)
  } finally {temp.delete()}
 }
 fun readBackup(input:InputStream,staging:File,password:CharArray?):BackupPreview {
  demand(!staging.exists()||staging.listFiles().isNullOrEmpty(),"STAGING_NOT_EMPTY");demand(staging.mkdirs()||staging.isDirectory,"FILE_IO_FAILED");val source=File(staging,"container.tmp");val zip=File(staging,"payload.tmp");var success=false
  try {
   source.outputStream().use{o->copyBounded(input,o,containerLimit)};val digest=sha256(source);var encrypted=false
   DataInputStream(source.inputStream().buffered()).use{d->val magic=ByteArray(8);d.readFully(magic);demand(magic.contentEquals("DAYBOOK1".toByteArray()),"FILE_VERSION_UNSUPPORTED");val suite=d.readUnsignedByte();demand(suite in 0..1,"FILE_VERSION_UNSUPPORTED");encrypted=suite==1;val length=d.readInt();demand(length in 1..4096,"FILE_SCHEMA_INVALID");val hb=ByteArray(length);d.readFully(hb);val h=fields(parse(hb,4096),"containerVersion suite salt nonce iterations payloadFormat");demand(h.n("containerVersion")==1L&&h.s("payloadFormat")=="zip","FILE_VERSION_UNSUPPORTED");val prefix=ByteArrayOutputStream().also{b->DataOutputStream(b).apply{write(magic);writeByte(suite);writeInt(length);write(hb)}}.toByteArray()
    zip.outputStream().use{o->if(encrypted){demand(h.s("suite")=="pbkdf2-sha256-aes256gcm"&&h.nn("iterations")==600000L,"FILE_VERSION_UNSUPPORTED");val salt=decode64(h.s("salt"),16);val nonce=decode64(h.s("nonce"),12);demand(password!=null,"PASSWORD_REQUIRED");val key=derive(password!!,salt);try{val c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.DECRYPT_MODE,SecretKeySpec(key,"AES"),GCMParameterSpec(128,nonce));c.updateAAD(prefix);try{cipherCopy(d,c,o,containerLimit)}catch(e:Exception){throw AppException("BACKUP_AUTH_FAILED")}}finally{key.fill(0)}}else{demand(h.s("suite")=="plain"&&h["salt"]==JsonNull&&h["nonce"]==JsonNull&&h["iterations"]==JsonNull,"FILE_SCHEMA_INVALID");copyBounded(d,o,containerLimit)}}
   }
   val entries=linkedMapOf<String,File>();var total=0L
   ZipInputStream(zip.inputStream().buffered()).use{z->while(true){val e=z.nextEntry?:break;val p=e.name;demand(!e.isDirectory&&p !in entries&&(p=="manifest.json"||p=="library.json"||p.matches(Regex("assets/[0-9a-f]{64}\\.(jpg|png|webp)"))),"BACKUP_PATH_INVALID");demand(entries.size<20000,"FILE_LIMIT_EXCEEDED");val f=File(staging,p);f.parentFile.mkdirs();f.outputStream().use{o->total+=copyBounded(z,o,if(p.startsWith("assets/"))26214400 else 64L*1024*1024)};demand(total<=expandedLimit&&(total<=1024*1024||total<=zip.length()*100),"FILE_LIMIT_EXCEEDED");entries[p]=f;z.closeEntry()}}
   val manifest=fields(parse((entries["manifest.json"]?:throw AppException("BACKUP_MANIFEST_INVALID")).readBytes(),64L*1024*1024),"format version backupId createdAt contentRevision snapshotSchemaVersion counts files");demand(manifest.s("format")=="daybook_manifest"&&manifest.n("version")==1L&&manifest.n("snapshotSchemaVersion")==1L,"FILE_VERSION_UNSUPPORTED");UUID.fromString(manifest.s("backupId"));Instant.parse(manifest.s("createdAt"));val listed=mutableSetOf<String>();manifest.a("files").forEach{v->val f=fields(v.o(),"path bytes sha256");val path=f.s("path");demand(listed.add(path)&&path!="manifest.json","BACKUP_MANIFEST_INVALID");val file=entries[path]?:throw AppException("BACKUP_MANIFEST_INVALID");demand(file.length()==f.n("bytes")&&sha256(file)==f.s("sha256"),"BACKUP_CHECKSUM_INVALID")};demand(listed==entries.keys-"manifest.json","BACKUP_MANIFEST_INVALID")
   val state=readSnapshot((entries["library.json"]?:throw AppException("BACKUP_MANIFEST_INVALID")).readBytes());val counts=fields(manifest.o("counts"),"books events actions assets");demand(counts.n("books")==state.books.size.toLong()&&counts.n("events")==state.events.size.toLong()&&counts.n("actions")==state.actions.size.toLong()&&counts.n("assets")==state.assets.size.toLong()&&manifest.n("contentRevision")==state.revision,"BACKUP_MANIFEST_INVALID")
   demand(entries.keys.filter{it.startsWith("assets/")}.toSet()==state.assets.map{it.relativePath}.toSet(),"BACKUP_MANIFEST_INVALID");state.assets.forEach{a->val f=entries[a.relativePath]?:throw AppException("ASSET_MISSING");demand(f.length()==a.bytes&&sha256(f)==a.sha256&&a.width.toLong()*a.height<=40000000,"ASSET_CORRUPT")};source.delete();zip.delete();entries["manifest.json"]?.delete();entries["library.json"]?.delete();success=true
   return BackupPreview(state.copy(epoch=newId(),events=state.events.map{e->e.copy(reminders=e.reminders.map{it.copy(enabled=false)})}),manifest.s("backupId"),staging,encrypted,digest)
  }catch(e:AppException){throw e}catch(e:Exception){throw AppException("BACKUP_FILE_INVALID")}finally{if(!success)staging.deleteRecursively()}
 }
 private fun decode64(value:String,size:Int):ByteArray = try{Base64.getDecoder().decode(value).also{demand(it.size==size&&Base64.getEncoder().encodeToString(it)==value,"FILE_SCHEMA_INVALID")}}catch(e:AppException){throw e}catch(e:Exception){throw AppException("FILE_SCHEMA_INVALID")}
 private fun safeAsset(root:File,path:String):File {demand(path.matches(Regex("assets/[0-9a-f]{64}\\.(jpg|png|webp)")),"BACKUP_PATH_INVALID");val f=File(root,path);demand(f.canonicalPath.startsWith(root.canonicalPath+File.separator),"BACKUP_PATH_INVALID");return f}
 private fun random(n:Int)=ByteArray(n).also{SecureRandom().nextBytes(it)}
 private fun derive(password:CharArray,salt:ByteArray):ByteArray {
  val chars=String(password);demand(chars.codePointCount(0,chars.length)>=8&&chars.toByteArray().size<=1024,"PASSWORD_INVALID");var i=0;while(i<chars.length){val c=chars[i];if(Character.isHighSurrogate(c)){demand(i+1<chars.length&&Character.isLowSurrogate(chars[i+1]),"PASSWORD_INVALID");i++}else demand(!Character.isLowSurrogate(c),"PASSWORD_INVALID");i++}
  val bytes=chars.toByteArray(StandardCharsets.UTF_8);try{val mac=Mac.getInstance("HmacSHA256");mac.init(SecretKeySpec(bytes,"HmacSHA256"));var u=mac.doFinal(salt+byteArrayOf(0,0,0,1));val result=u.clone();repeat(599999){val next=mac.doFinal(u);u.fill(0);u=next;for(j in result.indices)result[j]=(result[j].toInt() xor u[j].toInt()).toByte()};u.fill(0);return result}finally{bytes.fill(0)}
 }
 private fun cipherCopy(file:File,c:Cipher,out:OutputStream)=file.inputStream().use{cipherCopy(it,c,out,containerLimit)}
 private fun cipherCopy(input:InputStream,c:Cipher,out:OutputStream,max:Long){val buf=ByteArray(65536);var count=0L;while(true){val n=input.read(buf);if(n<0)break;count+=n;demand(count<=max,"FILE_LIMIT_EXCEEDED");c.update(buf,0,n)?.let{out.write(it)}};out.write(c.doFinal());buf.fill(0)}
 private fun copyBounded(input:InputStream,out:OutputStream,max:Long):Long{var total=0L;val b=ByteArray(65536);while(true){val n=input.read(b);if(n<0)break;total+=n;demand(total<=max,"FILE_LIMIT_EXCEEDED");out.write(b,0,n)};return total}
 private fun escapeFormula(s:String)=if(s.firstOrNull()?.let { it in "=+-@\t\r\n'" }==true)"'$s"else s
 private fun unescapeFormula(s:String)=if(s.length>=2&&s[0]=='\''&&s[1]in "=+-@\t\r\n'")s.substring(1)else s
 private fun csvQuote(s:String)="\"${s.replace("\"","\"\"")}\""
 private fun parseCsv(s:String):List<Pair<Int,List<String>>>{val result=mutableListOf<Pair<Int,List<String>>>();val row=mutableListOf<String>();val cell=StringBuilder();var quoted=false;var endedQuote=false;var line=1;var start=1;var i=0;while(i<s.length){val c=s[i];if(quoted){if(c=='"'){if(i+1<s.length&&s[i+1]=='"'){cell.append('"');i++}else{quoted=false;endedQuote=true}}else{cell.append(c);if(c=='\n')line++}}else when(c){'"'->{demand(cell.isEmpty()&&!endedQuote,"CSV_SYNTAX_INVALID");quoted=true};','->{row+=cell.toString();cell.clear();endedQuote=false};'\r','\n'->{if(c=='\r'&&i+1<s.length&&s[i+1]=='\n')i++;row+=cell.toString();result+=start to row.toList();row.clear();cell.clear();endedQuote=false;line++;start=line};else->{demand(!endedQuote,"CSV_SYNTAX_INVALID");cell.append(c)}};i++};demand(!quoted,"CSV_SYNTAX_INVALID");if(cell.isNotEmpty()||row.isNotEmpty()||endedQuote){row+=cell.toString();result+=start to row};return result}
 /** JSON's default parser accepts duplicate keys. Scan structure first with bounded nesting. */
 private fun rejectDuplicateKeys(text:String){var i=0;fun ws(){while(i<text.length&&text[i].isWhitespace())i++};fun string():String{val start=i++;while(i<text.length){val c=text[i++];if(c=='\\'){demand(i<text.length,"FILE_SCHEMA_INVALID");i++}else if(c=='"')return try{json.parseToJsonElement(text.substring(start,i)).jsonPrimitive.content.also{demand(validString(it),"FILE_ENCODING_INVALID")}}catch(e:Exception){throw AppException("FILE_SCHEMA_INVALID")}};throw AppException("FILE_SCHEMA_INVALID")};fun value(depth:Int){demand(depth<=32,"FILE_LIMIT_EXCEEDED");ws();demand(i<text.length,"FILE_SCHEMA_INVALID");when(text[i]){'{'->{i++;ws();val keys=mutableSetOf<String>();if(i<text.length&&text[i]=='}'){i++;return};while(true){ws();demand(i<text.length&&text[i]=='"',"FILE_SCHEMA_INVALID");demand(keys.add(string()),"FILE_DUPLICATE_KEY");ws();demand(i<text.length&&text[i++]==':',"FILE_SCHEMA_INVALID");value(depth+1);ws();demand(i<text.length,"FILE_SCHEMA_INVALID");val c=text[i++];if(c=='}')break;demand(c==',',"FILE_SCHEMA_INVALID")}};'['->{i++;ws();if(i<text.length&&text[i]==']'){i++;return};while(true){value(depth+1);ws();demand(i<text.length,"FILE_SCHEMA_INVALID");val c=text[i++];if(c==']')break;demand(c==',',"FILE_SCHEMA_INVALID")}};'"'->{string()};else->{val start=i;while(i<text.length&&text[i] !in ",]} \t\r\n")i++;demand(i>start,"FILE_SCHEMA_INVALID")}}};value(0);ws();demand(i==text.length,"FILE_SCHEMA_INVALID")}
 companion object {
  fun sha256(bytes:ByteArray)=hex(MessageDigest.getInstance("SHA-256").digest(bytes))
  fun sha256(file:File):String{val d=MessageDigest.getInstance("SHA-256");file.inputStream().use{i->val b=ByteArray(65536);while(true){val n=i.read(b);if(n<0)break;d.update(b,0,n)}};return hex(d.digest())}
  private fun hex(bytes:ByteArray)=bytes.joinToString(""){"%02x".format(it.toInt() and 255)}
 }
}
