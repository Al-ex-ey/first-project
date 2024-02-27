import os
import re
import openpyxl
import logging
import datetime as dt
import shutil
from openpyxl.styles import NamedStyle, Alignment, Font, Border, Side
from src.configs import configure_logging
from src.constants import (
    AMOUNT_ROW,
    AMOUNT_A,
    AMOUNT_ROW_TOTAL,
    AMOUNT_A_TOTAL,
    BASE_DIR,
    ARENDA_AMOUNT_ROW,
    DEBIT_AMOUNT_ROW,
    DT_FORMAT
)
from pathlib import Path
from tqdm import tqdm


configure_logging()

def parsing_excel(AMOUNT_ROW_TOTAL, AMOUNT_ROW, AMOUNT_A, AMOUNT_A_TOTAL, ARENDA_AMOUNT_ROW, DEBIT_AMOUNT_ROW):
    now = dt.datetime.now()

    try:
        pattern = re.compile(r"debet\_\d\d\.\d\d\.\d\d\d\d\_\d\d\-\d\d\.xlsx$")
        downloads_dir = BASE_DIR/"downloads"
        files_dir = os.listdir(downloads_dir)
        files_list = []
        for file in files_dir:
            if  re.search(pattern, file):
                files_list.append(file)
        if len(files_list) > 0:
            files = [os.path.join(downloads_dir, file) for file in files_list]
            files = [file for file in files if os.path.isfile(file)]
            file_path = max(files, key=os.path.getctime)
            file_name = file_path.split('\\')[-1]
            check_pattern = re.search(pattern, file_name)
            if check_pattern:
                arenda_dir = downloads_dir/"Arenda_2024.xlsx"
                debet_dir = file_path
            else:
                logging.ERROR(f"___{now.strftime(DT_FORMAT)}___There are no necessary files in the directory")
                raise
    except:
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when chose files")
        raise
    
    try:
        book_arenda = openpyxl.load_workbook(filename=arenda_dir)
        book_debet = openpyxl.load_workbook(filename=debet_dir)
    except:
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when open and reed files")
        # TypeError: 'int' object is not callable
        raise

    sheet_arenda = book_arenda.worksheets[-1]
    sheet_debet = book_debet.worksheets[0]
    lost_contracts = []
    arendators_not_in_debet_list = []
    arendator_debet_list = []
    arendator_list = []
    source = book_arenda.worksheets[-1]
    new_sheet = book_arenda.copy_worksheet(source)

    try:
        column_list = [1,3,4,5,6]
        for i in reversed(column_list):
            sheet_debet.delete_cols(i)
    except:
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when delete columns")
        raise

    try:
        sheet_debet.delete_rows(1, amount=7)
        for i in range(1, 2900):
            rows_debit = sheet_debet.cell(row=i, column=1)
            if rows_debit.value == "Итого":
                sheet_debet.delete_rows(i, amount=2)
                break
    except:
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when delete rows")
        raise


    for a in range(1, ARENDA_AMOUNT_ROW):
        arendator_cell = sheet_arenda.cell(row=a, column=1)
        if arendator_cell.value == "КОНТАКТЫ":
            break
        AMOUNT_ROW_TOTAL = AMOUNT_ROW_TOTAL + 1
        if (arendator_cell.value == None) or (arendator_cell.font.bold == True) or (arendator_cell.value in arendator_list):
            continue
        arendator_list.append(arendator_cell.value)

    for d in range(1, DEBIT_AMOUNT_ROW):
        debit_arendator_cell = sheet_debet.cell(row=d, column=1)
        if arendator_cell.value == "Итого":
            break
        if (debit_arendator_cell.value == None) or (debit_arendator_cell.alignment.indent > 0) or (debit_arendator_cell.value in arendator_debet_list):
            continue
        arendator_debet_list.append(debit_arendator_cell.value)

    for a in arendator_list:
        for d in arendator_debet_list:
            if a == d:
                continue
            if a not in arendator_debet_list and a not in arendators_not_in_debet_list:
                arendators_not_in_debet_list.append(a)

    pattern = re.compile(r'\w+[\-|\.]?\w+')

    for i in tqdm(range(1, AMOUNT_ROW_TOTAL), desc="Wait a going process"):
        arendator_cell = sheet_arenda.cell(row=i, column=1)
        if arendator_cell.value == "КОНТАКТЫ":
            break
        if arendator_cell.value == None or arendator_cell.font.bold == True:
            continue
        AMOUNT_ROW = AMOUNT_ROW + 1
        arendator = arendator_cell.value
        for d in sheet_debet.iter_rows(min_row=10, max_row=DEBIT_AMOUNT_ROW, min_col=1, max_col=3):
            debet_arendator_cell = d[0]
            arendator_d = debet_arendator_cell.value
            if arendator_d == None or debet_arendator_cell.alignment.indent > 0:
                continue
    
            pattern = re.compile(r'[\"|\(|\)]')
            comparison = re.search(re.sub(pattern, '', arendator.lower()), re.sub(pattern, '', arendator_d.lower()))

            cell_arenda_contract = sheet_arenda.cell(row=i, column=2)
            if cell_arenda_contract.value == None:
                if arendator not in lost_contracts:
                    lost_contracts.append(arendator)
                continue

            for contract in range(1, 20): 
                cell_debet_contract = debet_arendator_cell.offset(row=contract)
                try:
                    if comparison and (cell_arenda_contract.value == cell_debet_contract.value):
                        debet_amount = cell_debet_contract.offset(column=1)
                        credit_amount = cell_debet_contract.offset(column=2)
                        logging.info(f"___ {arendator} ----- {cell_arenda_contract.value} ----- {debet_amount.value} ----- {credit_amount.value}\n")
                        if not debet_amount.value:
                            style_bad = "Normal"
                        else:
                            style_bad = "Bad"
                        if credit_amount.value:
                            style_good = "Good"
                        else:
                            style_good = "Normal"
                        if debet_amount.value == None:
                            debet_amount.value = 0
                        if credit_amount.value == None:
                            credit_amount.value = 0
                        bd = Side(style='thin', color="00000000")
                        new_sheet.cell(i, column=3, value=debet_amount.value).style = style_bad
                        new_sheet.cell(i, column=3).alignment = Alignment(horizontal="center", vertical="center")
                        new_sheet.cell(i, column=3).border = Border(left=bd, top=bd, right=bd, bottom=bd)
                        new_sheet.cell(i, column=4, value=credit_amount.value).style = style_good
                        new_sheet.cell(i, column=4).alignment = Alignment(horizontal="center", vertical="center")
                        new_sheet.cell(i, column=4).border = Border(left=bd, top=bd, right=bd, bottom=bd)
                        AMOUNT_A = AMOUNT_A + 1
                        break
                except:
                    raise

    book_arenda.save(arenda_dir)
    AMOUNT_A = AMOUNT_A + len(arendators_not_in_debet_list)
    if AMOUNT_ROW != AMOUNT_A:
        color = 31
    else:
        color = 32
    print(f"\033[1;{color};40m ========== {AMOUNT_A} строк в выводе из {AMOUNT_ROW} (арендаторы в файле аренда) ========== \033[0;0m\n")
    print(f"Аредаторы без договоров____{lost_contracts}\n")
    print(f"Аредаторы отсутствующте в фале дебеторки - {arendators_not_in_debet_list}\n")
    print(f"Обработанный файл с дебеторкой {file_name} в директории {file_path}\n")
    logging.info(f"\033[1;{color};40m ========== {AMOUNT_A} строк в выводе из {AMOUNT_ROW} (арендаторы в файле аренда) ========== \033[0;0m\n")
    logging.info(f"Аредаторы без договоров____{lost_contracts}\n")
    logging.info(f"Аредаторы отсутствующте в фале дебеторки - {arendators_not_in_debet_list}\n")
    logging.info(f"Обработанный файл с дебеторкой {file_name} в директории {file_path}\n")
