const $=id=>document.getElementById(id);let jobId=null;
const UI_TEXT={
 tr:{
  "nav.studio":"Studio","nav.content":"İçerik üretimi","nav.projects":"Projeler","nav.media":"Video kütüphanesi","nav.platforms":"Platform profilleri","nav.settings":"Ayarlar",
  "appearance.label":"G\u00d6R\u00dcN\u00dcM TEMASI","language.label":"ARAY\u00dcZ D\u0130L\u0130","local.name":"LOCAL AI ENGINE","local.info":"Veriler bilgisayar\u0131nda i\u015flenir",
  "studio.title":"\u0130\u00e7eri\u011fini \u00e7o\u011falt.","studio.subtitle":"Uzun videolar\u0131 analiz et, g\u00fc\u00e7l\u00fc anlar\u0131 se\u00e7 ve t\u00fcm dikey platformlara haz\u0131rla.","studio.newProject":"Yeni video projesi","studio.youtubeUrl":"YouTube video ba\u011flant\u0131s\u0131","studio.analyze":"Analiz et","studio.downloads":"\u0130ndirilen videolar","studio.scan":"\u0130ndirilenler klas\u00f6r\u00fcn\u00fc tara","studio.clipCount":"Short adedi","studio.speechLanguage":"Konu\u015fma dili",
  "projects.title":"Projeler","media.title":"Video k\u00fct\u00fcphanesi","platforms.title":"Platform profilleri","settings.title":"Ayarlar","settings.localAI":"Yerel AI motoru","settings.whisper":"Whisper transkripsiyon","settings.languageTitle":"Dil ve yerelle\u015ftirme","settings.languageDescription":"Uygulama aray\u00fcz\u00fcn\u00fcn dilini se\u00e7. Tercihin bu taray\u0131c\u0131da saklan\u0131r.","settings.languageNote":"Dil tercihi an\u0131nda uygulan\u0131r; uygulamay\u0131 yeniden ba\u015flatman gerekmez.",
  "content.title":"\u0130\u00e7erik \u00fcretimi","content.subtitle":"Kesitleri olu\u015ftur, d\u00fczenle, SEO metinlerini haz\u0131rla ve d\u0131\u015fa aktar.","projects.subtitle":"Diskte saklanan analiz projeleri; uygulama yeniden ba\u015flasa da klipleri tekrar a\u00e7abilirsin.","media.subtitle":"\u00dcretilen Shorts, Reels ve TikTok videolar\u0131n\u0131 do\u011frudan Studio i\u00e7inde izle.","platforms.subtitle":"D\u0131\u015fa aktarma ayarlar\u0131n\u0131 d\u00fczenle, geli\u015ftirici bilgilerini kaydet ve resm\u00ee OAuth ile hesaplar\u0131n\u0131 ba\u011fla.","settings.subtitle":"Yerel AI motoru ve transkripsiyon tercihlerini yap\u0131land\u0131r.","tasks.title":"Kal\u0131c\u0131 g\u00f6rev ge\u00e7mi\u015fi","tasks.subtitle":"\u00c7ok ajanl\u0131 g\u00f6revler, ilerleme olaylar\u0131, iptal ve yeniden deneme kay\u0131tlar\u0131.","tasks.refresh":"Ge\u00e7mi\u015fi yenile",
  "metric.gpu":"GPU KULLANIMI","metric.cpu":"\u0130\u015eLEMC\u0130 KULLANIMI","metric.ram":"BELLEK","metric.vram":"GPU BELLE\u011e\u0130"
 },
 en:{
  "nav.studio":"\u25c8\u3000Studio","nav.content":"\u25a3\u3000Content","nav.projects":"\u25f7\u3000Projects","nav.media":"\u25b6\u3000Media library","nav.platforms":"\u25a4\u3000Platform profiles","nav.settings":"\u2699\u3000Settings",
  "appearance.label":"APPEARANCE","language.label":"INTERFACE LANGUAGE","local.name":"LOCAL AI ENGINE","local.info":"Your data is processed on this computer",
  "studio.title":"Create more from every video.","studio.subtitle":"Analyze long videos, find the strongest moments and prepare vertical content for every platform.","studio.newProject":"New video project","studio.youtubeUrl":"YouTube video URL","studio.analyze":"Analyze","studio.downloads":"Downloaded videos","studio.scan":"Scan Downloads folder","studio.clipCount":"Number of Shorts","studio.speechLanguage":"Speech language",
  "projects.title":"Projects","media.title":"Video library","platforms.title":"Platform profiles","settings.title":"Settings","settings.localAI":"Local AI engine","settings.whisper":"Whisper transcription","settings.languageTitle":"Language & localization","settings.languageDescription":"Choose the application interface language. Your preference is saved in this browser.","settings.languageNote":"Your language preference is applied immediately; no restart is required.",
  "content.title":"Content workspace","content.subtitle":"Create clips, edit them, prepare SEO metadata and export.","projects.subtitle":"Analysis projects are stored on disk and can be reopened after a restart.","media.subtitle":"Watch exported Shorts, Reels and TikTok videos directly in Studio.","platforms.subtitle":"Edit export settings, save developer credentials and connect accounts with official OAuth.","settings.subtitle":"Configure the local AI engine and transcription preferences.","tasks.title":"Persistent task history","tasks.subtitle":"Multi-agent tasks, progress events, cancellations and retry records.","tasks.refresh":"Refresh history",
  "metric.gpu":"GPU USAGE","metric.cpu":"CPU USAGE","metric.ram":"MEMORY","metric.vram":"GPU MEMORY"
 },
 de:{
  "nav.studio":"\u25c8\u3000Studio","nav.content":"\u25a3\u3000Inhalte","nav.projects":"\u25f7\u3000Projekte","nav.media":"\u25b6\u3000Mediathek","nav.platforms":"\u25a4\u3000Plattformprofile","nav.settings":"\u2699\u3000Einstellungen",
  "appearance.label":"DARSTELLUNG","language.label":"ANWENDUNGSSPRACHE","local.name":"LOKALE KI-ENGINE","local.info":"Deine Daten werden auf diesem Computer verarbeitet",
  "studio.title":"Mehr aus jedem Video machen.","studio.subtitle":"Lange Videos analysieren, starke Momente finden und vertikale Inhalte vorbereiten.","studio.newProject":"Neues Videoprojekt","studio.youtubeUrl":"YouTube-Video-URL","studio.analyze":"Analysieren","studio.downloads":"Heruntergeladene Videos","studio.scan":"Downloads-Ordner durchsuchen","studio.clipCount":"Anzahl der Shorts","studio.speechLanguage":"Gesprochene Sprache",
  "projects.title":"Projekte","media.title":"Mediathek","platforms.title":"Plattformprofile","settings.title":"Einstellungen","settings.localAI":"Lokale KI-Engine","settings.whisper":"Whisper-Transkription","settings.languageTitle":"Sprache & Lokalisierung","settings.languageDescription":"W\u00e4hle die Sprache der Anwendungsoberfl\u00e4che. Deine Auswahl wird in diesem Browser gespeichert.","settings.languageNote":"Die Sprachwahl wird sofort \u00fcbernommen; ein Neustart ist nicht erforderlich.",
  "content.title":"Inhaltsbereich","content.subtitle":"Clips erstellen, bearbeiten, SEO-Texte vorbereiten und exportieren.","projects.subtitle":"Gespeicherte Analysen k\u00f6nnen auch nach einem Neustart erneut ge\u00f6ffnet werden.","media.subtitle":"Exportierte Shorts, Reels und TikTok-Videos direkt im Studio ansehen.","platforms.subtitle":"Exportprofile bearbeiten und Konten \u00fcber offizielles OAuth verbinden.","settings.subtitle":"Lokale KI- und Transkriptionseinstellungen konfigurieren.","tasks.title":"Dauerhafter Aufgabenverlauf","tasks.subtitle":"Multi-Agent-Aufgaben, Fortschritt, Abbruch und Wiederholungen.","tasks.refresh":"Verlauf aktualisieren",
  "metric.gpu":"GPU-AUSLASTUNG","metric.cpu":"CPU-AUSLASTUNG","metric.ram":"ARBEITSSPEICHER","metric.vram":"GPU-SPEICHER"
 },
 es:{
  "nav.studio":"\u25c8\u3000Studio","nav.content":"\u25a3\u3000Contenido","nav.projects":"\u25f7\u3000Proyectos","nav.media":"\u25b6\u3000Biblioteca multimedia","nav.platforms":"\u25a4\u3000Perfiles de plataforma","nav.settings":"\u2699\u3000Ajustes",
  "appearance.label":"APARIENCIA","language.label":"IDIOMA DE LA APLICACI\u00d3N","local.name":"MOTOR DE IA LOCAL","local.info":"Tus datos se procesan en este equipo",
  "studio.title":"Crea m\u00e1s con cada v\u00eddeo.","studio.subtitle":"Analiza v\u00eddeos largos, encuentra los mejores momentos y prepara contenido vertical.","studio.newProject":"Nuevo proyecto de v\u00eddeo","studio.youtubeUrl":"URL del v\u00eddeo de YouTube","studio.analyze":"Analizar","studio.downloads":"V\u00eddeos descargados","studio.scan":"Buscar en la carpeta Descargas","studio.clipCount":"N\u00famero de Shorts","studio.speechLanguage":"Idioma hablado",
  "projects.title":"Proyectos","media.title":"Biblioteca de v\u00eddeos","platforms.title":"Perfiles de plataforma","settings.title":"Ajustes","settings.localAI":"Motor de IA local","settings.whisper":"Transcripci\u00f3n Whisper","settings.languageTitle":"Idioma y localizaci\u00f3n","settings.languageDescription":"Elige el idioma de la interfaz. Tu preferencia se guarda en este navegador.","settings.languageNote":"El idioma se aplica al instante; no es necesario reiniciar la aplicaci\u00f3n.",
  "content.title":"Espacio de contenido","content.subtitle":"Crea clips, ed\u00edtalos, prepara textos SEO y exp\u00f3rtalos.","projects.subtitle":"Los an\u00e1lisis guardados se pueden volver a abrir despu\u00e9s de reiniciar.","media.subtitle":"Mira Shorts, Reels y v\u00eddeos de TikTok exportados directamente en Studio.","platforms.subtitle":"Edita perfiles de exportaci\u00f3n y conecta cuentas mediante OAuth oficial.","settings.subtitle":"Configura el motor de IA local y las preferencias de transcripci\u00f3n.","tasks.title":"Historial de tareas persistente","tasks.subtitle":"Tareas multiagente, progreso, cancelaciones e intentos.","tasks.refresh":"Actualizar historial",
  "metric.gpu":"USO DE GPU","metric.cpu":"USO DE CPU","metric.ram":"MEMORIA","metric.vram":"MEMORIA DE GPU"
 }};
