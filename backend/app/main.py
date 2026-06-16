from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path

from backend.app import database as database_module
from backend.app.api import router
from backend.app.database import Base, ensure_database_ready

try:
    ensure_database_ready()
    Base.metadata.create_all(bind=database_module.engine)
except SQLAlchemyError:
    # Allow the API to boot even if Neon is temporarily unavailable.
    pass

app = FastAPI(title="Real Estate AI Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
