from app.learning import ViralLearningEngine

def sample(fingerprint, platform="youtube", views=100, likes=8, comments=2, shares=1, watch=30, duration=60):
    return {"clip_fingerprint": fingerprint, "platform": platform, "views": views,
            "likes": likes, "comments": comments, "shares": shares,
            "avg_watch_seconds": watch, "video_seconds": duration}

def test_record_returns_engagement_and_retention_rates(tmp_path):
    engine = ViralLearningEngine(tmp_path / "learning.sqlite3")
    result = engine.record(sample("clip-0001"))
    assert result["saved"] is True
    assert result["engagement_rate"] == 0.11
    assert result["retention_rate"] == 0.5

def test_adjustment_waits_for_three_samples(tmp_path):
    engine = ViralLearningEngine(tmp_path / "learning.sqlite3")
    engine.record(sample("clip-0001"))
    engine.record(sample("clip-0002"))
    assert engine.adjustment("youtube") == 0
    engine.record(sample("clip-0003"))
    assert isinstance(engine.adjustment("youtube"), int)

def test_platform_insights_are_isolated(tmp_path):
    engine = ViralLearningEngine(tmp_path / "learning.sqlite3")
    engine.record(sample("yt-000001", "youtube"))
    engine.record(sample("tt-000001", "tiktok", views=200))
    insights = engine.insights()
    assert insights["samples"] == 2
    assert insights["platforms"]["youtube"]["samples"] == 1
    assert insights["platforms"]["tiktok"]["views"] == 200
    assert engine.adjustment("instagram") == 0
