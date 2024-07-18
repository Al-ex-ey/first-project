# from fastapi import status
# from selenium import webdriver
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
from fastapi import Request
from urllib.parse import quote
import pyautogui
import time
import  webbrowser
from cachetools import TTLCache
from src.constants import PATH_TO_SETTINGS
from src.constants import PHONE_NAMBER 

cache = TTLCache(maxsize=10, ttl=3000)

def send_reminder(send_remainder_text):
    # # настройки браузера для отправки сообщений через WhatsApp Web
    # options = webdriver.ChromeOptions()
    # options.add_argument('--allow-profiles-outside-user-dir')
    # # options.add_argument('--allow-profiles-outside-user-dir') Эта строка добавляет аргумент --allow-profiles-outside-user-dir к настройкам браузера. Он указывает браузеру разрешить использование профилей пользователей вне рабочей директории пользователя.
    # options.add_argument('--enable-profile-shortcut-manager')
    # # options.add_argument('--enable-profile-shortcut-manager') Здесь добавляется аргумент --enable-profile-shortcut-manager к настройкам браузера. Он включает менеджер ярлыков профилей, который обеспечивает удобное управление профилями пользователей.
    # options.add_argument(f'user-data-dir={PATH_TO_SETTINGS}') # Пример: r'user-data-dir=\Users\user\Desktop\test'
    # # options.add_argument(r'user-data-dir=<Путь>') Эта строка добавляет аргумент user-data-dir, который задает путь к директории данных пользователя браузера. Вместо <Путь> вам нужно указать путь к желаемой директории. Это позволяет использовать предварительно настроенные профили или сохранять состояние браузера между запусками.
    # options.add_argument('--profile-directory=Profile 1')
    # # options.add_argument('--profile-directory=Profile 1') Здесь указывается аргумент --profile-directory, определяющий имя профиля, который будет использоваться в браузере. В данном случае, имя профиля установлено как "Profile 1".
    # options.add_argument('--profiling-flush=n')
    # # options.add_argument('--profiling-flush=n') Данная строка добавляет аргумент --profiling-flush к настройкам браузера. Он определяет, как часто происходит сброс данных профилирования. Здесь n представляет числовое значение, указывающее интервал сброса данных.
    # options.add_argument('--enable-aggressive-domstorage-flushing')
    # # options.add_argument('--enable-aggressive-domstorage-flushing') В данной строке добавляется аргумент --enable-aggressive-domstorage-flushing к настройкам браузера. Он включает агрессивную очистку хранилища DOM после каждого тестового случая, что может быть полезным при автоматизации тестирования.
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # wait = WebDriverWait(driver, 30)
    
    # отправка сообщения
    send_remainder_text = quote(send_remainder_text)
    webbrowser.open(f"https://web.whatsapp.com/send?phone={PHONE_NAMBER}&text={send_remainder_text}")
    time.sleep(15)
    screen_width, screen_height = pyautogui.size()
    pyautogui.click(screen_width/2, screen_height/2)
    pyautogui.press("enter")
    time.sleep(3)
    pyautogui.hotkey("win", "w")
    # driver.get(url)
    # wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button')))
    # driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button').click()


async def save_dictionary_list_to_cache(cache_name: str, dictionary_list: list):
    cache[cache_name] = dictionary_list
    return "Словарь сохранен в кэш"

async def get_dictionary_list_from_cashe(cache_name: str):
    if cache_name in cache:
        return cache[cache_name]
    else:
        return "Словарь не найден в кэше"

# async def template_processing(lessee, lease_contract_nomber, lease_contract_date):
#     document_templates_dir = BASE_DIR/"document_templates"
#     document_output_dir = BASE_DIR/"send_files"
#     template_filename = "Template_notification of late payments.docx"
#     output_filename = f"{lessee}_уведомление о повышении арендной платы по договору №{lease_contract_nomber} от {lease_contract_date}.docx"
#     doc = DocxTemplate(document_templates_dir/template_filename)
#     doc.render(TEXT_REPLACEMENTS)
#     doc.save(document_output_dir/output_filename)
#     return output_filename


def parse_keys_to_str(initial_value):
    if isinstance(initial_value, dict):
        return {str(key):value for key,value in initial_value.items()}
    return initial_value

