import re
import openpyxl
import logging
# import pandas as pd
import datetime as dt
# from openpyxl.writer.excel import ExcelWriter

DATE_NOW = '%d.%m.%Y'
DATATIME_NOW = '%d.%m.%Y %H:%M:%S'
PATH = "C:/Users/user/Desktop/Arenda_1.xlsx"
""" Переменные проверки"""
AMOUNT_R = 0  # кол-во обработанных строк в файле с арендаторами
AMOUNT_A = 0  # кол-во обработанных арендаторов в файле с арендаторами
AMOUNT_R_TOTAL = 28  # кол-во строк в файле с арендаторами
AMOUNT_A_TOTAL = 24  # кол-во строк с арендаторами в файле с арендаторами

logging.basicConfig(level=logging.INFO, filename="parsing_excel_log.txt",filemode="w")
# logging.basicConfig(level=logging.INFO, filename="/src/logs/parsing_excel_log.log",filemode="w")
now = dt.datetime.now()

try:
    book_arenda = openpyxl.load_workbook(filename=PATH)
    book_debet = openpyxl.load_workbook(filename="C:/Users/user/Desktop/debet_30.11.2023.xlsx")
except:
    logging.ERROR(f"___{now.strftime(DATATIME_NOW)}___Something went wrong when open and reed files")
    raise

sheet_arenda = book_arenda.worksheets[-1]
sheet_debet = book_debet.worksheets[0]

# data = sheet_arenda.values
# df = pd.DataFrame(data)
# df.to_excel('C:/Users/user/Desktop/Arenda_df.xlsx', index=False, header=False, sheet_name=f"{now.strftime(DATE_NOW)}_auto")

try:
    column_list = [1,3,4,5,6]
    for i in reversed(column_list):
        sheet_debet.delete_cols(i)
except:
    logging.ERROR(f"___{now.strftime(DATATIME_NOW)}___Something went wrong when delete columns")
    raise


def find_debet(cell):
    global AMOUNT_A
    for cell_debet in sheet_debet.iter_rows(min_row=11, max_row=3000, min_col=1, max_col=3):
        if cell_debet[0].value == None:
            continue
        pattern_a = re.compile(r'\S+')
        cell_arenda = pattern_a.findall(cell[0].value)
        if len(cell_arenda) < 2:
            cell_arenda = pattern_a.findall(cell[0].value)[0]
        else:
            cell_arenda = pattern_a.findall(cell[0].value)[0] + " " + pattern_a.findall(cell[0].value)[1]
        pattern = re.search(cell_arenda.lower(), cell_debet[0].value.lower())
        cell_downlow = cell[0].offset(column=1)
        for i in range(1, 20):
            cell_debet_downcell = cell_debet[0].offset(row=i)
            try:
                if pattern and (cell_debet_downcell.value.strip() == cell_downlow.value):
                    debet_amount = cell_debet_downcell.offset(column=1)
                    credit_amount = cell_debet_downcell.offset(column=2)
                    logging.info(f"___{now.strftime(DATATIME_NOW)}___{cell_debet[0].value}-----{cell[0].value} /// {cell_debet_downcell.value}-----{cell_downlow.value}-----{debet_amount.value}-----{credit_amount.value}\n")
                    new_sheet.cell(cell[2].row, cell[2].column, value=debet_amount.value)
                    new_sheet.cell(cell[3].row, cell[3].column, value=credit_amount.value)
                    AMOUNT_A = AMOUNT_A + 1
            except:
                raise
        
source = book_arenda.worksheets[-1]
new_sheet = book_arenda.copy_worksheet(source)

for cell in sheet_arenda.iter_rows(min_row=1, max_row=50, min_col=1, max_col=5):
    if cell[0].value == None:
        continue
    find_debet(cell)
    AMOUNT_R = AMOUNT_R + 1

book_arenda.save(PATH)

# title = f"{now.strftime(DATE_NOW)}_auto"
# book_arenda.create_sheet(title)
# source = book_arenda.worksheets[-1]
# new_sheet = book_arenda.copy_worksheet(source)
# with ExcelWriter(PATH, mode="a", if_sheet_exists="new") as writer:
#     book_arenda.
# sheet = source.get_sheet_by_name()
# sheet.title = title
# book_arenda.save(PATH)

if AMOUNT_R < 28 or AMOUNT_A < 24: 
    color = 31
else:
    color = 32
print (f"\033[1;{color};40m ========== {AMOUNT_R} строк обработано из 28 расчетных в файле аренда ========== {AMOUNT_A} строк в выводе из 24 расчетных (арендаторы в файле аренда) ========== \033[0;0m")
