@file:OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class, androidx.compose.foundation.layout.ExperimentalLayoutApi::class, androidx.compose.foundation.ExperimentalFoundationApi::class, androidx.compose.ui.ExperimentalComposeUiApi::class)
package cn.datebook.app.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.BitmapFactory
import android.os.Build
import android.view.WindowManager
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.AlertDialog as MaterialAlertDialog
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.*
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.focus.focusProperties
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.LocalTextToolbar
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.*
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.compose.*
import cn.datebook.app.platform.JobSnapshot
import cn.datebook.core.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import java.time.*
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@Serializable data object HomeRoute
@Serializable data object BooksRoute
@Serializable data object GoalsRoute
@Serializable data object SettingsRoute
@Serializable data object SearchRoute
@Serializable data object CalendarRoute
@Serializable data object ToolsRoute
@Serializable data class DetailRoute(val id:String)
@Serializable data class EditRoute(val id:String="",val parentId:String="",val bookId:String="",val goal:Boolean=false)
@Serializable data class BookRoute(val id:String)
@Serializable data class LifecycleRoute(val kind:String)
@Serializable data class ShareRoute(val id:String)

private val forest=Color(0xFF214F43)
private val cream=Color(0xFFF7F6F0)
private val lightScheme=lightColorScheme(primary=forest,secondary=Color(0xFFA26B3F),background=cream,surface=cream,surfaceVariant=Color(0xFFE6EBE5))
private val darkScheme=darkColorScheme(primary=Color(0xFF91C7B2),secondary=Color(0xFFE9BA8B),background=Color(0xFF131C18),surface=Color(0xFF131C18))
private val LocalClockTick=compositionLocalOf { 0L }
private val LocalLibraryLocked=compositionLocalOf { false }

/** Dialogs are separate windows: alpha on the underlying screen cannot hide them. */
@Composable private fun AlertDialog(onDismissRequest:()->Unit,confirmButton:@Composable ()->Unit,
 dismissButton:(@Composable ()->Unit)?=null,title:(@Composable ()->Unit)?=null,text:(@Composable ()->Unit)?=null) {
 if(!LocalLibraryLocked.current)MaterialAlertDialog(onDismissRequest=onDismissRequest,confirmButton=confirmButton,dismissButton=dismissButton,title=title,text=text)
}

@Composable fun DateBookRoot(vm:AppViewModel,activity:FragmentActivity,requested:StateFlow<String?>,consume:()->Unit) {
 val theme by vm.prefs.theme.collectAsStateWithLifecycle("system")
 val dark=theme=="dark" || theme=="system"&&isSystemInDarkTheme()
 MaterialTheme(colorScheme=if(dark)darkScheme else lightScheme, typography=Typography()) {
  val ready by vm.ready.collectAsStateWithLifecycle()
  val error by vm.startupError.collectAsStateWithLifecycle()
  val locked by vm.graph.lock.locked.collectAsStateWithLifecycle()
  val busy by vm.busy.collectAsStateWithLifecycle()
  val message by vm.message.collectAsStateWithLifecycle()
  val outgoing by vm.outgoing.collectAsStateWithLifecycle()
  val replacementPinEpoch by vm.prefs.replacementPinEpoch.collectAsStateWithLifecycle(null)
  val library by vm.library.collectAsStateWithLifecycle()
  var recovery by rememberSaveable { mutableStateOf(false) }
  val focus=LocalFocusManager.current;val keyboard=LocalSoftwareKeyboardController.current;val toolbar=LocalTextToolbar.current
  val snack=remember { SnackbarHostState() }
  SideEffect {
   if(vm.graph.lock.enabled) activity.window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
   else activity.window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
  }
  LaunchedEffect(message) { message?.let { snack.showSnackbar(it);vm.message.value=null } }
  LaunchedEffect(outgoing,locked) { if(!locked)outgoing?.let { try { activity.startActivity(it) } catch(e:Exception){vm.error(e)};vm.outgoing.value=null } }
  LaunchedEffect(locked,ready,replacementPinEpoch){if(ready&&!locked&&replacementPinEpoch==null)vm.resumePending()}
  LaunchedEffect(locked){if(locked){focus.clearFocus(true);keyboard?.hide();toolbar.hide()}}
  val tick by produceState(System.currentTimeMillis()) { while(true){delay(30000);value=System.currentTimeMillis()} }
  CompositionLocalProvider(LocalClockTick provides tick) { Surface(Modifier.fillMaxSize()) {
   when {
    error!=null -> Column(Modifier.padding(24.dp).fillMaxSize(),verticalArrangement=Arrangement.Center) { Text("无法安全打开资料库",style=MaterialTheme.typography.headlineSmall);Text("${error!!.code}\n资料未被清空。请保留应用数据并寻求修复；不要卸载应用。可重新启动后重试。");Button(onClick={activity.recreate()}){Text("重试打开")} }
    !ready -> Box(Modifier.fillMaxSize(),contentAlignment=Alignment.Center){CircularProgressIndicator()}
    replacementPinEpoch==library.epoch -> ReplacementPinScreen(vm)
    else -> {
     LaunchedEffect(locked) { if(!locked)recovery=false }
     val state by vm.library.collectAsStateWithLifecycle()
     val nav=rememberNavController()
     val request by requested.collectAsStateWithLifecycle()
     LaunchedEffect(request,state.epoch,locked) { if(!locked)request?.let { ref->val id=ref.substringAfter('/');val epoch=ref.substringBefore('/',"");if((epoch.isBlank()||epoch==state.epoch)&&state.events.any{it.id==id})nav.navigate(DetailRoute(id))else vm.message.value="此事件不存在或链接属于旧资料库";consume() } }
     Box(Modifier.fillMaxSize()) {
     Box(Modifier.fillMaxSize().focusProperties { enter={if(locked)FocusRequester.Cancel else FocusRequester.Default} }.focusGroup().then(if(locked)Modifier.alpha(0f).clearAndSetSemantics{}else Modifier)) {
     CompositionLocalProvider(LocalLibraryLocked provides locked) {
     Scaffold(snackbarHost={SnackbarHost(snack)},bottomBar={ NavigationBar {
      val entry by nav.currentBackStackEntryAsState()
      val tabs=listOf(Triple("日子",Icons.Default.Home,HomeRoute),Triple("日子本",Icons.Default.MenuBook,BooksRoute),Triple("目标",Icons.Default.Flag,GoalsRoute),Triple("设置",Icons.Default.Settings,SettingsRoute))
      tabs.forEachIndexed { i,t->
       val selected=when(i){0->entry?.destination?.hasRoute<HomeRoute>();1->entry?.destination?.hasRoute<BooksRoute>();2->entry?.destination?.hasRoute<GoalsRoute>();else->entry?.destination?.hasRoute<SettingsRoute>()}==true
       NavigationBarItem(selected,onClick={when(i){0->nav.navigate(HomeRoute){popUpTo<HomeRoute>{saveState=true};launchSingleTop=true;restoreState=true};1->nav.navigate(BooksRoute){launchSingleTop=true};2->nav.navigate(GoalsRoute){launchSingleTop=true};else->nav.navigate(SettingsRoute){launchSingleTop=true}}},icon={Icon(t.second,t.first)},label={Text(t.first)})
      }
     } }) { padding ->
      Box(Modifier.padding(padding)) {
       NavHost(nav,HomeRoute) {
        composable<HomeRoute>{HomeScreen(vm,state,nav)}
        composable<BooksRoute>{BooksScreen(vm,state,nav)}
        composable<GoalsRoute>{GoalsScreen(vm,state,nav)}
        composable<SettingsRoute>{SettingsScreen(vm,activity,nav)}
        composable<SearchRoute>{SearchScreen(vm,state,nav)}
        composable<CalendarRoute>{CalendarScreen(vm,state,nav)}
        composable<ToolsRoute>{ToolsScreen(vm,onBack={nav.popBackStack()})}
        composable<DetailRoute>{DetailScreen(vm,state,it.toRoute<DetailRoute>().id,nav)}
        composable<EditRoute>{EditorScreen(vm,state,it.toRoute<EditRoute>(),nav)}
        composable<BookRoute>{BookScreen(vm,state,it.toRoute<BookRoute>().id,nav)}
        composable<LifecycleRoute>{LifecycleScreen(vm,state,it.toRoute<LifecycleRoute>().kind,nav)}
        composable<ShareRoute>{ShareScreen(vm,state,it.toRoute<ShareRoute>().id,nav)}
       }
       if(busy) LinearProgressIndicator(Modifier.fillMaxWidth().align(Alignment.TopCenter))
      }
     }
     }
     }
     if(locked)Surface(onClick={},modifier=Modifier.fillMaxSize()) {
      if(recovery)Scaffold(snackbarHost={SnackbarHost(snack)}) { p->ToolsScreen(vm,Modifier.padding(p),recovery=true,onBack={recovery=false}) }
      else Scaffold(snackbarHost={SnackbarHost(snack)}){p->Box(Modifier.padding(p)){LockScreen(vm,activity){recovery=true}}}
     }
     }
    }
   }
  } }
  BackHandler(locked){if(recovery)recovery=false else activity.moveTaskToBack(true)}
 }
}

