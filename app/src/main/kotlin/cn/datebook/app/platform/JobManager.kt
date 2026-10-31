package cn.datebook.app.platform

import android.util.AtomicFile
import cn.datebook.core.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONObject
import java.io.File
import java.util.concurrent.ConcurrentHashMap

data class JobSnapshot(val id:String,val type:String,val state:String="preparing",val stage:String="准备中",val current:Long?=null,val total:Long?=null,val error:String?=null,val result:String?=null,val createdAt:Long=System.currentTimeMillis())
class JobManager(root:File,private val scope:CoroutineScope) {
 private val directory=File(root,"jobs").apply{mkdirs()}
 private val records=ConcurrentHashMap<String,MutableStateFlow<JobSnapshot>>()
 private val tasks=ConcurrentHashMap<String,Job>()
 init {directory.listFiles()?.filter{it.extension=="json"}?.forEach{f->try{val o=JSONObject(f.readText());val s=JobSnapshot(o.getString("id"),o.getString("type"),o.getString("state"),o.optString("stage",""),error=o.optString("error").takeIf{it.isNotEmpty()},createdAt=o.optLong("createdAt",f.lastModified()));val recovered=if(s.state in setOf("completed","canceled","failed"))s else s.copy(state="failed",stage="任务被进程退出中断，请重新操作",error="JOB_INTERRUPTED");records[s.id]=MutableStateFlow(recovered);save(recovered)}catch(_:Exception){f.delete()}}}
 @Synchronized fun start(type:String,block:suspend JobContext.()->String):String {demand(type.matches(Regex("[a-z_]{1,48}")),"JOB_TYPE_INVALID");val id=newId();val flow=MutableStateFlow(JobSnapshot(id,type));records[id]=flow;save(flow.value);tasks[id]=scope.launch(Dispatchers.IO,start=CoroutineStart.LAZY){try{val result=JobContext(id).block();update(id){it.copy(state="completed",stage="已完成",result=result)}}catch(e:CancellationException){update(id){it.copy(state="canceled",stage="已取消")}}catch(e:Exception){update(id){it.copy(state="failed",stage="操作失败",error=(e as? AppException)?.code?:"JOB_FAILED")}}finally{tasks.remove(id)}};tasks.getValue(id).start();return id}
 fun observe(id:String):StateFlow<JobSnapshot> = records[id]?:throw AppException("JOB_NOT_FOUND")
 fun latest():List<JobSnapshot> = records.values.map{it.value}.sortedByDescending{it.createdAt}.take(100)
 @Synchronized fun cancel(id:String):Boolean {val s=records[id]?.value?:throw AppException("JOB_NOT_FOUND");if(s.state=="committing"||s.state in setOf("completed","failed","canceled"))return false;update(id){it.copy(state="canceled",stage="正在取消")};tasks[id]?.cancel();return true}
 inner class JobContext internal constructor(private val id:String) {
  suspend fun progress(stage:String,current:Long?=null,total:Long?=null){currentCoroutineContext().ensureActive();demand(stage.length<=120,"JOB_STAGE_INVALID");update(id){demand(it.state!="canceled","JOB_CANCELED");it.copy(state=if(it.state=="committing")"committing"else"progress",stage=stage,current=current,total=total)}}
  /** The cancellation/commit decision uses the same monitor. Commit must finish atomically. */
  fun committing(){synchronized(this@JobManager){val s=records.getValue(id).value;demand(s.state!="canceled"&&tasks[id]?.isActive==true,"JOB_CANCELED");update(id){it.copy(state="committing",stage="正在提交，请勿关闭应用")}}}
 }
 @Synchronized private fun update(id:String,f:(JobSnapshot)->JobSnapshot){val flow=records.getValue(id);val next=f(flow.value);try{save(next)}catch(e:Exception){if(next.state !in setOf("completed","failed","canceled"))throw AppException("JOB_JOURNAL_FAILED");flow.value=next.copy(error=next.error?:"JOB_JOURNAL_FAILED",stage=if(next.state=="completed")"操作已完成，但任务记录写入失败"else next.stage);return};flow.value=next}
 private fun save(s:JobSnapshot){val f=AtomicFile(File(directory,"${s.id}.json"));val out=f.startWrite();try{val o=JSONObject().put("id",s.id).put("type",s.type).put("state",s.state).put("stage",s.stage).put("current",s.current).put("total",s.total).put("error",s.error).put("createdAt",s.createdAt);out.write(o.toString().toByteArray());f.finishWrite(out)}catch(e:Exception){f.failWrite(out);throw e}}
}
