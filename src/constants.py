import datetime as dt
import os
import json

from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

now = dt.datetime.now()

BASE_DIR = Path(__file__).parent
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATE_NOW = '%d.%m.%Y'


""" Переменные parsing_excel"""
AMOUNT_ROW: int = 0  # кол-во обработанных строк в файле с арендаторами - не пустые и не заголовки
AMOUNT_A: int = 0  # кол-во обработанных арендаторов в файле с арендаторами
AMOUNT_ROW_TOTAL: int = 0  # кол-во строк в файле с арендаторами
AMOUNT_A_TOTAL: int = 0  # кол-во строк с арендаторами
ARENDA_AMOUNT_ROW: int = 333  # примерное кол-во строк в файле Arenda 
DEBIT_AMOUNT_ROW: int = 2900  # примерное кол-во строк в файле debet


""" Переменные mail"""
MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_TO = os.getenv("MAIL_TO")
MAIL_CC = os.getenv("MAIL_CC")


""" Переменные auth"""
BOT_TOKEN = os.getenv("BOT_TOKEN")
# ALLOWED_USER_IDS = json.loads(os.getenv("USER_IDS", "[]"))
# USER_ID = set(ALLOWED_USER_IDS)
# ALLOWED_USER_IDS = list(map(int, os.getenv("USER_IDS").split(',')))

# TEXT_REPLACEMENTS = {
#     "lessor_name": "АО «Проспект недвижимость»",
#     "lessor_id": "ИНН 4401132298    ОГРН 1124401001867",
#     "lessor_adress": "156016г. Кострома, м/р-н Давыдовский-2, д.41, кв.72",
#     "doc_date": now.strftime(DATE_NOW),
#     "lessee_name": "ИП Авагян Вергине Ониковна",
#     "lessee_id": "ИНН 370603525843, ОГРНИП 315370600003096",
#     "lessee_adress": "155912, Ивановская обл., Шуйский район,\nг. Шуя,ул.Чехова, 65",
#     "lessee_email": "avag-111@yandex.ru",
#     "lessee_contract_nomber": "1",
#     "lessee_contract_date": "01.02.2021",
#     "leased_property": "земельный участок",
#     "leased_property_adress": "Ивановская область, г. Иваново, ул. Фрунзе, 66, общей площадью 10 кв.м.",
#     "contract_clause": "4.2.",
#     "rent_increase_date": "01.05.2024",
#     "percentage_increase": "10",
#     "new_rent": "19`965",
#     "director": "И.В. Синкина",
# }

LEGAL_ENTITY: list = {
    "KONSTRUKTIV": [],
    "KORPORACIA": [
        "АО «Корпорация»",
        "ИНН 0000000000",
        "ОГРН 0000000000000",
        "156000г. Кострома, ХХХХХХХХХХХХХХХХХХХ, д.ХХХ",
        "Х.Х. Бывших",
        "alexey01_01_0001@mail.ru",
    ],
    "AKTIV-1": [],
    "KVARTAL": [],
    "VENDEKS": [],
    "STRATEGIA": [],
    "RUSSKIY_ALIANS": [],
    "PRESTIZH": [],
    "IMPERATIV": [],
    "LEGAT": [],
    "RENTA_PLUS": [],
    "TREPOV_D_E": [],
    "PROSPEKT_NEDVIGIMOST": [
        "АО «Проспект недвижимость»",
        "ИНН 4401132298",
        "ОГРН 1124401001867",
        "156016г. Кострома, м/р-н Давыдовский-2, д.41, кв.72",
        "И.В. Синкина",
        "alexey01_01_0001@mail.ru",
    ],
    "ARENDA_PLUS": [],
    "LIZHOLD": [],
}