from fastapi import FastAPI
from src.api.routers import main_router
from .configs import settings


app = FastAPI(title=settings.app_title)

app.include_router(main_router)
