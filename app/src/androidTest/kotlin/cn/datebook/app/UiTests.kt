package cn.datebook.app

import android.content.Intent
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import cn.datebook.core.*
import kotlinx.coroutines.runBlocking
import org.junit.*
import java.time.LocalDate

/** Authored device tests; run connectedDebugAndroidTest. They are not host tests. */
class UiTests {
 @get:Rule val compose=createEmptyComposeRule()
 private lateinit var graph:AppGraph
 private var activity:ActivityScenario<MainActivity>?=null
 private lateinit var root:Event
 private lateinit var second:Event
 private lateinit var third:Event
 @Before fun seed()=runBlocking {
  val app=InstrumentationRegistry.getInstrumentation().targetContext.applicationContext as DateBookApplication
  graph=app.graph;graph.store.awaitReady();graph.lock.clearForReplacement()
  val old=graph.store.state.value;val state=defaultLibrary();val book=state.books.first().id
  val date=LocalDate.now().plusDays(30);val d=DateSpec(year=date.year,month=date.monthValue,day=date.dayOfMonth)
  root=Event(bookId=book,title="测试根",date=d,greeting="仅属于根的寄语")
  second=Event(bookId=book,parentId=root.id,title="测试二级",date=d,greeting="仅属于二级的寄语")
  third=Event(bookId=book,parentId=second.id,title="测试三级",date=d,greeting="仅属于三级的寄语")
  graph.store.install(state.copy(events=listOf(root,second,third)),old.revision,old.epoch)
 }
 private fun launch(id:String?=null) {
  val context=InstrumentationRegistry.getInstrumentation().targetContext
  activity=ActivityScenario.launch(Intent(context,MainActivity::class.java).apply{id?.let{putExtra("eventId",it)}})
  compose.waitForIdle()
 }
 @After fun close(){activity?.close();graph.lock.clearForReplacement()}
 @Test fun homeListsOnlyOptedInRoot(){launch();compose.onAllNodesWithText("测试根").onFirst().assertExists();compose.onNodeWithText("测试二级").assertDoesNotExist();compose.onNodeWithText("测试三级").assertDoesNotExist()}
 @Test fun rootDetailOnlyShowsItsImmediateChildren(){launch(root.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("测试二级"));compose.onNodeWithText("测试二级").assertExists();compose.onNodeWithText("测试三级").assertDoesNotExist();compose.onNodeWithText("仅属于二级的寄语",useUnmergedTree=true).assertExists()}
 @Test fun secondDetailShowsThirdNotItsDescendants(){launch(second.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("测试三级"));compose.onNodeWithText("测试三级").assertExists();compose.onNodeWithText("仅属于根的寄语").assertDoesNotExist()}
 @Test fun thirdDetailCannotCreateFourth(){launch(third.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("已到第三级，不支持继续新增下级"));compose.onNodeWithText("已到第三级，不支持继续新增下级").assertIsDisplayed();compose.onNodeWithText("添加子事件").assertDoesNotExist()}
 @Test fun greetingIsSingleCurrentEventText(){launch(root.id);compose.onNodeWithTag("detail_list").performScrollToNode(hasText("仅属于根的寄语"));compose.onNodeWithText("仅属于根的寄语").assertExists();compose.onNodeWithText("小纸条").assertDoesNotExist()}
 @Test fun missingDeepLinkDoesNotCreateAnEvent(){launch(newId());compose.onNodeWithText("重要的日子").assertExists();Assert.assertEquals(3,graph.store.state.value.events.size)}
 @Test fun appLockHidesLibraryBeforeUnlock(){graph.lock.setPin("123456".toCharArray());graph.lock.lock();launch(root.id);compose.onNodeWithText("请解锁本机资料库").assertExists();compose.onNodeWithText("测试根").assertDoesNotExist()}
 @Test fun appDeclaresNoInternetOrAccountsPermission(){
  val c=InstrumentationRegistry.getInstrumentation().targetContext
  @Suppress("DEPRECATION") val requested=c.packageManager.getPackageInfo(c.packageName,android.content.pm.PackageManager.GET_PERMISSIONS).requestedPermissions.orEmpty()
  Assert.assertFalse("android.permission.INTERNET" in requested);Assert.assertFalse("android.permission.GET_ACCOUNTS" in requested)
 }
}
