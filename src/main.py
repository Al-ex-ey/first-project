from fastapi import FastAPI
from src.api.routers import main_router
from .configs import settings
from starlette.middleware.sessions import SessionMiddleware

import secrets

app = FastAPI(title=settings.app_title)

secret_key = secrets.token_hex(32)
app.add_middleware(SessionMiddleware, secret_key=secret_key)

app.include_router(main_router)