@Composable private fun Header(title:String,subtitle:String?=null,back:(()->Unit)?=null,actions:@Composable RowScope.()->Unit={}) {
 Row(Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=14.dp),verticalAlignment=Alignment.CenterVertically) {
  if(back!=null) IconButton(back){Icon(Icons.AutoMirrored.Filled.ArrowBack,"返回")}
  Column(Modifier.weight(1f)){Text(title,fontSize=25.sp,fontWeight=FontWeight.Bold);if(subtitle!=null)Text(subtitle,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)}
  actions()
 }
}
@Composable private fun Section(title:String,content:@Composable ColumnScope.()->Unit) {
 ElevatedCard(Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=7.dp),shape=RoundedCornerShape(20.dp)) {
  Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(10.dp)){Text(title,fontWeight=FontWeight.SemiBold);content()}
 }
}
@Composable private fun Empty(text:String="还没有记录，留一个位置给重要的日子。") { Text(text,Modifier.padding(24.dp),color=MaterialTheme.colorScheme.onSurfaceVariant) }
@Composable private fun Options(label:String,value:String,options:List<Pair<String,String>>,change:(String)->Unit) {
 Column {Text(label,style=MaterialTheme.typography.labelLarge);Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)){options.forEach{(v,t)->FilterChip(value==v,{change(v)},label={Text(t)})}} }
}
@Composable private fun Field(label:String,value:String,change:(String)->Unit,lines:Int=1,modifier:Modifier=Modifier) {
 OutlinedTextField(value,change,label={Text(label)},modifier=modifier.fillMaxWidth(),singleLine=lines==1,minLines=lines)
}
@Composable private fun Toggle(label:String,value:Boolean,change:(Boolean)->Unit,detail:String?=null) {
 Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically) {Column(Modifier.weight(1f)){Text(label);if(detail!=null)Text(detail,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)};Switch(value,change)}
}
@Composable private fun Confirm(title:String,text:String,onDismiss:()->Unit,onConfirm:()->Unit) {
 AlertDialog(onDismissRequest=onDismiss,title={Text(title)},text={Text(text)},confirmButton={TextButton(onConfirm){Text("确认")}},dismissButton={TextButton(onDismiss){Text("取消")}})
}
@Composable private fun EventRow(vm:AppViewModel,s:LibraryState,e:Event,click:()->Unit,selected:Boolean?=null,select:(()->Unit)?=null,extra:@Composable RowScope.()->Unit={}) {
 val tick=LocalClockTick.current
 val p=runCatching{vm.graph.dates.evaluate(e.dateInput())}.getOrNull()
 Card(Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=5.dp).combinedClickable(onClick=click,onLongClick=select?:click),shape=RoundedCornerShape(17.dp),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surfaceContainerLow)) {
  Row(Modifier.padding(15.dp),verticalAlignment=Alignment.CenterVertically) {
   if(selected!=null) Checkbox(selected,{select?.invoke()})
   Column(Modifier.weight(1f)){Text(e.title,fontWeight=FontWeight.SemiBold);Text((s.books.find{it.id==e.bookId}?.name?:"")+if(e.parentId!=null)" · 第 ${depth(s,e.id)} 级"else"",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant);if(e.greeting.isNotBlank())Text(e.greeting,maxLines=1,style=MaterialTheme.typography.bodySmall)}
   Column(horizontalAlignment=Alignment.End){Text(p?.days?.toString()?:"—",fontSize=25.sp,fontWeight=FontWeight.Light,color=MaterialTheme.colorScheme.primary);Text(p?.label?:"日期待检查",style=MaterialTheme.typography.labelSmall)}
   extra()
  }
 }
}
@Composable private fun Hero(vm:AppViewModel,e:Event,onClick:()->Unit) {
 val tick=LocalClockTick.current
 val context=LocalContext.current
 var bitmap by remember(e.appearance.assetId) { mutableStateOf<ImageBitmap?>(null) }
 LaunchedEffect(e.appearance.assetId) { bitmap=withContext(Dispatchers.IO) { runCatching { e.appearance.assetId?.let{id->vm.library.value.assets.find{it.id==id}}?.let{a->
  val opts=BitmapFactory.Options().apply{inJustDecodeBounds=true};val file=vm.graph.store.assetFile(a.relativePath);BitmapFactory.decodeFile(file.path,opts);opts.inSampleSize=maxOf(1,maxOf(opts.outWidth,opts.outHeight)/1600);opts.inJustDecodeBounds=false;BitmapFactory.decodeFile(file.path,opts)?.asImageBitmap() }
 }.getOrNull() } }
 val p=runCatching{vm.graph.dates.evaluate(e.dateInput())}.getOrDefault(DateProjection(null,"日期待填写",null))
 val color=when(e.appearance.presetKey){"sunset"->Color(0xFF8B4F45);"ocean"->Color(0xFF345A79);"lavender"->Color(0xFF66557D);else->forest}
 val base=if(e.appearance.backgroundKind=="solid")Color(e.appearance.solidArgb)else color
 val text=when(e.appearance.textColorMode){"dark"->Color(0xFF18251E);"light"->Color.White;else->if(e.appearance.backgroundKind=="solid"&&base.luminance()>.55)Color(0xFF18251E)else Color.White}
 Card(onClick,Modifier.fillMaxWidth().padding(18.dp),shape=RoundedCornerShape(26.dp)) {
  Box(Modifier.fillMaxWidth().heightIn(min=225.dp).background(Brush.linearGradient(listOf(base,base.copy(alpha=.85f))))) {
   bitmap?.let{Image(it,null,Modifier.matchParentSize(),contentScale=ContentScale.Crop,alignment=BiasAlignment((e.appearance.focusX*2-1).toFloat(),(e.appearance.focusY*2-1).toFloat()))}
   if(bitmap!=null)Box(Modifier.matchParentSize().background(Color.Black.copy(alpha=e.appearance.dimAmount.toFloat())))
   Column(Modifier.padding(24.dp),verticalArrangement=Arrangement.spacedBy(8.dp)) {
    Text(e.title,color=text,fontSize=21.sp,fontWeight=FontWeight.Medium)
    Row(verticalAlignment=Alignment.Bottom){Text(p.days?.toString()?:"—",color=text,fontSize=64.sp,fontWeight=FontWeight.Light);Text(" 天",color=text,modifier=Modifier.padding(bottom=10.dp))}
    Text(p.label+(p.age?.let{" · ${it}岁"}?:""),color=text)
    Text(p.occurrence?.date?.toString()?:"无后续日期",color=text.copy(alpha=.75f),fontSize=12.sp)
   }
  }
 }
}

@Composable private fun HomeScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 val tick=LocalClockTick.current
 val list=vm.graph.service.homeEvents(s,s.home.selectedBookId)
 val hero=vm.graph.service.hero(s,s.home.selectedBookId)
 LazyColumn {
  item { Header("重要的日子",LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy 年 M 月 d 日")),actions={IconButton({nav.navigate(SearchRoute)}){Icon(Icons.Default.Search,"搜索")};IconButton({nav.navigate(CalendarRoute)}){Icon(Icons.Default.CalendarMonth,"日历")};IconButton({nav.navigate(EditRoute())}){Icon(Icons.Default.Add,"新建事件")}}) }
  item { Row(Modifier.padding(horizontal=18.dp).horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)) {
   FilterChip(s.home.selectedBookId==null,{vm.mutate{vm.graph.service.saveHome(s.home.copy(selectedBookId=null))}},label={Text("全部")})
   s.books.sortedBy{it.sortRank}.forEach{b->FilterChip(s.home.selectedBookId==b.id,{vm.mutate{vm.graph.service.saveHome(s.home.copy(selectedBookId=b.id))}},label={Text(b.name)})}
  } }
  if(hero!=null)item { Hero(vm,hero){nav.navigate(DetailRoute(hero.id))} }
  item { Row(Modifier.padding(horizontal=18.dp),verticalAlignment=Alignment.CenterVertically){Text("我的日子",Modifier.weight(1f),fontWeight=FontWeight.Bold);TextButton({vm.mutate{vm.graph.service.saveHome(s.home.copy(sortMode=if(s.home.sortMode=="date")"manual"else"date"))}}){Text(if(s.home.sortMode=="date")"按日期 · 切换手动"else"手动排序 · 切换日期")}} }
  if(list.isEmpty())item { Empty() }
  items(list,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))})}
  item { Spacer(Modifier.height(22.dp)) }
 }
}

@Composable private fun BooksScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var edit by remember{mutableStateOf<Book?>(null)}
 var creating by remember{mutableStateOf(false)}
 var name by remember{mutableStateOf("")}
 var icon by remember{mutableStateOf("book")};var color by remember{mutableIntStateOf(forest.toArgb())};var cover by remember{mutableStateOf<String?>(null)}
 val photo=rememberLauncherForActivityResult(ActivityResultContracts.GetContent()){uri->if(uri!=null)vm.afterUnlock{vm.photo(uri){cover=it.id}}}
 LazyColumn {
  item { Header("日子本","把相似的日子，放在一起。",actions={IconButton({creating=true;name="";icon="book";color=forest.toArgb();cover=null}){Icon(Icons.Default.Add,"创建日子本")}}) }
  items(s.books.sortedBy{it.sortRank},key={it.id}){b->
   ElevatedCard(onClick={nav.navigate(BookRoute(b.id))},Modifier.fillMaxWidth().padding(horizontal=18.dp,vertical=7.dp),shape=RoundedCornerShape(21.dp)) {
    Row(Modifier.padding(18.dp),verticalAlignment=Alignment.CenterVertically){Icon(when(b.iconKey){"birthday"->Icons.Default.Cake;"memorial"->Icons.Default.Favorite;"goal"->Icons.Default.Flag;"holiday"->Icons.Default.BeachAccess;else->Icons.Default.MenuBook},null,tint=Color(b.colorArgb));Column(Modifier.weight(1f).padding(start=14.dp)){Text(b.name,fontWeight=FontWeight.SemiBold);Text("${s.events.count{it.bookId==b.id&&s.lifecycle(it.id)=="active"}} 个日子",style=MaterialTheme.typography.bodySmall)};IconButton({reorderBook(vm,s,b,-1)}){Icon(Icons.Default.KeyboardArrowUp,"本子上移")};IconButton({reorderBook(vm,s,b,1)}){Icon(Icons.Default.KeyboardArrowDown,"本子下移")};IconButton({edit=b;name=b.name;icon=b.iconKey;color=b.colorArgb;cover=b.coverAssetId}){Icon(Icons.Default.Edit,"编辑本子")}}
    b.coverAssetId?.let{AssetPreview(vm,it,Modifier.fillMaxWidth().height(110.dp))}
   }
  }
 }
 if(creating||edit!=null)AlertDialog(onDismissRequest={creating=false;edit=null},title={Text(if(creating)"新建日子本"else"修改日子本")},text={Column(Modifier.heightIn(max=450.dp).verticalScroll(rememberScrollState())){Field("名称",name,{name=it});Options("图标",icon,listOf("book" to "书本","birthday" to "生日","memorial" to "纪念","goal" to "目标","holiday" to "假日")){icon=it};Options("颜色",color.toString(),listOf(forest.toArgb().toString() to "森林",0xFF345A79.toInt().toString() to "海蓝",0xFF8B4F45.toInt().toString() to "暖褐")){color=it.toInt()};TextButton({photo.launch("image/*")}){Text(if(cover==null)"选择封面照片"else"更换封面")};if(cover!=null){AssetPreview(vm,cover!!,Modifier.fillMaxWidth().height(100.dp));TextButton({cover=null}){Text("移除封面")}};Text("200 个本子以内；未分类本不能删除。",style=MaterialTheme.typography.bodySmall)}},confirmButton={TextButton({val old=edit;val b=(old?:Book(name=name,sortRank=(s.books.maxOfOrNull{it.sortRank}?:0)+1)).copy(name=name,iconKey=icon,colorArgb=color,coverAssetId=cover);vm.mutate("日子本已保存"){vm.graph.service.saveBook(b,old?.version)};creating=false;edit=null}){Text("保存")}},dismissButton={TextButton({creating=false;edit=null}){Text("取消")}})
}
private fun reorderBook(vm:AppViewModel,s:LibraryState,b:Book,delta:Int) {
 val all=s.books.sortedBy{it.sortRank}.toMutableList();val i=all.indexOfFirst{it.id==b.id};val j=i+delta;if(j !in all.indices)return
 val other=all[j];all[j]=b;all[i]=other;val ranks=all.mapIndexed{index,book->book.id to index.toLong()}.toMap()
 vm.mutate{vm.graph.store.transaction{state->Change(state.copy(books=state.books.map{it.copy(sortRank=ranks.getValue(it.id),version=it.version+1,updatedAt=System.currentTimeMillis())}),Unit)}}
}
@Composable private fun AssetPreview(vm:AppViewModel,id:String,modifier:Modifier) {
 var image by remember(id){mutableStateOf<ImageBitmap?>(null)}
 LaunchedEffect(id){image=withContext(Dispatchers.IO){runCatching{val a=vm.library.value.assets.first{it.id==id};val f=vm.graph.store.assetFile(a.relativePath);val options=BitmapFactory.Options().apply{inSampleSize=4};BitmapFactory.decodeFile(f.path,options)?.asImageBitmap()}.getOrNull()}}
 image?.let{Image(it,null,modifier,contentScale=ContentScale.Crop)}
}

