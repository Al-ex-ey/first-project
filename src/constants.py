from pathlib import Path

BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATE_NOW = '%d.%m.%Y'
PATH_A = "C:/Users/user/Desktop/real_debet/arenda_12.2023.xlsx"  #путь до файла с арендаторами
PATH_D = "C:/Users/user/Desktop/real_debet/debet_07.12.2023_18-17.xlsx"  #путь до файла с дебеторкой

""" Переменные проверки"""
AMOUNT_RAW = 0  # кол-во обработанных строк в файле с арендаторами
AMOUNT_A = 0  # кол-во обработанных арендаторов в файле с арендаторами
AMOUNT_RAW_TOTAL = 196  # кол-во строк в файле с арендаторами
AMOUNT_A_TOTAL = 171  # кол-во строк с арендаторами

