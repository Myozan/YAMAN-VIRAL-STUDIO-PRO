
import sqlite3
class ViralLearningEngine:
    def __init__(self,path):
        self.path=str(path)
        with self.connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS performance(id INTEGER PRIMARY KEY,fingerprint TEXT,platform TEXT,views INTEGER,likes INTEGER,comments INTEGER,shares INTEGER,watch REAL,duration REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    def connect(self): return sqlite3.connect(self.path)
    def record(self,d):
        with self.connect() as c:
            c.execute("INSERT INTO performance(fingerprint,platform,views,likes,comments,shares,watch,duration) VALUES(?,?,?,?,?,?,?,?)",(d["clip_fingerprint"],d["platform"],d["views"],d["likes"],d["comments"],d["shares"],d["avg_watch_seconds"],d["video_seconds"]))
        v=max(d["views"],1)
        return {"saved":True,"engagement_rate":(d["likes"]+d["comments"]+d["shares"])/v,"retention_rate":min(d["avg_watch_seconds"]/max(d["video_seconds"],1),2)}
    def insights(self):
        with self.connect() as c:
            rows=c.execute("SELECT platform,COUNT(*),SUM(views),SUM(likes+comments+shares),AVG(watch/duration) FROM performance GROUP BY platform").fetchall()
            n=c.execute("SELECT COUNT(*) FROM performance").fetchone()[0]
        return {"samples":n,"platforms":{p:{"samples":k,"views":v or 0,"engagement_rate":round((e or 0)/max(v or 0,1),4),"avg_retention":round(r or 0,4)} for p,k,v,e,r in rows}}
    def adjustment(self,platform):
        d=self.insights()["platforms"].get(platform)
        if not d or d["samples"]<3:return 0
        return max(-8,min(8,round((d["avg_retention"]-.5)*20+(d["engagement_rate"]-.04)*100)))
