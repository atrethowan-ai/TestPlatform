from fastapi import FastAPI
from .routes.health import router as health_router
from .routes.attempts import router as attempts_router
from .config import settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request
import os

app = FastAPI(title="Quiz Local Service", version="0.1")

# Mount API routers under /api
app.include_router(health_router)
app.include_router(attempts_router)

# Serve static frontend
frontend_dist = settings.FRONTEND_DIST_PATH.resolve()
if not frontend_dist.exists():
	raise RuntimeError(f"Frontend build directory not found: {frontend_dist}")
app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static-root")

# Catch-all for SPA routing (serves index.html for any non-API, non-asset route)
@app.get("/{full_path:path}")
async def spa_catch_all(request: Request, full_path: str):
	# Only serve index.html for non-API, non-asset routes
	if request.url.path.startswith("/api") or request.url.path.startswith("/assets"):
		return {"detail": "Not found"}
	index_path = frontend_dist / "index.html"
	if index_path.exists():
		return FileResponse(index_path)
	return {"detail": "Frontend not built"}