@Composable private fun BookScreen(vm:AppViewModel,s:LibraryState,id:String,nav:NavHostController) {
 val book=s.books.find{it.id==id}
 if(book==null){Empty("日子本已删除");return}
 var selected by rememberSaveable{idState()}
 var query by rememberSaveable{mutableStateOf("")}
 var allLevels by rememberSaveable{mutableStateOf(false)}
 var delete by remember{mutableStateOf(false)}
 var moving by remember{mutableStateOf(false)}
 var tagsDialog by remember{mutableStateOf(false)}
 val found=vm.graph.service.search(s,query,bookId=id).filter{allLevels||it.parentId==null}.let{if(s.home.sortMode=="manual")it.sortedBy{e->e.sortRank}else it}
 LazyColumn {
  item { Header(book.name,"默认只展示本子的根事件",{nav.popBackStack()},actions={IconButton({nav.navigate(EditRoute(bookId=id))}){Icon(Icons.Default.Add,"新建事件")};if(!book.isProtected)IconButton({delete=true}){Icon(Icons.Default.Delete,"删除本子")}}) }
  item { Column(Modifier.padding(horizontal=18.dp)){Field("搜索本子中的日子",query,{query=it});Toggle("显示所有层级（搜索列表）",allLevels,{allLevels=it});Options("排序",s.home.sortMode,listOf("date" to "日期","manual" to "手动")){v->vm.mutate{vm.graph.service.saveHome(s.home.copy(sortMode=v))}}} }
  if(selected.isNotEmpty())item { Section("已选 ${selected.size} 项") {
   FlowRow(horizontalArrangement=Arrangement.spacedBy(6.dp)){TextButton({val ids=selected.toList();vm.mutate{vm.graph.service.setLifecycle(ids,"archive")};selected=emptyList()}){Text("归档")};TextButton({val ids=selected.toList();vm.mutate{vm.graph.service.setLifecycle(ids,"trash")};selected=emptyList()}){Text("移到回收站")};TextButton({moving=true}){Text("移动")};TextButton({tagsDialog=true}){Text("批量标签")};TextButton({selected=found.map{it.id}}){Text("全选")};TextButton({selected=emptyList()}){Text("取消选择")}}
  } }
  if(found.isEmpty())item{Empty()}
  items(found,key={it.id}){e->EventRow(vm,s,e,{if(selected.isNotEmpty())selected=toggleId(selected,e.id)else nav.navigate(DetailRoute(e.id))},selected=if(selected.isNotEmpty())e.id in selected else null,select={selected=toggleId(selected,e.id)}){
   if(s.home.sortMode=="manual") {IconButton({reorder(vm,s,e,-1,found)}){Icon(Icons.Default.KeyboardArrowUp,"上移")};IconButton({reorder(vm,s,e,1,found)}){Icon(Icons.Default.KeyboardArrowDown,"下移")}}
  }}
 }
 if(delete)AlertDialog(onDismissRequest={delete=false},title={Text("删除 ${book.name}？")},text={Text("选择将全部事件移到未分类本，或将全部事件移到回收站；不会立即永久删除。")},confirmButton={TextButton({delete=false;vm.mutate{vm.graph.service.deleteBook(id,true)};nav.popBackStack()}){Text("事件移到回收站")}},dismissButton={Column{TextButton({delete=false;vm.mutate{vm.graph.service.deleteBook(id,false)};nav.popBackStack()}){Text("事件移到未分类")};TextButton({delete=false}){Text("取消")}}})
 if(moving)MoveDialog(s,selected.firstOrNull(),{moving=false}){bookId,parent->val ids=selected.toList();vm.mutate{vm.graph.service.moveSubtrees(ids,bookId,parent)};selected=emptyList();moving=false}
 if(tagsDialog)BatchTagsDialog(vm,s,selected.toList()){tagsDialog=false}
}
@Composable private fun BatchTagsDialog(vm:AppViewModel,s:LibraryState,ids:List<String>,dismiss:()->Unit) {
 var chosen by rememberSaveable{mutableStateOf<List<String>>(emptyList())}
 AlertDialog(onDismissRequest=dismiss,title={Text("替换所选 ${ids.size} 项的标签")},text={Column(Modifier.heightIn(max=400.dp).verticalScroll(rememberScrollState())){Text("确认后以此选择替换原标签；一个也不选会清空所选事件的标签。新标签可先在设置中创建。",style=MaterialTheme.typography.bodySmall);s.tags.forEach{tag->Row(verticalAlignment=Alignment.CenterVertically){Checkbox(tag.id in chosen,{if(tag.id in chosen||chosen.size<20)chosen=toggleId(chosen,tag.id)else vm.message.value="最多 20 个标签"});Text(tag.name)}}}},confirmButton={TextButton({val tags=chosen.toList();vm.mutate{vm.graph.service.setTags(ids,tags)};dismiss()}){Text("确认替换")}},dismissButton={TextButton(dismiss){Text("取消")}})
}
private fun idState()=mutableStateOf<List<String>>(emptyList())
private fun toggleId(ids:List<String>,id:String)=if(id in ids)ids-id else ids+id
private fun reorder(vm:AppViewModel,s:LibraryState,e:Event,delta:Int,list:List<Event>) {
 val siblings=list.filter{it.parentId==e.parentId}.sortedBy{it.sortRank}.toMutableList();val i=siblings.indexOfFirst{it.id==e.id};val j=i+delta;if(j !in siblings.indices)return
 val target=siblings[j];siblings[j]=e;siblings[i]=target
 vm.mutate { vm.graph.store.transaction { state ->
  val ranks=siblings.mapIndexed{index,event->event.id to index.toLong()}.toMap()
  Change(state.copy(events=state.events.map{if(it.id in ranks)it.copy(sortRank=ranks.getValue(it.id),version=it.version+1,updatedAt=System.currentTimeMillis())else it}),Unit)
 } }
}

@Composable private fun SearchScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var query by rememberSaveable{mutableStateOf("")};var scope by rememberSaveable{mutableStateOf("active")};var tag by rememberSaveable{mutableStateOf("")}
 val found=vm.graph.service.search(s,query,scope).filter{tag.isBlank()||tag in it.tagIds}
 LazyColumn {
  item { Header("搜索","标题、寄语、标签和日子本",{nav.popBackStack()}) }
  item { Column(Modifier.padding(horizontal=18.dp)){Field("关键词",query,{query=it});Options("范围",scope,listOf("active" to "使用中","archived" to "已归档","trash" to "回收站","all" to "全部")){scope=it};Options("标签",tag,listOf("" to "所有标签")+s.tags.map{it.id to it.name}){tag=it}} }
  item { Text("${found.size} 个结果",Modifier.padding(18.dp),style=MaterialTheme.typography.labelLarge) }
  items(found,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))})}
 }
}

@Composable private fun GoalsScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var filter by rememberSaveable{mutableStateOf("all")}
 val goals=s.events.filter{it.kind=="goal"&&s.lifecycle(it.id)=="active"&&(filter=="all"||it.goal?.state==filter)}
 LazyColumn {
  item { Header("向目标靠近","记录行动，也看见每一步。",actions={IconButton({nav.navigate(EditRoute(goal=true))}){Icon(Icons.Default.Add,"创建目标")}}) }
  item { Column(Modifier.padding(horizontal=18.dp)){Options("状态",filter,listOf("all" to "全部","not_started" to "未开始","in_progress" to "进行中","completed" to "已完成","canceled" to "已取消")){filter=it}} }
  if(goals.isEmpty())item{Empty("创建目标后，可以在详情中手动添加阶段目标和行动记录。")}
  items(goals,key={it.id}){e->Section(e.title){Text(goalLabel(e.goal!!.state));val rate=vm.graph.service.completionRate(s,e.id);Text(if(rate==null)"尚无参与统计的直属阶段"else"直属阶段 ${rate.first} / ${rate.second} 完成");LinearProgressIndicator(progress={if(rate==null)0f else rate.first.toFloat()/rate.second},modifier=Modifier.fillMaxWidth());TextButton({nav.navigate(DetailRoute(e.id))}){Text("查看目标")}}}
 }
}
private fun goalLabel(s:String)=mapOf("not_started" to "未开始","in_progress" to "进行中","completed" to "已完成","canceled" to "已取消")[s]?:s

