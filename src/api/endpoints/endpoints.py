# from fastapi import APIRouter, Request, status
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from ssl import create_default_context
# from email.mime.text import MIMEText
import os
import json
import logging
# from email.message import EmailMessage
# from src.utils import template_processing
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Form, status, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from .validators import load_validate
import shutil
import datetime as dt
from src.parsing_excel.parsing_excel import parsing_excel 
from src.utils import (
    cache,
    get_dictionary_list_from_cashe,
    save_dictionary_list_to_cache,
    # wa_message,
    email_message,
    info_validation
)
from src.configs import configure_logging
from src.constants import (
    AMOUNT_ROW,
    AMOUNT_A,
    AMOUNT_ROW_TOTAL,
    AMOUNT_A_TOTAL,
    ARENDA_AMOUNT_ROW,
    BASE_DIR,
    DEBIT_AMOUNT_ROW,
    DT_FORMAT,
    LEGAL_ENTITY,
    # MAIL_HOST, MAIL_USERNAME, MAIL_PASSWORD, MAIL_PORT, MAIL_TO, TEXT_REPLACEMENTS, MAIL_CC,

)


templates = Jinja2Templates(directory="src/templates")

configure_logging()

router = APIRouter()

@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get('/result', response_class=HTMLResponse)
async def result(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})


@router.get('/files', response_class=HTMLResponse)
async def upload (request: Request):
    return templates.TemplateResponse("upload_files.html", {"request": request})


@router.post('/upload_files', response_class=HTMLResponse)
async def upload_files(files: list[UploadFile], request: Request, error_message: str = None):
    load_validate(files)
    file_list = []
    for file in files:
        downloads_dir = BASE_DIR/"downloads"
        downloads_dir.mkdir(exist_ok=True)
        with open(downloads_dir/file.filename,"wb+") as buffer:
            try:
                shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise e
        file_list.append(file)

    try:
        query_params = parsing_excel(AMOUNT_ROW_TOTAL, AMOUNT_ROW, AMOUNT_A, AMOUNT_A_TOTAL, ARENDA_AMOUNT_ROW, DEBIT_AMOUNT_ROW)
    except Exception:
        raise HTTPException(status_code=404, detail="Ошибка. Проверьте, что файл существует, не поврежден, не защищен от записи и в нем есть страницы!")

    result_table: list = query_params.get("result_table", [])
    await save_dictionary_list_to_cache(cache_name="result_table", dictionary_list=result_table)
    legal_entity: list = LEGAL_ENTITY
    await save_dictionary_list_to_cache(cache_name="legal_entity", dictionary_list=legal_entity)

    path = BASE_DIR/"downloads"
    files_dir = os.listdir(path)
    if "Arenda_2024.xlsx" in files_dir:
        return templates.TemplateResponse("result.html", status_code=status.HTTP_303_SEE_OTHER, context={"request": request, "query_params": query_params})
    return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/download_file')
async def download_file(request: Request):
    downloads_dir = BASE_DIR/"downloads"
    downloads_dir.mkdir(exist_ok=True)
    files_dir = os.listdir(downloads_dir)
    if "Arenda_2024.xlsx" in files_dir:
        try:
            return FileResponse(f"{downloads_dir}/Arenda_2024.xlsx", media_type = "xlsx", filename="Arenda_2024.xlsx")
        except Exception as e:
            raise FileNotFoundError(f"File in '{downloads_dir}/Arenda_2024.xlsx' not found")
    else:
        return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/mail', response_class=HTMLResponse)
async def mail(request: Request):
    return templates.TemplateResponse("mail.html", {"request": request})


@router.get('/send_reminder/{key}', response_class=HTMLResponse)
async def send_reminder(request: Request, key: str):
    dictionary_list = await get_dictionary_list_from_cashe(cache_name="result_table")
    if not dictionary_list or dictionary_list is None:
        raise "Пользователь не найден"
    selected_dict: dict = None
    for i in dictionary_list:
        if key == next(iter(i)):
            selected_dict = i
            break

    if not selected_dict or selected_dict is None:
        raise "Сообщение не отправлено"
    arenator = selected_dict[key][0]
    email = selected_dict[key][3]
    phone_number = selected_dict[key][4]
    ul = selected_dict[key][5]
    send_remainder_text = f"Тест: Сообщение отправлено через web project для {arenator}"

    validation_info = await info_validation(email = email, phone_number = phone_number, ul = ul, send_remainder_text = send_remainder_text)
    wa_mes = "Сообщение не отправлено"
    email_mes = "Сообщение не отправлено"
    if validation_info is not None:
        # if validation_info["send_remainder_text"] is not None and validation_info["phone_number"] is not None:
        #     await wa_message(
        #         send_remainder_text = validation_info["send_remainder_text"],
        #         phone_number = validation_info["phone_number"],
        #     )
        #     wa_mes = "Сообщение отправлено"
        if validation_info["send_remainder_text"] is not None and validation_info["ul"] is not None and validation_info["email"] is not None:
            await email_message(
                send_remainder_text = validation_info["send_remainder_text"],
                email = validation_info["email"],
                ul = validation_info["ul"],
                arenator = arenator,
            )
            email_mes = "Сообщение отправлено"

    logging.info(f"-----Whatsapp: {wa_mes}, ------Email: {email_mes}\n")
    return f"Whatsapp: {wa_mes}, Email: {email_mes}"


@router.post('/send_mail', response_class=HTMLResponse)
async def mail(request: Request):
    pass


@router.post('/send_messege', response_class=HTMLResponse)
async def send_massege(request: Request):
    pass


# @router.post('/send_mail')
# async def send_mail():
#     file = await template_processing(lessee, lease_contract_nomber, lease_contract_date)
#     msg = EmailMessage()
#     msg['Subject'] = MAIL_SUBJECT
#     msg['From'] = MAIL_HOST
#     msg['To'] = MAIL_TO
#     msg['Cc'] = MAIL_CC
#     msg.set_content(MAIL_TEXT)

#     downloads_dir = BASE_DIR/"send_files"
#     with open(downloads_dir/file, 'rb') as f:
#         file_data = f.read()
#     msg.add_attachment(file_data, maintype="application", subtype="application/pdf", filename=file)

#     with smtplib.SMTP_SSL('smtp.mail.ru', MAIL_PORT) as smtp:
#         smtp.login(MAIL_HOST, MAIL_PASSWORD)
#         smtp.send_message(msg)

#     # imap = imaplib.IMAP4('smtp.mail.ru', 143)                     # Подключаемся в почтовому серверу
#     # imap.login(MAIL_HOST, MAIL_PASSWORD)                        # Логинимся в свой ящик
#     # imap.select('Sent')                                       # Переходим в папку Исходящие
#     # imap.append('Sent', None,                                 # Добавляем наше письмо в папку Исходящие
#     #             imaplib.Time2Internaldate(time.time()),
#     #             msg.as_bytes())
 
#     return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)
