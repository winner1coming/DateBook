package cn.datebook.app.platform

import android.Manifest
import android.app.*
import android.content.*
import android.content.pm.PackageManager
import android.graphics.*
import android.net.Uri
import android.os.Build
import android.provider.CalendarContract
import android.provider.Settings
import android.text.Layout
import android.text.StaticLayout
import android.text.TextPaint
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.room.withTransaction
import androidx.work.*
import androidx.glance.appwidget.updateAll
import cn.datebook.app.DateBookApplication
import cn.datebook.app.MainActivity
import cn.datebook.app.R
import cn.datebook.app.data.RoomStore
import cn.datebook.core.*
import kotlinx.coroutines.*
import java.io.File
import java.time.*
import java.util.concurrent.TimeUnit
import kotlin.math.max

class SystemServices(private val context:Context,private val store:RoomStore,private val dates:DateEngine) {
 private val alarms=requireNotNull(context.getSystemService(AlarmManager::class.java))
 private val manager=requireNotNull(context.getSystemService(NotificationManager::class.java))
 private data class Next(val key:String,val fire:Long,val expires:Long)
 private fun next(e:Event,r:ReminderRule,after:Instant):Next? {
  val zone=if(e.date.allDay)ZoneId.systemDefault()else ZoneId.of(e.date.zoneId)
  val seconds=r.offsetValue.toLong()*when(r.offsetUnit){"days"->86400;"hours"->3600;else->60}
  var day=(if(e.date.allDay)after.atZone(zone).toLocalDate().plusDays(r.offsetValue.toLong())else after.plusSeconds(seconds).atZone(zone).toLocalDate()).coerceAtLeast(LocalDate.of(1900,1,1))
  repeat(3){val occurrence=dates.nextOccurrence(e.dateInput(),day)?:return null;val fire=if(e.date.allDay)occurrence.date.minusDays(r.offsetValue.toLong()).atTime(LocalTime.parse(r.localTime?:"09:00")).atZone(zone).toInstant()else occurrence.instant!!.minusSeconds(seconds)
   if(fire>after){val expiry=if(e.date.allDay)fire.atZone(zone).toLocalDate().plusDays(1).atStartOfDay(zone).toInstant().minusMillis(1)else fire.plusSeconds(900);return Next("${occurrence.date}@${zone.id}",fire.toEpochMilli(),expiry.toEpochMilli())};day=occurrence.date.plusDays(1)};return null
 }
 private fun expiry(e:Event,key:String,fire:Long):Long = if(e.date.allDay)Instant.ofEpochMilli(fire).atZone(ZoneId.of(key.substringAfter('@'))).toLocalDate().plusDays(1).atStartOfDay(ZoneId.of(key.substringAfter('@'))).toInstant().minusMillis(1).toEpochMilli()else fire+900000
 fun notificationAllowed():Boolean = (Build.VERSION.SDK_INT<33||ContextCompat.checkSelfPermission(context,Manifest.permission.POST_NOTIFICATIONS)==PackageManager.PERMISSION_GRANTED)&&NotificationManagerCompat.from(context).areNotificationsEnabled()&&(manager.getNotificationChannel("events")?.importance?:NotificationManager.IMPORTANCE_DEFAULT)!=NotificationManager.IMPORTANCE_NONE
 fun exactAllowed()=Build.VERSION.SDK_INT<31||alarms.canScheduleExactAlarms()
 fun requestNotificationSettings()=Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE,context.packageName)
 fun requestExactSettings()=if(Build.VERSION.SDK_INT>=31)Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,Uri.parse("package:${context.packageName}"))else requestNotificationSettings()
 suspend fun reconcile(){store.awaitReady();store.withDb{db,state,_->
  val sql=db.openHelper.writableDatabase;val now=System.currentTimeMillis();val token=newId()
  db.withTransaction {
   invalidateZones(sql,state);consume(sql,state,now)
   val existing=mutableMapOf<String,Triple<Long,Long,Long>>()
   sql.query("SELECT rule_id,fire_at,rule_version,event_version FROM reminder_queue").use{c->while(c.moveToNext())existing[c.getString(0)]=Triple(c.getLong(1),c.getLong(2),c.getLong(3))}
   val active=state.events.filter{state.lifecycle(it.id)=="active"&&it.goal?.state !in setOf("completed","canceled")}
   val ids=mutableSetOf<String>();active.forEach{e->e.reminders.filter{it.enabled}.forEach{r->ids+=r.id;val old=existing[r.id];if(old==null||old.second!=r.version||old.third!=e.version){sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(r.id));next(e,r,Instant.ofEpochMilli(now))?.let{n->sql.execSQL("INSERT INTO reminder_queue(rule_id,occurrence_key,fire_at,rule_version,event_version,epoch) VALUES(?,?,?,?,?,?)",arrayOf(r.id,n.key,n.fire,r.version,e.version,state.epoch))}}}}
   existing.keys.filter{it !in ids}.forEach{sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(it))}
   sql.execSQL("INSERT OR REPLACE INTO device_epoch(singleton,epoch,plan_token,schedule_revision) VALUES(1,?,?,?)",arrayOf(state.epoch,token,state.revision))
  }
  postTickets(sql,state,now);schedule(sql,state,token)
  manager.activeNotifications.filter { it.tag?.startsWith(state.epoch+":") == false }.forEach { manager.cancel(it.tag,it.id) }
  sql.execSQL("DELETE FROM effect_outbox WHERE kind IN ('replan','widget_refresh') AND epoch=? AND target_revision<=?",arrayOf(state.epoch,state.revision))
 };refreshWidgets();WorkManager.getInstance(context).enqueueUniquePeriodicWork("datebook-maintenance",ExistingPeriodicWorkPolicy.KEEP,PeriodicWorkRequestBuilder<MaintenanceWorker>(6,TimeUnit.HOURS).build())}
 private fun invalidateZones(sql:androidx.sqlite.db.SupportSQLiteDatabase,state:LibraryState):Boolean {
  val invalid=mutableListOf<String>();sql.query("SELECT rule_id,occurrence_key FROM reminder_queue").use{c->while(c.moveToNext()){val e=state.events.firstOrNull{event->event.reminders.any{it.id==c.getString(0)}};if(e?.date?.allDay==true&&c.getString(1).substringAfter('@')!=ZoneId.systemDefault().id)invalid+=c.getString(0)}}
  invalid.forEach{sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(it))};return invalid.isNotEmpty()
 }
 private fun consume(sql:androidx.sqlite.db.SupportSQLiteDatabase,state:LibraryState,now:Long){
  val due=mutableListOf<List<Any>>();sql.query("SELECT rule_id,occurrence_key,fire_at,rule_version,event_version,epoch FROM reminder_queue WHERE fire_at<=?",arrayOf(now)).use{c->while(c.moveToNext())due+=listOf(c.getString(0),c.getString(1),c.getLong(2),c.getLong(3),c.getLong(4),c.getString(5))}
  due.forEach{q->val id=q[0]as String;val e=state.events.firstOrNull{ev->ev.reminders.any{it.id==id}};val r=e?.reminders?.firstOrNull{it.id==id};if(e!=null&&r!=null&&r.enabled&&state.lifecycle(e.id)=="active"&&e.goal?.state !in setOf("completed","canceled")&&r.version==q[3]&&e.version==q[4]&&state.epoch==q[5]){val valid=expiry(e,q[1]as String,q[2]as Long);val tag="${state.epoch}:$id:${r.version}:${q[1]}";sql.execSQL("INSERT OR IGNORE INTO delivery_log(epoch,rule_id,occurrence_key,event_id,rule_version,event_version,fire_at,valid_until,state,notification_tag,attempt_count,next_attempt_at) VALUES(?,?,?,?,?,?,?,?,?,?,0,?)",arrayOf(state.epoch,id,q[1],e.id,r.version,e.version,q[2],valid,if(now<=valid)"pending"else"skipped",tag,now));sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(id));next(e,r,Instant.ofEpochMilli(now))?.let{n->sql.execSQL("INSERT INTO reminder_queue VALUES(?,?,?,?,?,?)",arrayOf(id,n.key,n.fire,r.version,e.version,state.epoch))}}else sql.execSQL("DELETE FROM reminder_queue WHERE rule_id=?",arrayOf(id))}
 }
 private fun alarm(epoch:String,channel:String,token:String,flags:Int=PendingIntent.FLAG_UPDATE_CURRENT):PendingIntent?=PendingIntent.getBroadcast(context,0,Intent(context,ReminderReceiver::class.java).setData(Uri.parse("daybook://alarm/$epoch/$channel")).putExtra("token",token),flags or PendingIntent.FLAG_IMMUTABLE)
 private fun schedule(sql:androidx.sqlite.db.SupportSQLiteDatabase,state:LibraryState,token:String){
  for(channel in listOf("normal","precise")){val p=alarm(state.epoch,channel,token)!!;alarms.cancel(p);var fire:Long?=null;sql.query("SELECT min(q.fire_at) FROM reminder_queue q JOIN reminder_rule r ON r.id=q.rule_id WHERE q.epoch=? AND r.precision_mode=?",arrayOf(state.epoch,channel)).use{if(it.moveToFirst()&&!it.isNull(0))fire=it.getLong(0)};fire?.let{at->try{if(channel=="precise"&&exactAllowed())alarms.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p)else alarms.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p)}catch(_:SecurityException){alarms.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,p)}}}
 }
 suspend fun deliver(epoch:String,token:String){store.awaitReady();var rebuild=false;store.withDb{db,s,_->if(s.epoch==epoch){val sql=db.openHelper.writableDatabase;var valid=false;sql.query("SELECT plan_token FROM device_epoch WHERE singleton=1 AND epoch=?",arrayOf(epoch)).use{valid=it.moveToFirst()&&it.getString(0)==token};if(valid){val nextToken=newId();db.withTransaction{rebuild=invalidateZones(sql,s);if(!rebuild){consume(sql,s,System.currentTimeMillis());sql.execSQL("UPDATE device_epoch SET plan_token=? WHERE singleton=1",arrayOf(nextToken))}};if(!rebuild){postTickets(sql,s,System.currentTimeMillis());schedule(sql,s,nextToken)}}}};if(rebuild)reconcile()}
 private fun postTickets(sql:androidx.sqlite.db.SupportSQLiteDatabase,s:LibraryState,now:Long){
  manager.createNotificationChannel(NotificationChannel("events","重要日子提醒",NotificationManager.IMPORTANCE_DEFAULT))
  val pending=mutableListOf<List<Any>>();sql.query("SELECT epoch,rule_id,occurrence_key,event_id,rule_version,event_version,valid_until,notification_tag,attempt_count FROM delivery_log WHERE state IN ('pending','posting','failed') AND next_attempt_at<=? LIMIT 50",arrayOf(now)).use{c->while(c.moveToNext())pending+=listOf(c.getString(0),c.getString(1),c.getString(2),c.getString(3),c.getLong(4),c.getLong(5),c.getLong(6),c.getString(7),c.getLong(8))}
  pending.forEach{t->val e=s.events.firstOrNull{it.id==t[3]};val r=e?.reminders?.firstOrNull{it.id==t[1]};val where="epoch=? AND rule_id=? AND rule_version=? AND occurrence_key=?";val key=arrayOf(t[0],t[1],t[4],t[2]);if(t[0]!=s.epoch||e==null||r==null||!r.enabled||r.version!=t[4]||e.version!=t[5]||s.lifecycle(e.id)!="active"||e.goal?.state in setOf("completed","canceled")||now>t[6]as Long){sql.execSQL("UPDATE delivery_log SET state='skipped' WHERE $where",key);return@forEach};if(!notificationAllowed()){sql.execSQL("UPDATE delivery_log SET state='failed',last_error_code='NOTIFICATION_DISABLED',next_attempt_at=? WHERE $where",arrayOf(now+900000,*key));return@forEach}
   sql.execSQL("UPDATE delivery_log SET state='posting',attempted_at=?,attempt_count=attempt_count+1 WHERE $where",arrayOf(now,*key));try{val intent=Intent(context,MainActivity::class.java).setData(Uri.parse("daybook://event/${s.epoch}/${e.id}"));val open=PendingIntent.getActivity(context,0,intent,PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT);val notification=NotificationCompat.Builder(context,"events").setSmallIcon(R.drawable.ic_datebook).setContentTitle(if((context.applicationContext as DateBookApplication).graph.lock.enabled)"重要日子提醒"else e.title).setContentText(if((context.applicationContext as DateBookApplication).graph.lock.enabled)"打开应用解锁后查看"else dates.evaluate(e.dateInput()).label).setContentIntent(open).setAutoCancel(true).setOnlyAlertOnce(true).setVisibility(NotificationCompat.VISIBILITY_SECRET).build();manager.notify(t[7]as String,1,notification);sql.execSQL("UPDATE delivery_log SET state='posted',last_error_code=NULL WHERE $where",key)}catch(_:Exception){sql.execSQL("UPDATE delivery_log SET state='failed',last_error_code='NOTIFICATION_POST_FAILED',next_attempt_at=? WHERE $where",arrayOf(now+60000,*key))}}
  sql.execSQL("DELETE FROM delivery_log WHERE fire_at<? AND state IN ('posted','skipped')",arrayOf(now-30L*86400000))
  var retry=false;sql.query("SELECT 1 FROM delivery_log WHERE state IN ('pending','posting','failed') LIMIT 1").use{retry=it.moveToFirst()};if(retry)WorkManager.getInstance(context).enqueueUniqueWork("datebook-delivery-retry",ExistingWorkPolicy.KEEP,OneTimeWorkRequestBuilder<MaintenanceWorker>().setInitialDelay(1,TimeUnit.MINUTES).build())
 }
 suspend fun refreshWidgets(){DateBookWidget().updateAll(context)}
 fun calendarAdd(event:Event):Intent {val p=dates.evaluate(event.dateInput());val occurrence=p.occurrence?:throw AppException("DATE_EXHAUSTED");val start=occurrence.instant?:occurrence.date.atStartOfDay(ZoneId.of("UTC")).toInstant();val end=if(event.date.allDay)start.plusSeconds(86400)else start.plusSeconds(3600);return Intent(Intent.ACTION_INSERT).setData(CalendarContract.Events.CONTENT_URI).putExtra(CalendarContract.Events.TITLE,event.title).putExtra(CalendarContract.Events.DESCRIPTION,event.greeting).putExtra(CalendarContract.EXTRA_EVENT_BEGIN_TIME,start.toEpochMilli()).putExtra(CalendarContract.EXTRA_EVENT_END_TIME,end.toEpochMilli()).putExtra(CalendarContract.Events.ALL_DAY,event.date.allDay)}
 suspend fun calendarImport(from:LocalDate,to:LocalDate):List<Event> = withContext(Dispatchers.IO){demand(ContextCompat.checkSelfPermission(context,Manifest.permission.READ_CALENDAR)==PackageManager.PERMISSION_GRANTED,"CALENDAR_PERMISSION_REQUIRED");demand(to>=from&&to.toEpochDay()-from.toEpochDay()<=366,"CALENDAR_WINDOW_INVALID");val b=store.state.value.books.first{it.builtinKey=="uncategorized"};val uri=CalendarContract.Instances.CONTENT_URI.buildUpon().also{ContentUris.appendId(it,from.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli());ContentUris.appendId(it,to.plusDays(1).atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli())}.build();val out=mutableListOf<Event>();context.contentResolver.query(uri,arrayOf(CalendarContract.Instances.TITLE,CalendarContract.Instances.BEGIN,CalendarContract.Instances.ALL_DAY,CalendarContract.Instances.DESCRIPTION,CalendarContract.Instances.EVENT_TIMEZONE),null,null,CalendarContract.Instances.BEGIN+" ASC")?.use{c->while(c.moveToNext()){demand(out.size<2000,"IMPORT_LIMIT_EXCEEDED");val all=c.getInt(2)!=0;val zone=if(all)ZoneId.of("UTC")else runCatching{ZoneId.of(c.getString(4))}.getOrDefault(ZoneId.systemDefault());val time=Instant.ofEpochMilli(c.getLong(1)).atZone(zone);out+=Event(bookId=b.id,title=c.getString(0).orEmpty().ifBlank{"日历事件"}.also{demand(graphemeCount(it)<=60&&it.toByteArray().size<=4096,"CALENDAR_TEXT_TOO_LONG","title")},greeting=c.getString(3).orEmpty().also{demand(graphemeCount(it)<=2000&&it.toByteArray().size<=65536,"CALENDAR_TEXT_TOO_LONG","greeting")},date=DateSpec(year=time.year,month=time.monthValue,day=time.dayOfMonth,allDay=all,localTime=if(all)null else time.toLocalTime().withSecond(0).withNano(0).toString(),zoneId=if(all)null else zone.id))}};out}
 suspend fun validateBackupAssets(preview:BackupPreview)=withContext(Dispatchers.IO){
  preview.state.assets.forEach { a ->
   val file=File(preview.assetRoot,a.relativePath);val bounds=BitmapFactory.Options().apply{inJustDecodeBounds=true};BitmapFactory.decodeFile(file.path,bounds)
   demand(bounds.outWidth==a.width&&bounds.outHeight==a.height&&bounds.outMimeType==a.mimeType&&bounds.outWidth.toLong()*bounds.outHeight<=40000000,"ASSET_CORRUPT")
   var sample=1;while(max(bounds.outWidth,bounds.outHeight)/sample>2560)sample*=2
   val bitmap=BitmapFactory.decodeFile(file.path,BitmapFactory.Options().apply{inSampleSize=sample})?:throw AppException("ASSET_CORRUPT");bitmap.recycle()
  }
 }
 suspend fun stagePhoto(uri:Uri):Asset=withContext(Dispatchers.IO){
  val temporary=File.createTempFile("photo-",".tmp",context.cacheDir);val encoded=File.createTempFile("photo-",".jpg",context.cacheDir)
  try{
   context.contentResolver.openInputStream(uri)?.use{i->temporary.outputStream().use{o->val b=ByteArray(65536);var total=0L;while(true){val n=i.read(b);if(n<0)break;total+=n;demand(total<=25L*1024*1024,"PHOTO_TOO_LARGE");o.write(b,0,n)}}}?:throw AppException("PHOTO_UNREADABLE")
   val bounds=BitmapFactory.Options().apply{inJustDecodeBounds=true};BitmapFactory.decodeFile(temporary.path,bounds)
   demand(bounds.outWidth>0&&bounds.outHeight>0&&bounds.outWidth.toLong()*bounds.outHeight<=40000000,"PHOTO_DIMENSIONS_INVALID")
   var sample=1;while(max(bounds.outWidth,bounds.outHeight)/sample>2560)sample*=2
   val raw=BitmapFactory.decodeFile(temporary.path,BitmapFactory.Options().apply{inSampleSize=sample})?:throw AppException("PHOTO_DECODE_FAILED")
   val orientation=runCatching{android.media.ExifInterface(temporary.path).getAttributeInt(android.media.ExifInterface.TAG_ORIENTATION,1)}.getOrDefault(1)
   val matrix=Matrix().apply{when(orientation){2->setScale(-1f,1f);3->setRotate(180f);4->{setRotate(180f);postScale(-1f,1f)};5->{setRotate(90f);postScale(-1f,1f)};6->setRotate(90f);7->{setRotate(270f);postScale(-1f,1f)};8->setRotate(270f)}}
   val bitmap=try{if(orientation in 2..8)Bitmap.createBitmap(raw,0,0,raw.width,raw.height,matrix,true)else raw}catch(e:Exception){raw.recycle();throw AppException("PHOTO_DECODE_FAILED")}
   if(bitmap!==raw)raw.recycle()
   try{encoded.outputStream().use{demand(bitmap.compress(Bitmap.CompressFormat.JPEG,90,it),"PHOTO_ENCODE_FAILED")};store.addAsset(encoded,"image/jpeg",bitmap.width,bitmap.height)}finally{bitmap.recycle()}
  }finally{temporary.delete();encoded.delete()}
 }
 suspend fun renderCard(event:Event,includeGreeting:Boolean,ratio:String):List<File> = withContext(Dispatchers.IO){
  val width=1080;val base=when(ratio){"1:1"->1080;"9:16"->1920;else->1440};val pad=80;val textWidth=width-pad*2
  val snapshot=store.leaseSnapshot()
  try{
   val current=snapshot.state.events.firstOrNull{it.id==event.id}?:throw AppException("EVENT_NOT_FOUND")
   demand(current.version==event.version,"PREVIEW_STALE")
   val a=event.appearance
   var photo:Bitmap?=null
   try{
    a.assetId?.let{id->val asset=snapshot.state.assets.firstOrNull{it.id==id}?:throw AppException("ASSET_MISSING");val options=BitmapFactory.Options().apply{inJustDecodeBounds=true};val file=File(snapshot.root,asset.relativePath);BitmapFactory.decodeFile(file.path,options);demand(options.outWidth>0&&options.outHeight>0&&options.outWidth.toLong()*options.outHeight<=40000000,"ASSET_CORRUPT");var sample=1;while(max(options.outWidth,options.outHeight)/sample>2560)sample*=2;photo=BitmapFactory.decodeFile(file.path,BitmapFactory.Options().apply{inSampleSize=sample})?:throw AppException("ASSET_CORRUPT")}
    val palette=when(a.presetKey){"sunset"->intArrayOf(Color.rgb(154,83,64),Color.rgb(65,34,50));"ocean"->intArrayOf(Color.rgb(43,92,131),Color.rgb(15,39,75));"lavender"->intArrayOf(Color.rgb(108,82,138),Color.rgb(48,32,77));else->intArrayOf(Color.rgb(31,76,57),Color.rgb(15,32,28))}
    val background=if(a.backgroundKind=="solid")a.solidArgb else photo?.getPixel(photo!!.width/2,photo!!.height/2)?:palette[0]
    val luminance=(.2126*Color.red(background)+.7152*Color.green(background)+.0722*Color.blue(background))*(if(photo!=null)1-a.dimAmount else 1.0)
    val foreground=when(a.textColorMode){"dark"->Color.rgb(20,30,25);"light"->Color.WHITE;else->if(luminance>150)Color.rgb(20,30,25)else Color.WHITE}
    fun paint(size:Float)=TextPaint(Paint.ANTI_ALIAS_FLAG).apply{color=foreground;textSize=size;typeface=if(a.fontKey=="serif")Typeface.SERIF else Typeface.DEFAULT}
    fun layout(value:String,size:Float)=StaticLayout.Builder.obtain(value,0,value.length,paint(size),textWidth).setIncludePad(false).setLineSpacing(10f,1f).build()
    val title=layout(event.title,54f);val projection=dates.evaluate(event.dateInput());val count=layout(projection.label,80f);val date=layout(projection.occurrence?.date?.toString().orEmpty(),34f)
    val titleTop=80;val countTop=titleTop+title.height+44;val dateTop=countTop+count.height+20
    val headerBottom=dateTop+date.height+60;val height=max(base,headerBottom+180)
    val greeting=if(includeGreeting)event.greeting else "";val body=layout(greeting,40f);val capacity=height-headerBottom-80
    val segments=mutableListOf<Pair<Int,Int>>()
    if(greeting.isNotBlank()){var line=0;while(line<body.lineCount){val start=line;val top=body.getLineTop(start);while(line<body.lineCount&&body.getLineBottom(line)-top<=capacity)line++;demand(line>start,"CARD_LAYOUT_FAILED");segments+=start to line;demand(segments.size<=100,"CARD_LIMIT_EXCEEDED")}}else segments+=0 to 0
    val shares=File(context.cacheDir,"shares").apply{mkdirs()};val output=mutableListOf<File>()
    try{segments.forEachIndexed{page,segment->val bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888)
     try{val canvas=Canvas(bitmap);val backgroundPaint=Paint(Paint.ANTI_ALIAS_FLAG).apply{shader=LinearGradient(0f,0f,width.toFloat(),height.toFloat(),palette,null,Shader.TileMode.CLAMP)}
      canvas.drawRect(0f,0f,width.toFloat(),height.toFloat(),backgroundPaint);if(a.backgroundKind=="solid")canvas.drawColor(a.solidArgb)
      photo?.let{p->val scale=max(width.toFloat()/p.width,height.toFloat()/p.height);val w=p.width*scale;val h=p.height*scale;val left=(width-w)*a.focusX.toFloat();val top=(height-h)*a.focusY.toFloat();canvas.drawBitmap(p,null,RectF(left,top,left+w,top+h),null);canvas.drawColor(Color.argb((a.dimAmount*255).toInt(),0,0,0))}
      val shift=if(greeting.isBlank())(height-headerBottom)/2 else 0
      fun draw(l:StaticLayout,y:Int){canvas.save();canvas.translate(pad.toFloat(),(y+shift).toFloat());l.draw(canvas);canvas.restore()}
      draw(title,titleTop);draw(count,countTop);draw(date,dateTop)
      if(greeting.isNotBlank()){val top=body.getLineTop(segment.first);val bottom=body.getLineBottom(segment.second-1);canvas.save();canvas.clipRect(pad,headerBottom,width-pad,headerBottom+bottom-top);canvas.translate(pad.toFloat(),(headerBottom-top).toFloat());body.draw(canvas);canvas.restore()}
      if(segments.size>1)canvas.drawText("${page+1} / ${segments.size}",width-140f,height-24f,paint(22f))
      val file=File.createTempFile("card-",".png",shares);file.outputStream().use{demand(bitmap.compress(Bitmap.CompressFormat.PNG,100,it),"CARD_WRITE_FAILED")};output+=file
     }finally{bitmap.recycle()}
    };output}catch(e:Exception){output.forEach{it.delete()};throw e}
   }finally{photo?.recycle()}
  }finally{snapshot.close()}
 }
 fun share(files:List<File>):Intent {demand(files.isNotEmpty(),"SHARE_EMPTY");val shares=File(context.cacheDir,"shares").apply{mkdirs()};val safe=files.map{f->demand(f.isFile,"FILE_NOT_FOUND");if(f.canonicalPath.startsWith(shares.canonicalPath+File.separator))f else File.createTempFile("datebook-",".${f.extension.ifBlank{"bin"}}",shares).also{f.copyTo(it,true)}};val uris=ArrayList(safe.map{FileProvider.getUriForFile(context,"${context.packageName}.files",it)});return Intent(if(files.size==1)Intent.ACTION_SEND else Intent.ACTION_SEND_MULTIPLE).setType(if(files.all{it.extension=="png"})"image/png"else"application/octet-stream").addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION).apply{if(files.size==1)putExtra(Intent.EXTRA_STREAM,uris.first())else putParcelableArrayListExtra(Intent.EXTRA_STREAM,uris);clipData=ClipData.newRawUri("DateBook",uris.first()).also{c->uris.drop(1).forEach{c.addItem(ClipData.Item(it))}}}}
}

