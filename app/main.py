from fastapi import FastAPI
from app.api.routes import router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get("/")
def health():
    return {"status": "ok", "app": settings.app_name}
