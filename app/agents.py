
def run_agent_team(llm, job, clip, platforms):
    payload={"clips":job["clips"],"clip":clip,"platforms":platforms}
    def analysis(p):
        ranked=sorted(p["clips"],key=lambda x:x.get("score",0),reverse=True)
        return {"top_clip_ids":[x["id"] for x in ranked[:5]],"signals":["hook","clarity","curiosity","payoff"]}
    def editor(p): return {"aspect_ratio":"9:16","captions":True,"smart_framing":"OpenCV face tracking","clip_id":p["clip"]["id"]}
    def seo(p):
        result={}
        for platform in p["platforms"]:
            prompt="Return JSON title, description, hashtags array. Be accurate. Platform "+platform+". Transcript: "+p["clip"]["text"][:1200]
            try: result[platform]=llm(prompt,timeout=120)
            except Exception: result[platform]={"title":p["clip"].get("title",""),"description":p["clip"]["text"][:350],"hashtags":["#shorts","#reels","#tiktok"]}
        return result
    def publishing(p): return {"state":"export_ready","platforms":p["platforms"],"note":"OAuth authorization is required for real uploads; none performed."}
    tasks={"video-analysis":analysis,"editor":editor,"seo":seo,"publishing":publishing}
    return {name:{"agent":name,"status":"completed","result":fn(payload)} for name,fn in tasks.items()}
