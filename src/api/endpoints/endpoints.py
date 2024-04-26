# from fastapi import APIRouter, Request, status
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from ssl import create_default_context
# from email.mime.text import MIMEText
import os
import asyncio
import smtplib
import imaplib
import time
from email.message import EmailMessage
# from src.configs import *
# from src.constants import MAIL_HOST, MAIL_USERNAME, MAIL_PASSWORD, MAIL_PORT, MAIL_TO, TEXT_REPLACEMENTS, MAIL_CC
from src.utils import template_processing
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from .validators import load_validate
import shutil
import datetime as dt
from src.parsing_excel.parsing_excel import parsing_excel 
from src.utils import load_file
from src.configs import *
from src.constants import (
    AMOUNT_ROW,
    AMOUNT_A,
    AMOUNT_ROW_TOTAL,
    AMOUNT_A_TOTAL,
    ARENDA_AMOUNT_ROW,
    BASE_DIR,
    DEBIT_AMOUNT_ROW,
    DT_FORMAT,
    MAIL_HOST, MAIL_USERNAME, MAIL_PASSWORD, MAIL_PORT, MAIL_TO, TEXT_REPLACEMENTS, MAIL_CC
)

configure_logging()

router = APIRouter()

MAIL_TEXT = "Тестовое письмо"
MAIL_SUBJECT = "Тема письма"

file = "XXXX.pdf"
lease_contract_nomber = "1"
lessee = "АвагянВО"
lease_contract_date = "01.02.2021"

@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post('/mail')
async def send_mail():
    file = await template_processing(lessee, lease_contract_nomber, lease_contract_date)
    msg = EmailMessage()
    msg['Subject'] = MAIL_SUBJECT
    msg['From'] = MAIL_HOST
    msg['To'] = MAIL_TO
    msg['Cc'] = MAIL_CC
    msg.set_content(MAIL_TEXT)

    downloads_dir = BASE_DIR/"send_files"
    with open(downloads_dir/file, 'rb') as f:
        file_data = f.read()
    msg.add_attachment(file_data, maintype="application", subtype="application/pdf", filename=file)

    with smtplib.SMTP_SSL('smtp.mail.ru', MAIL_PORT) as smtp:
        smtp.login(MAIL_HOST, MAIL_PASSWORD)
        smtp.send_message(msg)

    # imap = imaplib.IMAP4('smtp.mail.ru', 143)                     # Подключаемся в почтовому серверу
    # imap.login(MAIL_HOST, MAIL_PASSWORD)                        # Логинимся в свой ящик
    # imap.select('Sent')                                       # Переходим в папку Исходящие
    # imap.append('Sent', None,                                 # Добавляем наше письмо в папку Исходящие
    #             imaplib.Time2Internaldate(time.time()),
    #             msg.as_bytes())
 
    return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/files', response_class=HTMLResponse)
async def upload_load_files(request: Request):
    return templates.TemplateResponse("upload_load_files.html", {"request": request})


@router.post('/upload_files')
async def upload_files(files: list[UploadFile]):
    load_validate(files)
    result = []
    for file in files:
        downloads_dir = BASE_DIR/"downloads"
        downloads_dir.mkdir(exist_ok=True)

        with open(downloads_dir/file.filename,"wb+") as buffer:
            try:
                shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise e

        result.append(file)

    parsing_excel(AMOUNT_ROW_TOTAL, AMOUNT_ROW, AMOUNT_A, AMOUNT_A_TOTAL, ARENDA_AMOUNT_ROW, DEBIT_AMOUNT_ROW)
    path = BASE_DIR/"downloads"
    files_dir = os.listdir(path)
    return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/download_file')
async def download_file():
    downloads_dir = BASE_DIR/"downloads"
    downloads_dir.mkdir(exist_ok=True)
    files_dir = os.listdir(downloads_dir)
    try:
        return FileResponse(f"{downloads_dir}/Arenda_2024.xlsx", media_type = "xlsx", filename="Arenda_2024.xlsx")
    except Exception as e:
        raise FileNotFoundError(f"File '{downloads_dir}/Arenda_2024.xlsx' not found")


    

