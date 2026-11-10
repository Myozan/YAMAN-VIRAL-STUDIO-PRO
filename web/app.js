const $=id=>document.getElementById(id);let jobId=null;
async function health(){try{const r=await fetch("/api/health");const d=await r.json();$("health").textContent=`FFmpeg ${d.ffmpeg?"✓":"×"} · Ollama ${d.ollama?"✓":"×"}`;}catch{$("health").textContent="API bağlantısı yok";}}
health();
async function refreshSystemMetrics(){
 try{const r=await fetch("/api/system/metrics",{cache:"no-store"});const d=await r.json();if(!r.ok||d.error)throw new Error(d.error||"Ölçüm alınamadı");
  $("cpuValue").textContent=d.cpu_percent+"%";$("cpuBar").style.width=d.cpu_percent+"%";
  $("ramValue").textContent=d.ram_percent+"%";$("ramBar").style.width=d.ram_percent+"%";
  $("ramDetail").textContent=(d.ram_used_mb/1024).toFixed(1)+" GB / "+(d.ram_total_mb/1024).toFixed(1)+" GB kullanılıyor";
  if(d.gpu_available===true&&Number.isFinite(Number(d.gpu_percent))){$("gpuValue").textContent=Number(d.gpu_percent).toFixed(0)+"%";$("gpuBar").style.width=Math.max(0,Math.min(100,Number(d.gpu_percent)))+"%";$("gpuDetail").textContent=(d.gpu_name||"NVIDIA GPU")+" · VRAM "+Math.round(d.vram_used_mb||0)+" / "+Math.round(d.vram_total_mb||0)+" MB · "+(d.gpu_temp_c??"--")+"°C";}
  else{$("gpuValue").textContent="N/A";$("gpuBar").style.width="0%";$("gpuDetail").textContent=d.gpu_error||"GPU ölçümü kullanılamıyor";}
 }catch(e){$("cpuValue").textContent="N/A";$("ramDetail").textContent="Sistem ölçümü alınamadı: "+e.message;$("gpuValue").textContent="N/A";$("gpuBar").style.width="0%";$("gpuDetail").textContent="GPU ölçüm hatası: "+e.message;}
}
refreshSystemMetrics();setInterval(refreshSystemMetrics,2000);
function notice(t){$("notice").textContent=t}
function updateProgress(state){
 const box=$("globalProgress");if(box){box.classList.remove("hidden");$("progressStage").textContent=state.stage||"İşlem sürüyor";$("progressPercent").textContent=(state.percent||0)+"%";$("progressFill").style.width=(state.percent||0)+"%";$("progressDetail").textContent=state.status==="completed"?"Tamamlandı":state.status==="failed"?"Hata: "+(state.error||"Bilinmeyen hata"):"Canlı işlem durumu";}
 const stage=(state.stage||"").toLocaleLowerCase("tr-TR");
 let active=1, completed=0, failed=state.status==="failed";
 if(stage.includes("whisper")||stage.includes("konuşma")||stage.includes("transkrips")){active=2;completed=1;}
 else if(stage.includes("aday")||stage.includes("ai editör")||stage.includes("shorts")){active=3;completed=2;}
 else if(stage.includes("kadraj")||stage.includes("render")||stage.includes("platform")||stage.includes("youtube shorts")||stage.includes("instagram reels")||stage.includes("tiktok")){active=4;completed=3;if(stage.includes("tamamlandı")||stage.includes("çıktılar hazır")){active=5;completed=4;}}
 if(state.status==="completed"){if(stage.includes("çıktılar hazır")||stage.includes("dışa aktar")){completed=5;active=5;}else{completed=3;active=3;}}
 for(let i=1;i<=5;i++){
  const card=document.querySelector(`[data-pipeline-step="${i}"]`),label=$("pipelineStatus"+i);if(!card||!label)continue;
  card.classList.toggle("is-done",i<=completed&&!failed);card.classList.toggle("is-active",i===active&&!failed);card.classList.toggle("is-error",failed&&i===active);
  const defaults={1:"Kaynak · YouTube bağlantısı",2:"Whisper · Zaman damgaları",3:"Yerel AI · Kesit seçimi",4:"Kurgu · Dikey kadraj ve altyazı",5:"Çıktı · Shorts / Reels / TikTok"};
  label.textContent=failed&&i===active?"Hata · "+(state.error||state.stage):i<=completed?"Tamamlandı ✓":i===active?(state.stage||"Çalışıyor…"):"Bekliyor · "+defaults[i];
 }
}
async function waitForTask(taskId,onUpdate=null){
 while(true){
  const r=await fetch("/api/tasks/"+encodeURIComponent(taskId),{cache:"no-store"});
  const state=await r.json();if(!r.ok)throw new Error(state.detail||"İşlem durumu okunamadı");
  updateProgress(state);
  if(typeof onUpdate==="function")onUpdate(state);
  if(state.status==="completed")return state.result;
  if(state.status==="failed")throw new Error(state.error||"İşlem başarısız");
  await new Promise(resolve=>setTimeout(resolve,900));
 }
}
function displayShorts(clips){
 const box=$("contentShortsList");if(!box)return;
 box.innerHTML="";
 clips.forEach((clip,index)=>{
  const card=document.createElement("article");card.className="content-short";
  const title=document.createElement("b");title.textContent=(index+1)+". "+(clip.title||"Shorts kesiti");
  const body=document.createElement("p");body.textContent=clip.text||"";
  const meta=document.createElement("small");meta.textContent=clip.start+"s – "+clip.end+"s · "+clip.duration+" sn · AI skor "+clip.score;
  const actions=document.createElement("div");actions.className="actions";
  const render=document.createElement("button");render.textContent="Shorts / Reels / TikTok üret";
  render.onclick=()=>renderClip(clip.id,render);
  const metadata=document.createElement("button");metadata.className="secondary";metadata.textContent="SEO metinleri";
  metadata.onclick=()=>makeMetadata(clip.id,metadata);
  const agents=document.createElement("button");agents.className="secondary";agents.textContent="AI ajanlarını çalıştır";
  agents.onclick=async()=>{
   agents.disabled=true;agents.textContent="Ajanlar çalışıyor…";
   try{
    const r=await fetch("/api/agents/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:jobId,clip_id:clip.id,platforms:["youtube","instagram","tiktok"]})});
    const d=await r.json();if(!r.ok)throw new Error(d.detail||"Ajanlar çalıştırılamadı");
    const pre=document.createElement("pre");pre.textContent=JSON.stringify(d.agents,null,2);card.append(pre);agents.textContent="Ajan raporu hazır ✓";
   }catch(e){agents.disabled=false;agents.textContent="Tekrar dene";notice(e.message);}
  };
  actions.append(render,metadata,agents);card.append(title,body,meta,actions);box.append(card);
 });
}
$("analyze").onclick=async()=>{
 const url=$("url").value.trim();if(!url){notice("Önce bir YouTube bağlantısı gir.");return}
 const b=$("analyze");b.disabled=true;b.textContent="Analiz ediliyor…";
 notice("Analiz arka planda başlatıldı. İlerleme üst çubukta gösteriliyor.");
 try{
  const r=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url,clips:+$("clips").value,min_seconds:20,max_seconds:+$("length").value,language:$("language").value})});
  const queued=await r.json();if(!r.ok)throw new Error(queued.detail||"Analiz başlatılamadı");
  const d=await waitForTask(queued.task_id);jobId=d.job_id;
  $("results").classList.remove("hidden");$("clipslist").innerHTML="";
  d.clips.forEach(c=>{
   const el=document.createElement("article");el.className="clip";
   const left=document.createElement("div");const h=document.createElement("h4");h.textContent=c.title||"Önerilen kesit";
   const p=document.createElement("p");p.textContent=c.text;
   const meta=document.createElement("div");meta.className="meta";meta.textContent=`${c.start}s–${c.end}s · ${c.duration} sn · ${c.reason}`;
   const actions=document.createElement("div");actions.className="actions";
   const render=document.createElement("button");render.textContent="Üç platform için üret";
   render.onclick=()=>renderClip(c.id,render);
   const metadata=document.createElement("button");metadata.className="secondary";metadata.textContent="SEO metinleri üret";
   metadata.onclick=()=>makeMetadata(c.id,metadata);
   const team=document.createElement("button");team.className="secondary";team.textContent="AI ajan ekibini çalıştır";
   team.onclick=async()=>{team.disabled=true;team.textContent="Ajanlar çalışıyor…";try{const r=await fetch("/api/agents/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:jobId,clip_id:c.id,platforms:["youtube","instagram","tiktok"]})});const d=await r.json();if(!r.ok)throw new Error(d.detail);const pre=document.createElement("pre");pre.textContent=JSON.stringify(d.agents,null,2);team.after(pre);team.textContent="Ajan raporu hazır ✓";}catch(e){team.disabled=false;team.textContent="Tekrar dene";notice(e.message)}};
   actions.append(render,metadata,team);left.append(h,p,meta,actions);
   const score=document.createElement("div");score.className="score";score.innerHTML=`${c.score}<small>AI SCORE</small>`;
   el.append(left,score);$("clipslist").append(el);
  });
  displayShorts(d.clips);
  notice(`Tamamlandı · ${d.language} · ${Math.round(d.duration)} saniye · ${d.clips.length} kesit önerildi.`);
  $("results").scrollIntoView({behavior:"smooth"});
 }catch(e){notice("Hata: "+e.message);$("progressStage").textContent="İşlem başarısız";$("progressDetail").textContent=e.message}
 finally{b.disabled=false;b.innerHTML="Analiz et <b>→</b>"}
};
function createMediaCard(item, compact=false){
 const card=document.createElement("article");card.className="media-card"+(compact?" compact":"");
 const head=document.createElement("div");head.className="media-card-head";
 const title=document.createElement("b");title.textContent=item.label||"Üretilen video";
 const badge=document.createElement("span");badge.className="media-platform";badge.textContent=(item.platform||"mp4").toUpperCase();
 head.append(title,badge);
 const video=document.createElement("video");video.className="media-player";video.controls=true;video.preload="metadata";video.playsInline=true;video.src=item.file;
 video.setAttribute("aria-label",(item.label||"Video")+" önizlemesi");
 const info=document.createElement("small");info.className="media-info";
 info.textContent="Klip #"+(item.clip_id??"—")+" · "+(item.size_mb!=null?item.size_mb+" MB":"MP4 video");
 video.addEventListener("loadedmetadata",()=>{if(Number.isFinite(video.duration)){const mm=Math.floor(video.duration/60),ss=Math.floor(video.duration%60);info.textContent+=" · "+mm+":"+String(ss).padStart(2,"0");}});
 video.addEventListener("error",()=>{info.textContent="Video yüklenemedi. Dosya yolu veya MP4 kodlamasını kontrol edin.";});
 const actions=document.createElement("div");actions.className="actions media-actions";
 const download=document.createElement("a");download.className="media-download";download.href=item.file;download.download=item.filename||("clip_"+item.clip_id+"_"+item.platform+".mp4");download.textContent="⬇ MP4 indir";
 const open=document.createElement("a");open.className="media-open";open.href=item.file;open.target="_blank";open.rel="noopener";open.textContent="Yeni sekmede aç";
 actions.append(download,open);card.append(head,video,info,actions);return card;
}
async function loadMediaLibrary(){
 const box=$("mediaLibraryGrid");if(!box)return;
 box.innerHTML='<div class="empty">Video kütüphanesi taranıyor…</div>';
 try{
  const r=await fetch("/api/media/library",{cache:"no-store"});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Medya listesi alınamadı");
  $("mediaCount").textContent=(d.count||0)+" VİDEO";
  box.innerHTML="";
  if(!d.items?.length){box.innerHTML='<div class="empty media-empty">Henüz render edilmiş MP4 yok. Analiz tamamlanması tek başına video üretmez; klip kartında “Üç platform için üret” seçeneğini çalıştır. Her platform tamamlandıkça oynatıcı burada görünür.</div>';return;}
  d.items.forEach(item=>box.append(createMediaCard(item)));
 }catch(e){box.innerHTML='<div class="empty">Video kütüphanesi yüklenemedi: '+e.message+'</div>';}
}
$("refreshMedia")?.addEventListener("click",loadMediaLibrary);
loadMediaLibrary();

async function renderClip(id,b){
 b.disabled=true;b.textContent="Render kuyruğa alınıyor…";
 const box=document.createElement("div");box.className="outputs media-render-results";
 const shown=new Set();
 const appendOutputs=(outputs=[])=>{
  outputs.forEach(o=>{
   const key=o.file||o.filename||o.platform;if(shown.has(key))return;shown.add(key);
   const item={job_id:jobId,clip_id:id,platform:o.platform,label:o.label,file:o.file,filename:o.filename||o.file.split("/").pop(),size_mb:o.size_mb};
   box.append(createMediaCard(item,true));
  });
 };
 try{
  const r=await fetch("/api/render",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:jobId,clip_id:id,platforms:["youtube","instagram","tiktok"],captions:true})});
  const queued=await r.json();if(!r.ok)throw new Error(queued.detail||"Render başlatılamadı");
  b.parentElement.after(box);b.textContent="Render ediliyor…";
  const d=await waitForTask(queued.task_id,state=>appendOutputs(state.outputs));
  appendOutputs(d.outputs);b.textContent="Üretildi ✓";b.disabled=true;
  loadMediaLibrary();
 }catch(e){if(!box.children.length)box.remove();b.textContent="Tekrar dene";b.disabled=false;notice("Render hatası: "+e.message);$("progressStage").textContent="Render başarısız";$("progressDetail").textContent=e.message}
}
async function makeMetadata(id,b){
 b.disabled=true;b.textContent="Metin hazırlanıyor…";
 try{
  const r=await fetch("/api/metadata",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:jobId,clip_id:id,platforms:["youtube","instagram","tiktok"]})});
  const d=await r.json();if(!r.ok)throw new Error(d.detail||"Metin üretilemedi");
  const box=document.createElement("div");box.className="metadata";
  for(const [platform,m] of Object.entries(d.metadata)){const h=document.createElement("b");h.textContent=m.platform.toUpperCase()+" · "+m.title;const pre=document.createElement("pre");pre.textContent=m.description+"\n"+(m.hashtags||[]).join(" ");box.append(h,pre)}
  b.parentElement.after(box);b.textContent="Metinler hazır ✓";
 }catch(e){b.textContent="Tekrar dene";b.disabled=false;notice(e.message)}
}

