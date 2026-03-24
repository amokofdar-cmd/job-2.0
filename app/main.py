from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.api.ui_routes import router as ui_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent / "ui" / "static"
app.mount("/ui/static", StaticFiles(directory=str(static_dir)), name="ui-static")

app.include_router(api_router)
app.include_router(ui_router)


@app.get("/")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "ui": "/app",
        "docs": "/docs",
    }
