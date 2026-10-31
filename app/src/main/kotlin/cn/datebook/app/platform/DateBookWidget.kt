package cn.datebook.app.platform

import android.app.Activity
import android.appwidget.AppWidgetManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.AtomicFile
import android.widget.*
import androidx.glance.*
import androidx.glance.appwidget.action.actionStartActivity
import androidx.glance.action.clickable
import androidx.glance.appwidget.*
import androidx.glance.layout.*
import androidx.glance.text.Text
import androidx.glance.text.TextStyle
import androidx.glance.unit.ColorProvider
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import cn.datebook.app.DateBookApplication
import cn.datebook.app.MainActivity
import cn.datebook.core.*
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.File

data class WidgetConfig(val mode:String="recent",val eventId:String?=null,val showGreeting:Boolean=false,val showPhoto:Boolean=false)
object WidgetPreferences {
 private fun file(context:Context,id:Int)=AtomicFile(File(context.noBackupFilesDir,"widgets/$id.json").also{it.parentFile!!.mkdirs()})
 fun read(context:Context,id:Int):WidgetConfig=try{val o=JSONObject(file(context,id).openRead().bufferedReader().use{it.readText()});WidgetConfig(o.optString("mode","recent"),o.optString("eventId").takeIf{it.isNotBlank()},o.optBoolean("showGreeting",false),o.optBoolean("showPhoto",false))}catch(_:Exception){WidgetConfig()}
 fun write(context:Context,id:Int,value:WidgetConfig){val f=file(context,id);val out=f.startWrite();try{out.write(JSONObject().put("mode",value.mode).put("eventId",value.eventId).put("showGreeting",value.showGreeting).put("showPhoto",value.showPhoto).toString().toByteArray());f.finishWrite(out)}catch(e:Exception){f.failWrite(out);throw e}}
 fun delete(context:Context,id:Int)=file(context,id).delete()
}
class DateBookWidget:GlanceAppWidget(){
 override suspend fun provideGlance(context:Context,id:GlanceId){
  val g=(context.applicationContext as DateBookApplication).graph;g.store.awaitReady();val widgetId=GlanceAppWidgetManager(context).getAppWidgetId(id);val config=WidgetPreferences.read(context,widgetId)
  // Snapshot assets are leased through rendering; no generation file is held across library installs.
  val snapshot=g.store.leaseSnapshot();try{val state=snapshot.state;val locked=g.lock.enabled
   val active=state.events.filter{state.lifecycle(it.id)=="active"&&it.goal?.state !in setOf("completed","canceled")};val selected=if(config.mode=="single")active.filter{it.id==config.eventId}.take(1)else active.filter{it.homeVisible}.sortedWith(compareBy<Event>{!it.pinned}.thenBy{g.dates.evaluate(it.dateInput()).occurrence?.date}).take(3)
   val photo=if(!locked&&config.showPhoto&&selected.size==1)selected.first().appearance.assetId?.let{key->state.assets.firstOrNull{it.id==key}}?.let{File(snapshot.root,it.relativePath).takeIf(File::isFile)?.let{f->android.graphics.BitmapFactory.decodeFile(f.path)}}else null
   provideContent {GlanceTheme{Box(modifier=GlanceModifier.fillMaxSize().background(ColorProvider(Color(0xFF173D30))).padding(16.dp).clickable(actionStartActivity(Intent(context,MainActivity::class.java)))){if(photo!=null)Image(provider=ImageProvider(photo),contentDescription=null,modifier=GlanceModifier.fillMaxSize(),contentScale=ContentScale.Crop);Column{Text("DateBook",style=TextStyle(color=ColorProvider(Color.White),fontSize=15.sp));Spacer(GlanceModifier.height(8.dp));when{locked->Text("应用锁已开启，请打开应用查看",style=TextStyle(color=ColorProvider(Color.White)));selected.isEmpty()->Text("暂无可显示的日子，请重新配置",style=TextStyle(color=ColorProvider(Color.White)));else->selected.forEach{e->Column(modifier=GlanceModifier.padding(bottom=8.dp).clickable(actionStartActivity(Intent(context,MainActivity::class.java).setData(android.net.Uri.parse("daybook://event/${state.epoch}/${e.id}"))))){Text(e.title,style=TextStyle(color=ColorProvider(Color.White),fontSize=17.sp),maxLines=2);Text(g.dates.evaluate(e.dateInput()).label,style=TextStyle(color=ColorProvider(Color.White),fontSize=22.sp));if(config.showGreeting&&e.greeting.isNotBlank())Text(e.greeting,style=TextStyle(color=ColorProvider(Color.White),fontSize=12.sp),maxLines=2)}}}}}}}
  }finally{snapshot.close()}
 }
}
class DateBookWidgetReceiver:GlanceAppWidgetReceiver(){override val glanceAppWidget:GlanceAppWidget=DateBookWidget();override fun onDeleted(context:Context,appWidgetIds:IntArray){appWidgetIds.forEach{WidgetPreferences.delete(context,it)};super.onDeleted(context,appWidgetIds)}}
class WidgetConfigureActivity:Activity(){
 private var id=AppWidgetManager.INVALID_APPWIDGET_ID
 override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);setResult(RESULT_CANCELED);id=intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,AppWidgetManager.INVALID_APPWIDGET_ID);if(id==AppWidgetManager.INVALID_APPWIDGET_ID){finish();return};val g=(application as DateBookApplication).graph
  val layout=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(32,32,32,32)};layout.addView(TextView(this).apply{text="选择桌面组件内容";textSize=22f});setContentView(layout)
  if(g.lock.enabled){layout.addView(TextView(this).apply{text="应用锁已开启。桌面仅显示安全入口；在应用关闭锁后可重新配置。"});layout.addView(Button(this).apply{text="添加安全入口";setOnClickListener{finishConfig(WidgetConfig())}});return}
  val loading=TextView(this).apply{text="正在加载本机事件…"};layout.addView(loading)
  g.scope.launch(Dispatchers.Main){try{g.store.awaitReady();layout.removeView(loading);val rows=g.store.state.value.events.filter{g.store.state.value.lifecycle(it.id)=="active"};val mode=Spinner(this@WidgetConfigureActivity);mode.adapter=ArrayAdapter(this@WidgetConfigureActivity,android.R.layout.simple_spinner_dropdown_item,listOf("最近三个日子","指定一个日子"));layout.addView(mode);val selection=Spinner(this@WidgetConfigureActivity);selection.adapter=ArrayAdapter(this@WidgetConfigureActivity,android.R.layout.simple_spinner_dropdown_item,rows.map{it.title}.ifEmpty{listOf("暂无事件")});layout.addView(selection);val greeting=CheckBox(this@WidgetConfigureActivity).apply{text="在桌面公开寄语（默认关闭）"};val photo=CheckBox(this@WidgetConfigureActivity).apply{text="在桌面公开背景照片（默认关闭）"};layout.addView(greeting);layout.addView(photo);layout.addView(Button(this@WidgetConfigureActivity).apply{text="保存并添加";setOnClickListener{if(mode.selectedItemPosition==1&&rows.isEmpty())return@setOnClickListener;finishConfig(WidgetConfig(if(mode.selectedItemPosition==1)"single"else"recent",rows.getOrNull(selection.selectedItemPosition)?.id,greeting.isChecked,photo.isChecked))}})}catch(_:Exception){loading.text="数据加载失败，请返回应用检查"}}
 }
 private fun finishConfig(config:WidgetConfig){WidgetPreferences.write(this,id,config);val g=(application as DateBookApplication).graph;g.scope.launch{DateBookWidget().updateAll(this@WidgetConfigureActivity)};setResult(RESULT_OK,Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,id));finish()}
}
