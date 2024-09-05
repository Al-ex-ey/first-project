from fastapi import FastAPI, HTTPException
from src.api.routers import main_router
from .configs import settings
from src.api.endpoints.error_handlers import http_exception_handler

# import secrets

app = FastAPI(title=settings.app_title)

from fastapi.templating import Jinja2Templates

# secret_key = secrets.token_hex(32)
# app.add_middleware(SessionMiddleware, secret_key=secret_key)

app.include_router(main_router)

app.exception_handler(HTTPException)(http_exception_handler)