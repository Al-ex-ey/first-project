import logging
import re
from fastapi import HTTPException
from src.configs import configure_logging


configure_logging()


def load_validate(files: list):
    logging.info(f"==================== load_validate - валидация загруженных файлов! ====================")
    if len(files) < 2 or len(files) > 3:
        raise HTTPException(
            status_code=406,
            detail="File upload failed: needed 3 files!"
        )
    logging.info(f"==================== load_validate - проверка кол-ва загружаемых файлов прошла успешно! ====================") 
    for file in files:
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            raise HTTPException(
            status_code=406,
            detail="File upload failed: file not choised or does not fit .xlsx format!"   
        )
        logging.info(f"==================== load_validate - проверка формата загружаемых файлов прошла успешно! ====================")
        if file.size > 4000000:    
            raise HTTPException(
            status_code=406,
            detail="File upload failed: file size is very big!"
        )
        logging.info(f"==================== load_validate - проверка загружаемых файлов на допустимый объем прошла успешно! ====================")    
    logging.info(f"==================== load_validate - валидация загруженных файлов прошла успешно! ====================\n")


# def filename_validate(file):
#     pattern = re.compile(r'\w+[\-|\.]?\w+')