const LOCALE_SELECTORS={
 "nav.studio":'#sidebarNav [data-page="studio"]',"nav.content":'#sidebarNav [data-page="content"]',"nav.projects":'#sidebarNav [data-page="projects"]',"nav.media":'#sidebarNav [data-page="media"]',"nav.platforms":'#sidebarNav [data-page="platforms"]',"nav.settings":'#sidebarNav [data-page="settings"]',
 "appearance.label":'label[for="themeSelect"]',"language.label":'label[for="languageSelect"]',"settings.languageTitle":'#page-settings .language-settings-panel h3',"settings.languageDescription":'#page-settings .language-settings-panel .panelhead p',"settings.languageNote":'#page-settings .language-settings-panel .notice',"local.name":'.local b',"local.info":'.local small',
 "studio.title":'#page-studio header h1',"studio.subtitle":'#page-studio header p',"studio.newProject":'#page-studio .panelhead h3',"studio.youtubeUrl":'#page-studio label[data-i18n="studio.youtubeUrl"]',"studio.analyze":'#analyze span',"studio.downloads":'#page-studio h3[data-i18n="studio.downloads"]',"studio.scan":'#scanDownloads',"studio.clipCount":'label[data-i18n="studio.clipCount"]',"studio.speechLanguage":'label[data-i18n="studio.speechLanguage"]',
 "projects.title":'#page-projects header h1',"media.title":'#page-media header h1',"platforms.title":'#page-platforms header h1',"settings.title":'#page-settings header h1',"settings.localAI":'#page-settings h3[data-i18n="settings.localAI"]',"settings.whisper":'#page-settings h3[data-i18n="settings.whisper"]',
 "metric.gpu":'.system-monitor .metric-card:nth-child(1) .metric-label',"metric.cpu":'.system-monitor .metric-card:nth-child(2) .metric-label',"metric.ram":'.system-monitor .metric-card:nth-child(3) .metric-label',"metric.vram":'.system-monitor .metric-card:nth-child(4) .metric-label'
};
function applyLocale(locale){
 const lang=UI_TEXT[locale]?locale:"tr";document.documentElement.lang=lang;
 const picker=$("languageSelect");if(picker&&picker.value!==lang)picker.value=lang;
 const dict=UI_TEXT[lang];
 Object.entries(LOCALE_SELECTORS).forEach(([key,selector])=>{const el=document.querySelector(selector);if(el&&dict[key])el.textContent=dict[key];});
 try{localStorage.setItem("yaman-viral-locale",lang);}catch{}
}
const savedLocale=(()=>{try{return localStorage.getItem("yaman-viral-locale")||"tr";}catch{return "tr";}})();
$("languageSelect")?.addEventListener("change",e=>applyLocale(e.target.value));

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
   $("cpuDetail").textContent=d.cpu_name||"CPU";
  $("ramValue").textContent=Math.round(d.ram_percent)+"%";setGauge("ramGauge",d.ram_percent);
  $("ramDetail").textContent=(d.ram_used_mb/1024).toFixed(1)+" GB / "+(d.ram_total_mb/1024).toFixed(1)+" GB kullanılıyor";
  if(d.gpu_available===true&&Number.isFinite(Number(d.gpu_percent))){
   $("gpuValue").textContent=Math.round(d.gpu_percent)+"%";setGauge("gpuGauge",d.gpu_percent);
    $("gpuDetail").textContent=d.gpu_name||"NVIDIA GPU";
   const vp=d.vram_total_mb?d.vram_used_mb/d.vram_total_mb*100:0;
   $("vramValue").textContent=Math.round(vp)+"%";setGauge("vramGauge",vp);
   $("vramDetail").textContent=Math.round(d.vram_used_mb)+" / "+Math.round(d.vram_total_mb)+" MB";
  }else{
    $("gpuDetail").textContent=d.gpu_name||"NVIDIA GPU";
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
 button.disabled=true;button.textContent="Ajanlar ba\u015flat\u0131l\u0131yor...";
 const pending=document.createElement("section");pending.className="agent-report";
 const h=document.createElement("div");h.className="agent-report-head";
 const name=document.createElement("b");name.textContent="AI ajan ekibi \u00b7 G\u00f6rev kuyru\u011fu";
 const state=document.createElement("small");state.textContent="12 uzman ajan haz\u0131rlan\u0131yor...";
 h.append(name,state);pending.append(h);
 const list=document.createElement("div");list.className="agent-live-list";
 const agentLabels=[
 ["viral-strategist","Viral Stratejist"],["hook-writer","Hook ve A\u00e7\u0131l\u0131\u015f Yazar\u0131"],["editor-director","Kurgu Y\u00f6netmeni"],["seo-specialist","SEO ve Da\u011f\u0131t\u0131m Uzman\u0131"],["claim-reviewer","\u0130\u00e7erik Risk Denet\u00e7isi"],["caption-qa","Altyaz\u0131 Kalite Kontrol\u00fc"],["clip-qa","Kesit Teknik Kontrol\u00fc"],["publishing-coordinator","Yay\u0131n Koordinat\u00f6r\u00fc"],["audience-retention","\u0130zleyici Tutma Analisti"],["thumbnail-director","Kapak ve G\u00f6rsel Y\u00f6netmeni"],["localization-specialist","\u00c7ok Dilli Yerelle\u015ftirme Uzman\u0131"],["accessibility-reviewer","Eri\u015filebilirlik Denet\u00e7isi"]];
 agentLabels.forEach(([id,label],i)=>{const row=document.createElement("div");row.className="agent-live-row";row.dataset.agentId=id;const n=document.createElement("b");n.textContent=String(i+1).padStart(2,"0")+" \u00b7 "+label;const st=document.createElement("span");st.className="agent-status queued";st.textContent="S\u0131rada";row.append(n,st);list.append(row);});
 pending.append(list);anchor.after(pending);
 let taskId=null;
 try{
  const r=await fetch("/api/agents/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:job,clip_id:clip,platforms:["youtube","instagram","tiktok"]})});
  const q=await r.json();if(!r.ok)throw new Error(q.detail||"Ajan g\u00f6revi ba\u015flat\u0131lamad\u0131");taskId=q.task_id;
  const cancel=document.createElement("button");cancel.className="secondary";cancel.textContent="G\u00f6revi iptal et";cancel.onclick=async()=>{cancel.disabled=true;await fetch("/api/tasks/"+encodeURIComponent(taskId)+"/cancel",{method:"POST"});state.textContent="\u0130ptal iste\u011fi g\u00f6nderildi";};h.append(cancel);
  state.textContent="Ajanlar \u00e7al\u0131\u015f\u0131yor \u00b7 G\u00f6rev "+taskId;
  const report=await waitForTask(taskId,task=>{
   if(task.agent_statuses)Object.entries(task.agent_statuses).forEach(([id,status])=>{const row=list.querySelector('[data-agent-id="'+id+'"]');if(!row)return;const badge=row.querySelector(".agent-status");badge.className="agent-status "+status;badge.textContent=status==="completed"?"Tamamland\u0131":status==="running"?"\u00c7al\u0131\u015f\u0131yor":status==="fallback"?"Yedek":"S\u0131rada";});
   state.textContent=(task.completed_agents||0)+"/12 ajan tamamland\u0131 \u00b7 "+(task.stage||"\u00c7al\u0131\u015f\u0131yor");
  });
  pending.replaceWith(renderAgentReport(report));button.textContent="Ajan raporu haz\u0131r";
 }catch(e){
  state.textContent="G\u00f6rev durdu";const err=document.createElement("small");err.className="agent-error";err.textContent=e.message;pending.append(err);
  if(taskId){const retry=document.createElement("button");retry.className="secondary";retry.textContent="G\u00f6revi yeniden dene";retry.onclick=async()=>{retry.disabled=true;try{const r=await fetch("/api/tasks/"+encodeURIComponent(taskId)+"/retry",{method:"POST"});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Retry failed");pending.remove();executeAgentTeam(job,clip,button,anchor);}catch(x){err.textContent=x.message;retry.disabled=false;}};pending.append(retry);}
  button.disabled=false;button.textContent="Tekrar \u00e7al\u0131\u015ft\u0131r";notice("Ajan hatas\u0131: "+e.message);
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
 info.textContent="Klip #"+(item.clip_id == null ? "\u2014" : item.clip_id)+" \u00b7 "+(item.size_mb!=null?item.size_mb+" MB":"MP4 video");
 video.addEventListener("loadedmetadata",()=>{if(Number.isFinite(video.duration)){const mm=Math.floor(video.duration/60),ss=Math.floor(video.duration%60);info.textContent+=" · "+mm+":"+String(ss).padStart(2,"0");}});
 video.addEventListener("error",()=>{info.textContent="Video yüklenemedi. Dosya yolu veya MP4 kodlamasını kontrol edin.";});
 const actions=document.createElement("div");actions.className="actions media-actions";
 const download=document.createElement("a");download.className="media-download";download.href=item.file;download.download=item.filename||("clip_"+item.clip_id+"_"+item.platform+".mp4");download.textContent="⬇ MP4 indir";
 const open=document.createElement("a");open.className="media-open";open.href=item.file;open.target="_blank";open.rel="noopener";open.textContent="Yeni sekmede aç";
 const en=document.documentElement.lang==="en";
 const publish=document.createElement("button");publish.className="secondary";publish.textContent=en?"Publish to platform":"Platformda yay\u0131nla";
 publish.addEventListener("click",async()=>{
   publish.disabled=true;
   try{
    const titleText=prompt(en?"Post title:":"Yay\u0131n ba\u015fl\u0131\u011f\u0131:",item.label||"YAMAN Viral Studio");if(titleText===null||!titleText.trim())return;
    const caption=prompt(en?"Description / hashtags (optional):":"A\u00e7\u0131klama / hashtag (iste\u011fe ba\u011fl\u0131):","");if(caption===null)return;
    let mediaUrl=null;if(item.platform==="instagram"){mediaUrl=prompt(en?"Public HTTPS video URL for Instagram Reels:":"Instagram Reels i\u00e7in herkese a\u00e7\u0131k HTTPS video URL'si:");if(!mediaUrl)return;}
    let privacy="private";
    if(item.platform==="tiktok"){
     const creatorResponse=await fetch("/api/publish/tiktok/creator");const creator=await creatorResponse.json();
     if(!creatorResponse.ok)throw new Error(creator.detail||"TikTok creator info unavailable");
     const options=creator.privacy_level_options||[];if(!options.length)throw new Error("TikTok privacy options unavailable");
     const choice=prompt((en?"Account: ":"Hesap: ")+(creator.creator_nickname||creator.creator_username||"TikTok")+"\n"+(en?"Choose a privacy option:\n":"Gizlilik se\u00e7ene\u011fini se\u00e7in:\n")+options.join("\n"),options.includes("SELF_ONLY")?"SELF_ONLY":options[0]);
     if(choice===null||!options.includes(choice)){notice(en?"Choose a valid TikTok privacy option.":"Ge\u00e7erli bir TikTok gizlilik se\u00e7ene\u011fi girin.");return;}
     privacy=choice;
    }
    const isAigc=item.platform==="tiktok"?confirm(en?"Add the AI-generated label to this TikTok post?":"TikTok g\u00f6nderisine AI-generated etiketi eklensin mi?"):false;
    if(!confirm(en?"Start uploading to "+item.platform.toUpperCase()+" with "+privacy+" visibility?":item.platform.toUpperCase()+" hesab\u0131na "+privacy+" gizlilik d\u00fczeyinde y\u00fckleme ba\u015flat\u0131ls\u0131n m\u0131?"))return;
    publish.textContent=en?"Uploading...":"Y\u00fckleniyor...";
    const response=await fetch("/api/publish/"+item.platform,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:item.job_id,clip_id:item.clip_id,title:titleText,description:caption,privacy,media_url:mediaUrl,is_aigc:isAigc,confirm_publish:true})});
    const result=await response.json();if(!response.ok)throw new Error(result.detail||"Publish failed");
    info.textContent=result.published?(en?"Published to platform.":"Platforma g\u00f6nderildi."):(result.note||"Upload processing");
   }catch(e){info.textContent=e.message;}finally{publish.disabled=false;publish.textContent=en?"Publish to platform":"Platformda yay\u0131nla";}
  });
  actions.append(download,open);
  if(["youtube","instagram","tiktok"].includes(item.platform))actions.append(publish);
  card.append(head,video,info,actions);return card;
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
$("refreshPlatforms")?.addEventListener("click",loadPlatforms);
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
const pageNames=["studio","content","autopilot","projects","media","platforms","settings"];
function showPage(name){
 if(!pageNames.includes(name)) name="studio";
 document.querySelectorAll(".page").forEach(x=>x.classList.toggle("active",x.id==="page-"+name));
 document.querySelectorAll("#sidebarNav a").forEach(x=>x.classList.toggle("active",x.dataset.page===name));
 const crumb=$("currentSection");if(crumb){const active=document.querySelector("#sidebarNav a[data-page=\""+name+"\"] .nav-label");crumb.textContent=active?.textContent?.trim()||name;}
 if(name==="projects") loadProjects();
 if(name==="media") loadMediaLibrary();
 if(name==="platforms") loadPlatforms();
 if(name==="settings"){loadSettings();const theme=$("themeSelect");if(theme)theme.value=document.documentElement.dataset.theme||"dark";}
  if(name==="content") loadTaskHistory();
 if(name==="autopilot") loadAutopilots();
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
 const box=$("platformList");if(!box)return;const en=document.documentElement.lang==="en";
 box.textContent=en?"Loading platform accounts...":"Platform hesaplar\u0131 y\u00fckleniyor...";
 try{
  const [r,sr,cr]=await Promise.all([fetch("/api/platforms",{cache:"no-store"}),fetch("/api/oauth/status",{cache:"no-store"}),fetch("/api/oauth/config/status",{cache:"no-store"})]);
  const profiles=await r.json(),oauth=await sr.json(),configs=await cr.json();if(!r.ok)throw new Error(profiles.detail||"Platform profiles unavailable");box.innerHTML="";
  const labels={youtube:"YouTube Shorts",instagram:"Instagram Reels",tiktok:"TikTok"};
  Object.entries(profiles).forEach(([key,profile])=>{
   const card=document.createElement("article");card.className="platform-card";
   const head=document.createElement("div");head.className="platform-card-head";const title=document.createElement("h3");title.textContent=labels[key]||profile.label;
   const connected=!!oauth[key]?.connected;const status=document.createElement("span");status.className="state-pill "+(connected?"connected":"pending");status.textContent=connected?(en?"Account connected":"Hesap ba\u011fl\u0131"):(en?"Not connected":"Ba\u011flant\u0131 bekleniyor");head.append(title,status);
   const desc=document.createElement("p");
   desc.textContent=key==="instagram"?(en?"Instagram Reels requires a professional account and a public HTTPS media URL.":"Instagram Reels i\u00e7in profesyonel hesap ve herkese a\u00e7\u0131k HTTPS video adresi gerekir."):(key==="tiktok"?(en?"TikTok Direct Post requires approved video.publish permission. Unaudited apps are limited to private posts.":"TikTok Direct Post i\u00e7in onayl\u0131 video.publish izni gerekir. Denetlenmemi\u015f uygulamalar \u00f6zel g\u00f6nderiyle s\u0131n\u0131rl\u0131d\u0131r."):(en?"YouTube Data API and youtube.upload permission are required. Default visibility is private.":"YouTube Data API ve youtube.upload izni gerekir. Varsay\u0131lan gizlilik \u00f6zeldir."));
   const credentialFields=document.createElement("div");credentialFields.className="platform-profile-fields";
   const client=document.createElement("input");client.type="text";client.autocomplete="off";client.placeholder="Developer Client ID / Key";client.value=configs[key]?.client_id||"";
   const secret=document.createElement("input");secret.type="password";secret.autocomplete="new-password";secret.placeholder="Developer Client Secret";
   const field=(labelText,control)=>{const wrap=document.createElement("label");wrap.className="profile-field";const label=document.createElement("span");label.textContent=labelText;wrap.append(label,control);credentialFields.append(wrap);};
   field(en?"Developer Client ID":"Geli\u015ftirici Client ID",client);field(en?"Developer Client Secret":"Geli\u015ftirici Client Secret",secret);
   const callback=document.createElement("small");callback.className="profile-feedback";callback.textContent="OAuth Callback: "+location.origin+"/api/oauth/callback/"+key;
   const accountActions=document.createElement("div");accountActions.className="actions";
   const saveCredentials=document.createElement("button");saveCredentials.className="secondary";saveCredentials.textContent=configs[key]?.configured?(en?"Update credentials":"Kimlik bilgilerini g\u00fcncelle"):(en?"Save credentials securely":"Kimlik bilgilerini g\u00fcvenli kaydet");
   saveCredentials.onclick=async()=>{saveCredentials.disabled=true;try{const response=await fetch("/api/oauth/config",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({platform:key,client_id:client.value.trim(),client_secret:secret.value})});const result=await response.json();if(!response.ok)throw new Error(result.detail||"Credential save failed");secret.value="";callback.textContent=en?"Developer app credentials encrypted and saved locally.":"Geli\u015ftirici uygulamas\u0131 bilgileri \u015fifrelenerek yerel diske kaydedildi.";}catch(e){callback.textContent=e.message;}finally{saveCredentials.disabled=false;}};
   const connect=document.createElement("button");connect.className="secondary";connect.textContent=connected?(en?"Reconnect account":"Hesab\u0131 yeniden ba\u011fla"):(en?"Connect account with OAuth":"OAuth ile hesap ba\u011fla");
   connect.onclick=async()=>{connect.disabled=true;const popup=window.open("about:blank","yaman-oauth","width=620,height=760");try{const response=await fetch("/api/oauth/start/"+key);const auth=await response.json();if(!response.ok)throw new Error(auth.detail||"OAuth could not start");if(popup)popup.location=auth.authorization_url;else callback.textContent=auth.authorization_url;callback.textContent=(en?"Register this exact callback URL in the developer console: ":"Bu callback adresini geli\u015ftirici konsoluna birebir ekleyin: ")+auth.redirect_uri;}catch(e){if(popup)popup.close();callback.textContent=e.message;}finally{connect.disabled=false;}};
   accountActions.append(saveCredentials,connect);
   if(connected){const disconnect=document.createElement("button");disconnect.className="secondary";disconnect.textContent=en?"Disconnect account":"Hesap ba\u011flant\u0131s\u0131n\u0131 kes";disconnect.onclick=async()=>{if(!confirm(en?"Disconnect this platform account?":"Bu platform hesab\u0131n\u0131n ba\u011flant\u0131s\u0131 kesilsin mi?"))return;await fetch("/api/oauth/"+key,{method:"DELETE"});loadPlatforms();};accountActions.append(disconnect);}
   const profileFields=document.createElement("div");profileFields.className="platform-profile-fields";
   const ratio=document.createElement("select");[["9:16",en?"Vertical ? 9:16":"Dikey ? 9:16"],["1:1",en?"Square ? 1:1":"Kare ? 1:1"],["16:9",en?"Landscape ? 16:9":"Yatay ? 16:9"]].forEach(([v,t])=>{const o=document.createElement("option");o.value=v;o.textContent=t;ratio.append(o)});ratio.value=profile.aspect_ratio||"9:16";
   const resolution=document.createElement("select");[1080,720].forEach(v=>{const o=document.createElement("option");o.value=String(v);o.textContent=v+"p";resolution.append(o)});resolution.value=String(profile.width===720?720:1080);
   const max=document.createElement("select");[15,30,60,90,120,180].forEach(v=>{const o=document.createElement("option");o.value=String(v);o.textContent=v+(en?" sec":" saniye");max.append(o)});max.value=String(profile.max_seconds);
   const profileField=(labelText,control)=>{const wrap=document.createElement("label");wrap.className="profile-field";const label=document.createElement("span");label.textContent=labelText;wrap.append(label,control);profileFields.append(wrap);};
   profileField(en?"Aspect ratio":"Video oran\u0131",ratio);profileField(en?"Resolution":"\u00c7\u00f6z\u00fcn\u00fcrl\u00fck",resolution);profileField(en?"Maximum duration":"Azami s\u00fcre",max);
   const saveProfile=document.createElement("button");saveProfile.className="secondary";saveProfile.textContent=en?"Save export profile":"D\u0131\u015fa aktarma profilini kaydet";
   const feedback=document.createElement("small");feedback.className="profile-feedback";feedback.textContent=(en?"Current output: ":"Mevcut \u00e7\u0131kt\u0131: ")+profile.width+" x "+profile.height+" / "+profile.max_seconds+(en?" sec":" sn");
   saveProfile.onclick=async()=>{saveProfile.disabled=true;try{const response=await fetch("/api/platforms/profile",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({platform:key,aspect_ratio:ratio.value,resolution:Number(resolution.value),max_seconds:Number(max.value)})});const result=await response.json();if(!response.ok)throw new Error(result.detail||"Profile save failed");feedback.textContent=(en?"Saved: ":"Kaydedildi: ")+result.width+" x "+result.height+" / "+result.max_seconds+(en?" sec":" sn");}catch(e){feedback.textContent=e.message;}finally{saveProfile.disabled=false;}};
   card.append(head,desc,credentialFields,accountActions,callback,profileFields,saveProfile,feedback);box.append(card);
  });
 }catch(e){box.textContent=(en?"Platform profiles unavailable: ":"Platform profilleri y\u00fcklenemedi: ")+e.message;}
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
 if(panel){panel.classList.remove("hidden");$("summaryFeedback").textContent="Video analiz edildi. \u00d6zet s\u00fcresini se\u00e7ip ak\u0131ll\u0131 \u00f6zet videosu olu\u015fturabilirsin.";}
}
function showSummaryResult(data){
 const box=$("summaryResult");box.innerHTML="";box.classList.remove("hidden");
 if($("summaryFormat")&&data.format)$("summaryFormat").value=data.format;
 const title=document.createElement("h3");title.textContent=data.title||"Video \u00f6zeti";
 const desc=document.createElement("p");desc.textContent=data.summary||"";
 const points=document.createElement("ul");(data.key_points||[]).forEach(x=>{const li=document.createElement("li");li.textContent=x;points.append(li);});
 const moments=document.createElement("div");moments.className="summary-moments";
 const formatBadge=document.createElement("div");formatBadge.className="story-format-badge";formatBadge.textContent=data.format_label||"Akıllı özet";
 (data.moments||[]).forEach((m,i)=>{const row=document.createElement("div");row.className="summary-moment";row.textContent=(m.section?m.section+" · ":(i+1)+". ")+Number(m.start).toFixed(1)+"s - "+Number(m.end).toFixed(1)+"s \u00b7 "+(m.reason||"\u00d6nemli an");moments.append(row);});
 const video=document.createElement("video");video.className="summary-player";video.controls=true;video.preload="metadata";video.src=data.output.file;
 const actions=document.createElement("div");actions.className="actions";
 const download=document.createElement("a");download.className="summary-download";download.href=data.output.file;download.download=data.output.filename||"summary_video.mp4";const formatNames={documentary:"Belgesel",education:"E\u011fitim",product:"\u00dcr\u00fcn tan\u0131t\u0131m\u0131",story:"Hik\u00e2ye ak\u0131\u015f\u0131"};download.textContent=(formatNames[data.format]||"Ozet")+" MP4 indir";
 const method=document.createElement("small");method.className="muted";method.textContent="AI y\u00f6ntemi: "+(data.method||"Yerel transkript analizi")+" \u00b7 "+data.output.size_mb+" MB";
 actions.append(download,method);box.append(title,formatBadge,desc,points,moments,video,actions);
}
async function generateSummaryVideo(){
 if(!jobId){$("summaryFeedback").textContent="\u00d6nce bir video analiz et.";return;}
 const button=$("generateSummary");button.disabled=true;button.textContent="\u00d6zet haz\u0131rlan\u0131yor...";
 const selectedFormat=$("summaryFormat")?.value||"smart";
 const formatMessages={documentary:"Belgesel b?l?mleri se?iliyor; sahneler kesilip s?ralan?yor ve otomatik birle?tiriliyor.",education:"??renme b?l?mleri se?iliyor; sahneler kesilip s?ralan?yor ve otomatik birle?tiriliyor.",product:"?r?n b?l?mleri kaynak transkriptinden se?iliyor ve otomatik birle?tiriliyor.",story:"Hik?ye b?l?mleri s?ralan?yor ve otomatik birle?tiriliyor."};$("summaryFeedback").textContent=(formatMessages[selectedFormat]||"AI ?nemli anlar? se?iyor, gereksiz b?l?mleri at?yor ve videoyu otomatik kurguluyor.")+" Ge?i?: "+(($("editTransition")?.value||"fade")==="fade"?"yumu?ak kararma":"temiz kesme")+".";

 try{
  const r=await fetch("/api/summary/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:jobId,target_seconds:+$("summaryLength").value,format:$("summaryFormat")?.value||"smart",transition:$("editTransition")?.value||"fade",captions:$("editCaptions")?.checked!==false,chapter_titles:$("editChapters")?.checked!==false})});
  const q=await r.json();if(!r.ok)throw new Error(q.detail||"\u00d6zet video ba\u015flat\u0131lamad\u0131");
  const data=await waitForTask(q.task_id,task=>{$("summaryFeedback").textContent=(task.stage||"\u00d6zet haz\u0131rlan\u0131yor")+" \u00b7 "+(task.percent||0)+"%";});
  showSummaryResult(data);$("summaryFeedback").textContent="\u00d6zet video ba\u015far\u0131yla olu\u015fturuldu.";loadMediaLibrary();
 }catch(e){$("summaryFeedback").textContent="\u00d6zet video hatas\u0131: "+e.message;notice("\u00d6zet video hatas\u0131: "+e.message);}
 finally{button.disabled=false;const names={documentary:"Belgesel anlat\u0131m\u0131n\u0131",education:"E\u011fitim videosunu",product:"\u00dcr\u00fcn tan\u0131t\u0131m\u0131n\u0131",story:"Hik\u00e2ye ak\u0131\u015f\u0131n\u0131"};button.textContent=(names[selectedFormat]||"Akilli ozeti")+" tekrar olustur";}
}
$("summaryFormat")?.addEventListener("change",()=>{
 const button=$("generateSummary");if(!button)return;
 const format=$("summaryFormat").value;const labels={documentary:"Belgesel anlat\u0131m\u0131",education:"E\u011fitim videosu",product:"\u00dcr\u00fcn tan\u0131t\u0131m\u0131",story:"Hik\u00e2ye ak\u0131\u015f\u0131"};button.textContent=(labels[format]||"Akilli ozet videosu")+" olustur ->";
});
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


async function loadAutopilots(){
 const box=$("autopilotList");if(!box)return;
 try{
  const r=await fetch("/api/autopilot",{cache:"no-store"}),d=await r.json();
  if(!r.ok)throw new Error(d.detail||"Autopilot listesi alınamadı");
  $("autoSourceFolder").textContent=d.source_folder||"Downloads";
  if(!d.autopilots.length){box.innerHTML='<div class="empty">Henüz otomasyon yok. İlk Autopilot görevini yukarıdan oluştur.</div>';return;}
  box.innerHTML=d.autopilots.map(a=>{
   const outputs=(a.last_outputs||[]).map(o=>'<a href="'+escapeHtml(o.url)+'" target="_blank" rel="noopener">'+escapeHtml(o.type==="voiceover"?"MP3 Seslendirme":o.type==="script"?"Senaryo":o.type==="trend_research"?"Trend Raporu":"MP4 Çıktı")+'</a>').join("");
   return '<article class="autopilot-card"><div class="autopilot-card-head"><div><b>'+escapeHtml(a.name)+'</b><small>'+escapeHtml(a.niche)+' · '+(a.frequency==="weekly"?"Haftalık":"Her gün")+' · '+escapeHtml(a.publish_time)+' '+escapeHtml(a.timezone)+'</small></div><span class="autopilot-status '+escapeHtml(a.last_status)+'">'+escapeHtml(a.last_status==="ready"?"HAZIR":a.last_status==="running"?"ÇALIŞIYOR":a.last_status==="review"?"ONAY BEKLİYOR":a.last_status==="failed"?"HATA":a.last_status.toUpperCase())+'</span></div><p>'+escapeHtml(a.last_message||("Sonraki çalışma: "+new Date(a.next_run).toLocaleString("tr-TR")))+'</p><small>'+escapeHtml(a.platforms.join(" · "))+' · '+(a.enabled?"Zamanlama açık":"Duraklatıldı")+'</small>'+(outputs?'<div class="autopilot-output-links">'+outputs+'</div>':'')+'<div class="autopilot-card-actions"><button class="secondary" data-auto-run="'+a.id+'">Şimdi çalıştır</button><button class="secondary" data-auto-toggle="'+a.id+'" data-enabled="'+(!a.enabled)+'">'+(a.enabled?"Duraklat":"Etkinleştir")+'</button><button class="secondary danger" data-auto-delete="'+a.id+'">Sil</button></div></article>';
  }).join("");
  box.querySelectorAll("[data-auto-run]").forEach(b=>b.addEventListener("click",async()=>{b.disabled=true;b.textContent="Kuyruğa alınıyor…";try{const x=await fetch("/api/autopilot/"+b.dataset.autoRun+"/run",{method:"POST"});const v=await x.json();if(!x.ok)throw new Error(v.detail);$("autopilotFeedback").textContent=v.message||"İşlem kuyruğa alındı."; }catch(e){$("autopilotFeedback").textContent=e.message;}finally{b.disabled=false;b.textContent="Şimdi çalıştır";loadAutopilots();}}));
  box.querySelectorAll("[data-auto-toggle]").forEach(b=>b.addEventListener("click",async()=>{const id=b.dataset.autoToggle;const item=d.autopilots.find(x=>x.id===id);const body={name:item.name,niche:item.niche,language:item.language,clips:item.clips,min_seconds:item.min_seconds,max_seconds:item.max_seconds,platforms:item.platforms,frequency:item.frequency,publish_time:item.publish_time,timezone:item.timezone,enabled:b.dataset.enabled==="true"};try{const x=await fetch("/api/autopilot/"+id,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const v=await x.json();if(!x.ok)throw new Error(v.detail);loadAutopilots();}catch(e){$("autopilotFeedback").textContent=e.message;}}));
  box.querySelectorAll("[data-auto-delete]").forEach(b=>b.addEventListener("click",async()=>{if(!confirm("Bu Autopilot otomasyonunu silmek istiyor musun?"))return;const x=await fetch("/api/autopilot/"+b.dataset.autoDelete,{method:"DELETE"});if(x.ok)loadAutopilots();}));
 }catch(e){box.innerHTML='<div class="empty">Autopilot yüklenemedi: '+escapeHtml(e.message)+'</div>';}
}
function escapeHtml(value){return String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
$("autopilotForm")?.addEventListener("submit",async e=>{
 e.preventDefault();const btn=$("saveAutopilot"),feedback=$("autopilotFeedback");btn.disabled=true;btn.textContent="Kaydediliyor…";
 const payload={name:$("autoName").value.trim(),niche:$("autoNiche").value.trim(),language:$("autoLanguage").value,clips:Number($("autoClips").value),min_seconds:Number($("autoMin").value),max_seconds:Number($("autoMax").value),platforms:[...document.querySelectorAll('input[name="autoPlatform"]:checked')].map(x=>x.value),frequency:$("autoFrequency").value,publish_time:$("autoTime").value,timezone:"Europe/Istanbul",enabled:$("autoEnabled").checked};
 try{const r=await fetch("/api/autopilot",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}),d=await r.json();if(!r.ok)throw new Error(d.detail||"Autopilot oluşturulamadı");feedback.textContent="Autopilot kaydedildi. İlk çalışma: "+new Date(d.autopilot.next_run).toLocaleString("tr-TR");$("autoNiche").value="";loadAutopilots();}
 catch(err){feedback.textContent=err.message;}
 finally{btn.disabled=false;btn.textContent="Autopilot oluştur →";}
});
$("refreshAutopilot")?.addEventListener("click",loadAutopilots);


let latestTrendTopics=[];
$("researchTrends")?.addEventListener("click",async()=>{
 const btn=$("researchTrends"),box=$("trendResults"),notice=$("trendNotice");
 btn.disabled=true;btn.textContent="Kaynaklar taranıyor…";box.innerHTML='<div class="empty">Google Trends, haberler ve topluluk akışları kontrol ediliyor…</div>';notice.textContent="";
 try{
  const r=await fetch("/api/content/trends",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({niche:$("trendNiche").value,region:$("trendRegion").value,limit:18})});
  const d=await r.json();if(!r.ok)throw new Error(d.detail||"Trend araştırması başarısız");
  latestTrendTopics=d.topics||[];
  box.innerHTML=latestTrendTopics.length?latestTrendTopics.map((t,i)=>'<button type="button" class="trend-item" data-trend="'+i+'"><span><b>'+escapeHtml(t.title)+'</b><small>'+escapeHtml(t.source)+' · '+escapeHtml(t.published||"Tarih belirtilmedi")+'</small></span><em>'+t.relevance+'/100</em></button>').join(""):'<div class="empty">Kaynaklardan konu bulunamadı. Nişi genişletip yeniden dene.</div>';
  box.querySelectorAll("[data-trend]").forEach(b=>b.addEventListener("click",()=>{$("scriptTopic").value=latestTrendTopics[Number(b.dataset.trend)].title;$("scriptNiche").value=$("trendNiche").value;$("scriptTopic").focus();}));
  notice.textContent=(d.sources||[]).join(" · ")+" | "+(d.errors||[]).join(" | ")+" "+(d.notice||"");
 }catch(e){box.innerHTML='<div class="empty">'+escapeHtml(e.message)+'</div>';}
 finally{btn.disabled=false;btn.textContent="Trendleri araştır";}
});
$("generateScript")?.addEventListener("click",async()=>{
 const btn=$("generateScript"),feedback=$("scriptFeedback");btn.disabled=true;btn.textContent="Ollama senaryo yazıyor…";feedback.textContent="";
 try{
  const r=await fetch("/api/content/script",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({niche:$("scriptNiche").value,topic:$("scriptTopic").value,language:$("scriptLanguage").value,duration:Number($("scriptDuration").value)})});
  const d=await r.json();if(!r.ok)throw new Error(d.detail||"Senaryo oluşturulamadı");
  $("scriptOutput").value=d.script;$("scriptMeta").textContent=d.title+" · "+(d.hashtags||[]).join(" ")+" · "+(d.scenes||[]).length+" sahne";
  feedback.textContent="Senaryo yerel Ollama ile oluşturuldu ve diske kaydedildi.";
 }catch(e){feedback.textContent=e.message;}
 finally{btn.disabled=false;btn.textContent="AI senaryo oluştur →";}
});
$("generateVoiceover")?.addEventListener("click",async()=>{
 const btn=$("generateVoiceover"),feedback=$("voiceFeedback");btn.disabled=true;btn.textContent="Ses üretiliyor…";feedback.textContent="";
 try{
  const r=await fetch("/api/content/voiceover",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:$("scriptOutput").value,voice:$("voiceSelect").value})});
  const d=await r.json();if(!r.ok)throw new Error(d.detail||"Seslendirme oluşturulamadı");
  $("voicePreview").src=d.audio_url;$("voicePreview").hidden=false;$("voiceDownload").href=d.audio_url;$("voiceDownload").hidden=false;$("voiceDownload").textContent="MP3 seslendirmeyi indir";
  feedback.textContent=d.engine+" · "+Math.round(d.bytes/1024)+" KB. "+d.notice;
 }catch(e){feedback.textContent=e.message;}
 finally{btn.disabled=false;btn.textContent="AI seslendirme üret";}
});
$("autoNiche")?.addEventListener("change",()=>{$("trendNiche").value=$("autoNiche").value;$("scriptNiche").value=$("autoNiche").value;});

