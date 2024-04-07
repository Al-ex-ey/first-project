from fastapi import APIRouter, FastAPI, Request, UploadFile, HTTPException, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from .validators import load_validate
import shutil
import datetime as dt
from src.parsing_excel.parsing_excel import parsing_excel 
import os
from src.configs import *
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


@router.get('/', response_class=HTMLResponse)
async def upload_load_files(request: Request):
    return templates.TemplateResponse("upload_load_files.html", {"request": request})


@router.post('/upload_files')
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
    return FileResponse(path, media_type = "xlsx", filename="Arenda_2024.xlsx")


@router.get('/load_file')
def load_file():
    path = BASE_DIR/"downloads"
    files_dir = os.listdir(path)
    if "Arenda_2024.xlsx" in files_dir:
       return FileResponse(f"{path}/Arenda_2024.xlsx", media_type = "xlsx", filename="Arenda_2024.xlsx")
    else:
        raise HTTPException(status_code=404, detail="File not found")
