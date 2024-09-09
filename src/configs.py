import logging
from src.constants import BASE_DIR, LOG_FORMAT, DT_FORMAT
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Project MH'
    # database_url: str
    # POSTGRES_DB: str
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str``
    # PGADMIN_DEFAULT_EMAIL: str
    # PGADMIN_DEFAULT_PASSWORD: str
    # PGADMIN_CONFIG_SERVER_MODE: str
    # PGADMIN_LISTEN_ADDRESS: str
    # PGADMIN_LISTEN_PORT: int
    # PATH_TO_SETTINGS: str
    # PHONE_NAMBER: str
    # MAIL_PORT: int
    # MAIL_PASSWORD: str
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