@Composable private fun DetailScreen(vm:AppViewModel,s:LibraryState,id:String,nav:NavHostController) {
 val tick=LocalClockTick.current
 val e=s.events.find{it.id==id}
 if(e==null){Column{Header("事件不存在",back={nav.popBackStack()});Empty("可能已被永久删除，或资料库已替换。")};return}
 val level=depth(s,id);val lifecycle=s.lifecycle(id)
 val goal=e.goal;val parentId=e.parentId
 var actionEdit by remember{mutableStateOf<ActionRecord?>(null)};var newAction by remember{mutableStateOf(false)}
 var move by remember{mutableStateOf(false)};var delete by remember{mutableStateOf(false)}
 var sort by rememberSaveable{mutableStateOf("date")};var pages by rememberSaveable(id){mutableIntStateOf(1)}
 val children=remember(s.revision,id,sort,pages,tick){
  val rows=mutableListOf<ChildSummary>();var cursor:String?=null
  repeat(pages){val page=vm.graph.service.directChildren(s,id,sort,cursor);rows+=page.rows;cursor=page.cursor;if(!page.hasMore)return@remember rows to false}
  rows to (cursor!=null)
 }
 val scroll=rememberLazyListState()
 LazyColumn(state=scroll,modifier=Modifier.testTag("detail_list")) {
  item { Header(e.title,"第 $level 级 · ${if(lifecycle=="active")"使用中"else if(lifecycle=="trash")"回收站"else"已归档"}",{nav.popBackStack()},actions={if(lifecycle!="trash")IconButton({nav.navigate(EditRoute(id=id))}){Icon(Icons.Default.Edit,"编辑事件")};IconButton({nav.navigate(ShareRoute(id))}){Icon(Icons.Default.Share,"分享卡片")}}) }
  if(parentId!=null)item{TextButton({nav.navigate(DetailRoute(parentId))}){Text("所属事件：${s.events.find{it.id==parentId}?.title?:"已删除"}")}}
  item { Hero(vm,e){} }
  if(e.greeting.isNotBlank())item { Section("事件寄语"){SelectionContainerCompat(e.greeting)} }
  item { Section("事件信息") {Text("日期：${dateText(e.date)}${if(e.date.calendar=="lunar")"（农历）"else""}");Text("${if(e.countMode=="up")"正数日"else"倒数日"} · ${repeatLabel(e.repeat.frequency)}");if(!e.date.allDay)Text("${e.date.localTime} · ${e.date.zoneId}");if(e.tagIds.isNotEmpty())Text("标签："+e.tagIds.mapNotNull{id2->s.tags.find{it.id==id2}?.name}.joinToString(" / "));Text("提醒："+e.reminders.filter{it.enabled}.joinToString{r->"提前${r.offsetValue}${if(r.offsetUnit=="minutes")"分钟"else"天"} ${r.localTime?:""}"}.ifBlank{"未开启"});Toggle("在首页列表展示",e.homeVisible,{v->vm.mutate{vm.graph.service.saveEvent(e.copy(homeVisible=v),e.version)}});Toggle("置顶",e.pinned,{v->vm.mutate{vm.graph.service.saveEvent(e.copy(pinned=v),e.version)}});TextButton({vm.mutate{vm.graph.service.saveHome(s.home.copy(heroMode="fixed",fixedEventId=id))}}){Text("固定为首页大卡片")}} }
  if(goal!=null)item { Section("目标进度") {
   Text("状态：${goalLabel(goal.state)}")
   if(lifecycle!="trash")FlowRow {(when(goal.state){"not_started"->listOf("in_progress","completed","canceled");"in_progress"->listOf("completed","canceled");else->listOf("in_progress")}).forEach{v->TextButton({vm.mutate{vm.graph.service.setGoalState(id,v)}}){Text(goalLabel(v))}}}
   val rate=vm.graph.service.completionRate(s,id);Text(if(rate==null)"无参与统计的直属阶段"else"直属阶段完成 ${rate.first} / ${rate.second}")
   if(rate!=null)LinearProgressIndicator(progress={rate.first.toFloat()/rate.second},modifier=Modifier.fillMaxWidth())
   Text("时间进度：${(vm.graph.service.timeProgress(s,id)*100).toInt()}%（不是完成率）")
   LinearProgressIndicator(progress={vm.graph.service.timeProgress(s,id).toFloat()},modifier=Modifier.fillMaxWidth())
  } }
  item { Section(if(e.goal!=null)"直属阶段与子事件"else"直属子事件") {
   Text("只显示下一级；点击条目进入它的详情，不在此展开第三级。",style=MaterialTheme.typography.bodySmall)
   Options("排序",sort,listOf("date" to "日期","manual" to "手动")){sort=it;pages=1}
   if(level<3&&lifecycle=="active")Button({nav.navigate(EditRoute(parentId=id,bookId=e.bookId,goal=e.kind=="goal"))}){Text(if(e.kind=="goal")"添加阶段或子事件"else"添加子事件")}
   else Text(if(level==3)"已到第三级，不支持继续新增下级"else"恢复事件后可新增下级",style=MaterialTheme.typography.bodySmall)
  } }
  items(children.first,key={it.event.id}){c->EventRow(vm,s,c.event,{nav.navigate(DetailRoute(c.event.id))}){
   if(sort=="manual"){IconButton({reorder(vm,s,c.event,-1,children.first.map{it.event})}){Icon(Icons.Default.KeyboardArrowUp,"上移")};IconButton({reorder(vm,s,c.event,1,children.first.map{it.event})}){Icon(Icons.Default.KeyboardArrowDown,"下移")}}
  }}
  if(children.second)item{TextButton({pages++},Modifier.fillMaxWidth()){Text("再加载 20 项")}}
  if(e.goal!=null) {
   item { Section("行动记录"){if(lifecycle!="trash")Button({newAction=true}){Text("记录一次行动")};Text("每条独立记录日期、内容与可选用时；不会写成事件寄语。",style=MaterialTheme.typography.bodySmall)} }
   items(s.actions.filter{it.goalEventId==id}.sortedWith(compareByDescending<ActionRecord>{it.date}.thenByDescending{it.createdAt}),key={it.id}){a->Section(a.date+(a.minutes?.let{" · $it 分钟"}?:"")){Text(a.body);Row{if(lifecycle!="trash"){TextButton({actionEdit=a}){Text("编辑")};TextButton({vm.mutate{vm.graph.service.deleteAction(a.id)}}){Text("删除记录")}}}}}
  }
  item { Section("更多操作") {
   FlowRow {if(lifecycle!="trash"){TextButton({vm.mutate{vm.graph.service.copySubtree(id,true)}}){Text("复制含子树")};TextButton({vm.mutate{vm.graph.service.copySubtree(id,false)}}){Text("仅复制当前")};TextButton({move=true}){Text("移动子树")};TextButton({vm.mutate{vm.graph.service.setLifecycle(listOf(id),"archive")}}){Text("归档")};TextButton({delete=true}){Text("移到回收站")};TextButton({try{vm.outgoing.value=vm.graph.systems.calendarAdd(e)}catch(ex:Exception){vm.error(ex)}}){Text("添加到系统日历")}}
    else TextButton({nav.navigate(LifecycleRoute("trash"))}){Text("到回收站恢复或永久删除")}
   }
  } }
 }
 if(delete)Confirm("移到回收站？","当前事件及其全部下级会一并移入。30 天后可被自动清理；此前可恢复。",{delete=false}){delete=false;vm.mutate{vm.graph.service.setLifecycle(listOf(id),"trash")};nav.popBackStack()}
 if(move)MoveDialog(s,id,{move=false}){book,parent->move=false;vm.mutate{vm.graph.service.moveSubtree(id,book,parent)}}
 if(newAction||actionEdit!=null)ActionDialog(vm,id,actionEdit){newAction=false;actionEdit=null}
}
@Composable private fun SelectionContainerCompat(text:String) { androidx.compose.foundation.text.selection.SelectionContainer { Text(text) } }
private fun dateText(d:DateSpec)=(d.year?.toString()?:"--")+"-%02d-%02d".format(d.month,d.day)
private fun repeatLabel(v:String)=mapOf("none" to "不重复","yearly" to "每年","monthly" to "每月","weekly" to "每周","every_n_days" to "每 N 天")[v]?:v

@Composable private fun MoveDialog(s:LibraryState,id:String?,dismiss:()->Unit,confirm:(String,String?)->Unit) {
 var book by remember{mutableStateOf(s.events.find{it.id==id}?.bookId?:s.books.first().id)};var parent by remember{mutableStateOf<String?>(null)}
 val excluded=if(id==null)emptySet()else descendants(s,id)
 AlertDialog(onDismissRequest=dismiss,title={Text("移动事件及其全部下级")},text={Column(Modifier.heightIn(max=450.dp).verticalScroll(rememberScrollState())){
  Text("移动不会改变日期；目标层级超过三级会被拒绝。")
  Options("目标本",book,s.books.map{it.id to it.name}){book=it;parent=null}
  FilterChip(parent==null,{parent=null},label={Text("作为根事件")})
  s.events.filter{it.bookId==book&&it.id !in excluded&&s.lifecycle(it.id)=="active"&&depth(s,it.id)<3}.forEach{e->FilterChip(parent==e.id,{parent=e.id},label={Text("第${depth(s,e.id)}级 · ${e.title}")})}
 }},confirmButton={TextButton({confirm(book,parent)}){Text("移动")}},dismissButton={TextButton(dismiss){Text("取消")}})
}

@Composable private fun ActionDialog(vm:AppViewModel,id:String,existing:ActionRecord?,dismiss:()->Unit) {
 var date by rememberSaveable{mutableStateOf(existing?.date?:LocalDate.now().toString())};var body by rememberSaveable{mutableStateOf(existing?.body?:"")};var minutes by rememberSaveable{mutableStateOf(existing?.minutes?.toString()?:"")}
 AlertDialog(onDismissRequest=dismiss,title={Text(if(existing==null)"记录行动"else"编辑行动")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(8.dp)){Field("行动日期 YYYY-MM-DD",date,{date=it});Field("记录内容（最多 1000 字符）",body,{body=it},4);Field("用时分钟（可留空，0–1440）",minutes,{minutes=it})}},confirmButton={TextButton({val n=if(minutes.isBlank())null else minutes.toIntOrNull();if(minutes.isNotBlank()&&n==null){vm.message.value="用时必须为整数"}else{vm.mutate("行动已记录"){vm.graph.service.saveAction(existing?.copy(date=date,body=body,minutes=n)?:ActionRecord(goalEventId=id,date=date,body=body,minutes=n),existing?.version)};dismiss()}}){Text("保存")}},dismissButton={TextButton(dismiss){Text("取消")}})
}

