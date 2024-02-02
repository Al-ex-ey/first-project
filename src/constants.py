from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATE_NOW = '%d.%m.%Y'
# PATH_A = "C:/Users/user/Desktop/debet_2024/Arenda_2024.xlsx"  #путь до файла с арендаторами
# PATH_D = "C:/Users/user/Desktop/debet_2024/debet_18.01.2024г_16-05.xlsx"  #путь до файла с дебеторкой
ARENDA_AMOUNT_ROW = 333  # примерное кол-во строк в файле Arenda 
DEBIT_AMOUNT_ROW = 2900  # примерное кол-во строк в файле debet

""" Переменные проверки"""

AMOUNT_ROW = 0  # кол-во обработанных строк в файле с арендаторами - не пустые и не заголовки
AMOUNT_A = 0  # кол-во обработанных арендаторов в файле с арендаторами
AMOUNT_ROW_TOTAL = 0  # кол-во строк в файле с арендаторами
AMOUNT_A_TOTAL = 184  # кол-во строк с арендаторами
