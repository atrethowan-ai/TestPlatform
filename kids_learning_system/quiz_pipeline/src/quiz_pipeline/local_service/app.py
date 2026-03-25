from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.health import router as health_router
from .routes.attempts import router as attempts_router
from .routes.admin import router as admin_router
from .routes.quizzes import router as quizzes_router
from .config import settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request
import os

app = FastAPI(title="Quiz Local Service", version="0.1")
LOCAL_BUILD_STAMP = "2026-03-18T18:20-firefox-debug"


@app.middleware("http")
async def disable_browser_cache(request: Request, call_next):
    # Local dev service should always return fresh assets/data after GUI or content changes.
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Quiz-Build"] = LOCAL_BUILD_STAMP
    return response

# Allow CORS for admin API calls during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers under /api
app.include_router(health_router)
app.include_router(attempts_router)
app.include_router(admin_router)
app.include_router(quizzes_router)

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