applyLocale(savedLocale);
loadAutopilots();

window.addEventListener("focus",()=>{if(document.querySelector("#page-platforms.active"))loadPlatforms();});

async function loadTaskHistory(){
 const box=$("taskHistoryList");if(!box)return;box.textContent="G\u00f6rev ge\u00e7mi\u015fi y\u00fckleniyor...";
 try{const r=await fetch("/api/tasks/history?limit=80",{cache:"no-store"}),d=await r.json();if(!r.ok)throw new Error(d.detail||"G\u00f6rev ge\u00e7mi\u015fi al\u0131namad\u0131");box.innerHTML="";
  if(!d.tasks?.length){box.textContent="Hen\u00fcz kaydedilmi\u015f g\u00f6rev yok.";return;}
  d.tasks.forEach(t=>{const row=document.createElement("article");row.className="task-history-row";const meta=document.createElement("div");const title=document.createElement("b");title.textContent=(t.task_type==="agents"?"AI ajan g\u00f6revi":"\u0130\u015flem")+" \u00b7 "+t.task_id;const detail=document.createElement("small");detail.textContent=(t.stage||t.status)+" \u00b7 %"+(t.percent||0)+" \u00b7 "+(t.updated_at||"");meta.append(title,detail);const actions=document.createElement("div");actions.className="actions";const events=document.createElement("button");events.className="secondary";events.textContent="Olaylar";events.onclick=async()=>{const x=await fetch("/api/tasks/"+encodeURIComponent(t.task_id)+"/events");const v=await x.json();detail.textContent=(v.events||[]).map(e=>e.event+" \u00b7 "+e.state.stage).join(" | ");};actions.append(events);if(t.task_type==="agents"&&["failed","cancelled","interrupted"].includes(t.status)){const retry=document.createElement("button");retry.className="secondary";retry.textContent="Yeniden dene";retry.onclick=async()=>{retry.disabled=true;const x=await fetch("/api/tasks/"+encodeURIComponent(t.task_id)+"/retry",{method:"POST"});const v=await x.json();detail.textContent=x.ok?"Yeni g\u00f6rev: "+v.task_id:(v.detail||"Retry failed");retry.disabled=false;loadTaskHistory();};actions.append(retry);}row.append(meta,actions);box.append(row);});
 }catch(e){box.textContent=e.message;}
}
$("refreshTaskHistory")?.addEventListener("click",loadTaskHistory);


