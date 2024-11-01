import logging
from fastapi import FastAPI, HTTPException
from src.api.routers import main_router
from .configs import configure_logging, settings
from src.api.endpoints.error_handlers import http_exception_handler


configure_logging()

app = FastAPI(title=settings.app_title)

app.include_router(main_router)

app.exception_handler(HTTPException)(http_exception_handler)

logging.info(f"==================== Приложение запущено! ====================\n\n\n")
