from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import engine, Base
from app.api import api_router


# Создаем таблицы при запуске
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при запуске
    Base.metadata.create_all(bind=engine)

    # Создаем директорию для загрузок
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    yield

    # Очистка при завершении
    pass


app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION, lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "QR Scanner System API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