/* v1.5: section breadcrumb follows existing navigation */
(function(){const labels={studio:"Studio",content:"İçerik üretimi",autopilot:"Autopilot",projects:"Projeler",media:"Video kütüphanesi",platforms:"Platform profilleri",settings:"Ayarlar"};function sync(){const a=document.querySelector("#sidebarNav a.active"),t=document.getElementById("currentSection");if(a&&t)t.textContent=labels[a.dataset.page]||"Studio"}document.querySelectorAll("#sidebarNav a[data-page]").forEach(a=>a.addEventListener("click",()=>requestAnimationFrame(sync)));document.querySelectorAll("[data-go]").forEach(a=>a.addEventListener("click",()=>setTimeout(sync,0)));sync()})();


/* PWA install and service-worker registration */
(function initPWA(){
  const installButton=document.getElementById("installApp");
  let installPrompt=null;
  const isIOS=/iphone|ipad|ipod/i.test(navigator.userAgent);
  const isStandalone=window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone===true;

  if("serviceWorker" in navigator && window.isSecureContext){
    window.addEventListener("load",()=>{
      navigator.serviceWorker.register("/sw.js",{scope:"/"})
        .catch(error=>console.warn("PWA service worker registration failed:",error));
    });
  }

  if(!installButton || isStandalone) return;

  window.addEventListener("beforeinstallprompt",event=>{
    event.preventDefault();
    installPrompt=event;
    installButton.hidden=false;
  });

  window.addEventListener("appinstalled",()=>{
    installPrompt=null;
    installButton.hidden=true;
    installButton.blur();
  });

  if(isIOS){
    installButton.hidden=false;
    installButton.addEventListener("click",()=>{
      window.alert("iPhone/iPad: Safari'de Paylaş düğmesine dokun, ardından 'Ana Ekrana Ekle' seçeneğini seç.");
    });
    return;
  }

  installButton.addEventListener("click",async()=>{
    if(!installPrompt) return;
    installButton.disabled=true;
    try{
      await installPrompt.prompt();
      await installPrompt.userChoice;
      installPrompt=null;
      installButton.hidden=true;
    }catch(error){
      console.warn("PWA install prompt failed:",error);
    }finally{
      installButton.disabled=false;
    }
  });
})();

