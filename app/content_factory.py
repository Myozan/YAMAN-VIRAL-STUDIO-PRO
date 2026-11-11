"""Trend discovery, local-LLM script writing, and online neural narration."""
from __future__ import annotations
import asyncio
import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote_plus
import requests
from app.secure_http import request_public_https

USER_AGENT = "YAMAN-VIRAL-STUDIO-PRO/1.6.0 (+local creator research)"
VOICE_CATALOG = {
    "tr-TR-EmelNeural": {"label":"Emel · Türkçe kadın", "language":"tr"},
    "tr-TR-AhmetNeural": {"label":"Ahmet · Türkçe erkek", "language":"tr"},
    "en-US-AriaNeural": {"label":"Aria · English female", "language":"en"},
    "en-US-GuyNeural": {"label":"Guy · English male", "language":"en"},
    "en-GB-SoniaNeural": {"label":"Sonia · British English female", "language":"en"},
}

def _rss_items(url: str, source: str, limit: int = 12):
    response = request_public_https("GET", url, headers={"User-Agent":USER_AGENT}, timeout=18, max_redirects=4)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    found=[]
    for node in root.findall(".//item")[:limit]:
        title=(node.findtext("title") or "").strip()
        link=(node.findtext("link") or "").strip()
        pub=(node.findtext("pubDate") or "").strip()
        desc=re.sub(r"<[^>]+>"," ",node.findtext("description") or "").strip()
        if title:
            found.append({"title":title,"url":link,"published":pub,"source":source,"summary":desc[:280]})
    return found

def research_trends(niche: str, region: str = "TR", limit: int = 18):
    niche=niche.strip()[:160]
    if not niche: raise ValueError("Kanal konusu boş olamaz.")
    region=region if region in {"TR","US","GB","DE"} else "TR"
    sources=[]
    locale={"TR":("tr","TR","TR:tr"),"US":("en-US","US","US:en"),"GB":("en-GB","GB","GB:en"),"DE":("de","DE","DE:de")}[region]
    urls=[
        (f"https://trends.google.com/trending/rss?geo={region}","Google Trends"),
        (f"https://news.google.com/rss/search?q={quote_plus(niche)}&hl={locale[0]}&gl={locale[1]}&ceid={locale[2]}","Google News"),
        (f"https://www.reddit.com/search.rss?q={quote_plus(niche)}&sort=hot&t=week","Reddit"),
    ]
    errors=[]
    for url,label in urls:
        try: sources.extend(_rss_items(url,label,limit))
        except Exception as exc: errors.append(f"{label}: {str(exc)[:160]}")
    unique={}
    for item in sources:
        key=re.sub(r"\W+"," ",item["title"].lower()).strip()
        if key and key not in unique: unique[key]=item
    results=list(unique.values())
    terms=set(re.findall(r"[\wğüşöçıİĞÜŞÖÇ]{3,}",niche.lower()))
    for item in results:
        title_terms=set(re.findall(r"[\wğüşöçıİĞÜŞÖÇ]{3,}",item["title"].lower()))
        item["relevance"]=min(100,35+min(45,len(terms & title_terms)*15)+(15 if item["source"]=="Google Trends" else 0))
    results.sort(key=lambda x:(x["relevance"],x["source"]=="Google Trends"),reverse=True)
    return {"niche":niche,"region":region,"topics":results[:limit],"sources":list(dict.fromkeys(x["source"] for x in results)),"errors":errors,
            "notice":"Trend RSS sonuçları keşif sinyalidir; resmi izlenme/popülerlik sıralaması değildir. Yayın öncesi kaynakları doğrulayın."}

def generate_script(ollama_url: str, model: str, niche: str, topic: str, language: str="tr", duration: int=60, style: str="shorts", shot_count: int=5):
    lang="Turkish" if language=="tr" else "English"
    creative = ("Create a cinematic trailer, not a normal explainer. Build a three-act arc: mysterious cold open, escalating reveals, emotional climax and memorable final title/CTA. Write short punchy narrator lines, deliberate pauses, visual metaphors, varied shot scale, dramatic camera movement, rich atmosphere and sound-design cues in scene metadata. Each scene must have a concrete filmable visual, not abstract text. Avoid unsupported factual claims." if style=="trailer" else "Create a fast, clear vertical short with a powerful first-two-second hook, visual variety, concise narration and a strong payoff.")
    prompt=f"""You are an award-winning trailer editor and short-form film director. Create a {duration}-second {style} video script in {lang}.
Channel niche: {niche}
Chosen topic: {topic}
Creative direction: {creative}
Return JSON only with keys: title, hook, script, scenes (exactly {shot_count} objects, each with narration, visual_direction, camera_motion, mood, shot_type), description, hashtags (array).
Rules: every scene must describe a distinct coherent visual shot; maintain continuity of characters, wardrobe, setting and art direction; write rich image-generation prompts with subject, environment, lighting, lens, composition and camera motion; no text, subtitles, logos or watermarks inside generated imagery; do not imitate a living artist or existing film franchise; no invented facts, statistics, quotes or claims; narration is clean spoken text, without camera directions; match total narration to about {duration} seconds and use natural pauses.
"""
    try:
        r=requests.post(f"{ollama_url.rstrip('/')}/api/generate",json={"model":model,"prompt":prompt,"stream":False,"format":"json","think":False,"options":{"num_predict":1300}},timeout=(4,180))
        r.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("Ollama servisine bağlanılamıyor. Ayarlar bölümünden Ollama'yı başlatıp bağlantıyı yeniden kontrol edin.") from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("Ollama yanıt süresi doldu. Daha küçük bir model veya daha kısa bir senaryo deneyin.") from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Ollama API hatası: {exc}") from exc
    import json
    data=json.loads(r.json().get("response","{}"))
    if not isinstance(data,dict) or not str(data.get("script","")).strip():
        raise RuntimeError("Yerel model geçerli senaryo üretemedi.")
    data["title"]=str(data.get("title",topic))[:180]
    data["script"]=str(data["script"]).strip()[:12000]
    data["scenes"]=data.get("scenes",[]) if isinstance(data.get("scenes",[]),list) else []
    data["hashtags"]=data.get("hashtags",[]) if isinstance(data.get("hashtags",[]),list) else []
    return data

def create_voiceover(text: str, voice: str, output: Path):
    if voice not in VOICE_CATALOG: raise ValueError("Desteklenmeyen ses seçimi.")
    if not text.strip() or len(text)>12000: raise ValueError("Seslendirilecek metin boş veya çok uzun.")
    try: import edge_tts
    except ImportError as exc: raise RuntimeError("edge-tts kurulu değil. requirements.txt bağımlılıklarını yükleyin.") from exc
    async def render():
        communicate=edge_tts.Communicate(text=text,voice=voice,rate="+0%",volume="+0%")
        await communicate.save(str(output))
    asyncio.run(render())
    if not output.is_file() or output.stat().st_size<1024: raise RuntimeError("Ses dosyası oluşturulamadı.")
    return output