async function refreshLearning(){try{const r=await fetch("/api/learning");const d=await r.json();$("learningSummary").textContent=`Kayıt: ${d.samples} · Platformlar: ${JSON.stringify(d.platforms)}`;}catch{}}
refreshLearning();
$("saveMetrics").onclick=async()=>{try{const body={clip_fingerprint:$("metricFingerprint").value,platform:$("metricPlatform").value,views:+$("metricViews").value,likes:+$("metricLikes").value,comments:+$("metricComments").value,shares:+$("metricShares").value,avg_watch_seconds:+$("metricWatch").value,video_seconds:+$("metricDuration").value};const r=await fetch("/api/learning/record",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)throw new Error(d.detail);notice(`Kaydedildi · Etkileşim %${(d.engagement_rate*100).toFixed(1)} · İzlenme tutma %${(d.retention_rate*100).toFixed(1)}`);refreshLearning();}catch(e){notice(e.message)}};

// Main navigation: each sidebar item opens a real application workspace.
const pageNames=["studio","content","projects","media","platforms","settings"];
function showPage(name){
 if(!pageNames.includes(name)) name="studio";
 document.querySelectorAll(".page").forEach(x=>x.classList.toggle("active",x.id==="page-"+name));
 document.querySelectorAll("#sidebarNav a").forEach(x=>x.classList.toggle("active",x.dataset.page===name));
 if(name==="projects") loadProjects();
 if(name==="media") loadMediaLibrary();
 if(name==="platforms") loadPlatforms();
 if(name==="settings") loadSettings();
}
document.querySelectorAll("#sidebarNav a").forEach(a=>a.addEventListener("click",e=>{e.preventDefault();showPage(a.dataset.page);}));
document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>showPage(b.dataset.go)));
async function loadProjects(){
 const box=$("projectList");box.innerHTML='<div class="empty">Projeler yükleniyor…</div>';
 try{const r=await fetch("/api/projects");const d=await r.json();
 if(!d.projects.length){box.innerHTML='<div class="empty">Henüz proje yok. Studio bölümünden ilk videonu analiz et.</div>';return;}
 box.innerHTML="";
 d.projects.forEach(p=>{const el=document.createElement("article");el.className="project-row";
 const info=document.createElement("div");const title=document.createElement("b");title.textContent="Proje "+p.job_id;
 const sub=document.createElement("small");sub.textContent=`${p.duration} sn kaynak · ${p.clip_count} kesit · ${p.language}`;
 info.append(title,sub);const actions=document.createElement("div");actions.className="actions";const open=document.createElement("button");open.className="secondary";open.textContent="Klipleri aç";open.onclick=()=>openProject(p.job_id,open);actions.append(open);el.append(info,actions);box.append(el);});
 }catch(e){box.innerHTML='<div class="empty">Proje listesi alınamadı: '+e.message+'</div>';}
}
$("refreshProjects")?.addEventListener("click",loadProjects);
async function openProject(id,b){
 b.disabled=true;b.textContent="Proje yükleniyor…";
 try{
  const r=await fetch("/api/jobs/"+encodeURIComponent(id),{cache:"no-store"});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Proje açılamadı");
  jobId=d.job_id;showPage("studio");$("results").classList.remove("hidden");$("clipslist").innerHTML="";
  d.clips.forEach(c=>{
   const el=document.createElement("article");el.className="clip";
   const left=document.createElement("div");const h=document.createElement("h4");h.textContent=c.title||"Önerilen kesit";
   const p=document.createElement("p");p.textContent=c.text||"";
   const meta=document.createElement("div");meta.className="meta";meta.textContent=c.start+"s–"+c.end+"s · "+c.duration+" sn · "+(c.reason||"Kayıtlı kesit");
   const actions=document.createElement("div");actions.className="actions";
   const render=document.createElement("button");render.textContent="Üç platform için üret";render.onclick=()=>renderClip(c.id,render);
   const metadata=document.createElement("button");metadata.className="secondary";metadata.textContent="SEO metinleri üret";metadata.onclick=()=>makeMetadata(c.id,metadata);
   actions.append(render,metadata);left.append(h,p,meta,actions);
   const score=document.createElement("div");score.className="score";score.innerHTML=(c.score||0)+"<small>AI SCORE</small>";
   el.append(left,score);$("clipslist").append(el);
  });
  displayShorts(d.clips);notice("Kayıtlı proje açıldı. Kesitleri yeniden render edebilir ve oynatabilirsin.");
  $("results").scrollIntoView({behavior:"smooth"});
 }catch(e){notice("Proje açılamadı: "+e.message);}
 finally{b.disabled=false;b.textContent="Klipleri aç";}
}
async function loadPlatforms(){
 const box=$("platformList");box.innerHTML='<div class="empty">Platformlar yükleniyor…</div>';
 try{const r=await fetch("/api/platforms");const d=await r.json();box.innerHTML="";
 Object.entries(d).forEach(([key,p])=>{const el=document.createElement("article");el.className="platform-card";
 const title=document.createElement("h3");title.textContent=p.label;
 const desc=document.createElement("p");desc.textContent=`${p.width} × ${p.height} · En fazla ${p.max_seconds} saniye`;
 const status=document.createElement("span");status.className="state-pill pending";status.textContent="Hesap bağlı değil";
 const note=document.createElement("small");note.textContent="Dışa aktarma profili hazır · OAuth bağlantısı bekleniyor";
 el.append(title,desc,status,note);box.append(el);});
 }catch(e){box.textContent="Platform profilleri yüklenemedi: "+e.message;}
}
async function loadSettings(){
 try{const r=await fetch("/api/settings");const d=await r.json();
 $("settingModel").value=d.ollama_model;$("settingWhisper").value=d.whisper_model;$("settingDevice").value=d.whisper_device;
 $("ollamaSettingStatus").textContent="Ollama adresi: "+d.ollama_url+" · Model: "+d.ollama_model;
 const h=await fetch("/api/health");const healthData=await h.json();
 $("dependencyStatus").innerHTML="";
 [["FFmpeg / FFprobe",healthData.ffmpeg],["Ollama API",healthData.ollama],["Whisper",true]].forEach(([name,ok])=>{const el=document.createElement("div");el.className="dependency";const b=document.createElement("b");b.textContent=name;const s=document.createElement("span");s.className=ok?"ok":"bad";s.textContent=ok?"Hazır":"Eksik";el.append(b,s);$("dependencyStatus").append(el);});
 }catch(e){$("ollamaSettingStatus").textContent="Ayarlar alınamadı: "+e.message;}
}
$("saveSettings")?.addEventListener("click",async()=>{
 const btn=$("saveSettings");btn.disabled=true;btn.textContent="Kaydediliyor…";
 try{const payload={ollama_model:$("settingModel").value.trim(),whisper_model:$("settingWhisper").value,whisper_device:$("settingDevice").value};
 const r=await fetch("/api/settings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
 const d=await r.json();if(!r.ok)throw new Error(d.detail||"Ayarlar kaydedilemedi");
 $("settingsFeedback").textContent="Ayarlar kaydedildi ✓";$("ollamaSettingStatus").textContent="Model tercihi kaydedildi: "+d.settings.ollama_model;
 }catch(e){$("settingsFeedback").textContent=e.message;}finally{btn.disabled=false;btn.textContent="Ayarları kaydet";}
});
