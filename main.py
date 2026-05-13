from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from scheduler import start_scheduler, scheduler, poll_cbse
from state import init_db, get_history
from ws_manager import manager
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="CBSE Monitor", lifespan=lifespan)

# ── REST endpoints ────────────────────────────────────────────

@app.get("/status")
async def status():
    """Current scheduler health + next run time."""
    job = scheduler.get_job("cbse_poll")
    return {
        "running": scheduler.running,
        "next_run": str(job.next_run_time) if job else None,
        "target_url": settings.target_url,
    }

@app.get("/history")
async def history():
    """All previously detected result links."""
    return get_history()

@app.get("/poll/now")
async def force_poll():
    """Manually trigger a scrape immediately."""
    await poll_cbse()
    return {"message": "Poll triggered"}

@app.put("/config/interval/{seconds}")
async def update_interval(seconds: int):
    """Hot-update the polling interval without restart."""
    scheduler.reschedule_job(
        "cbse_poll", trigger="interval", seconds=seconds
    )
    return {"interval_seconds": seconds}

# ── WebSocket endpoint ────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()   # keep connection alive; client can send pings
    except WebSocketDisconnect:
        manager.disconnect(ws)

# ── Minimal test UI ───────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html><head><title>CBSE Monitor</title></head>
    <body style="font-family:sans-serif;padding:2rem">
      <h2>CBSE Result Monitor</h2>
      <div id="status" style="padding:1rem;background:#f0f0f0;border-radius:8px">Connecting…</div>
      <script>
        const ws = new WebSocket(`ws://${location.host}/ws`);
        ws.onmessage = e => {
          const data = JSON.parse(e.data);
          if (data.event === "result_found") {
            document.getElementById("status").innerHTML =
              `<strong>🎉 Result found!</strong><br>${data.title}<br>
               <a href="${data.url}" target="_blank">${data.url}</a>`;
          }
        };
        ws.onopen = () => document.getElementById("status").textContent = "✅ Connected — waiting for results…";
        ws.onclose = () => document.getElementById("status").textContent = "❌ Disconnected";
      </script>
    </body></html>
    """