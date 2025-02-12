# from fastapi import APIRouter, Request, status
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from ssl import create_default_context
# from email.mime.text import MIMEText
import os
import logging
import hmac
import hashlib
import time
# from email.message import EmailMessage
# from src.utils import template_processing
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, Request, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote
from .validators import load_validate
import shutil
import datetime as dt
from src.parsing_excel.parsing_excel import parsing_excel 
from src.utils import (
    cache,
    get_dictionary_list_from_cashe,
    save_dictionary_list_to_cache,
    delete_dictionary_list_from_cache,
    wa_message,
    email_message,
    info_validation,
    get_qr_code
    # verify_telegram_signature,
    # get_current_user,
)
from src.configs import configure_logging, settings
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


def delete_files():
    logging.info(f"==================== delete_files - Запущена очистка папки downloads! ====================\n")
    downloads_dir = BASE_DIR/"downloads"
    # Проверяем, существует ли директория
    if downloads_dir.exists() and downloads_dir.is_dir():
        for file in os.listdir(downloads_dir):
            file_path = downloads_dir/file
            try:
                if file_path.is_file():  # Проверяем, является ли путь файлом
                    os.remove(file_path)  # Удаляем файл
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error deleting file {file}: {str(e)}")
        return logging.info(f"==================== Папка downloads очищена! ====================\n")
    else:
        logging.warning(f"==================== Папка downloads не найдена! ====================\n")
        return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)


