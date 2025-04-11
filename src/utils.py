import datetime as dt
import logging
import hmac
import hashlib
import os
# import pyautogui
import re
import smtplib
import time
import random
import  webbrowser

from datetime import datetime, timedelta
from enum import Enum
from email.message import EmailMessage
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr, ValidationError
from cachetools import TTLCache
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from src.constants import (
    MAIL_PORT,
    MAIL_PASSWORD,
    BOT_TOKEN,
    BASE_DIR,
    DATE_NOW,
)
from src.configs import configure_logging

templates = Jinja2Templates(directory="src/templates")

cache = TTLCache(maxsize=3, ttl=3600)
configure_logging()
now = dt.datetime.now()
date = now.strftime(DATE_NOW)


router = APIRouter()

# BOT_TOKEN_HASH = hashlib.sha256(BOT_TOKEN.encode()).hexdigest()

class Organizations(Enum):
    PROSPEKTNEDVIGIMOST = "Проспект недвижимость"
    KORPORACIA = "Корпорация"


def is_valid_email(email: str) -> bool:
    logging.info(f"==================== is_valid_email - проверка формата эл. почты! ====================\n")
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


async def save_dictionary_list_to_cache(cache_name: str, dictionary_list: list | dict):
    logging.info(f"==================== save_dictionary_list_to_cache - сохранение словаря в кеш! ====================\n")
    cache[cache_name] = dictionary_list
    return logging.info(f"___Словарь сохранен в кеш___")


async def get_dictionary_list_from_cashe(cache_name: str):
    logging.info(f"==================== get_dictionary_list_from_cashe - получение словаря из кеша! ====================\n")
    if cache_name in cache:
        logging.info(f"==================== get_dictionary_list_from_cashe - завершено успешно - получение словаря из кеша! ====================\n")
        return cache[cache_name]
    else:
        return logging.info(f"==================== get_dictionary_list_from_cashe - завершено НЕ успешно - словарь в кэше НЕ найден! ====================\n")


def delete_dictionary_list_from_cache(cache_name: str):
    logging.info(f"==================== delete_dictionary_list_from_cache - удаление словаря из кеша! ====================\n")
    if cache_name in cache:
        del cache[cache_name]
        logging.info(f"==================== delete_dictionary_list_from_cache - завершено успешно - {cache_name} словарь удален! ====================\n")
    else:
        logging.info(f"==================== delete_dictionary_list_from_cache - завершено НЕ успешно - {cache_name} словарь не найден! ====================\n")


async def info_validation(**kwargs):
    logging.info(f"==================== info_validation - проверка параметров! ====================\n")
    if not kwargs:
        logging.info(f"___Параметры не переданы___")
        return HTTPException(status_code=400, detail="Параметры не переданы")
    validation_info: dict = {}
    for kwarg in kwargs:
        validation_info[kwarg] = None

    if 'phone_number' in kwargs:
        phone_number = kwargs['phone_number']
        logging.info(f"==================== info_validation === phone_number: {phone_number} ====================\n")
        phone_number = str(phone_number)
        pattern = re.compile(r'\D')
        c = re.sub(pattern, '', phone_number)
        logging.info(f"==================== info_validation === c: {c} ====================\n")
        if len(c) >= 10:
            number = c[-10:]
            phone_number_re = f"+7{number}"
            validation_info["phone_number"] = phone_number_re
            logging.info(f"==================== info_validation === phone_number_re: {phone_number_re} ====================\n")
            logging.info(f"==================== info_validation - проверка номера телефона завершена успешно! ====================\n")
        else:
            logging.info(f"==================== info_validation - проверка номера телефона ПРОВАЛЕНА! Кол-во цифр в номере меньше стандарта !====================\n")
    else:
        logging.info(f"==================== info_validation - ппроверка номера телефона ПРОВАЛЕНА! Параметр не передан!====================\n")

    if 'send_remainder_text' in kwargs:
        send_remainder_text = kwargs['send_remainder_text']
        if isinstance(send_remainder_text, str):
            validation_info["send_remainder_text"] = send_remainder_text
            logging.info(f"==================== info_validation - проверка сообщения завершена успешно! ====================\n")

    if 'email' in kwargs:
        email: EmailStr | list[EmailStr] = kwargs['email']
        validation_info["email"] = email
        logging.info(f"==================== info_validation - проверка эл. почты завершена успешно! ====================\n")

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
                    logging.info(f"==================== info_validation - проверка юр. лица завершена успешно! ====================\n")

    return validation_info



