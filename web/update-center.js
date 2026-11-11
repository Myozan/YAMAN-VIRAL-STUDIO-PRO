/* YAMAN Update Center — user-approved updates only */
(() => {
 const $ = id => document.getElementById(id);
 const box = $("updateNotice");
 const button = $("applyUpdateButton");
 const dismiss = $("dismissUpdateButton");
 const notesButton = $("updateNotesButton");
 if (!box || !button) return;
 let pending = null;
 const dismissedKey = "yaman-update-dismissed-commit";
 const show = state => {
   pending = state;
   const version = state.latest_version || "Yeni sürüm";
   $("updateNoticeTitle").textContent = version + " güncellemesi hazır";
   $("updateNoticeText").textContent = "Mevcut: " + state.current_version + " · Yeni: " + version + " · " + state.message;
   box.hidden = false;
   if (notesButton) notesButton.hidden = !state.release_notes;
   button.disabled = false;
   button.textContent = "Şimdi güncelle";
 };
 async function check() {
   try {
     const response = await fetch("/api/update/status", {cache:"no-store"});
     const state = await response.json();
     if (!response.ok || state.check_failed) return;
     const dismissed = localStorage.getItem(dismissedKey);
     if (state.available && dismissed !== state.latest_commit) show(state);
     else if (!state.available) box.hidden = true;
   } catch (error) {
     console.warn("Update check failed:", error);
   }
 }
 dismiss?.addEventListener("click", () => {
   if (pending?.latest_commit) localStorage.setItem(dismissedKey, pending.latest_commit);
   box.hidden = true;
 });
 notesButton?.addEventListener("click", () => {
   if (!pending) return;
   const text = pending.release_notes || pending.message || "";
   const w = window.open("", "_blank", "noopener");
   if (!w) { alert(text); return; }
   const pre = w.document.createElement("pre");
   pre.textContent = text;
   pre.style.cssText = "white-space:pre-wrap;font:14px/1.7 system-ui;padding:28px;max-width:850px;margin:40px auto";
   w.document.body.append(pre);
 });
 button.addEventListener("click", async () => {
   if (!pending?.latest_commit) return;
   if (!confirm("YAMAN VIRAL STUDIO PRO " + (pending.latest_version || "") + " sürümüne güncellensin mi?\n\nYerel videolar, ayarlar, oturumlar ve workspace dosyaları korunur. Önce uygulama yedeği oluşturulur.")) return;
   button.disabled = true;
   button.textContent = "Yedek alınıyor ve kuruluyor…";
   try {
     const response = await fetch("/api/update/apply", {
       method:"POST", headers:{"Content-Type":"application/json"},
       body:JSON.stringify({expected_commit:pending.latest_commit})
     });
     const result = await response.json();
     if (!response.ok) throw new Error(result.detail || "Güncelleme başarısız.");
     if (result.updated) {
       $("updateNoticeTitle").textContent = "Güncelleme kuruldu";
       $("updateNoticeText").textContent = result.message + " Yedek: " + result.backup;
       if (result.restart_scheduled) {
         button.textContent = "Sunucu yeniden başlatılıyor…";
         button.disabled = true;
         let attempts = 0;
         const poll = window.setInterval(async () => {
           attempts += 1;
           try {
             const ready = await fetch("/api/update/status", {cache:"no-store"});
             if (ready.ok) {
               window.clearInterval(poll);
               button.disabled = false;
               button.textContent = "Studio'yu yenile";
               button.onclick = () => location.reload();
             }
           } catch (_) {}
           if (attempts >= 30) {
             window.clearInterval(poll);
             $("updateNoticeText").textContent += " Sunucu otomatik açılmazsa terminal penceresini yeniden başlatın.";
             button.textContent = "Sayfayı yenile";
             button.disabled = false;
             button.onclick = () => location.reload();
           }
         }, 3000);
       } else {
         $("updateNoticeText").textContent += " Uygulamayı kapatıp run_windows.bat ile yeniden başlatın.";
         button.textContent = "Yeniden başlatma gerekli";
         button.disabled = true;
       }
     } else {
       $("updateNoticeText").textContent = result.message;
       button.textContent = "Güncelsiniz";
       button.disabled = true;
     }
   } catch (error) {
     $("updateNoticeText").textContent = "Güncelleme yapılamadı: " + error.message;
     button.textContent = "Tekrar dene";
     button.disabled = false;
   }
 });
 check();
 window.setInterval(check, 6 * 60 * 60 * 1000);
})();
