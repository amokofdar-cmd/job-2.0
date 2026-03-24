from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
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
app.include_router(router)

ui_dir = Path(__file__).parent / "ui"
app.mount("/ui-static", StaticFiles(directory=ui_dir), name="ui-static")


@app.get("/")
def health():
    return {"status": "ok", "app": settings.app_name, "ui": "/ui"}


@app.get("/ui", response_class=HTMLResponse)
def ui():
    return (ui_dir / "index.html").read_text(encoding="utf-8")