@Composable private fun EditorScreen(vm:AppViewModel,s:LibraryState,route:EditRoute,nav:NavHostController) {
 val existing=s.events.find{it.id==route.id}
 if(route.id.isNotEmpty()&&existing==null){Empty("事件已不存在，请返回重新选择");return}
 val key=if(existing!=null)existing.id else "new-${route.parentId}-${route.bookId}-${route.goal}"
 val book=route.parentId.takeIf{it.isNotBlank()}?.let{s.event(it).bookId}?:route.bookId.takeIf{b->s.books.any{it.id==b}}?:s.books.firstOrNull{it.builtinKey==if(route.goal)"goal"else"uncategorized"}!!.id
 val base=remember(key){existing?:Event(bookId=book,parentId=route.parentId.takeIf{it.isNotBlank()},title="",kind=if(route.goal)"goal"else"ordinary",date=DateSpec(year=LocalDate.now().year,month=LocalDate.now().monthValue,day=LocalDate.now().dayOfMonth),goal=if(route.goal)GoalDetail(LocalDate.now().toString())else null)}
 var draft by remember(key){mutableStateOf(EditorDraft(base,dateText(base.date),base.goal?.startDate?:LocalDate.now().toString(),base.tagIds.mapNotNull{id->s.tags.find{it.id==id}?.name}.joinToString(",")))}
 var loaded by remember(key){mutableStateOf(false)}
 var askExit by remember{mutableStateOf(false)}
 var conflict by remember{mutableStateOf(false)}
 var parentPicker by remember{mutableStateOf(false)}
 val busy by vm.busy.collectAsStateWithLifecycle()
 val scope=rememberCoroutineScope()
 LaunchedEffect(key){val saved=withContext(Dispatchers.IO){vm.prefs.draft(key)};if(saved!=null)runCatching{vm.json.decodeFromString<EditorDraft>(saved)}.onSuccess{d->if(existing==null||d.event.version==existing.version)draft=d else conflict=true};loaded=true}
 LaunchedEffect(draft,loaded){if(loaded){delay(500);withContext(Dispatchers.IO){vm.prefs.saveDraft(key,vm.json.encodeToString(draft))}}}
 fun setEvent(f:(Event)->Event){draft=draft.copy(event=f(draft.event))}
 fun leave(){scope.launch{withContext(Dispatchers.IO){vm.prefs.saveDraft(key,vm.json.encodeToString(draft))};nav.popBackStack()}}
 BackHandler{askExit=true}
 val e=draft.event
 val photo=rememberLauncherForActivityResult(ActivityResultContracts.GetContent()){uri->if(uri!=null)vm.afterUnlock{vm.photo(uri){a->setEvent{it.copy(appearance=it.appearance.copy(backgroundKind="photo",assetId=a.id))}}}}
 val notification=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){allowed->vm.message.value=if(allowed)"通知权限已开启"else"通知未授权，事件仍可保存"}
 LazyColumn(contentPadding=PaddingValues(bottom=30.dp)) {
  item { Header(if(existing==null)"留住一个日子"else"编辑日子",if(e.parentId==null)"根事件"else"属于：${s.events.find{it.id==e.parentId}?.title}",{askExit=true},actions={TextButton({vm.save(draft,existing,key){id->nav.popBackStack();if(existing==null)nav.navigate(DetailRoute(id))}},enabled=!busy&&loaded){Text("保存",fontWeight=FontWeight.Bold)}}) }
  if(!loaded)item{LinearProgressIndicator(Modifier.fillMaxWidth())}
  item { Section("基本信息") {
   Field("日子名称（最多 60 字符）",e.title,{v->setEvent{it.copy(title=v)}})
   Options("类型",e.kind,listOf("ordinary" to "普通","birthday" to "生日","memorial" to "纪念日","holiday" to "假日","goal" to "目标")){kind->setEvent{old->old.copy(kind=kind,countMode=if(kind in setOf("birthday","goal"))"down"else old.countMode,date=if(kind in setOf("birthday","goal"))old.date.copy(calendar=if(kind=="goal")"gregorian"else old.date.calendar,allDay=true,localTime=null,zoneId=null,leapMonth=if(kind=="goal")false else old.date.leapMonth)else old.date,repeat=if(kind=="birthday")RecurrenceSpec("yearly")else if(kind=="goal")RecurrenceSpec()else old.repeat,goal=if(kind=="goal")old.goal?:GoalDetail(draft.startDate)else null,reminders=if(kind=="birthday"&&old.reminders.isEmpty())listOf(ReminderRule(enabled=true,offsetValue=7),ReminderRule(enabled=true))else old.reminders)}}
   if(existing==null){Options("所属本",e.bookId,s.books.map{it.id to it.name}){v->if(e.parentId==null)setEvent{it.copy(bookId=v)}else vm.message.value="子事件与父事件必须属于同一本"};TextButton({parentPicker=true}){Text(if(e.parentId==null)"作为根事件 · 选择上级"else"更改上级（同本）")}}
   else Text("所属本与上级请在详情的‘移动子树’中更改。",style=MaterialTheme.typography.bodySmall)
   Options("计算方式",e.countMode,if(e.kind in setOf("birthday","goal"))listOf("down" to "倒数")else listOf("down" to "倒数","up" to "正数")){v->setEvent{it.copy(countMode=v,repeat=if(v=="up")RecurrenceSpec()else it.repeat)}}
   if(e.countMode=="up")Toggle("包含开始当天",e.includeStartDay,{v->setEvent{it.copy(includeStartDay=v)}})
   Toggle("在首页列表显示",e.homeVisible,{v->setEvent{it.copy(homeVisible=v)}})
   Toggle("置顶事件",e.pinned,{v->setEvent{it.copy(pinned=v)}})
   Field("标签（英文或中文逗号分隔）",draft.tags,{draft=draft.copy(tags=it)})
  } }
  item { Section("日期与重复") {
   Options("历法",e.date.calendar,if(e.kind=="goal"||!e.date.allDay)listOf("gregorian" to "公历")else listOf("gregorian" to "公历","lunar" to "农历")){v->setEvent{it.copy(date=it.date.copy(calendar=v,leapMonth=false),repeat=if(v=="lunar"&&it.repeat.frequency !in setOf("none","yearly"))RecurrenceSpec()else it.repeat)}}
   Field("日期 YYYY-MM-DD",draft.dateText,{draft=draft.copy(dateText=it)})
   Text(if(e.kind=="birthday")"未知出生年份可用 ---MM-DD，例如 ---10-31；不显示年龄。"else"公历 1900–2100；农历 1901–2099。",style=MaterialTheme.typography.bodySmall)
   if(e.date.calendar=="lunar"){
    Toggle("闰月生日 / 日期",e.date.leapMonth,{v->setEvent{it.copy(date=it.date.copy(leapMonth=v))}})
    Options("当年无闰月",e.date.lunarLeapPolicy,listOf("normal_fallback" to "落到普通月","leap_only" to "仅闰月年份")){v->setEvent{it.copy(date=it.date.copy(lunarLeapPolicy=v))}}
    Options("当月没有三十日",e.date.lunarSmallMonthPolicy,listOf("month_end" to "月末","skip" to "跳过该年")){v->setEvent{it.copy(date=it.date.copy(lunarSmallMonthPolicy=v))}}
   }else Options("2 月 29 日非闰年",e.date.feb29Policy,listOf("feb28" to "2 月 28 日","mar01" to "3 月 1 日")){v->setEvent{it.copy(date=it.date.copy(feb29Policy=v))}}
   if(e.kind !in setOf("birthday","goal")&&e.date.calendar=="gregorian")Toggle("全天事件",e.date.allDay,{v->setEvent{it.copy(date=it.date.copy(allDay=v,localTime=if(v)null else"09:00",zoneId=if(v)null else ZoneId.systemDefault().id),reminders=it.reminders.map{r->r.copy(offsetUnit="days",localTime=if(v)"09:00"else null,version=r.version+1)})}})
   if(!e.date.allDay){Field("当地时间 HH:mm",e.date.localTime.orEmpty(),{v->setEvent{it.copy(date=it.date.copy(localTime=v))}});Field("时区，如 Asia/Shanghai",e.date.zoneId.orEmpty(),{v->setEvent{it.copy(date=it.date.copy(zoneId=v))}});Text("夏令时缺口向后移到有效时间；重复时间取较早偏移。",style=MaterialTheme.typography.bodySmall)}
   val repeats=when{e.kind=="birthday"->listOf("yearly" to "每年");e.kind=="goal"||e.countMode=="up"->listOf("none" to "不重复");e.date.calendar=="lunar"->listOf("none" to "不重复","yearly" to "每年");else->listOf("none" to "不重复","yearly" to "每年","monthly" to "每月","weekly" to "每周","every_n_days" to "每 N 天")}
   Options("重复",e.repeat.frequency,repeats){v->setEvent{it.copy(repeat=it.repeat.copy(frequency=v,intervalDays=if(v=="every_n_days")1 else null,until=if(v=="none")null else it.repeat.until))}}
   if(e.repeat.frequency=="every_n_days")Field("间隔天数 1–365",e.repeat.intervalDays?.toString().orEmpty(),{v->setEvent{it.copy(repeat=it.repeat.copy(intervalDays=v.toIntOrNull()))}})
   if(e.repeat.frequency!="none")Field("重复截止日期（可留空）",e.repeat.until.orEmpty(),{v->setEvent{it.copy(repeat=it.repeat.copy(until=v.takeIf{it.isNotBlank()}))}})
   if(e.kind=="goal"){Field("目标开始日 YYYY-MM-DD",draft.startDate,{draft=draft.copy(startDate=it)});Toggle("作为父目标的参与统计阶段",e.goal?.includeInParent?:true,{v->setEvent{it.copy(goal=(it.goal?:GoalDetail(draft.startDate)).copy(includeInParent=v))}})}
  } }
  item { Section("事件寄语") {Field("写一段想留住的话（可空，最多 2000 字符）",e.greeting,{v->setEvent{it.copy(greeting=v)}},4);Text("只有这一段文字，不生成日记或多条小纸条。",style=MaterialTheme.typography.bodySmall)} }
  item { Section("背景与文字") {
   Options("背景",e.appearance.backgroundKind,listOf("gradient" to "渐变","solid" to "纯色","photo" to "照片")){v->if(v=="photo"&&e.appearance.assetId==null)photo.launch("image/*")else setEvent{it.copy(appearance=it.appearance.copy(backgroundKind=v,assetId=if(v=="photo")it.appearance.assetId else null))}}
   if(e.appearance.backgroundKind=="gradient")Options("主题",e.appearance.presetKey,listOf("forest" to "森林","sunset" to "晚霞","ocean" to "海洋","lavender" to "薰衣草")){v->setEvent{it.copy(appearance=it.appearance.copy(presetKey=v))}}
   if(e.appearance.backgroundKind=="solid")Options("颜色",e.appearance.solidArgb.toString(),listOf(0xFF214F43.toInt().toString() to "森林绿",0xFF345A79.toInt().toString() to "海蓝",0xFFF1E8D5.toInt().toString() to "奶油白",0xFF8B4F45.toInt().toString() to "暖褐")){v->setEvent{it.copy(appearance=it.appearance.copy(solidArgb=v.toInt()))}}
   if(e.appearance.backgroundKind=="photo"){TextButton({photo.launch("image/*")}){Text("选择 / 更换照片")};Text("横向焦点");Slider(e.appearance.focusX.toFloat(),{v->setEvent{it.copy(appearance=it.appearance.copy(focusX=v.toDouble()))}});Text("纵向焦点");Slider(e.appearance.focusY.toFloat(),{v->setEvent{it.copy(appearance=it.appearance.copy(focusY=v.toDouble()))}});Text("遮罩深度");Slider(e.appearance.dimAmount.toFloat(),{v->setEvent{it.copy(appearance=it.appearance.copy(dimAmount=v.toDouble()))}})}
   Options("文字颜色",e.appearance.textColorMode,listOf("auto" to "自动对比度","light" to "浅色","dark" to "深色")){v->setEvent{it.copy(appearance=it.appearance.copy(textColorMode=v))}}
   Hero(vm,e.copy(title=e.title.ifBlank{"你的重要日子"},date=runCatching{val p=draft.dateText.split('-');e.date.copy(year=p[0].toInt(),month=p[1].toInt(),day=p[2].toInt())}.getOrDefault(base.date),repeat=if(e.kind=="birthday")RecurrenceSpec("yearly")else e.repeat)){}
  } }
  item { Section("本机提醒") {
   Text("生日默认提前 7 天和当天 09:00。普通提醒不保证秒级；精准提醒需系统许可。",style=MaterialTheme.typography.bodySmall)
   if(!vm.graph.systems.notificationAllowed())TextButton({if(Build.VERSION.SDK_INT>=33)notification.launch(Manifest.permission.POST_NOTIFICATIONS)else vm.outgoing.value=vm.graph.systems.requestNotificationSettings()}){Text("开启系统通知权限")}
   e.reminders.forEachIndexed{i,r->
    fun change(f:(ReminderRule)->ReminderRule){setEvent{it.copy(reminders=it.reminders.mapIndexed{index,old->if(index==i)f(old).copy(version=old.version+1)else old})}}
    HorizontalDivider();Toggle("提醒 ${i+1}",r.enabled,{v->change{it.copy(enabled=v)}})
    Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){Field("提前数值",r.offsetValue.toString(),{v->change{it.copy(offsetValue=v.toIntOrNull()?:-1)}},modifier=Modifier.weight(1f));TextButton({setEvent{it.copy(reminders=it.reminders.filterIndexed{index,_->index!=i})}}){Text("删除")}}
    if(!e.date.allDay)Options("单位",r.offsetUnit,listOf("days" to "天","hours" to "小时","minutes" to "分钟")){v->change{it.copy(offsetUnit=v)}}
    if(e.date.allDay)Field("提醒时间 HH:mm",r.localTime?:"09:00",{v->change{it.copy(localTime=v)}})
    Options("精度",r.precisionMode,listOf("normal" to "普通","precise" to "精准")){v->change{it.copy(precisionMode=v)}}
   }
   if(e.reminders.size<5)TextButton({setEvent{it.copy(reminders=it.reminders+ReminderRule(enabled=true,localTime=if(it.date.allDay)"09:00"else null))}}){Text("添加提醒（最多 5 条）")}
  } }
  item { Button({vm.save(draft,existing,key){id->nav.popBackStack();if(existing==null)nav.navigate(DetailRoute(id))}},Modifier.fillMaxWidth().padding(18.dp),enabled=!busy&&loaded){Text("保存这个日子")} }
 }
 if(askExit)AlertDialog(onDismissRequest={askExit=false},title={Text("离开编辑？")},text={Text("未保存内容可保留为本机草稿，下次打开同一事件可继续。")},confirmButton={TextButton({askExit=false;leave()}){Text("保留草稿并离开")}},dismissButton={Column{TextButton({askExit=false;scope.launch{vm.prefs.deleteDraft(key);nav.popBackStack()}}){Text("丢弃草稿并离开")};TextButton({askExit=false}){Text("继续编辑")}}})
 if(conflict)Confirm("草稿版本已过期","事件已被其他操作更新。本次已使用最新保存内容；旧草稿不会自动覆盖。",{conflict=false}){conflict=false}
 if(parentPicker)MoveDialog(s,null,{parentPicker=false}){b,parent->val valid=parent==null||depth(s,parent)<3;if(valid){setEvent{it.copy(bookId=b,parentId=parent,homeVisible=parent==null)};parentPicker=false}else vm.message.value="最多支持三级事件"}
}

