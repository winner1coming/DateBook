package cn.datebook.app.platform

import android.content.Context
import android.os.SystemClock
import android.util.AtomicFile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONObject
import java.io.File
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec
import cn.datebook.core.AppException
import cn.datebook.core.demand

/** A UI access lock, not database encryption. The verifier stays in noBackup storage. */
class LockManager(context:Context) {
 private val file=AtomicFile(File(context.noBackupFilesDir,"lock.json"))
 var error:AppException?=null
  private set
 private var config=read()
 private val mutableLocked=MutableStateFlow(config!=null)
 val locked:StateFlow<Boolean> = mutableLocked
 val enabled:Boolean get()=synchronized(this){config!=null}
 private var failures=0
 private var deadline=0L
 init { config?.let { failures=it.optInt("failures",0); val persisted=it.optLong("retryAt",0);deadline=SystemClock.elapsedRealtime()+(persisted-System.currentTimeMillis()).coerceIn(0,300000) } }
 @Synchronized fun setPin(pin:CharArray){demand(!enabled||!mutableLocked.value,"LOCK_REQUIRED");replacePinAfterLibraryReplacement(pin)}
 /** Coordinator-only: require its durable, validated replacement-epoch gate first. No delete gap. */
 @Synchronized fun replacePinAfterLibraryReplacement(pin:CharArray){validate(pin);val salt=ByteArray(16).also{SecureRandom().nextBytes(it)};val hash=hash(pin,salt);try{val next=JSONObject().put("salt",android.util.Base64.encodeToString(salt,2)).put("hash",android.util.Base64.encodeToString(hash,2)).put("failures",0).put("retryAt",0);persist(next);config=next;error=null;failures=0;deadline=0;mutableLocked.value=false}finally{hash.fill(0)}}
 @Synchronized fun unlock(pin:CharArray):Boolean {
  error?.let{throw it}
  if(!enabled){mutableLocked.value=false;return true};if(remainingLockMillis()>0)return false
  val c=config!!;val salt=android.util.Base64.decode(c.getString("salt"),2);val actual=hash(pin,salt);val expected=android.util.Base64.decode(c.getString("hash"),2);val good=MessageDigest.isEqual(actual,expected);actual.fill(0);expected.fill(0)
  if(good){failures=0;deadline=0;mutableLocked.value=false}else{failures++;val wait=if(failures<5)0L else (30000L shl (failures-5).coerceAtMost(3)).coerceAtMost(300000);deadline=SystemClock.elapsedRealtime()+wait};c.put("failures",failures).put("retryAt",System.currentTimeMillis()+remainingLockMillis());persist();return good
 }
 @Synchronized fun biometricUnlock(){error?.let{throw it};if(enabled){mutableLocked.value=false;failures=0;deadline=0;config!!.put("failures",0).put("retryAt",0);persist()}}
 @Synchronized fun lock(){if(enabled)mutableLocked.value=true}
 @Synchronized fun disable(pin:CharArray){demand(unlock(pin),"PIN_INCORRECT");file.delete();config=null;mutableLocked.value=false}
 /** Only after an authenticated replacement has committed, never before backup validation. */
 @Synchronized fun clearForReplacement(){file.delete();config=null;error=null;failures=0;deadline=0;mutableLocked.value=false}
 fun remainingLockMillis()=(deadline-SystemClock.elapsedRealtime()).coerceAtLeast(0)
 private fun validate(pin:CharArray){demand(pin.size in 6..12&&pin.all{it in '0'..'9'},"PIN_INVALID")}
 private fun hash(pin:CharArray,salt:ByteArray):ByteArray{validate(pin);val spec=PBEKeySpec(pin,salt,210000,256);return try{SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).encoded}finally{spec.clearPassword()}}
 private fun read():JSONObject?=try{if(file.baseFile.exists()||File(file.baseFile.path+".bak").exists()||File(file.baseFile.path+".new").exists())JSONObject(file.openRead().bufferedReader().use{it.readText()}).also{demand(android.util.Base64.decode(it.getString("salt"),2).size==16&&android.util.Base64.decode(it.getString("hash"),2).size==32,"LOCK_STATE_CORRUPT")}else null}catch(e:Exception){error=AppException("LOCK_STATE_CORRUPT");JSONObject().put("corrupt",true)}
 private fun persist(value:JSONObject=config!!){val stream=file.startWrite();try{stream.write(value.toString().toByteArray());file.finishWrite(stream)}catch(e:Exception){file.failWrite(stream);throw AppException("FILE_IO_FAILED")}}
}
