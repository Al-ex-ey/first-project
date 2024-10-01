# from fastapi import APIRouter, Request, status
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from ssl import create_default_context
# from email.mime.text import MIMEText
import os
import logging
import hmac
import hashlib
import urllib.parse
# from email.message import EmailMessage
# from src.utils import template_processing
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, Request, UploadFile, status, HTTPException
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
    info_validation,
    # verify_telegram_signature,
    get_current_user,
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
    USER_ID,
    BOT_TOKEN,
    # MAIL_HOST, MAIL_USERNAME, MAIL_PASSWORD, MAIL_PORT, MAIL_TO, TEXT_REPLACEMENTS, MAIL_CC,
)


templates = Jinja2Templates(directory="src/templates")

configure_logging()

router = APIRouter()


@router.get('/t_login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("t_login.html", {"request": request})


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("user_id")
    return response


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    # current_user = await get_current_user(request)
    # if current_user is None: 
    #     return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
    return templates.TemplateResponse("index.html", {"request": request})


@router.get('/result', response_class=HTMLResponse)
async def result(request: Request):
    current_user = await get_current_user(request)
    if current_user is None: 
        return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
    return templates.TemplateResponse("result.html", {"request": request})


@router.get('/files', response_class=HTMLResponse)
async def upload (request: Request):
    current_user = await get_current_user(request)
    if current_user is None: 
        return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
    return templates.TemplateResponse("upload_files.html", {"request": request})


@router.post('/upload_files', response_class=HTMLResponse)
async def upload_files(files: list[UploadFile], request: Request, error_message: str = None):
    current_user = await get_current_user(request)
    if current_user is None: 
        return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
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
    current_user = await get_current_user(request)
    if current_user is None: 
        return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
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
    
    
@router.get('/download_logs')
async def download_logs(request: Request):
    # current_user = await get_current_user(request)
    # if current_user is None: 
    #     return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
    downloads_dir = BASE_DIR/"logs"
    downloads_dir.mkdir(exist_ok=True)
    files_dir = os.listdir(downloads_dir)
    if "parsing_excel_log.log" in files_dir:
        try:
            return FileResponse(f"{downloads_dir}/parsing_excel_log.log", media_type = "log", filename="parsing_excel_log.log")
        except Exception as e:
            raise FileNotFoundError(f"File in '{downloads_dir}/parsing_excel_log.log' not found")
    else:
        return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)


@router.get('/mail', response_class=HTMLResponse)
async def mail(request: Request, current_user: int = Depends(get_current_user)):
    current_user = await get_current_user(request)
    if current_user is None: 
        return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
    return templates.TemplateResponse("mail.html", {"request": request, "user_id": current_user})


@router.get('/send_reminder/{key}', response_class=HTMLResponse)
async def send_reminder(request: Request, key: str):
    current_user = await get_current_user(request)
    if current_user is None: 
        return templates.TemplateResponse("/t_login.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
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


# Эндпоинт для обработки колбэка от Telegram
@router.get("/auth/telegram/callback")
async def telegram_callback(request: Request):
    # data = request.query_params._dict  # Получаем параметры запроса как словарь
    # if not verify_telegram_signature(data):
    #     raise HTTPException(status_code=403, detail="Invalid hash")
    # logging.info(f'==================================data==={data}==========================================\n')
    # user_id = int(data['id'])
    # logging.info(f'=================================user_id==={user_id}=======================================\n')
    # if user_id not in USER_ID:
    #     logging.info(f'=================================USER_ID==={USER_ID}=======================================\n')
    #     # raise HTTPException(status_code=403, detail="User not allowed")
    #     return RedirectResponse(url="/t_login", status_code=status.HTTP_303_SEE_OTHER)

    # # Сохранение user_id в кэше
    # await save_dictionary_list_to_cache(cache_name="user_cache", dictionary_list=user_id)
    # logging.info(f'=================================await get_dictionary_list_from_cashe(cache_name="user_cache")==={await get_dictionary_list_from_cashe(cache_name="user_cache")}=======================================\n')
    # # Установка куки с user_id для дальнейшей аутентификации
    # response = RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    # response.set_cookie(key="user_id", value=str(user_id), httponly=True)
    # logging.info(f'=================================request.cookies.get("user_id")==={request.cookies.get("user_id")}=======================================\n')
    # return response
    # Получаем данные из запроса
    data = request.query_params
    hash = data.get("hash")
    
    # Удаляем параметр hash из данных для проверки
    data_without_hash = data.copy()
    data_without_hash.pop("hash")
    
    # Сортируем параметры по ключам
    sorted_data = sorted(data_without_hash.items())
    
    # Создаем строку для проверки
    check_string = '\n'.join(f"{key}={value}" for key, value in sorted_data)
    
    # Получаем токен бота из переменных окружения
    bot_token = BOT_TOKEN
    
    # Создаем подпись
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    generated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    
    # Сравниваем хеши
    if generated_hash != hash:
        raise HTTPException(status_code=403, detail="Invalid hash")
    
    # Проверяем user_id
    user_id = data.get("id")
    if user_id and int(user_id) in USER_ID:
        response = RedirectResponse(url="/")
        response.set_cookie(key="user_id", value=user_id)
        return response
    else:
        return RedirectResponse(url="/t_login")



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
