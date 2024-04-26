import os
from pathlib import Path
from dotenv import load_dotenv
import datetime as dt

load_dotenv()

now = dt.datetime.now()

BASE_DIR = Path(__file__).parent
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATE_NOW = '%d.%m.%Y'

""" Переменные parsing_excel"""
AMOUNT_ROW = 0  # кол-во обработанных строк в файле с арендаторами - не пустые и не заголовки
AMOUNT_A = 0  # кол-во обработанных арендаторов в файле с арендаторами
AMOUNT_ROW_TOTAL = 0  # кол-во строк в файле с арендаторами
AMOUNT_A_TOTAL = 184  # кол-во строк с арендаторами
ARENDA_AMOUNT_ROW = 333  # примерное кол-во строк в файле Arenda 
DEBIT_AMOUNT_ROW = 2900  # примерное кол-во строк в файле debet

""" Переменные mail"""
MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_TO = os.getenv("MAIL_TO")
MAIL_CC = os.getenv("MAIL_CC")

TEXT_REPLACEMENTS = {
    "lessor_name": "АО «Проспект недвижимость»",
    "lessor_id": "ИНН 4401132298    ОГРН 1124401001867",
    "lessor_adress": "156016г. Кострома, м/р-н Давыдовский-2, д.41, кв.72",
    "doc_date": now.strftime(DATE_NOW),
    "lessee_name": "ИП Авагян Вергине Ониковна",
    "lessee_id": "ИНН 370603525843, ОГРНИП 315370600003096",
    "lessee_adress": "155912, Ивановская обл., Шуйский район,\nг. Шуя,ул.Чехова, 65",
    "lessee_email": "avag-111@yandex.ru",
    "lessee_contract_nomber": "1",
    "lessee_contract_date": "01.02.2021",
    "leased_property": "земельный участок",
    "leased_property_adress": "Ивановская область, г. Иваново, ул. Фрунзе, 66, общей площадью 10 кв.м.",
    "contract_clause": "4.2.",
    "rent_increase_date": "01.05.2024",
    "percentage_increase": "10",
    "new_rent": "19`965",
    "director": "И.В. Синкина",
}
