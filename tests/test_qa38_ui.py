from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_autopilot_page_contains_queue_health_and_worker_monitor():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
    for element_id in (
        "refreshQueue", "queueQueued", "queueRunning", "queueCompleted",
        "queueFailed", "queueWorkers", "queueConcurrency", "queueWorkerList",
        "queueTaskList", "queueMonitorFeedback",
    ):
        assert f'id="{element_id}"' in html
    assert "async function loadQueueMonitor()" in script
    assert "/api/queue/health" in script
    assert "/api/queue/tasks?limit=12" in script
    assert 'data-queue-retry' in script
    assert "queue-stat-grid" in styles
    assert "@media(max-width:560px)" in styles


def test_index_and_service_worker_use_qa38_asset_versions():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    worker = (ROOT / "web" / "sw.js").read_text(encoding="utf-8")
    assert "style.css?v=v180qa38" in html
    assert "app.js?v=v180qa38" in html
    assert "yaman-viral-studio-shell-v1.8.0-qa38-1" in worker
    assert "style.css?v=v180qa38" in worker
    assert "app.js?v=v180qa38" in worker