// One-click, source-free creator: trend/topic -> local Ollama -> neural voice -> scene video -> MP4.
$("createCompleteVideo")?.addEventListener("click",async()=>{
 const btn=$("createCompleteVideo"),feedback=$("factoryFeedback"),out=$("factoryOutput");
 btn.disabled=true;btn.textContent="Üretim hazırlanıyor…";feedback.textContent="Trend, senaryo, seslendirme ve sahneler hazırlanıyor. Bu işlem birkaç dakika sürebilir.";out.classList.add("hidden");out.innerHTML="";
 try{
  const body={niche:$("factoryNiche").value,topic:$("factoryTopic").value.trim(),region:$("factoryRegion").value,language:$("factoryLanguage").value,duration:Number($("factoryDuration").value),voice:$("factoryVoice").value,captions:$("factoryCaptions").checked,auto_trend:$("factoryAutoTrend").checked};
  const r=await fetch("/api/content/create-video",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const d=await r.json();if(!r.ok)throw new Error(d.detail||"Video üretilemedi");
  feedback.textContent="Tamamlandı · "+d.duration_seconds+" sn · "+d.size_mb+" MB · "+d.visual_mode;
  out.classList.remove("hidden");
  const title=document.createElement("h3");title.textContent=d.title;
  const video=document.createElement("video");video.controls=true;video.playsInline=true;video.src=d.video_url;video.className="factory-preview";
  const actions=document.createElement("div");actions.className="factory-actions";
  const download=document.createElement("a");download.href=d.video_url;download.download=d.filename;download.className="nav-cta";download.textContent="MP4 videoyu indir";
  const script=document.createElement("a");script.href=d.script_url;script.className="secondary-link";script.textContent="Senaryoyu indir";
  const audio=document.createElement("a");audio.href=d.audio_url;audio.className="secondary-link";audio.textContent="MP3 seslendirmeyi indir";
  actions.append(download,script,audio);out.append(title,video,actions);
  if(d.notice){const note=document.createElement("p");note.className="muted";note.textContent=d.notice;out.append(note);}
 }catch(e){feedback.textContent="Üretim tamamlanamadı: "+e.message;}
 finally{btn.disabled=false;btn.innerHTML="✦ Senaryo + ses + görseller + MP4 oluştur <span>→</span>";}
});
