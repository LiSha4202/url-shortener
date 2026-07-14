from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from src.core.config import settings
from src.core.database.base import Base
from src.core.database.engine import db_engine

from src.api import router as v1_routes

app = FastAPI()

app.include_router(v1_routes)  # Подключение API роутера (src/api/v1/routes)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
