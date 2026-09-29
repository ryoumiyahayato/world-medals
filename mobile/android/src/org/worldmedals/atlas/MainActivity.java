package org.worldmedals.atlas;

import android.app.*;
import android.os.*;
import android.content.*;
import android.content.res.Configuration;
import android.graphics.Color;
import android.net.Uri;
import android.view.*;
import android.webkit.*;
import android.widget.*;
import org.json.JSONObject;
import org.json.JSONArray;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class MainActivity extends Activity {
 private static final String HOST="appassets.androidplatform.net";
 private static final String RELEASES="https://github.com/ryoumiyahayato/world-medals/releases";
 private WebView web;
 private ValueCallback<Uri[]> fileResult;
 private boolean checking=false;
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  if(Build.VERSION.SDK_INT>=30)getWindow().setDecorFitsSystemWindows(false);
  FrameLayout root=new FrameLayout(this); root.setBackgroundColor(Color.rgb(16,29,49));
  root.setOnApplyWindowInsetsListener((v,insets)->{
   if(Build.VERSION.SDK_INT>=30){android.graphics.Insets s=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout()|WindowInsets.Type.ime());v.setPadding(s.left,s.top,s.right,s.bottom);}
   else{v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());}
   return insets.consumeSystemWindowInsets();
  });
  web=new WebView(this);root.addView(web,new FrameLayout.LayoutParams(-1,-1));setContentView(root);
  WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);
  settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
  settings.setSupportZoom(true);settings.setBuiltInZoomControls(true);settings.setDisplayZoomControls(false);
  web.setWebViewClient(new WebViewClient(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
    Uri u=request.getUrl();if(!"https".equals(u.getScheme())||!HOST.equals(u.getHost()))return response(403,"Forbidden",new byte[0],"text/plain");
    String path=u.getPath();if(path==null||path.contains("..")||path.contains("\\"))return response(403,"Forbidden",new byte[0],"text/plain");
    if(path.equals("/"))path="/index.html";
    try{String mime=path.endsWith(".js")?"application/javascript":path.endsWith(".css")?"text/css":path.endsWith(".html")?"text/html":path.endsWith(".json")?"application/json":path.endsWith(".png")?"image/png":path.endsWith(".woff2")?"font/woff2":path.endsWith(".otf")?"font/otf":"image/webp";
     Map<String,String> headers=new HashMap<>();headers.put("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'none'");
     return new WebResourceResponse(mime,"UTF-8",200,"OK",headers,getAssets().open("site"+path));
    }catch(IOException e){return response(404,"Not Found",new byte[0],"text/plain");}
   }
   @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest r){
    Uri u=r.getUrl();if(r.isForMainFrame()&&"medalatlas".equals(u.getScheme())&&"authorize".equals(u.getHost())){UpdateAuth.show(MainActivity.this,()->checkUpdates(true));return true;}if("medalatlas".equals(u.getScheme())&&"updates".equals(u.getHost())){checkUpdates(true);return true;}
    if(r.isForMainFrame()&&"medalatlas".equals(u.getScheme())&&"easter-exit".equals(u.getHost())){finishAndRemoveTask();new Handler(Looper.getMainLooper()).postDelayed(()->android.os.Process.killProcess(android.os.Process.myPid()),200);return true;}
    if("https".equals(u.getScheme())&&HOST.equals(u.getHost()))return false;
    if(r.isForMainFrame()&&("https".equals(u.getScheme())||"http".equals(u.getScheme())))openExternal(u);
    return true;
   }
   @Override public void onPageFinished(WebView view,String url){syncSystemTheme();}
  });
  web.setWebChromeClient(new WebChromeClient(){
   @Override public boolean onShowFileChooser(WebView v,ValueCallback<Uri[]> callback,FileChooserParams params){
    if(fileResult!=null)fileResult.onReceiveValue(null);fileResult=callback;
    Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);intent.setType("image/*");intent.addCategory(Intent.CATEGORY_OPENABLE);
    try{startActivityForResult(intent,30);}catch(ActivityNotFoundException e){fileResult.onReceiveValue(null);fileResult=null;Toast.makeText(MainActivity.this,"未找到图片选择器",Toast.LENGTH_LONG).show();}return true;
   }
  });
  web.loadUrl("https://"+HOST+"/index.html");
  
 }
 private WebResourceResponse response(int status,String reason,byte[] bytes,String mime){return new WebResourceResponse(mime,"UTF-8",status,reason,Collections.emptyMap(),new ByteArrayInputStream(bytes));}
 private void syncSystemTheme(){boolean dark=(getResources().getConfiguration().uiMode&Configuration.UI_MODE_NIGHT_MASK)==Configuration.UI_MODE_NIGHT_YES;web.evaluateJavascript("window.nativeSystemDark="+dark+";if(typeof applyTheme==='function')applyTheme();",null);}
 @Override public void onConfigurationChanged(Configuration c){super.onConfigurationChanged(c);syncSystemTheme();}
 @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==30&&fileResult!=null){fileResult.onReceiveValue(result==RESULT_OK&&data!=null&&data.getData()!=null?new Uri[]{data.getData()}:null);fileResult=null;}}
 private void openExternal(Uri uri){try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(ActivityNotFoundException e){Toast.makeText(this,"未找到浏览器",Toast.LENGTH_LONG).show();}}
 private void message(String title,String text){if(isFinishing()||isDestroyed())return;new AlertDialog.Builder(this).setTitle(title).setMessage(text).setPositiveButton("打开发布页",(d,w)->openExternal(Uri.parse(RELEASES))).setNegativeButton("关闭",null).show();}
 private final Handler updateHandler=new Handler(Looper.getMainLooper());
 private final Runnable updatePoll=new Runnable(){public void run(){checkUpdates(false);updateHandler.postDelayed(this,15*60*1000L);}};
 @Override protected void onResume(){super.onResume();updateHandler.removeCallbacks(updatePoll);updateHandler.post(updatePoll);}
 @Override protected void onPause(){updateHandler.removeCallbacks(updatePoll);super.onPause();}
 private void updateStatus(String text){web.evaluateJavascript("(()=>{const e=document.getElementById('update-status');if(e)e.textContent="+JSONObject.quote(text)+";})()",null);}
 private void checkUpdates(boolean manual){
  long now=System.currentTimeMillis(),last=getPreferences(0).getLong("lastAttempt",0);
  if(checking||(!manual&&now>=last&&now-last<15*60*1000L))return;
  checking=true;getPreferences(0).edit().putLong("lastAttempt",now).apply();
  updateStatus("正在检查 GitHub 更新…");
  new Thread(()->{
   try{
    String current=getPackageManager().getPackageInfo(getPackageName(),0).versionName;
    String token=UpdateAuth.read(this);String best=null; boolean complete=false;
    for(int page=1;page<=10;page++){
     HttpURLConnection connection=(HttpURLConnection)new URL("https://api.github.com/repos/ryoumiyahayato/world-medals/releases?per_page=100&page="+page).openConnection();
     try{
      connection.setInstanceFollowRedirects(false);if(!token.isEmpty())connection.setRequestProperty("Authorization","Bearer "+token);connection.setConnectTimeout(12000);connection.setReadTimeout(12000);connection.setRequestProperty("Accept","application/vnd.github+json");connection.setRequestProperty("User-Agent","WorldMedals-Android");
      int status=connection.getResponseCode();
      if(status!=200){
       String reason=status==401?"GitHub 授权已失效，请在设置中重新填写令牌。":status==404?"无法读取私有仓库的更新。请在浏览器登录 GitHub 后查看发布页；尚未确认是否为最新版本。":status==403||status==429?"GitHub 暂时限制了请求，请稍后重试；尚未确认是否为最新版本。":"更新服务返回 HTTP "+status+"；尚未确认是否为最新版本。";
       runOnUiThread(()->{updateStatus(reason);if(manual)message("未能检查更新",reason);});return;
      }
      ByteArrayOutputStream buffer=new ByteArrayOutputStream();try(InputStream in=connection.getInputStream()){byte[] chunk=new byte[8192];int n;while((n=in.read(chunk))!=-1){if(buffer.size()+n>2*1024*1024)throw new IOException("Response too large");buffer.write(chunk,0,n);}}
      JSONArray releases=new JSONArray(buffer.toString("UTF-8"));
      for(int i=0;i<releases.length();i++){
       JSONObject release=releases.getJSONObject(i);String tag=release.optString("tag_name");
       if(release.optBoolean("draft")||!UpdateVersion.valid(tag))continue;
       boolean apk=false;JSONArray assets=release.optJSONArray("assets");
       if(assets!=null)for(int j=0;j<assets.length();j++){JSONObject asset=assets.getJSONObject(j);if(asset.optString("name").equals("world-medals-"+tag.substring(8)+".apk")&&asset.optLong("size")>0&&"uploaded".equals(asset.optString("state")))apk=true;}
       if(apk&&(best==null||UpdateVersion.newer(tag,best)))best=tag;
      }
      if(releases.length()<100){complete=true;break;}
     }finally{connection.disconnect();}
    }
    if(!complete)throw new IOException("Release pagination incomplete");
    final String tag=best;
    String result=tag==null?"尚无已发布且含 APK 的手机版本；不能确认当前版本是否最新。":UpdateVersion.newer(tag,current)?"发现新版本 "+tag:"已检查：当前版本 "+current+"，没有更高的已发布手机版本。";
    runOnUiThread(()->{
     updateStatus(result);
     if(tag!=null&&UpdateVersion.newer(tag,current)){
      if(manual||!tag.equals(getPreferences(0).getString("notifiedRelease",""))){getPreferences(0).edit().putString("notifiedRelease",tag).apply();message("发现新版本 "+tag,"请在发布页下载新版 APK，并由 Android 确认安装。同一签名更新会保留收藏与设置。");}
     }else if(manual)message("检查更新",result);
    });
   }catch(Exception e){runOnUiThread(()->{String text="网络或更新数据异常，未能确认最新版本。请稍后重试。";updateStatus(text);if(manual)message("暂时无法检查更新",text);});}
   finally{runOnUiThread(()->checking=false);}
  },"release-check").start();
 }
 @Override public void onBackPressed(){web.evaluateJavascript("(()=>{const d=document.querySelector('dialog[open]');if(d){d.close();return true;}const s=document.getElementById('splash');if(s&&!s.hidden){finishSplash();return true;}if(document.body.classList.contains('book-is-open')&&window.closeReadingBook){closeReadingBook();return true;}if(typeof state!=='undefined'&&(state.tab!=='catalog'||document.body.classList.contains('book-is-open'))){document.getElementById('query').value='';document.getElementById('volume').value='';if(window.resetBook)resetBook();navigate('catalog');return true;}return false;})()",value->{if(!"true".equals(value))super.onBackPressed();});}
 @Override protected void onDestroy(){if(fileResult!=null)fileResult.onReceiveValue(null);web.destroy();super.onDestroy();}
}



