"""YAMAN VIRAL STUDIO PRO — local multi-agent team.

The agents are deliberately small, task-scoped workers. They reuse the
application's existing local Ollama JSON function and deterministic validators;
no additional agent framework or cloud API is required.
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone


AGENT_CATALOG = [
    {"id": "viral-strategist", "name": "Viral Stratejist", "role": "Kesitin hook, açıklık, merak, duygu ve sonuç gücünü değerlendirir.", "mode": "AI"},
    {"id": "hook-writer", "name": "Hook & Açılış Yazarı", "role": "İlk saniyeler için alternatif açılışlar ve CTA önerir.", "mode": "AI"},
    {"id": "editor-director", "name": "Kurgu Yönetmeni", "role": "Tempo, vurgu, altyazı, kadraj ve B-roll planı hazırlar.", "mode": "AI"},
    {"id": "seo-specialist", "name": "SEO & Dağıtım Uzmanı", "role": "YouTube, Instagram ve TikTok için ayrı metaveri üretir.", "mode": "AI"},
    {"id": "claim-reviewer", "name": "İçerik Risk Denetçisi", "role": "Metindeki doğrulanması gereken iddiaları ve yayın risklerini işaretler.", "mode": "AI"},
    {"id": "caption-qa", "name": "Altyazı Kalite Kontrolü", "role": "Okunabilirlik, kelime yoğunluğu ve altyazı uzunluğunu denetler.", "mode": "RULES"},
    {"id": "clip-qa", "name": "Kesit Teknik Kontrolü", "role": "Süre, zaman aralığı, içerik ve platform sınırlarını doğrular.", "mode": "RULES"},
    {"id": "publishing-coordinator", "name": "Yayın Koordinatörü", "role": "Platform bazlı yayın hazırlık listesini oluşturur; izinsiz paylaşım yapmaz.", "mode": "RULES"},
    {"id": "audience-retention", "name": "\u0130zleyici Tutma Analisti", "role": "Anlat\u0131 ak\u0131\u015f\u0131, merak d\u00f6ng\u00fcs\u00fc ve izleyici kayb\u0131 risklerini inceler.", "mode": "AI"},
    {"id": "thumbnail-director", "name": "Kapak ve G\u00f6rsel Y\u00f6netmeni", "role": "Kapak fikri, ba\u015fl\u0131k ve g\u00f6rsel \u00fcretim briefi haz\u0131rlar.", "mode": "AI"},
    {"id": "localization-specialist", "name": "\u00c7ok Dilli Yerelle\u015ftirme Uzman\u0131", "role": "Ba\u015fl\u0131k ve a\u00e7\u0131klamalar\u0131 farkl\u0131 dillere uyarlar.", "mode": "AI"},
    {"id": "accessibility-reviewer", "name": "Eri\u015filebilirlik Denet\u00e7isi", "role": "Altyaz\u0131 okunabilirli\u011fi ve eri\u015filebilir video sunumunu denetler.", "mode": "AI"},
]


def _run_ai(llm, agent_id, name, role, prompt, fallback, timeout=90):
    started = time.perf_counter()
    error=None
    result=fallback
    status="fallback"
    attempts=0
    for attempt in range(2):
        attempts=attempt+1
        try:
            result=llm(prompt,timeout=timeout)
            if not isinstance(result,dict):raise ValueError("Model JSON object expected")
            status="completed";error=None;break
        except Exception as exc:
            error=str(exc)[:240]
            if "cancelled by user" in error.lower():raise
            if attempt==0:time.sleep(0.6)
    if status!="completed":result=fallback
    return {
        "id": agent_id, "agent": name, "role": role, "status": status,
        "duration_ms": round((time.perf_counter() - started) * 1000),
        "attempts": attempts, "result": result, "error": error,
    }


def _rule_agent(agent_id, name, role, fn):
    started = time.perf_counter()
    try:
        result = fn()
        status, error = "completed", None
    except Exception as exc:
        result, status, error = {"checks": [], "note": "Kontrol tamamlanamadı."}, "failed", str(exc)[:240]
    return {
        "id": agent_id, "agent": name, "role": role, "status": status,
        "duration_ms": round((time.perf_counter() - started) * 1000),
        "result": result, "error": error,
    }


def run_agent_team(llm, job, clip, platforms, progress_callback=None):
    """Run each specialist independently and return a UI-ready report."""
    text = str(clip.get("text", "")).strip()
    title = str(clip.get("title", "")).strip()
    duration = float(clip.get("duration", max(0, float(clip.get("end", 0)) - float(clip.get("start", 0)))))
    source_duration = float(job.get("duration", 0) or 0)
    selected = [p for p in dict.fromkeys(platforms) if p in {"youtube", "instagram", "tiktok"}]
    transcript = text[:2600]
    base = {"clip_id": clip.get("id"), "title": title, "transcript": transcript, "duration": duration}

    def notify(agent_id, status):
        if progress_callback:
            progress_callback(agent_id, status)

    strategist_fallback = {
        "score": int(clip.get("score", 0)), "verdict": "Mevcut kesit puanı korundu",
        "hook_strength": "Henüz AI değerlendirmesi yok", "clarity": "Manuel inceleme önerilir",
        "emotion": "Belirlenemedi", "payoff": "Belirlenemedi",
        "why": str(clip.get("reason", "")), "improvement": "İlk iki saniyeyi manuel kontrol edin",
    }
    notify("viral-strategist", "running")
    strategist = _run_ai(
        llm, "viral-strategist", "Viral Stratejist", "İçerik potansiyeli ve izleyici tutma değerlendirmesi",
        "Türkçe yanıt ver. Bu kısa video kesitini editoryal olarak değerlendir. "
        "Sadece verilen transkripte dayan; viral olma garantisi verme. "
        "JSON alanları: score (0-100 integer), verdict, hook_strength, clarity, emotion, payoff, why, improvement. "
        "Metin: " + transcript,
        strategist_fallback,
    )

    notify("viral-strategist", "completed")

    hook_fallback = {
        "hooks": [text[:85]] if text else [],
        "cta": "Devamı için takip et.",
        "style": "Doğal açılış",
    }
    notify("hook-writer", "running")
    hook = _run_ai(
        llm, "hook-writer", "Hook & Açılış Yazarı", "Açılış cümlesi, merak unsuru ve harekete geçirici çağrı",
        "Türkçe üret. Yalnızca aşağıdaki konuşmanın anlamını koruyarak kısa video için 3 farklı açılış cümlesi yaz. "
        "Yanıltıcı clickbait kullanma. Ayrıca kısa bir CTA ve hook stili üret. "
        "JSON alanları: hooks (3 string), cta, style. Konuşma: " + transcript,
        hook_fallback,
    )

    notify("hook-writer", "completed")

    editor_fallback = {
        "opening_seconds": 2, "pacing": "Konuşmanın doğal ritmini koru",
        "caption_emphasis": [], "broll_suggestions": [],
        "audio_notes": "Konuşma sesini net ve önde tut",
        "framing": "9:16 merkez kadraj; yüz/konuşmacı güvenli alanda",
    }
    notify("editor-director", "running")
    editor = _run_ai(
        llm, "editor-director", "Kurgu Yönetmeni", "Kurgu, tempo, altyazı vurgusu ve dikey kadraj yönetimi",
        "Türkçe bir editör planı üret. Kaynak video süresi ve mevcut kesit zamanları değiştirilmeyecek. "
        "JSON alanları: opening_seconds (1-3), pacing, caption_emphasis (en fazla 5 kısa ifade), "
        "broll_suggestions (en fazla 3), audio_notes, framing. "
        "Kesit: " + str(base),
        editor_fallback,
    )

    notify("editor-director", "completed")

    seo_fallback = {
        "platforms": {
            p: {"title": title[:95], "description": text[:350],
                "hashtags": ["#shorts", "#reels", "#tiktok"]}
            for p in selected
        }
    }
    notify("seo-specialist", "running")
    seo = _run_ai(
        llm, "seo-specialist", "SEO & Dağıtım Uzmanı", "Platforma özel başlık, açıklama ve hashtag üretimi",
        "Türkçe üret. Her platform için ayrı ve doğal metaveri oluştur. Gerçek olmayan iddia ekleme. "
        "JSON şeması: {platforms:{youtube:{title,description,hashtags:[]},"
        "instagram:{title,description,hashtags:[]},tiktok:{title,description,hashtags:[]}}}. "
        "Yalnızca şu platformları döndür: " + ", ".join(selected) + ". Konuşma: " + transcript,
        seo_fallback,
        timeout=120,
    )
    notify("seo-specialist", "completed")

    seo_result = seo.get("result", {})
    platform_data = seo_result.get("platforms", {}) if isinstance(seo_result, dict) else {}
    for p in selected:
        if not isinstance(platform_data.get(p), dict):
            platform_data[p] = seo_fallback["platforms"][p]
        platform_data[p].setdefault("title", title[:95])
        platform_data[p].setdefault("description", text[:350])
        platform_data[p].setdefault("hashtags", ["#shorts", "#reels", "#tiktok"])
    seo["result"] = {"platforms": platform_data}

    risk_fallback = {
        "risk_level": "review", "claims_to_verify": [],
        "warnings": ["AI risk taraması çalışmadı; yayın öncesi insan kontrolü gerekli."],
        "review_note": "Bu kontrol harici kaynaklardan doğrulama yapmaz.",
    }
    notify("claim-reviewer", "running")
    risk = _run_ai(
        llm, "claim-reviewer", "İçerik Risk Denetçisi", "İddia, yanıltıcılık ve yayın güvenliği taraması",
        "Türkçe yanıt ver. Transkriptte doğrulanması gereken olgusal iddiaları, sağlık/finans/hukuk gibi "
        "yüksek riskli tavsiyeleri ve bağlamından koparma riskini işaretle. Harici doğrulama yaptığını iddia etme. "
        "JSON alanları: risk_level (low/medium/high), claims_to_verify (array), warnings (array), review_note. "
        "Transkript: " + transcript,
        risk_fallback,
    )

    notify("claim-reviewer", "completed")

    def caption_checks():
        words = re.findall(r"\S+", text)
        wpm = round(len(words) / duration * 60, 1) if duration > 0 else 0
        long_words = [w for w in words if len(w) > 22][:10]
        return {
            "word_count": len(words), "estimated_words_per_minute": wpm,
            "long_tokens": long_words,
            "readability": "high_density" if wpm > 210 else ("low_density" if wpm < 55 else "normal"),
            "checks": [
                {"name": "Metin boş değil", "passed": bool(text)},
                {"name": "Kelime yoğunluğu", "passed": 55 <= wpm <= 210, "value": wpm},
                {"name": "Aşırı uzun kelime", "passed": not long_words},
            ],
            "recommendation": "Altyazıyı 1-4 kelimelik gruplara böl; özel isim ve sayıları yayın öncesi doğrula.",
        }

    notify("caption-qa", "running")
    captions = _rule_agent(
        "caption-qa", "Altyazı Kalite Kontrolü", "Okunabilirlik ve metin yoğunluğu doğrulaması",
        caption_checks,
    )

    notify("caption-qa", "completed")

    def clip_checks():
        start = float(clip.get("start", 0))
        end = float(clip.get("end", start + duration))
        checks = [
            {"name": "Pozitif süre", "passed": duration > 0, "value": duration},
            {"name": "Shorts süre sınırı", "passed": 1 <= duration <= 180},
            {"name": "Zaman aralığı geçerli", "passed": start >= 0 and end > start},
            {"name": "Kaynak video sınırı", "passed": not source_duration or end <= source_duration + 0.5},
            {"name": "Konuşma metni mevcut", "passed": bool(text)},
        ]
        failed = [x["name"] for x in checks if not x["passed"]]
        return {"checks": checks, "passed": not failed, "issues": failed,
                "time_range": {"start": start, "end": end}, "platforms": selected}

    notify("clip-qa", "running")
    clip_qa = _rule_agent(
        "clip-qa", "Kesit Teknik Kontrolü", "Süre, zaman aralığı ve kaynak bütünlüğü",
        clip_checks,
    )

    notify("clip-qa", "completed")

    def publishing_checklist():
        return {
            "state": "manual_review_required",
            "uploads_performed": False,
            "platforms": {
                p: {
                    "video_profile": "1080x1920 · 9:16",
                    "metadata_ready": isinstance(platform_data.get(p), dict),
                    "human_approval_required": True,
                    "oauth_connected": False,
                } for p in selected
            },
            "checklist": [
                "Videoyu oynatıp ses ve altyazıyı kontrol et",
                "Başlık, açıklama ve hashtagleri onayla",
                "Telif ve kullanım haklarını doğrula",
                "Platform hesabında yayın öncesi son kontrolü yap",
            ],
            "note": "Bu ajan dosyaları yayın için hazırlar; OAuth entegrasyonu olmadan otomatik yükleme yapmaz.",
        }

    notify("publishing-coordinator", "running")
    publishing = _rule_agent(
        "publishing-coordinator", "Yayın Koordinatörü", "Yayın hazırlığı ve güvenli manuel onay",
        publishing_checklist,
    )

    notify("publishing-coordinator", "completed")

    # Additional focused workers; all inference remains on local Ollama.
    retention_fallback = {"retention_risks": [], "story_arc": "Manual review required", "recommendations": ["\u0130lk 2 saniyede konuyu netle\u015ftir", "Gereksiz duraklamalar\u0131 kes", "Kapan\u0131\u015f\u0131 ana fikre ba\u011fla"]}
    notify("audience-retention", "running")
    retention = _run_ai(llm, "audience-retention", "\u0130zleyici Tutma Analisti", "\u0130zleyici tutma ve anlat\u0131 ak\u0131\u015f\u0131 analizi",
        "Respond in Turkish. Analyze the transcript for audience drop-off risks, curiosity loops and narrative flow. Do not invent timestamps. JSON keys: retention_risks (array), story_arc, recommendations (array). Transcript: " + transcript,
        retention_fallback)
    notify("audience-retention", "completed")

    thumbnail_fallback = {"concept": "Use the clearest real visual from the topic", "headline_options": [], "visual_prompt": "Accurate vertical social video cover based only on the transcript", "avoid": ["Misleading visuals", "People or events not present"]}
    notify("thumbnail-director", "running")
    thumbnail = _run_ai(llm, "thumbnail-director", "Kapak ve G\u00f6rsel Y\u00f6netmeni", "Kapak fikri, k\u0131sa ba\u015fl\u0131k ve g\u00f6rsel brief",
        "Respond in Turkish. Create three concise cover headlines and a visual design brief based only on the transcript. Do not invent people or events. JSON keys: concept, headline_options (3 strings), visual_prompt, avoid (array). Transcript: " + transcript,
        thumbnail_fallback)
    notify("thumbnail-director", "completed")

    localization_fallback = {"turkish_title": title[:95], "english_title": "", "english_description": "", "notes": ["Translation needs human localization review"]}
    notify("localization-specialist", "running")
    localization = _run_ai(llm, "localization-specialist", "\u00c7ok Dilli Yerelle\u015ftirme Uzman\u0131", "Ba\u015fl\u0131k ve a\u00e7\u0131klamalar\u0131 farkl\u0131 hedef kitlelere uyarlar",
        "Respond in Turkish. Write natural English title and description while preserving the original meaning and proper nouns. Do not add facts. JSON keys: turkish_title, english_title, english_description, notes (array). Title: " + title + " Transcript: " + transcript,
        localization_fallback)
    notify("localization-specialist", "completed")

    accessibility_fallback = {"caption_readability": "review", "issues": [], "recommendations": ["Use high-contrast captions", "Keep captions in the safe area", "Describe important non-speech sounds"]}
    notify("accessibility-reviewer", "running")
    accessibility = _run_ai(llm, "accessibility-reviewer", "Eri\u015filebilirlik Denet\u00e7isi", "Altyaz\u0131 okunabilirli\u011fi ve eri\u015filebilir video sunumu",
        "Respond in Turkish. Review caption readability, technical terms, meaningful non-speech sounds and mobile-screen clarity. Do not invent content. JSON keys: caption_readability, issues (array), recommendations (array). Transcript: " + transcript,
        accessibility_fallback)
    notify("accessibility-reviewer", "completed")

    agents = [strategist, hook, editor, seo, risk, captions, clip_qa, publishing,
              retention, thumbnail, localization, accessibility]
    counts = {
        "total": len(agents),
        "completed": sum(a["status"] == "completed" for a in agents),
        "fallback": sum(a["status"] == "fallback" for a in agents),
        "failed": sum(a["status"] == "failed" for a in agents),
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clip_id": clip.get("id"),
        "summary": counts,
        "agents": agents,
    }
