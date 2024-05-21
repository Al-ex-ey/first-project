import logging
from src.constants import BASE_DIR, LOG_FORMAT, DT_FORMAT
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings
# from fastapi import FastAPI


class Settings(BaseSettings):
    app_title: str = 'Project MH'
    database_url: str

    class Config:
        env_file = '.env'

settings = Settings() 

def configure_logging():
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parsing_excel_log.log'
    
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(logging.FileHandler(log_file, encoding='utf-8', mode="w"),)
    )

templates = Jinja2Templates(directory="src/templates")
