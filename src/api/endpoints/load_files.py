from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
# from typing import List
from .validators import load_validate
import shutil
from src.parsing_excel.parsing_excel import parsing_excel 
# from typing import Annotated
# import os
# import re
# import openpyxl
# import logging
# import datetime as dt
# from openpyxl.styles import NamedStyle, Alignment, Font, Border, Side
from src.configs import configure_logging
from src.constants import (
    AMOUNT_ROW,
    AMOUNT_A,
    AMOUNT_ROW_TOTAL,
    AMOUNT_A_TOTAL,
    ARENDA_AMOUNT_ROW,
    BASE_DIR,
    DEBIT_AMOUNT_ROW,
    DT_FORMAT
)


configure_logging()

router = APIRouter()

app = FastAPI()

# staticfiles = StaticFiles(directory="src/front/static")
# app.mount("/static", StaticFiles(directory="src/front/static"), name="static")
templates = Jinja2Templates(directory="src/frontend/templates")


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post('/upload')
def upload_files(files: list[UploadFile]):
    load_validate(files)
    result = []
    for file in files:
        downloads_dir = BASE_DIR/"downloads"
        downloads_dir.mkdir(exist_ok=True)
        with open(downloads_dir/file.filename,"wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result.append(file)
    parsing_excel(AMOUNT_ROW_TOTAL, AMOUNT_ROW, AMOUNT_A, AMOUNT_A_TOTAL, ARENDA_AMOUNT_ROW, DEBIT_AMOUNT_ROW)
    path = f"{BASE_DIR}/downloads/Arenda_2024.xlsx"
    return FileResponse(path) 
    # return result
