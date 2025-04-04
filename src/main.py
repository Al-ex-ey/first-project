import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from selenium import webdriver
from src.api.routers import main_router
from .configs import configure_logging, settings
from src.api.endpoints.error_handlers import http_exception_handler


configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при старте
    app.state.driver = None
    yield
    # Очистка при завершении
    if app.state.driver:
        app.state.driver.quit()

app = FastAPI(title=settings.app_title, lifespan=lifespan)

app.include_router(main_router)

app.exception_handler(HTTPException)(http_exception_handler)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

logging.info(f"==================== Приложение запущено! ====================\n\n\n")
