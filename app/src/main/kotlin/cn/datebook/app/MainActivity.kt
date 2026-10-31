package cn.datebook.app

import android.content.Intent
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.fragment.app.FragmentActivity
import cn.datebook.app.ui.AppViewModel
import cn.datebook.app.ui.DateBookRoot
import kotlinx.coroutines.flow.MutableStateFlow

class MainActivity : FragmentActivity() {
 private val model: AppViewModel by viewModels()
 private val requestedEvent=MutableStateFlow<String?>(null)
 override fun onCreate(savedInstanceState:Bundle?) {
  super.onCreate(savedInstanceState)
  window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
  readIntent(intent)
  setContent { DateBookRoot(model,this,requestedEvent) { requestedEvent.value=null } }
 }
 override fun onNewIntent(intent:Intent) { super.onNewIntent(intent); setIntent(intent);readIntent(intent) }
 private fun readIntent(intent:Intent?) {
  val uri=intent?.data
  requestedEvent.value=if(uri?.scheme=="daybook"&&uri.host=="event"&&uri.pathSegments.size==2)uri.pathSegments.joinToString("/")
   else intent?.getStringExtra("eventId")?:intent?.getStringExtra("event_id")?:intent?.getStringExtra("id")
 }
 override fun onStop() { super.onStop(); if(!isChangingConfigurations) (application as DateBookApplication).graph.lock.lock() }
}