def wa_message(request: Request, send_remainder_text: str, phone_number: str) -> bool:
    logging.info(f"==================== wa_message - старт утилиты отправки сообщения через WhatsApp! ====================\n")

    driver = request.app.state.driver
    if not driver:
        logging.info(f"==================== wa_message - драйвер НЕ НАЙДЕН, редирект для сканирования qr-кода! ====================\n")
        return RedirectResponse(url="/qr_code", status_code=status.HTTP_303_SEE_OTHER)

    logging.info(f"==================== wa_message - драйвер найден, отправка сообщения! ====================\n")
    
    delay_sec: float = 2.0
        
    try:
        # 1. Открываем чат напрямую (надежнее поиска)
        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")
        
        start_time = time.time()  # Запоминаем время начала ожидания
        
        time.sleep(random.uniform(4, 6))
        
        # 2. Ждём, пока загрузится интерфейс чата (не только поле ввода)
        try:
            logging.info("Ожидаем загрузку чата...")
            # WebDriverWait(driver, 30).until(
            #     EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Чат"]'))
            # )
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@role="textbox"][@contenteditable="true"]'))
            )
            logging.info("Чат успешно загружен")
        except TimeoutException:
            logging.error("Чат не загрузился за 20 секунд")
            return False
        
        # 2. Ожидание полной загрузки чата
        # WebDriverWait(driver, 60).until(
        #     EC.presence_of_element_located((By.XPATH, '//div[@data-testid="conversation-panel-body"]'))
        # )
        
        # qr_code_path = BASE_DIR/"static"/"qr_code"
        
        # # Ожидание полной загрузки чата
        # wait_time = 0
        # while wait_time < 15:  # Максимальное время ожидания 30 секунд
        #     time.sleep(1)  # Ждем 1 секунду
        #     wait_time += 1
            
        #     if wait_time == 5:
        #         driver.save_screenshot(qr_code_path/"wait_chat_5.png")
        #         logging.info("Скриншот сохранен: wait_chat_5.png")
                
        #     if wait_time == 10:
        #         driver.save_screenshot(qr_code_path/"wait_chat_10.png")
        #         logging.info("Скриншот сохранен: wait_chat_10.png")
            
        #     try:
        #         WebDriverWait(driver, 1).until(
        #             EC.visibility_of_element_located((By.XPATH, '//div[@data-testid="conversation-panel-body"]'))
        #         )
        #         break  # Если элемент найден, выходим из цикла
        #     except:
        #         continue  # Если элемент не найден, продолжаем ожидание
        

        
        # 3. Поиск поля ввода (с явными проверками)
        try:
            logging.info("Ожидаем загрузку поле для ввода сообщения...")
            input_box = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            logging.info("Поле успешно загружено")
        except TimeoutException:
            logging.error("Поле ввода не загрузилось за 60 секунд")
            return False
        
        # input_box = WebDriverWait(driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        # )
        
        elapsed_time = time.time() - start_time  # Вычисляем время ожидания
        logging.info(f"Поле ввода стало доступным за {elapsed_time:.2f} секунд.")
        
        # 4. Эмуляция человеческого ввода
        time.sleep(delay_sec)
        for chunk in [send_remainder_text[i:i+50] for i in range(0, len(send_remainder_text), 50)]:
            input_box.send_keys(chunk)
            time.sleep(0.3)
        
        # 5. Отправка
        input_box.send_keys(Keys.ENTER)
        time.sleep(delay_sec)
        
        # 6. Проверяем, что сообщение ушло (двойная галочка)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-dblcheck"]'))
        )

        logging.info(f"==================== wa_message - Сообщение {send_remainder_text} для {phone_number} отправлено! ====================\n")
        return True
    
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")
        logging.info(f"==================== wa_message - Сообщение {send_remainder_text} для {phone_number} НЕ ОТПРАВЛЕНО !!! ====================\n")
        return False

    finally:
        logging.info(f"==================== wa_message - утилита отправки сообщения через WhatsApp работу закончила! ====================\n")


