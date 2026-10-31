package cn.datebook.app

import android.app.Application
import android.content.Context
import androidx.work.*
import cn.datebook.app.data.RoomStore
import cn.datebook.app.platform.*
import cn.datebook.core.*
import kotlinx.coroutines.*
import java.time.Clock
import java.util.concurrent.TimeUnit

class DateBookApplication : Application() {
 lateinit var graph: AppGraph; private set
 override fun onCreate() {
  super.onCreate()
  graph = AppGraph(this)
  // Previews are process-local. Snapshot only pre-existing private staging paths;
  // never sweep a newly-created current-process restore or a user-picked backup.
  val orphanStaging=cacheDir.listFiles().orEmpty().filter{it.name.matches(Regex("(?:restore|merge)-[0-9a-f-]{36}"))}
  val orphanFiles=cacheDir.listFiles().orEmpty().filter{it.name.matches(Regex("export-[0-9a-f-]{36}\\.tmp|photo-[0-9-]+\\.(?:tmp|jpg)"))}+
   graph.store.root.listFiles().orEmpty().filter{it.name.matches(Regex("datebook-payload-[0-9-]+\\.zip"))}
  graph.scope.launch {
   orphanFiles.forEach { file -> runCatching {
    if(file.parentFile?.canonicalFile in setOf(cacheDir.canonicalFile,graph.store.root.canonicalFile))java.nio.file.Files.deleteIfExists(file.toPath())
   } }
   orphanStaging.forEach { directory -> runCatching {
    if(directory.parentFile?.canonicalFile==cacheDir.canonicalFile)java.nio.file.Files.walkFileTree(directory.toPath(),object:java.nio.file.SimpleFileVisitor<java.nio.file.Path>() {
     override fun visitFile(file:java.nio.file.Path,attrs:java.nio.file.attribute.BasicFileAttributes):java.nio.file.FileVisitResult {java.nio.file.Files.deleteIfExists(file);return java.nio.file.FileVisitResult.CONTINUE}
     override fun postVisitDirectory(dir:java.nio.file.Path,error:java.io.IOException?):java.nio.file.FileVisitResult {if(error!=null)throw error;java.nio.file.Files.deleteIfExists(dir);return java.nio.file.FileVisitResult.CONTINUE}
    })
   } }
  }
  graph.scope.launch {
   try {
    graph.store.awaitReady()
    graph.service.purgeExpired()
    graph.systems.reconcile()
    graph.systems.refreshWidgets()
    graph.store.gc()
   } catch (_: Exception) { /* Startup error is exposed by RoomStore, never replace data. */ }
  }
  WorkManager.getInstance(this).enqueueUniquePeriodicWork("datebook-maintenance", ExistingPeriodicWorkPolicy.KEEP,
   PeriodicWorkRequestBuilder<MaintenanceWorker>(12, TimeUnit.HOURS).build())
 }
}

class AppGraph(context: Context) {
 val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
 val store = RoomStore(context)
 val dates = DateEngine(Clock.systemDefaultZone(), LunarAdapter())
 val service = DateBookService(store, dates, Clock.systemDefaultZone())
 val codec = FileCodec(dates)
 val lock = LockManager(context)
 val jobs = JobManager(store.root, scope)
 val systems = SystemServices(context, store, dates)
}
