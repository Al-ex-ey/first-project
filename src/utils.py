import datetime as dt
import logging
import hmac
import hashlib
# import pyautogui
import re
import smtplib
import time
import  webbrowser
from enum import Enum
from email.message import EmailMessage
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr, ValidationError
from cachetools import TTLCache
from urllib.parse import quote
from src.constants import (
    MAIL_PORT,
    MAIL_PASSWORD,
    BOT_TOKEN,
)
from src.configs import configure_logging

templates = Jinja2Templates(directory="src/templates")

cache = TTLCache(maxsize=3, ttl=3600)
configure_logging()
now = dt.datetime.now()

router = APIRouter()

class Organizations(Enum):
    PROSPEKTNEDVIGIMOST = "Проспект недвижимость"
    KORPORACIA = "Корпорация"


def is_valid_email(email: str) -> bool:
    # проверка формата электронной почты
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


async def save_dictionary_list_to_cache(cache_name: str, dictionary_list: list | dict):
    cache[cache_name] = dictionary_list
    return logging.info(f"___Словарь сохранен в кеш___")

async def get_dictionary_list_from_cashe(cache_name: str):
    if cache_name in cache:
        logging.info(f"___Запрос словаря из кеша___")
        return cache[cache_name]
    else:
        return logging.info(f"____Словарь в кеше не найден___")
    

async def info_validation(**kwargs):
    if not kwargs:
        logging.info(f"___Параметры не переданы___")
        return HTTPException(status_code=400, detail="Параметры не переданы")
    validation_info: dict = {}
    for kwarg in kwargs:
        validation_info[kwarg] = None

    if 'phone_number' in kwargs:
        phone_number = kwargs['phone_number']
        if isinstance(phone_number, str):
            # phone_pattern = re.compile(r'\+7\d{10}')
            pattern = re.compile(r'\D')
            c:str = re.sub(pattern, '', phone_number)
            if len(c) >= 10:
                number = c[-10:]
                phone_number_re = f"+7{number}"
                validation_info["phone_number"] = phone_number_re

    if 'send_remainder_text' in kwargs:
        send_remainder_text = kwargs['send_remainder_text']
        if isinstance(send_remainder_text, str):
            validation_info["send_remainder_text"] = send_remainder_text

    if 'email' in kwargs:
        email: EmailStr | list[EmailStr] = kwargs['email']
        validation_info["email"] = email

    if 'ul' in kwargs:
        ul = kwargs['ul']
        if isinstance(ul, str):
            ul_list = await get_dictionary_list_from_cashe(cache_name="legal_entity")
            if ul_list and ul_list is not None:
                if ul in (org.value for org in Organizations):
                    ul_name = Organizations(ul).name
                    le: list = None 
                    for key in ul_list.keys():
                        if key == ul_name:
                            le = ul_list[key]
                    validation_info["ul"] = le

    return validation_info


# async def wa_message(send_remainder_text: str, phone_number: str):
#     send_remainder_text = quote(send_remainder_text)
#     # phone_pattern = re.compile(r'\+7\d{10}')
#     # if not re.search(phone_pattern, phone_number):
#     #     pattern = re.compile(r'\D')
#     #     c:str = re.sub(pattern, '', phone_number)
#     #     if len(c) < 10:
#     #         raise HTTPException(status_code=400, detail="Некорректный номер телефона")
#     #     nomber = c[-10:]
#     # phone_number_re = f"+7{nomber}"
#     # print(f"{phone_number_re}\n")
#     webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_number}&text={send_remainder_text}")
#     time.sleep(15)
#     # screen_width, screen_height = pyautogui.size()
#     # pyautogui.click(screen_width/2, screen_height/2)
#     # pyautogui.press("enter")
#     time.sleep(2)
#     pyautogui.hotkey("ctrl", "w")
#     logging.info(f"___Напоминание отправлено на WhatsApp, на номер {phone_number}\n")
#     return 


async def email_message(send_remainder_text: str, email: EmailStr | list[EmailStr], ul: list, arenator: str):
    # print(f"{email} --- {send_remainder_text} --- {ul} --- {arenator}\n")
    # ul_list = await get_dictionary_list_from_cashe(cache_name="legal_entity")
    # if not ul_list or ul_list is None:
    #     raise "Организация не найдена"
    # print(f" ------------ {ul_list} ------------------\n")
    # try:
    #     le_name = Organizations(ul).name
    #     le = None 
    #     for key in ul_list.keys():
    #         if key == le_name:
    #             le = ul_list[key]
    #     if le is None:
    #         raise logging.error(f"______Организация в списке не найдена")
    # except Exception:
    #     logging.error(f"______Организация в списке не найдена")
    #     raise

    msg = EmailMessage()
    msg['Subject'] = f"Внимание! Напоминаю о задолженности по арендным платежам! {ul[0]} - {arenator}"
    msg['From'] = ul[5]
    msg['To'] = email
    msg['Cc'] = ul[5]
    msg.set_content(send_remainder_text)

    with smtplib.SMTP_SSL('smtp.mail.ru', MAIL_PORT) as smtp:
        smtp.login(ul[5], MAIL_PASSWORD)
        smtp.send_message(msg)

    logging.info(f"___Напоминание отправлено на эл. почту, для {arenator} от {ul[0]}\n")
    return 


# async def template_processing(lessee, lease_contract_nomber, lease_contract_date):
#     document_templates_dir = BASE_DIR/"document_templates"
#     document_output_dir = BASE_DIR/"send_files"
#     template_filename = "Template_notification of late payments.docx"
#     output_filename = f"{lessee}_уведомление о повышении арендной платы по договору №{lease_contract_nomber} от {lease_contract_date}.docx"
#     doc = DocxTemplate(document_templates_dir/template_filename)
#     doc.render(TEXT_REPLACEMENTS)
#     doc.save(document_output_dir/output_filename)
#     return output_filename


# Функция проверки подписи от Telegram
def verify_telegram_signature(data: dict) -> bool:
    hash_str = ''.join(f'{key}={value}\n' for key, value in sorted(data.items()) if key != 'hash')
    computed_hash = hmac.new(BOT_TOKEN.encode(), hash_str.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_hash, data['hash'])


# Зависимость для проверки аутентификации
async def get_current_user(request: Request):
    # Получаем user_id из куки
    user_id = request.cookies.get("user_id")  
    user_cache = await get_dictionary_list_from_cashe(cache_name="user_cache")
    if not user_id or user_id is None or int(user_id) not in user_cache:
        return None
    return int(user_id)