@Composable private fun LifecycleScreen(vm:AppViewModel,s:LibraryState,kind:String,nav:NavHostController) {
 var purge by remember{mutableStateOf<String?>(null)}
 val events=s.events.filter{s.lifecycle(it.id)==kind}
 LazyColumn {
  item { Header(if(kind=="trash")"回收站"else"已归档",if(kind=="trash")"30 天后可自动清理；永久删除不可恢复"else"不会触发提醒，也不参与首页排序",{nav.popBackStack()}) }
  if(events.isEmpty())item{Empty("这里是空的")}
  items(events,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))}){if(kind=="trash")IconButton({purge=e.id}){Icon(Icons.Default.DeleteForever,"永久删除")}}}
  item { Section("恢复批次") {
   Text("恢复会撤销所选批次的原因；如果仍受到别的归档或回收站批次影响，会继续保持隐藏。",style=MaterialTheme.typography.bodySmall)
   s.causes.filter{it.kind==if(kind=="trash")"trash"else"archive"}.sortedByDescending{it.createdAt}.forEach{c->
    Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text("${c.members.size} 项 · ${Instant.ofEpochMilli(c.createdAt).atZone(ZoneId.systemDefault()).toLocalDate()}");c.purgeAfter?.let{Text("最早清理：${Instant.ofEpochMilli(it).atZone(ZoneId.systemDefault()).toLocalDate()}",style=MaterialTheme.typography.bodySmall)}};TextButton({vm.mutate("已恢复该批次"){vm.graph.service.restoreCause(c.id)}}){Text("恢复")}}
   }
  } }
 }
 if(purge!=null)Confirm("永久删除子树？","此操作会删除当前事件、全部下级及其行动记录，不能撤销。请先确认已有备份。",{purge=null}){val id=purge!!;purge=null;vm.mutate{vm.graph.service.purge(listOf(id));vm.graph.store.gc()}}
}

@Composable private fun CalendarScreen(vm:AppViewModel,s:LibraryState,nav:NavHostController) {
 var monthText by rememberSaveable{mutableStateOf(YearMonth.now().toString())};var selected by rememberSaveable{mutableStateOf(LocalDate.now().toString())}
 val month=YearMonth.parse(monthText);val monday by vm.prefs.weekMonday.collectAsStateWithLifecycle(true)
 val start=month.atDay(1);val end=month.atEndOfMonth()
 val map=remember(s.revision,monthText){val days=mutableMapOf<LocalDate,MutableList<Event>>();s.events.filter{s.lifecycle(it.id)=="active"}.forEach{e->if(e.countMode=="down")runCatching{vm.graph.dates.occurrences(e.dateInput(),start,end)}.getOrDefault(emptyList()).forEach{days.getOrPut(it.date){mutableListOf()}+=e}};days}
 LazyColumn {
  item { Header("日历","按发生日期展开重复事项",{nav.popBackStack()}) }
  item { Section(monthText) {
   Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){TextButton({monthText=month.minusMonths(1).toString()}){Text("上个月")};TextButton({monthText=YearMonth.now().toString();selected=LocalDate.now().toString()}){Text("今天")};TextButton({monthText=month.plusMonths(1).toString()}){Text("下个月")}}
   Row{(if(monday)listOf("一","二","三","四","五","六","日")else listOf("日","一","二","三","四","五","六")).forEach{Text(it,Modifier.weight(1f),textAlign=androidx.compose.ui.text.style.TextAlign.Center)}}
   val offset=if(monday)start.dayOfWeek.value-1 else start.dayOfWeek.value%7
   val total=((offset+month.lengthOfMonth()+6)/7)*7
   (0 until total step 7).forEach{row->Row{(row until row+7).forEach{i->val day=i-offset+1;if(day !in 1..month.lengthOfMonth())Spacer(Modifier.weight(1f).height(50.dp))else{val date=month.atDay(day);Column(Modifier.weight(1f).height(50.dp).background(if(selected==date.toString())MaterialTheme.colorScheme.primaryContainer else Color.Transparent,RoundedCornerShape(10.dp)).clickable{selected=date.toString()},horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){Text(day.toString());Text(if(map[date].isNullOrEmpty())" "else"•",color=MaterialTheme.colorScheme.primary)}}}}}
  } }
  item{Text(selected,Modifier.padding(18.dp),fontWeight=FontWeight.Bold)}
  val events=map[LocalDate.parse(selected)].orEmpty();if(events.isEmpty())item{Empty("这一天没有倒数事件")}
  items(events,key={it.id}){e->EventRow(vm,s,e,{nav.navigate(DetailRoute(e.id))})}
 }
}

@Composable private fun ShareScreen(vm:AppViewModel,s:LibraryState,id:String,nav:NavHostController) {
 val e=s.events.find{it.id==id};if(e==null){Empty("事件不存在");return}
 var greeting by rememberSaveable{mutableStateOf(e.greeting.isNotBlank())};var ratio by rememberSaveable{mutableStateOf("3:4")};val busy by vm.busy.collectAsStateWithLifecycle()
 val json=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"json",setOf(id))}}
 val csv=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("text/csv")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"csv",setOf(id))}}
 LazyColumn {
  item { Header("分享这个日子","卡片只包含当前事件，不带子事件和行动记录",{nav.popBackStack()}) }
  item { Hero(vm,e){} }
  item { Section("卡片内容") {
   if(e.greeting.isNotBlank())Toggle("展示事件寄语",greeting,{greeting=it})else Text("寄语为空，导出卡片将突出倒数日期与背景。")
   Options("比例",ratio,listOf("1:1" to "方形","3:4" to "竖版","9:16" to "长图")){ratio=it}
   if(greeting)Text(e.greeting)
   Text("长寄语自动分成多张图，不截断文字。分享前请确认其中没有不想公开的内容。",style=MaterialTheme.typography.bodySmall)
   Button({vm.shareCard(id,greeting,ratio)},enabled=!busy){Text("生成并分享图片")}
  } }
  item { Section("文本分享") {Text("JSON 保留树关系和文字，照片只保留主题回退；CSV 是平面交换，复杂字段会在导入预览中报告。导入的事件是独立副本，不是实时共享。",style=MaterialTheme.typography.bodySmall);Button({json.launch("DateBook-events.json")},enabled=!busy){Text("导出事件及其子树 JSON")};OutlinedButton({csv.launch("DateBook-events.csv")},enabled=!busy){Text("导出当前事件 CSV")}} }
 }
}

