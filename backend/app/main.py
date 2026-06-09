from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api import router
from backend.app.database import Base, engine

try:
    Base.metadata.create_all(bind=engine)
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
