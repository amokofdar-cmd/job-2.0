from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = BASE_DIR / "ui" / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

router = APIRouter(tags=["ui"])


@router.get("/app", response_class=HTMLResponse)
def operator_console(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