@Composable private fun SettingsScreen(vm:AppViewModel,activity:FragmentActivity,nav:NavHostController) {
 val s by vm.library.collectAsStateWithLifecycle()
 val theme by vm.prefs.theme.collectAsStateWithLifecycle("system")
 val monday by vm.prefs.weekMonday.collectAsStateWithLifecycle(true)
 val scope=rememberCoroutineScope()
 var pinDialog by remember{mutableStateOf(false)};var disableLock by remember{mutableStateOf(false)}
 var tagDialog by remember{mutableStateOf(false)}
 var notificationState by remember{mutableStateOf(vm.graph.systems.notificationAllowed())}
 var exactState by remember{mutableStateOf(vm.graph.systems.exactAllowed())}
 val permission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){notificationState=vm.graph.systems.notificationAllowed()}
 val setting=rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()){notificationState=vm.graph.systems.notificationAllowed();exactState=vm.graph.systems.exactAllowed();vm.mutate("已重新检查系统状态"){}}
 LazyColumn {
  item { Header("设置","无需账号，资料只在这部手机。") }
  item { Section("外观与首页") {
   Options("主题",theme,listOf("system" to "跟随系统","light" to "浅色","dark" to "深色")){v->scope.launch{vm.prefs.theme(v)}}
   Toggle("日历一周从周一开始",monday,{v->scope.launch{vm.prefs.weekMonday(v)}})
   Options("首页大卡片",s.home.heroMode,listOf("auto" to "自动最近事件","fixed" to "手动固定")){v->if(v=="fixed"&&s.home.fixedEventId==null)vm.message.value="请在某个事件详情点击‘固定为首页大卡片’"else vm.mutate{vm.graph.service.saveHome(s.home.copy(heroMode=v))}}
   TextButton({tagDialog=true}){Text("管理标签")}
  } }
  item { Section("提醒与系统功能") {
   Text("通知：${if(notificationState)"已允许"else"未允许 / 通知渠道关闭"}")
   Text("精准闹钟：${if(exactState)"可用"else"未允许，将使用普通提醒"}")
   TextButton({if(Build.VERSION.SDK_INT>=33&&!notificationState)permission.launch(Manifest.permission.POST_NOTIFICATIONS)else setting.launch(vm.graph.systems.requestNotificationSettings())}){Text("管理通知权限")}
   TextButton({setting.launch(vm.graph.systems.requestExactSettings())}){Text("管理精准提醒权限")}
   TextButton({vm.mutate("已重新安排提醒并刷新组件") {}}){Text("立即修复提醒 / 刷新组件")}
   Text("桌面长按空白处 → 组件 → 重要的日子，可选择单事件或最近三项。照片、寄语默认不公开；开启应用锁时桌面仅显示安全入口。",style=MaterialTheme.typography.bodySmall)
   Text("关机、强制停止、厂商省电策略可能延迟提醒，普通模式不承诺精确到分钟。没有后台服务器补发消息。",style=MaterialTheme.typography.bodySmall)
  } }
  item { Section("本机隐私") {
   Text("应用锁：${if(vm.graph.lock.enabled)"已开启"else"未开启"}")
   Button({pinDialog=true}){Text(if(vm.graph.lock.enabled)"修改 PIN"else"设置 PIN 与应用锁")}
   if(vm.graph.lock.enabled){OutlinedButton({disableLock=true}){Text("关闭应用锁")};TextButton({vm.graph.lock.lock()}){Text("立即锁定")}}
   Text("这是访问锁，不是数据库加密。没有账号找回 PIN。可使用本机强生物识别，或验证备份后替换全部资料 / 清空本机资料。",style=MaterialTheme.typography.bodySmall)
   Text("本应用不请求网络权限，不部署云数据库，不加入统计、广告或登录 SDK。Android 自动云备份与设备传输备份已排除应用资料；迁移请手动导出。",style=MaterialTheme.typography.bodySmall)
  } }
  item { Section("资料与工具") {
   TextButton({nav.navigate(ToolsRoute)}){Text("导入 / 导出 / 加密备份 / 恢复 / 日期工具")}
   TextButton({nav.navigate(LifecycleRoute("archived"))}){Text("已归档事件")}
   TextButton({nav.navigate(LifecycleRoute("trash"))}){Text("回收站")}
   Text("版本 1.0.0 · ${s.events.size} / 2000 个事件 · ${s.books.size} / 200 个本子",style=MaterialTheme.typography.bodySmall)
   Text("离线农历：lunar-java 1.7.7（MIT），1901–2099。第三方许可见源码中的 THIRD_PARTY_NOTICES.md。",style=MaterialTheme.typography.bodySmall)
  } }
 }
 if(pinDialog)PinDialog(vm,false){pinDialog=false}
 if(disableLock)PinDialog(vm,true){disableLock=false}
 if(tagDialog)TagsDialog(vm,s){tagDialog=false}
}

