const $=id=>document.getElementById(id);let jobId=null;
async function health(){try{const r=await fetch("/api/health");const d=await r.json();$("health").textContent=`FFmpeg ${d.ffmpeg?"✓":"×"} · Ollama ${d.ollama?"✓":"×"}`;}catch{$("health").textContent="API bağlantısı yok";}}
health();
function setGauge(id,value){
 const el=$(id);if(!el)return;
 const v=Math.max(0,Math.min(100,Number(value)||0));
 el.style.setProperty("--value",v.toFixed(1));
}
async function refreshSystemMetrics(){
 try{
  const r=await fetch("/api/system/metrics",{cache:"no-store"}),d=await r.json();
  if(!r.ok||d.error)throw new Error(d.error||"Sistem ölçümü alınamadı");
  $("cpuValue").textContent=Math.round(d.cpu_percent)+"%";setGauge("cpuGauge",d.cpu_percent);
  $("cpuTemp").textContent=d.cpu_temp_c===null||d.cpu_temp_c===undefined?"N/A":Number(d.cpu_temp_c).toFixed(1)+" °C";
  $("cpuTempSource").textContent=d.cpu_temp_c===null?"LibreHardwareMonitor / OpenHardwareMonitor gerekli":(d.cpu_temp_source||"CPU sensörü");
  $("cpuName").textContent=d.cpu_name||"CPU";
  $("cpuClock").textContent=d.cpu_clock_mhz?Number(d.cpu_clock_mhz).toLocaleString("tr-TR")+" MHz":"Anlık saat hızı alınamadı";
  $("cpuCores").textContent=String(d.cpu_cores == null ? "--" : d.cpu_cores)+" / "+String(d.cpu_threads == null ? "--" : d.cpu_threads);
  $("cpuGaugeInfo").textContent=String(d.cpu_cores == null ? "--" : d.cpu_cores)+"C / "+String(d.cpu_threads == null ? "--" : d.cpu_threads)+"T";
  $("gpuTemp").textContent=d.gpu_available&&Number.isFinite(Number(d.gpu_temp_c))?Number(d.gpu_temp_c).toFixed(1)+" °C":"N/A";
  $("gpuTempSource").textContent=d.gpu_available?"NVIDIA GPU sensörü":"GPU sıcaklık sensörü yok";
  $("ramValue").textContent=Math.round(d.ram_percent)+"%";setGauge("ramGauge",d.ram_percent);
  $("ramDetail").textContent=(d.ram_used_mb/1024).toFixed(1)+" GB / "+(d.ram_total_mb/1024).toFixed(1)+" GB kullanılıyor";
  if(d.gpu_available===true&&Number.isFinite(Number(d.gpu_percent))){
   $("gpuValue").textContent=Math.round(d.gpu_percent)+"%";setGauge("gpuGauge",d.gpu_percent);
   $("gpuDetail").textContent=(d.gpu_name||"NVIDIA GPU")+" \u00b7 "+Math.round(d.gpu_temp_c == null ? 0 : d.gpu_temp_c)+"\u00b0C";
   const vp=d.vram_total_mb?d.vram_used_mb/d.vram_total_mb*100:0;
   $("vramValue").textContent=Math.round(vp)+"%";setGauge("vramGauge",vp);
   $("vramDetail").textContent=Math.round(d.vram_used_mb)+" / "+Math.round(d.vram_total_mb)+" MB";
  }else{
   $("gpuValue").textContent="N/A";setGauge("gpuGauge",0);$("gpuDetail").textContent=d.gpu_error||"GPU telemetrisi kullanılamıyor";
   $("vramValue").textContent="N/A";setGauge("vramGauge",0);$("vramDetail").textContent="VRAM verisi yok";
  }
 }catch(e){
  $("cpuValue").textContent="N/A";$("gpuValue").textContent="N/A";$("ramValue").textContent="N/A";$("vramValue").textContent="N/A";
  ["cpuGauge","gpuGauge","ramGauge","vramGauge"].forEach(id=>setGauge(id,0));
  $("ramDetail").textContent="Ölçüm alınamadı: "+e.message;
 }
}
refreshSystemMetrics();setInterval(refreshSystemMetrics,2000);