class ReminderReceiver:BroadcastReceiver(){override fun onReceive(context:Context,intent:Intent){val result=goAsync();val app=context.applicationContext as DateBookApplication;app.graph.scope.launch(Dispatchers.IO){try{val parts=intent.data?.pathSegments.orEmpty();if(parts.size==2)app.graph.systems.deliver(parts[0],intent.getStringExtra("token").orEmpty())}catch(_:Exception){WorkManager.getInstance(context).enqueueUniqueWork("datebook-receiver-retry",ExistingWorkPolicy.KEEP,OneTimeWorkRequestBuilder<MaintenanceWorker>().build())}finally{result.finish()}}}}
class RebuildReceiver:BroadcastReceiver(){override fun onReceive(context:Context,intent:Intent){WorkManager.getInstance(context).enqueueUniqueWork("datebook-rebuild",ExistingWorkPolicy.REPLACE,OneTimeWorkRequestBuilder<MaintenanceWorker>().build())}}
class MaintenanceWorker(context:Context,params:WorkerParameters):CoroutineWorker(context,params){override suspend fun doWork():Result=try{val g=(applicationContext as DateBookApplication).graph;g.store.awaitReady();g.service.purgeExpired();g.systems.reconcile();g.store.gc();Result.success()}catch(_:Exception){Result.retry()}}