@Composable private fun PinDialog(vm:AppViewModel,disable:Boolean,dismiss:()->Unit) {
 var pin by remember{mutableStateOf("")};var repeat by remember{mutableStateOf("")};val locked by vm.graph.lock.locked.collectAsStateWithLifecycle()
 AlertDialog(onDismissRequest=dismiss,title={Text(if(disable)"关闭应用锁"else"设置 6–12 位数字 PIN")},text={Column(verticalArrangement=Arrangement.spacedBy(8.dp)){OutlinedTextField(pin,{pin=it},label={Text(if(disable)"当前 PIN"else"新 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword));if(!disable)OutlinedTextField(repeat,{repeat=it},label={Text("重复 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword));Text("没有邮箱或账号找回，请妥善记住。",style=MaterialTheme.typography.bodySmall)}},confirmButton={TextButton({if(!disable&&pin!=repeat)vm.message.value="两次 PIN 不一致"else{val chars=pin.toCharArray();pin="";repeat="";vm.execute("应用锁设置已更新"){try{if(disable)vm.graph.lock.disable(chars)else vm.graph.lock.setPin(chars);vm.graph.systems.refreshWidgets()}finally{chars.fill('\u0000')}};dismiss()}}){Text(if(disable)"验证并关闭"else"保存")}},dismissButton={TextButton({pin="";repeat="";dismiss()}){Text("取消")}})
}

@Composable private fun TagsDialog(vm:AppViewModel,s:LibraryState,dismiss:()->Unit) {
 var value by remember{mutableStateOf("")};var editing by remember{mutableStateOf<Tag?>(null)};var deleting by remember{mutableStateOf<Tag?>(null)}
 AlertDialog(onDismissRequest=dismiss,title={Text("标签管理")},text={Column(Modifier.heightIn(max=460.dp).verticalScroll(rememberScrollState())) {
  Field(if(editing==null)"新标签"else"修改标签",value,{value=it});TextButton({val tag=editing?.copy(name=value)?:Tag(name=value);vm.mutate{vm.graph.service.saveTag(tag)};editing=null;value=""}){Text("保存标签")}
  s.tags.sortedBy{it.name}.forEach{tag->Row(verticalAlignment=Alignment.CenterVertically){Text(tag.name,Modifier.weight(1f));IconButton({editing=tag;value=tag.name}){Icon(Icons.Default.Edit,"修改")};IconButton({deleting=tag}){Icon(Icons.Default.Delete,"删除")}}}
 }},confirmButton={TextButton(dismiss){Text("完成")}})
 if(deleting!=null)Confirm("删除标签？","标签会从所有事件解除，但事件本身不会删除。",{deleting=null}){val id=deleting!!.id;deleting=null;vm.mutate{vm.graph.service.deleteTag(id)}}
}

@Composable private fun LockScreen(vm:AppViewModel,activity:FragmentActivity,recovery:()->Unit) {
 var pin by remember{mutableStateOf("")};var feedback by remember{mutableStateOf("")};var attempts by remember{mutableIntStateOf(0)}
 var waiting by remember{mutableLongStateOf(vm.graph.lock.remainingLockMillis())}
 val scope=rememberCoroutineScope();var working by remember{mutableStateOf(false)}
 LaunchedEffect(attempts){while(true){waiting=vm.graph.lock.remainingLockMillis();if(waiting<=0)break;delay(1000)}}
 Column(Modifier.fillMaxSize().padding(30.dp).verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.Center,horizontalAlignment=Alignment.CenterHorizontally) {
  Icon(Icons.Default.Lock,"应用锁",Modifier.size(48.dp),tint=MaterialTheme.colorScheme.primary);Spacer(Modifier.height(16.dp));Text("把重要的日子留给自己",fontSize=24.sp,fontWeight=FontWeight.SemiBold);Text("请解锁本机资料库",Modifier.padding(vertical=12.dp))
  OutlinedTextField(pin,{pin=it},label={Text("6–12 位 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword),singleLine=true,modifier=Modifier.fillMaxWidth(),enabled=!working&&waiting<=0)
  if(feedback.isNotBlank())Text(feedback,color=MaterialTheme.colorScheme.error)
  if(waiting>0)Text("请 ${((waiting+999)/1000)} 秒后重试")
  Button({working=true;val chars=pin.toCharArray();pin="";scope.launch{try{val ok=withContext(Dispatchers.IO){vm.graph.lock.unlock(chars)};if(!ok){feedback="PIN 不正确或暂时禁止重试";attempts++}}catch(e:Exception){feedback=AppViewModel.friendly(e)}finally{chars.fill('\u0000');working=false}}},Modifier.fillMaxWidth().padding(top=14.dp),enabled=!working&&waiting<=0){Text("解锁")}
  if(vm.graph.lock.error!=null)Text("应用锁验证资料损坏，已安全锁定。只能从备份替换或清空本机资料。",color=MaterialTheme.colorScheme.error)
  val bioAvailable=vm.graph.lock.error==null&&BiometricManager.from(activity).canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)==BiometricManager.BIOMETRIC_SUCCESS
  if(bioAvailable)OutlinedButton({
   val prompt=BiometricPrompt(activity,ContextCompat.getMainExecutor(activity),object:BiometricPrompt.AuthenticationCallback(){override fun onAuthenticationSucceeded(result:BiometricPrompt.AuthenticationResult){super.onAuthenticationSucceeded(result);scope.launch{try{withContext(Dispatchers.IO){vm.graph.lock.biometricUnlock()}}catch(e:Exception){feedback=AppViewModel.friendly(e)}}};override fun onAuthenticationError(code:Int,message:CharSequence){feedback=message.toString()}})
   prompt.authenticate(BiometricPrompt.PromptInfo.Builder().setTitle("解锁重要的日子").setSubtitle("使用本机强生物识别验证身份").setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG).setNegativeButtonText("使用 PIN").build())
  },Modifier.fillMaxWidth()){Text("使用指纹 / 面容验证")}
  TextButton(recovery){Text("忘记 PIN：从备份替换或清空本机资料")}
  Text("没有登录和云端找回；上述恢复会替换或删除当前资料，不会绕过锁展示旧资料。",style=MaterialTheme.typography.bodySmall)
 }
}

@Composable private fun ReplacementPinScreen(vm:AppViewModel) {
 var pin by remember{mutableStateOf("")};var repeat by remember{mutableStateOf("")}
 val busy by vm.busy.collectAsStateWithLifecycle()
 val message by vm.message.collectAsStateWithLifecycle()
 Column(Modifier.fillMaxSize().padding(28.dp),verticalArrangement=Arrangement.Center) {
  Text("资料已安全替换",fontSize=25.sp,fontWeight=FontWeight.Bold)
  Text("请为新的本机资料设置 6–12 位 PIN 后进入。原来的锁不会被用来解锁旧资料。",Modifier.padding(vertical=16.dp))
  OutlinedTextField(pin,{pin=it},label={Text("新 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword),singleLine=true,modifier=Modifier.fillMaxWidth())
  OutlinedTextField(repeat,{repeat=it},label={Text("重复 PIN")},visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.NumberPassword),singleLine=true,modifier=Modifier.fillMaxWidth())
  if(message!=null)Text(message!!,color=MaterialTheme.colorScheme.error)
  Button({if(pin!=repeat)vm.message.value="两次 PIN 不一致"else{val chars=pin.toCharArray();pin="";repeat="";vm.replacementPin(chars)}},enabled=!busy,modifier=Modifier.fillMaxWidth().padding(top=16.dp)){Text("设置 PIN 并进入")}
 }
 BackHandler {vm.message.value="请先完成新 PIN 设置，或关闭应用后再继续"}
}

@Composable private fun ToolsScreen(vm:AppViewModel,modifier:Modifier=Modifier,recovery:Boolean=false,onBack:()->Unit) {
 val s by vm.library.collectAsStateWithLifecycle();val preview by vm.preview.collectAsStateWithLifecycle();val busy by vm.busy.collectAsStateWithLifecycle()
 val candidates by vm.calendarCandidates.collectAsStateWithLifecycle()
 val jobId by vm.currentJob.collectAsStateWithLifecycle()
 var password by remember{mutableStateOf("")};var confirmation by remember{mutableStateOf("")};var clear by remember{mutableStateOf(false)}
 var includeTrash by rememberSaveable{mutableStateOf(false)};var selected by rememberSaveable{mutableStateOf<List<String>>(emptyList())}
 var from by rememberSaveable{mutableStateOf(LocalDate.now().toString())};var to by rememberSaveable{mutableStateOf(LocalDate.now().plusDays(30).toString())}
 val jsonImport=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null)vm.afterUnlock{vm.importText(uri,false)}}
 val csvImport=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null)vm.afterUnlock{vm.importText(uri,true)}}
 val backupImport=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null){val chars=password.toCharArray();password="";vm.readBackup(uri,chars)}}
 val jsonExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"json")}}
 val csvExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("text/csv")){uri->if(uri!=null)vm.afterUnlock{vm.export(uri,"csv")}}
 val backupExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/octet-stream")){uri->if(uri!=null){val chars=password.toCharArray();password="";vm.afterUnlock{vm.export(uri,"backup",password=chars,includeTrash=includeTrash)}}}
 val readPermission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){allowed->if(allowed)vm.afterUnlock{try{vm.calendarRead(LocalDate.parse(from),LocalDate.parse(to))}catch(e:Exception){vm.error(e)}}else vm.message.value="日历权限未授予，不影响本机倒数事件"}
 LazyColumn(modifier) {
  item { Header(if(recovery)"锁定资料恢复"else"资料与日期工具",if(recovery)"只允许验证备份后替换，或明确清空本机"else"导出是独立副本，不会跨设备同步",onBack) }
  if(!recovery)item { Section("文本交换") {
   Text("JSON 保留选择事件的子树、寄语与目标数据，不含照片、提醒和设备设置；CSV 为平面交换。请先预览再导入。",style=MaterialTheme.typography.bodySmall)
   Row{TextButton({jsonImport.launch(arrayOf("application/json","text/plain","application/octet-stream"))},enabled=!busy){Text("导入 JSON")};TextButton({jsonExport.launch("DateBook-events.json")},enabled=!busy){Text("导出全部 JSON")}}
   Row{TextButton({csvImport.launch(arrayOf("text/*","application/octet-stream"))},enabled=!busy){Text("导入 CSV")};TextButton({csvExport.launch("DateBook-events.csv")},enabled=!busy){Text("导出全部 CSV")}}
  } }
  item { Section("完整备份与迁移") {
   Text("备份包括本子、三级事件、寄语、目标、行动、背景及归档原因。不包括应用锁、设备日历关联、桌面组件或系统任务。请把备份复制到另一处安全位置；卸载应用会丢失本机原始资料。",style=MaterialTheme.typography.bodySmall)
   OutlinedTextField(password,{password=it},label={Text("加密密码（恢复时填原密码）")},visualTransformation=PasswordVisualTransformation(),modifier=Modifier.fillMaxWidth(),singleLine=true)
   Text("密码为空时导出明文完整备份。密码无法找回；建议至少 8 个字符。",style=MaterialTheme.typography.bodySmall)
   if(!recovery){Toggle("备份包含回收站",includeTrash,{includeTrash=it});Button({backupExport.launch("DateBook-${LocalDate.now()}.dbkp")},enabled=!busy){Text("生成完整备份")}}
   OutlinedButton({backupImport.launch(arrayOf("*/*"))},enabled=!busy){Text("选择备份并验证")}
  } }
  if(preview!=null)item { val p=preview!!;Section("导入预览 · 尚未修改本机资料") {
   Text("${p.state.books.size} 个本子 / ${p.state.events.size} 个事件 / ${p.state.actions.size} 条行动 / ${p.state.assets.size} 张背景")
   if(p.backup!=null)Text(if(p.backup.encrypted)"已完成加密认证和完整性校验"else"明文备份，已校验完整性")
   p.imported?.issues?.forEach{issue->Text("第 ${issue.line} 行：${issue.code} · ${issue.message}",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.error)}
   p.state.events.take(20).forEach{Text("${it.title} · ${dateText(it.date)} · 第 ${depth(p.state,it.id)} 级",style=MaterialTheme.typography.bodySmall)}
   if(p.state.events.size>20)Text("另有 ${p.state.events.size-20} 项；导入保留全部，不截断。",style=MaterialTheme.typography.bodySmall)
   Text("合并使用独立 ID 副本；相同来源重复导入会跳过已导入项。新导入事项的提醒默认关闭，不补发过去提醒。",style=MaterialTheme.typography.bodySmall)
   if(!recovery)Button({vm.commitPreview(false)},enabled=!busy){Text("确认合并导入")}
   if(p.backup!=null){Field("替换确认：替换本机全部数据",confirmation,{confirmation=it});Text("替换不可撤销，会切换整座资料库，不会混入设备配置。",color=MaterialTheme.colorScheme.error,style=MaterialTheme.typography.bodySmall);OutlinedButton({vm.commitPreview(true,confirmation);confirmation=""},enabled=!busy&&confirmation=="替换本机全部数据"){Text("确认替换本机全部资料")}}
   TextButton({vm.deletePreview();confirmation=""}){Text("取消预览")}
  } }
  if(!recovery)item { Section("从系统日历复制") {
   Field("开始日期",from,{from=it});Field("结束日期（范围不超过 366 天）",to,{to=it})
   TextButton({val context=vm.getApplication<android.app.Application>();if(ContextCompat.checkSelfPermission(context,Manifest.permission.READ_CALENDAR)==PackageManager.PERMISSION_GRANTED)try{vm.calendarRead(LocalDate.parse(from),LocalDate.parse(to))}catch(e:Exception){vm.error(e)}else readPermission.launch(Manifest.permission.READ_CALENDAR)}){Text("读取并预览系统日历")}
   Text("只读取你选择的日期范围；确认后复制为本地独立事件。不会自动双向同步，也不会删除系统日历事项。",style=MaterialTheme.typography.bodySmall)
   candidates.forEach{e->Row(verticalAlignment=Alignment.CenterVertically){Checkbox(e.id in selected,{selected=toggleId(selected,e.id)});Text(e.title+" · "+dateText(e.date),Modifier.weight(1f))}}
   if(candidates.isNotEmpty()){Row{TextButton({selected=candidates.map{it.id}}){Text("全选")};TextButton({selected=emptyList()}){Text("清空选择")}};Button({vm.calendarImport(selected.toSet());selected=emptyList()},enabled=selected.isNotEmpty()&&!busy){Text("复制所选 ${selected.size} 项")}}
  } }
  if(!recovery)item { DateCalculator(vm) }
  if(jobId!=null)item { JobPanel(vm,jobId!!) }
  if(jobId==null&&vm.graph.jobs.latest().isNotEmpty())item { Section("最近文件任务") {vm.graph.jobs.latest().take(8).forEach{job->TextButton({vm.currentJob.value=job.id}){Text("${job.type} · ${job.stage}")}}} }
  item { Section("危险操作") {
   Text("清空会删除这部手机中的全部事件和背景，并重置应用锁；不会删除你保存在其他位置的备份文件。",style=MaterialTheme.typography.bodySmall)
   TextButton({clear=true}){Text("清空本机全部资料",color=MaterialTheme.colorScheme.error)}
  } }
 }
 if(clear)AlertDialog(onDismissRequest={clear=false},title={Text("清空本机全部资料？")},text={Column{Text("不可撤销。输入下列完整文字以确认：清空本机全部数据");Field("确认文字",confirmation,{confirmation=it})}},confirmButton={TextButton({vm.clearAll(confirmation);confirmation="";clear=false},enabled=confirmation=="清空本机全部数据"){Text("永久清空")}},dismissButton={TextButton({clear=false;confirmation=""}){Text("取消")}})
}

@Composable private fun JobPanel(vm:AppViewModel,id:String) {
 val job by vm.graph.jobs.observe(id).collectAsStateWithLifecycle()
 Section("文件任务") {
  Text(job.stage);if(job.total!=null&&job.total!!>0)LinearProgressIndicator(progress={(job.current?:0L).toFloat()/job.total!!},modifier=Modifier.fillMaxWidth())else if(job.state in setOf("preparing","progress","committing"))LinearProgressIndicator(Modifier.fillMaxWidth())
  if(job.state in setOf("preparing","progress"))TextButton({vm.graph.jobs.cancel(id)}){Text("取消任务")}
  if(job.state=="committing")Text("正在原子提交，暂时不能取消。",style=MaterialTheme.typography.bodySmall)
  job.error?.let{Text(it,color=MaterialTheme.colorScheme.error)}
  if(job.state in setOf("completed","failed","canceled"))TextButton({vm.currentJob.value=null}){Text("关闭任务状态")}
 }
}

@Composable private fun DateCalculator(vm:AppViewModel) {
 var a by rememberSaveable{mutableStateOf(LocalDate.now().toString())};var b by rememberSaveable{mutableStateOf(LocalDate.now().plusDays(100).toString())};var n by rememberSaveable{mutableStateOf("100")};var result by rememberSaveable{mutableStateOf("")}
 Section("日期计算器") {
  Field("起始日期 YYYY-MM-DD",a,{a=it});Field("结束日期 YYYY-MM-DD",b,{b=it});Field("增加 / 减少天数",n,{n=it})
  FlowRow {TextButton({try{result="两个日期相差 ${ChronoUnit.DAYS.between(LocalDate.parse(a),LocalDate.parse(b))} 天（不含起始日）"}catch(e:Exception){result="请检查日期格式"}}){Text("计算相差天数")};TextButton({try{val amount=n.toLong();demand(amount in -73050..73050,"DATE_RANGE");result=LocalDate.parse(a).plusDays(amount).toString()}catch(e:Exception){result="请检查日期和天数范围"}}){Text("计算 N 天后")};TextButton({try{val d=LocalDate.parse(a);val lunar=com.nlf.calendar.Solar.fromYmd(d.year,d.monthValue,d.dayOfMonth).lunar;result="农历 ${lunar.year} 年 ${lunar.monthInChinese}月${lunar.dayInChinese}"}catch(e:Exception){result="请检查公历日期"}}){Text("公历转农历")}}
  if(result.isNotBlank())SelectionContainerCompat(result)
 }
}
