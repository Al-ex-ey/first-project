import re
import openpyxl
import logging
# import pandas as pd
# import datetime as dt

DATE_NOW = '%d.%m.%Y'
AMOUNT_R = 0  # кол-во обработанных строк в файле с арендаторами
AMOUNT_A = 0  # кол-во обработанных арендаторов в файле с арендаторами

logging.basicConfig(level=logging.INFO, filename="parsing_excel_log.log",filemode="w")


try:
    book_arenda = openpyxl.load_workbook(filename="C:/Users/user/Desktop/Arenda_1.xlsx")
    book_debet = openpyxl.load_workbook(filename="C:/Users/user/Desktop/debet_30.11.2023.xlsx")
except:
    print(f"Something went wrong when open and reed files")
    raise

sheet_arenda = book_arenda.worksheets[-1]
sheet_debet = book_debet.worksheets[0]

# data = sheet_arenda.values
# df = pd.DataFrame(data)
# now = dt.datetime.now()
# df.to_excel('C:/Users/user/Desktop/Arenda_df.xlsx', index=False, header=False, sheet_name=f"{now.strftime(DATE_NOW)}_auto")

for cell in sheet_debet.iter_rows(min_row=12, max_row=22, min_col=2, max_col=7, values_only=True):
    print(cell)

try:
    rowsList = [1,3,4,5,6]
    for i in reversed(rowsList):
        sheet_debet.delete_cols(i)
except:
    print(f"Something went wrong when delete columns")
    raise
else:
    for cell in sheet_debet.iter_rows(min_row=12, max_row=22, min_col=1, max_col=3, values_only=True):
        print(cell)

def find_debet(cell):
    global AMOUNT_A
    for cell_debet in sheet_debet.iter_rows(min_row=11, max_row=3000, min_col=1, max_col=3):
        if cell_debet[0].value == None:
            continue
        pattern_a = re.compile(r'\S+')
        cell_arenda = pattern_a.findall(cell[0].value)
        logging.info(f"{cell_arenda}")
        if len(cell_arenda) < 2:
            cell_arenda = pattern_a.findall(cell[0].value)[0]
        else:
            cell_arenda = pattern_a.findall(cell[0].value)[0] + " " + pattern_a.findall(cell[0].value)[1]
        pattern = re.search(cell_arenda.lower(), cell_debet[0].value.lower())
        cell_downlow = cell[0].offset(column=1)
        for i in range(1, 20):
            cell_debet_downcell = cell_debet[0].offset(row=i)
            try:
                if pattern and cell_debet_downcell.value.strip() == cell_downlow.value.strip():
                    print(f"{cell_debet[0].value}-----{cell[0].value} /// {cell_debet_downcell.value}-----{cell_downlow.value}\n")
                    AMOUNT_A = AMOUNT_A + 1
            except:
                continue

for cell in sheet_arenda.iter_rows(min_row=1, max_row=50, min_col=1, max_col=5):
    if cell[0].value == None:
        continue
    find_debet(cell)
    AMOUNT_R = AMOUNT_R + 1

if AMOUNT_R < 28 or AMOUNT_A < 24: 
    print (f"\033[1;31;40m ========== {AMOUNT_R} строк обработано из 28 расчетных в файле аренда ========== {AMOUNT_A} строк в выводе из 24 расчетных (арендаторы в файле аренда) ========== \033[0;0m")
else:
    print (f"\033[1;32;40m ========== {AMOUNT_R} строк обработано из 28 расчетных в файле аренда ========== {AMOUNT_A} строк в выводе из 24 расчетных (арендаторы в файле аренда) ========== \033[0;0m")