def check_signature(data: dict, token: str) -> bool:
    logging.info(f"==================== check_signature - Проверка подписи данных от Telegram! ====================\n")
    check_hash = data.pop('hash', None)
    if not check_hash:
        raise Exception("Hash not found in the provided data")
    # string_to_check = '_'.join(sorted_parts)
    data_check_arr = [f"{key}={value}" for key, value in data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(token.encode()).digest()
    # Создаем подпись
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    # Сравниваем подпись
    if not hmac.compare_digest(hash_value, check_hash):
        raise Exception('Data is NOT from Telegram')
    # Проверка времени авторизации
    if (time.time() - int(data['auth_date'])) > 86400:
        raise Exception('Data is outdated')
    logging.info(f"==================== check_signature - Завершено успешно! ====================\n")
    return True


async def get_current_user(request: Request):
    logging.info(f"==================== get_current_user - Проверка авторизации пользователя! ====================\n")
    user_id = await get_dictionary_list_from_cashe("user_id")
    if user_id is None or int(user_id) not in settings.allowed_user_ids:
        logging.warning("Unauthorized access attempt")
        raise HTTPException(status_code=403, detail="Not authorized")
    logging.info(f"==================== get_current_user - Завершено успешно! ====================\n")
    return int(user_id)


@router.get('/t_login', response_class=HTMLResponse)
async def login(request: Request):
    logging.info(f"==================== t_login - Перенаправление на страницу авторизации! ====================\n")
    return templates.TemplateResponse("t_login.html", {"request": request})


@router.get("/logout")
async def logout(request: Request):
    logging.info(f"==================== logout - выход - отчистка кеша, отвязка пользователя! ====================\n")
    delete_files()
    delete_dictionary_list_from_cache("result_table")
    delete_dictionary_list_from_cache("legal_entity")
    delete_dictionary_list_from_cache("user_id")
    return templates.TemplateResponse("index.html", {"request": request})


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    logging.info(f"==================== index - переход на главную страницу! ====================\n")
    return templates.TemplateResponse("index.html", {"request": request})


@router.get('/result', response_class=HTMLResponse)
async def result(request: Request):
    logging.info(f"==================== result - перенаправление на страницу с результатом обработки файлов! ====================\n")
    return templates.TemplateResponse("result.html", {"request": request})


@router.get('/files', response_class=HTMLResponse)
async def upload (request: Request):
    logging.info(f"==================== files - перенаправление на страницу загрузки файлов! ====================\n")
    return templates.TemplateResponse("upload_files.html", {"request": request})


@router.post('/upload_files', response_class=HTMLResponse)
async def upload_files(files: list[UploadFile], request: Request, error_message: str = None):
    logging.info(f"==================== upload_files - загрузка файлов для обработки! ====================\n")
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
        logging.info(f"==================== upload_files - завершено успешно! ====================\n")
        return templates.TemplateResponse("result.html", status_code=status.HTTP_303_SEE_OTHER, context={"request": request, "query_params": query_params})
    return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/download_file')
async def download_file(request: Request):
    logging.info(f"==================== download_file - скачать обработанный файл! ====================\n")
    downloads_dir = BASE_DIR/"downloads"
    downloads_dir.mkdir(exist_ok=True)
    files_dir = os.listdir(downloads_dir)
    if "Arenda_2024.xlsx" in files_dir:
        try:
            logging.info(f"==================== download_file - завершено успешно! ====================\n")
            return FileResponse(f"{downloads_dir}/Arenda_2025.xlsx", media_type = "xlsx", filename="Arenda_2025.xlsx")
        except Exception as e:
            raise FileNotFoundError(f"File in not found")
    else:
        logging.info(f"==================== download_file - завершено НЕ успешно! ====================\n")
    # return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request})
    
    
@router.get('/download_logs')
async def download_logs(request: Request):
# async def download_logs(request: Request, current_user: int = Depends(get_current_user)):
    logging.info(f"==================== download_logs - скачать логи! ====================\n")
    logs_dir = BASE_DIR/"logs"
    logs_dir.mkdir(exist_ok=True)
    files_dir = os.listdir(logs_dir)
    if "parsing_excel_log.log" in files_dir:
        try:
            return FileResponse(f"{logs_dir}/parsing_excel_log.log", media_type = "log", filename="parsing_excel_log.log")
        except Exception as e:
            raise FileNotFoundError(f"File in not found")
    else:
        logging.info(f"==================== download_logs - завершено НЕ успешно! ====================\n")
    # return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request})
    # return templates.TemplateResponse("index.html", {"request": request, "user_id": current_user})


@router.get('/mail', response_class=HTMLResponse)
async def mail(request: Request):
# async def mail(request: Request, current_user: int = Depends(get_current_user)):
    logging.info(f"==================== mail - Переход на страницу отправки почты! ====================\n")
    return templates.TemplateResponse("mail.html", {"request": request})
    # return templates.TemplateResponse("mail.html", {"request": request, "user_id": current_user})


@router.get('/send_reminder/{key}', response_class=HTMLResponse)
async def send_reminder(request: Request, key: str):
# async def send_reminder(request: Request, key: str,current_user: int = Depends(get_current_user)):
    logging.info(f"==================== send_reminder - Отправка уведомления! ====================\n")
    qr_code_path = BASE_DIR/"static"/"qr_code"/"qr_code.png"
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
        if validation_info["send_remainder_text"] is not None and validation_info["phone_number"] is not None:
            if not os.path.exists(qr_code_path):
                # return templates.TemplateResponse("qr_code.html", {"request": request, "user_id": current_user})
                return RedirectResponse(url="/qr_code", status_code=status.HTTP_303_SEE_OTHER)
            await wa_message(
                send_remainder_text = validation_info["send_remainder_text"],
                phone_number = validation_info["phone_number"],
            )
            wa_mes = "Сообщение отправлено"
        if validation_info["send_remainder_text"] is not None and validation_info["ul"] is not None and validation_info["email"] is not None:
            await email_message(
                send_remainder_text = validation_info["send_remainder_text"],
                email = validation_info["email"],
                ul = validation_info["ul"],
                arenator = arenator,
            )
            logging.info(f"==================== send_reminder - Отправка уведомления для пользователя {arenator} выполнена! ====================\n")
            email_mes = "Сообщение отправлено"

    logging.info(f"-----Whatsapp: {wa_mes}, ------Email: {email_mes}\n")
    return f"Whatsapp: {wa_mes}, Email: {email_mes}"


@router.get('/qr_code', response_class=HTMLResponse)
async def qr_code(request: Request):
# async def qr_code(request: Request, current_user: int = Depends(get_current_user)):
    logging.info(f"==================== qr_code - Переход на страницу получения QR кода! ====================\n")
    qr_code_path = get_qr_code()
    return templates.TemplateResponse("qr_code.html", {"request": request, "qr_code_path": qr_code_path})
    # return templates.TemplateResponse("qr_code.html", {"request": request, "user_id": current_user, "qr_code_path": qr_code_path})


@router.post('/send_mail', response_class=HTMLResponse)
async def mail(request: Request):
    logging.info(f"==================== send_mail - Отправка почтового сообщения! ====================\n")
    pass


@router.post('/send_messege', response_class=HTMLResponse)
async def send_massege(request: Request):
    logging.info(f"==================== send_messege - Отправка сообщения! ====================\n")
    pass


# Эндпоинт для обработки колбэка от Telegram
@router.get("/auth/telegram/callback")
async def telegram_callback(request: Request):
    logging.info(f"==================== auth - авторизация пользователя через Telegram Login Widget! ====================\n")
    data = request.query_params
    decoded_data = {key: unquote(value) for key, value in data.items()}
    user_id = decoded_data.get("id")
    token = settings.bot_token
    # Проверка подписи
    if not check_signature(decoded_data, token):
        logging.info(f"==================== auth - check_signature - ошибка подписи! ====================\n")
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    if user_id and int(user_id) in settings.allowed_user_ids:
        await save_dictionary_list_to_cache("user_id", user_id)  # Сохраняем user_id в кэш
        user_id_saved = await get_dictionary_list_from_cashe("user_id")
        response = RedirectResponse(url="/")
        logging.info(f"==================== auth - авторизация прошла успешно! ====================\n")
        return response
    else:
        logging.info(f"==================== auth - авторизация прошла НЕ успешно! ====================\n")
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    
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