// Theme preference is stored locally in this browser only.
function applyTheme(theme){
 const allowed=["dark","light","ocean"],chosen=allowed.includes(theme)?theme:"dark";
 document.documentElement.dataset.theme=chosen;
 const select=$("themeSelect");if(select)select.value=chosen;
 try{localStorage.setItem("yaman-viral-theme",chosen);}catch{}
}
$("themeSelect")?.addEventListener("change",e=>applyTheme(e.target.value));
let savedTheme="dark";try{savedTheme=localStorage.getItem("yaman-viral-theme")||"dark";}catch{}
applyTheme(savedTheme);
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

async function executeAgentTeam(job,clip,button,anchor){
 button.disabled=true;button.textContent="Ajanlar gorev aldi...";
 const pending=document.createElement("section");pending.className="agent-report";
 const h=document.createElement("div");h.className="agent-report-head";
 const name=document.createElement("b");name.textContent="AI ajan ekibi \u00b7 Gorev kuyrugu";
 const state=document.createElement("small");state.textContent="8 uzman ajan hazirlaniyor...";
 h.append(name,state);pending.append(h);
 const list=document.createElement("div");list.className="agent-live-list";
 const agentLabels=[["viral-strategist","Viral Stratejist"],["hook-writer","Hook & Acilis Yazari"],["editor-director","Kurgu Yonetmeni"],["seo-specialist","SEO & Dagitim Uzmani"],["claim-reviewer","Icerik Risk Denetcisi"],["caption-qa","Altyazi Kalite Kontrolu"],["clip-qa","Kesit Teknik Kontrolu"],["publishing-coordinator","Yayin Koordinatoru"]];
 agentLabels.forEach(([id,label],i)=>{
  const row=document.createElement("div");row.className="agent-live-row";row.dataset.agentId=id;
  const n=document.createElement("b");n.textContent=String(i+1).padStart(2,"0")+" \u00b7 "+label;
  const st=document.createElement("span");st.className="agent-status queued";st.textContent="Sirada";
  row.append(n,st);list.append(row);
 });
 pending.append(list);anchor.after(pending);
 try{
  const r=await fetch("/api/agents/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:job,clip_id:clip,platforms:["youtube","instagram","tiktok"]})});
  const q=await r.json();if(!r.ok)throw new Error(q.detail||"Ajan gorevi baslatilamadi");
  state.textContent="Ajanlar calisiyor \u00b7 Gorev "+q.task_id;
  const report=await waitForTask(q.task_id,task=>{
   if(task.agent_statuses){
    Object.entries(task.agent_statuses).forEach(([id,status])=>{
     const row=list.querySelector('[data-agent-id="'+id+'"]');if(!row)return;
     const badge=row.querySelector(".agent-status");badge.className="agent-status "+status;
     badge.textContent=status==="completed"?"Tamamland\u0131":"\u00c7al\u0131\u015f\u0131yor";
    });
    state.textContent=(task.completed_agents||0)+"/8 ajan tamamlandi \u00b7 "+(task.stage||"Calisiyor");
   }
  });
  pending.replaceWith(renderAgentReport(report));
  button.textContent="Ajan raporu hazir";
 }catch(e){
  state.textContent="Gorev basarisiz";
  const err=document.createElement("small");err.className="agent-error";err.textContent=e.message;pending.append(err);
  button.disabled=false;button.textContent="Tekrar calistir";notice("Ajan hatasi: "+e.message);
 }
}

function renderAgentReport(payload){
 const wrap=document.createElement("section");wrap.className="agent-report";
 const head=document.createElement("div");head.className="agent-report-head";
 const title=document.createElement("b");title.textContent="AI ajan raporu";
 const summary=payload.summary||{};
 const stats=document.createElement("small");
 stats.textContent=(summary.completed||0)+" başarılı · "+(summary.fallback||0)+" yedek · "+(summary.failed||0)+" hata";
 head.append(title,stats);wrap.append(head);
 (Array.isArray(payload.agents)?payload.agents:[]).forEach(agent=>{
  const details=document.createElement("details");details.className="agent-report-item";
  const summaryEl=document.createElement("summary");
  const name=document.createElement("b");name.textContent=agent.agent||agent.id||"AI ajan";
  const status=document.createElement("span");status.className="agent-status "+(agent.status||"unknown");
  status.textContent=agent.status==="completed"?"Tamamlandı":agent.status==="fallback"?"Yedek sonuç":agent.status==="failed"?"Hata":"Bekliyor";
  const timing=document.createElement("small");timing.textContent=(agent.duration_ms||0)+" ms";
  summaryEl.append(name,status,timing);
  const role=document.createElement("p");role.textContent=agent.role||"";
  const pre=document.createElement("pre");pre.textContent=JSON.stringify(agent.result||{},null,2);
  details.append(summaryEl,role,pre);
  if(agent.error){const err=document.createElement("small");err.className="agent-error";err.textContent="Not: "+agent.error;details.append(err);}
  wrap.append(details);
 });
 if(!payload.agents?.length){const empty=document.createElement("p");empty.textContent="Ajan raporu bulunamadı.";wrap.append(empty);}
 return wrap;
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
  agents.onclick=()=>executeAgentTeam(jobId,clip.id,agents,card);
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
  const d=await waitForTask(queued.task_id);jobId=d.job_id;showTranscript(d.transcript||[]);revealSummaryPanel();
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
   team.onclick=()=>executeAgentTeam(jobId,c.id,team,el);
   actions.append(render,metadata,team);left.append(h,p,meta,actions);
   const score=document.createElement("div");score.className="score";score.innerHTML=`${c.score}<small>AI SCORE</small>`;
   el.append(left,score);$("clipslist").append(el);
  });
  displayShorts(d.clips);
  notice(`Tamamlandı · ${d.language} · ${Math.round(d.duration)} saniye · ${d.clips.length} kesit önerildi.`);
  $("results").scrollIntoView({behavior:"smooth"});
 }catch(e){notice("Hata: "+e.message);$("progressStage").textContent="İşlem başarısız";$("progressDetail").textContent=e.message}
 finally{b.disabled=false;b.innerHTML="Analiz et <b>â†’</b>"}
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
 info.textContent="Klip #"+(item.clip_id == null ? "\u2014" : item.clip_id)+" \u00b7 "+(item.size_mb!=null?item.size_mb+" MB":"MP4 video");
 video.addEventListener("loadedmetadata",()=>{if(Number.isFinite(video.duration)){const mm=Math.floor(video.duration/60),ss=Math.floor(video.duration%60);info.textContent+=" · "+mm+":"+String(ss).padStart(2,"0");}});
 video.addEventListener("error",()=>{info.textContent="Video yüklenemedi. Dosya yolu veya MP4 kodlamasını kontrol edin.";});
 const actions=document.createElement("div");actions.className="actions media-actions";
 const download=document.createElement("a");download.className="media-download";download.href=item.file;download.download=item.filename||("clip_"+item.clip_id+"_"+item.platform+".mp4");download.textContent="â¬‡ MP4 indir";
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
  if(!d.items?.length){box.textContent="Hen\u00fcz render edilmi\u015f MP4 yok. Analiz tamamland\u0131ktan sonra klip kart\u0131ndan platform videolar\u0131n\u0131 \u00fcretin; haz\u0131r dosyalar burada listelenir.";return;}
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
  jobId=d.job_id;showPage("studio");revealSummaryPanel();$("results").classList.remove("hidden");$("clipslist").innerHTML="";
  try{const sr=await fetch("/api/summary/"+encodeURIComponent(jobId));if(sr.ok)showSummaryResult(await sr.json());}catch{}
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
 const box=$("platformList");if(!box)return;box.innerHTML='<div class="empty">Platform profilleri y\u00fckleniyor\u2026</div>';
 try{const r=await fetch("/api/platforms",{cache:"no-store"}),d=await r.json();if(!r.ok)throw new Error(d.detail||"Profiller al\u0131namad\u0131");box.innerHTML="";
 const labels={youtube:"YouTube Shorts",instagram:"Instagram Reels",tiktok:"TikTok"};
 Object.entries(d).forEach(([key,p])=>{
  const card=document.createElement("article");card.className="platform-card";
  const head=document.createElement("div");head.className="platform-card-head";
  const title=document.createElement("h3");title.textContent=labels[key]||p.label;
  const status=document.createElement("span");status.className="state-pill pending";status.textContent="D\u0131\u015fa aktarma haz\u0131r";head.append(title,status);
  const desc=document.createElement("p");desc.textContent="Bu profil render s\u0131ras\u0131nda kullan\u0131lacak. Hesaba otomatik yay\u0131n ba\u011flant\u0131s\u0131 ayr\u0131 OAuth kurulumu gerektirir.";
  const fields=document.createElement("div");fields.className="platform-profile-fields";
  const makeField=(labelText,control)=>{const wrap=document.createElement("label");wrap.className="profile-field";const label=document.createElement("span");label.textContent=labelText;wrap.append(label,control);fields.append(wrap);};
  const ratio=document.createElement("select");[["9:16","Dikey \u00b7 9:16"],["1:1","Kare \u00b7 1:1"],["16:9","Yatay \u00b7 16:9"]].forEach(([v,t])=>{const o=document.createElement("option");o.value=v;o.textContent=t;ratio.append(o)});ratio.value=p.aspect_ratio||"9:16";
  const resolution=document.createElement("select");[1080,720].forEach(v=>{const o=document.createElement("option");o.value=String(v);o.textContent=v+"p";resolution.append(o)});resolution.value=String(p.width===720?720:1080);
  const max=document.createElement("select");[15,30,60,90,120,180].forEach(v=>{const o=document.createElement("option");o.value=String(v);o.textContent=v+" saniye";max.append(o)});max.value=String(p.max_seconds);
  makeField("Video oran\u0131",ratio);makeField("\u00c7\u00f6z\u00fcn\u00fcrl\u00fck",resolution);makeField("Azami s\u00fcre",max);
  const save=document.createElement("button");save.className="secondary profile-save";save.textContent="Profili kaydet";
  const feedback=document.createElement("small");feedback.className="profile-feedback";feedback.textContent="Mevcut \u00e7\u0131kt\u0131: "+p.width+" \u00d7 "+p.height+" \u00b7 "+p.max_seconds+" sn";
  save.addEventListener("click",async()=>{save.disabled=true;save.textContent="Kaydediliyor\u2026";try{const response=await fetch("/api/platforms/profile",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({platform:key,aspect_ratio:ratio.value,resolution:Number(resolution.value),max_seconds:Number(max.value)})});const result=await response.json();if(!response.ok)throw new Error(result.detail||"Profil kaydedilemedi");feedback.textContent="Kaydedildi: "+result.width+" \u00d7 "+result.height+" \u00b7 "+result.max_seconds+" sn";status.textContent="Profil kaydedildi";status.className="state-pill";}catch(e){feedback.textContent=e.message;}finally{save.disabled=false;save.textContent="Profili kaydet";}});
  card.append(head,desc,fields,save,feedback);box.append(card);
 });
 }catch(e){box.textContent="Platform profilleri y\u00fcklenemedi: "+e.message;}
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