# def get_qr_code(request: Request):
#     logging.info(f"==================== get_qr_code - утилита делает скриншот страницы с qr-кодом! ====================\n")
#     if request.app.state.driver:
#         logging.info(f"==================== get_qr_code - сессия запущена, сканирование qr-кода не требуется! ====================\n")
#         return False
#     qr_code_path = BASE_DIR/"static"/"qr_code"

#     try:
#         driver = get_chrome_driver()
#         driver.get("https://web.whatsapp.com")

#         # # Ждем загрузки страницы (проверяем по наличию любого значимого элемента)
#         # WebDriverWait(driver, 30).until(
#         #     lambda d: d.execute_script("return document.readyState") == "complete"
#         # )

#         # Добавляем небольшую паузу для гарантированной отрисовки QR-кода
#         time.sleep(random.uniform(7, 12))

#         # Делаем скриншот всей страницы
#         driver.save_screenshot(qr_code_path/"qr_code.png")
#         logging.info(f"Скриншот сохранен в {qr_code_path}\n")
#         return True
#     except Exception as e:
#         logging.error(f"Ошибка при получении скриншота: {str(e)}")
#         return False
    # finally:
    #     if driver:
    #         driver.quit()


def email_message(send_remainder_text: str, email: EmailStr | list[EmailStr], ul: list, arenator: str):
    logging.info(f"==================== email_message - утилита по отправки письма! ====================\n")
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

    try:
        msg = EmailMessage()
        msg['Subject'] = f"Внимание! Напоминаю о задолженности по арендным платежам! {ul[0]} - {arenator}"
        msg['From'] = ul[5]
        msg['To'] = email
        msg['Cc'] = ul[5]
        msg.set_content(send_remainder_text)

        with smtplib.SMTP_SSL('smtp.mail.ru', MAIL_PORT) as smtp:
            smtp.login(ul[5], MAIL_PASSWORD)
            smtp.send_message(msg)

        logging.info(f"==================== email_message - письмо для {arenator} от {ul[0]} отправлено! ====================\n")
        return True
    except Exception as e:
        logging.error(f"Ошибка при отправке email-сообщения: {e}")
        logging.info(f"==================== email_message - письмо для {arenator} от {ul[0]} НЕ ОТПРАВЛЕНО !!! ====================\n")
        return False
    finally:
            logging.info(f"==================== email_message - утилита отправки email-сообщения работу закончила! ====================\n")

def get_chrome_driver(request: Request):
    # Настройка опций для запуска браузера
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--lang=ru-RU,ru;q=0.9")
    
    chrome_options.add_argument("--force-device-scale-factor=1.0")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--window-size=1440,900")
    chrome_options.add_argument("--disable-webrtc")

    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")

    chrome_options.add_argument("--user-data-dir=/tmp/chrome-profile")
    chrome_options.add_argument("--disable-extensions")
    
    # chrome_options.add_argument("--allow-running-insecure-content")
    # chrome_options.add_argument("--ignore-certificate-errors")

    chrome_options.binary_location = "/usr/bin/chromium"

    try:
        request.app.state.driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Chrome(
        #     options=chrome_options,
        #     service=ChromeService(
        #         ChromeDriverManager().install()
        #     )
        # )
        driver = request.app.state.driver

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru']});
            window.chrome = {app: {isInstalled: false}, runtime: {}};
            """
        })
        
            # Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            # window.chrome = {runtime: {}};
        
    except Exception as e:
        logging.error(f"Ошибка при запуске Chrome: {e}")
        raise
    
    return driver


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
# def verify_telegram_signature(data: dict) -> bool:
#     hash_str = ''.join(f'{key}={value}\n' for key, value in sorted(data.items()) if key != 'hash')
#     computed_hash = hmac.new(BOT_TOKEN.encode(), hash_str.encode(), hashlib.sha256).hexdigest()
#     return hmac.compare_digest(computed_hash, data['hash'])


# Зависимость для проверки аутентификации
# async def get_current_user(request: Request):
#     user_id = request.cookies.get("user_id")
#     logging.info(f"==================================== user_id ==={user_id}=======================================\n")
#     user_cache = await get_dictionary_list_from_cashe(cache_name="user_cache")
#     logging.info(f"==================================== user_cache ==={user_cache}=======================================\n")
#     if not user_id or user_id is None or int(user_id) not in user_cache:
#         raise HTTPException(status_code=403, detail="Not authorized")
#     return int(user_id)