// Local Downloads scanner and Whisper transcription
let latestTranscriptText="";
function showTranscript(segments){
 latestTranscriptText=(segments||[]).map(s=>"["+Number(s.start).toFixed(2)+" - "+Number(s.end).toFixed(2)+"] "+(s.text||"")).join("\n");
 const panel=$("transcriptPanel"),pre=$("transcriptText");
 if(panel&&pre){pre.textContent=latestTranscriptText||"Konuşma algılanamadı.";panel.classList.remove("hidden");}
}
$("downloadTranscript")?.addEventListener("click",()=>{
 const blob=new Blob([latestTranscriptText],{type:"text/plain;charset=utf-8"});
 const u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download="yaman-transkript.txt";a.click();URL.revokeObjectURL(u);
});
function revealSummaryPanel(){
 const panel=$("summaryPanel");
 if(panel){panel.classList.remove("hidden");$("summaryFeedback").textContent="Video analiz edildi. \\u00d6zet s\u00fcresini se\u00e7ip ak\u0131ll\u0131 \u00f6zet videosu olu\u015fturabilirsin.";}
}
function showSummaryResult(data){
 const box=$("summaryResult");box.innerHTML="";box.classList.remove("hidden");
 const title=document.createElement("h3");title.textContent=data.title||"Video \u00f6zeti";
 const desc=document.createElement("p");desc.textContent=data.summary||"";
 const points=document.createElement("ul");(data.key_points||[]).forEach(x=>{const li=document.createElement("li");li.textContent=x;points.append(li);});
 const moments=document.createElement("div");moments.className="summary-moments";
 (data.moments||[]).forEach((m,i)=>{const row=document.createElement("div");row.className="summary-moment";row.textContent=(i+1)+". "+Number(m.start).toFixed(1)+"s - "+Number(m.end).toFixed(1)+"s \u00b7 "+(m.reason||"\u00d6nemli an");moments.append(row);});
 const video=document.createElement("video");video.className="summary-player";video.controls=true;video.preload="metadata";video.src=data.output.file;
 const actions=document.createElement("div");actions.className="actions";
 const download=document.createElement("a");download.className="summary-download";download.href=data.output.file;download.download=data.output.filename||"summary_video.mp4";download.textContent="\u00d6zet MP4 indir";
 const method=document.createElement("small");method.className="muted";method.textContent="AI y\u00f6ntemi: "+(data.method||"Yerel transkript analizi")+" \u00b7 "+data.output.size_mb+" MB";
 actions.append(download,method);box.append(title,desc,points,moments,video,actions);
}
async function generateSummaryVideo(){
 if(!jobId){$("summaryFeedback").textContent="\u00d6nce bir video analiz et.";return;}
 const button=$("generateSummary");button.disabled=true;button.textContent="\u00d6zet haz\u0131rlan\u0131yor...";
 $("summaryFeedback").textContent="Transkript \u00f6zetleniyor, \u00f6nemli anlar se\u00e7iliyor ve MP4 haz\u0131rlan\u0131yor.";
 try{
  const r=await fetch("/api/summary/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:jobId,target_seconds:+$("summaryLength").value})});
  const q=await r.json();if(!r.ok)throw new Error(q.detail||"\u00d6zet video ba\u015flat\u0131lamad\u0131");
  const data=await waitForTask(q.task_id,task=>{$("summaryFeedback").textContent=(task.stage||"\u00d6zet haz\u0131rlan\u0131yor")+" \u00b7 "+(task.percent||0)+"%";});
  showSummaryResult(data);$("summaryFeedback").textContent="\u00d6zet video ba\u015far\u0131yla olu\u015fturuldu.";loadMediaLibrary();
 }catch(e){$("summaryFeedback").textContent="\u00d6zet video hatas\u0131: "+e.message;notice("\u00d6zet video hatas\u0131: "+e.message);}
 finally{button.disabled=false;button.textContent="Tekrar \u00f6zet olu\u015ftur";}
}
$("generateSummary")?.addEventListener("click",generateSummaryVideo);

async function scanDownloads(){
 const box=$("downloadsList");if(!box)return;box.innerHTML='<div class="empty">İndirilenler taranıyor…</div>';
 try{
  const r=await fetch("/api/local/videos",{cache:"no-store"}),d=await r.json();if(!r.ok)throw new Error(d.detail||"Klasör taranamadı");
  $("downloadsFolder").textContent=d.folder||"";box.innerHTML="";
  if(!d.items?.length){box.innerHTML='<div class="empty">Desteklenen video bulunamadı.</div>';return;}
  d.items.forEach(item=>{
   const row=document.createElement("article");row.className="download-item";
   const info=document.createElement("div"),name=document.createElement("b"),meta=document.createElement("small");
   name.textContent=item.filename;meta.textContent=item.size_mb+" MB";info.append(name,meta);
   const btn=document.createElement("button");btn.textContent="Transkribe et ve analiz et";
   btn.onclick=()=>analyzeLocalVideo(item.filename,btn);row.append(info,btn);box.append(row);
  });
 }catch(e){box.innerHTML='<div class="empty">Tarama hatası: '+e.message+'</div>';}
}
$("scanDownloads")?.addEventListener("click",scanDownloads);
async function analyzeLocalVideo(filename,button){
 button.disabled=true;button.textContent="Analiz ediliyor…";notice("Yerel video kopyalanıyor ve Whisper transkripsiyonu başlatılıyor.");
 try{
  const r=await fetch("/api/analyze/local",{method:"POST",headers:{"Content-Type":"application/json"},
   body:JSON.stringify({filename,clips:+$("clips").value,min_seconds:20,max_seconds:+$("length").value,language:$("language").value})});
  const q=await r.json();if(!r.ok)throw new Error(q.detail||"Analiz başlatılamadı");
  const d=await waitForTask(q.task_id);jobId=d.job_id;showTranscript(d.transcript||[]);revealSummaryPanel();
  $("results").classList.remove("hidden");displayShorts(d.clips);
  notice("Tamamlandı · "+d.language+" · "+Math.round(d.duration)+" saniye · "+d.clips.length+" kesit önerildi.");
  $("results").scrollIntoView({behavior:"smooth"});
 }catch(e){notice("Yerel video hatası: "+e.message);}
 finally{button.disabled=false;button.textContent="Tekrar analiz et";}
}
