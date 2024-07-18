import os
import re
import openpyxl
import logging
# import pandas as pd
import datetime as dt
import shutil
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

# from openpyxl.styles import PatternFill
# from openpyxl.styles.differential import DifferentialStyle
# from openpyxl.formatting.rule import Rule
from openpyxl.styles import NamedStyle, Alignment, Font, Border, Side, PatternFill
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

router = APIRouter()

# data = sheet_arenda.values
# df = pd.DataFrame(data)
# df.to_excel('C:/Users/user/Desktop/Arenda_df.xlsx', index=False, header=False, sheet_name=f"{now.strftime(DATE_NOW)}_auto")


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
    except Exception:
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when chose files")
        raise
    
    try:
        book_arenda = openpyxl.load_workbook(filename=arenda_dir)
        book_debet = openpyxl.load_workbook(filename=debet_dir)
    except (OSError, IOError):
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___KeyError")
        raise HTTPException(
            status_code=404, detail="Ошибка ввода-вывода. Tip: проверьте что файл существует или диск не заполнен!"
        )
    except Exception:
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when open and reed files")
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
        if (arendator_cell.value == None) or (arendator_cell.font.bold == True):
            continue
        new_sheet.cell(a, column=3, value='').fill = PatternFill(fill_type='solid', start_color='FFFFC0')
        new_sheet.cell(a, column=4, value='').fill = PatternFill(fill_type='solid', start_color='FFFFC0')
        

    # for a in range(1, ARENDA_AMOUNT_ROW):
    #     arendator_cell = sheet_arenda.cell(row=a, column=1)
    #     if arendator_cell.value == "КОНТАКТЫ":
    #         break
    #     AMOUNT_ROW_TOTAL = AMOUNT_ROW_TOTAL + 1
    #     if (arendator_cell.value == None) or (arendator_cell.font.bold == True) or (arendator_cell.value in arendator_list):
    #         continue
    #     arendator_list.append(arendator_cell.value)

    # for d in range(1, DEBIT_AMOUNT_ROW):
    #     debit_arendator_cell = sheet_debet.cell(row=d, column=1)
    #     if arendator_cell.value == "Итого":
    #         break
    #     if (debit_arendator_cell.value == None) or (debit_arendator_cell.alignment.indent > 0) or (debit_arendator_cell.value in arendator_debet_list):
    #         continue
    #     arendator_debet_list.append(debit_arendator_cell.value)

    # for a in arendator_list:
    #     for d in arendator_debet_list:
    #         if a == d:
    #             continue
    #         if a not in arendator_debet_list and a not in arendators_not_in_debet_list:
    #             arendators_not_in_debet_list.append(a)

    pattern = re.compile(r'\w+[\-|\.]?\w+')

    for i in tqdm(range(1, AMOUNT_ROW_TOTAL), desc="Wait a going process"):
        arendator_cell = sheet_arenda.cell(row=i, column=1)
        if arendator_cell.value == "КОНТАКТЫ":
            break
        AMOUNT_A_TOTAL = AMOUNT_A_TOTAL + 1
        if arendator_cell.value == None or arendator_cell.font.bold == True:
            continue
        # AMOUNT_ROW = AMOUNT_ROW + 1
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

            for r in range(1, 20): 
                cell_debet_contract = debet_arendator_cell.offset(row=r)
                if comparison and (cell_arenda_contract.value == cell_debet_contract.value):
                    debet_cell = cell_debet_contract.offset(column=1)
                    credit_cell = cell_debet_contract.offset(column=2)
                    logging.info(f"___ {arendator} ----- {cell_arenda_contract.value} ----- {debet_cell.value} ----- {credit_cell.value}\n")
                    if not debet_cell.value:
                        style_bad = "Normal"
                    else:
                        style_bad = "Bad"
                    if credit_cell.value:
                        style_good = "Good"
                    else:
                        style_good = "Normal"
                    if debet_cell.value == None:
                        debet_cell.value = 0
                    if credit_cell.value == None:
                        credit_cell.value = 0
                    bd = Side(style='thin', color="00000000")
                    new_sheet.cell(i, column=3, value=debet_cell.value).style = style_bad
                    new_sheet.cell(i, column=3).alignment = Alignment(horizontal="center", vertical="center")
                    new_sheet.cell(i, column=3).border = Border(left=bd, top=bd, right=bd, bottom=bd)
                    new_sheet.cell(i, column=4, value=credit_cell.value).style = style_good
                    new_sheet.cell(i, column=4).alignment = Alignment(horizontal="center", vertical="center")
                    new_sheet.cell(i, column=4).border = Border(left=bd, top=bd, right=bd, bottom=bd)
                    AMOUNT_A = AMOUNT_A + 1
                    break

    book_arenda.save(arenda_dir)

    """Проверка файла по критериям: арендаторы без договоров, необработанные позиции"""
    arendator_without_contract = []
    not_processed = {}

    """ Проверка результата работы - Поиск необработанных позиций в только что созданом файле"""
    path = BASE_DIR/"downloads"
    files_dir = os.listdir(path)
    if "Arenda_2024.xlsx" in files_dir:
       book_arenda = openpyxl.load_workbook(filename=arenda_dir)
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
    sheet_arenda = book_arenda.worksheets[-1]
    result_table: list = []
    total_credit: float = 0
    total_debet: float = 0
    counter: int = 1
    
    for b in range(1, AMOUNT_A_TOTAL):
    # for b in tqdm(sheet_arenda.iter_rows(min_row=1, max_col=10, max_row=AMOUNT_A_TOTAL), desc="Wait a going process"):
        key_counter: str = f"key " + str(counter)
        arendator_cell = sheet_arenda.cell(row=b, column=1) # Арендатор 
        contract_cell = sheet_arenda.cell(row=b, column=2)  # Договор
        debet_cell = sheet_arenda.cell(row=b, column=3) # Дебет
        credit_cell = sheet_arenda.cell(row=b, column=4)    # Кредит
        email_cell = sheet_arenda.cell(row=b, column=9) # E-mail
        if arendator_cell.value == "КОНТАКТЫ":  # достигнут конец таблицы
            break
        if (arendator_cell.value == None) or (arendator_cell.font.bold == True):    # пропускаем пустые и жирные(заголовки) строки
            continue
        AMOUNT_ROW = AMOUNT_ROW + 1 # счетчик обработанных позиций
        if contract_cell.value == None:
            arendator_without_contract.append(arendator_cell.value)
            continue
        if debet_cell.fill == PatternFill(fill_type='solid', start_color='FFFFC0') or credit_cell.fill == PatternFill(fill_type='solid', start_color='FFFFC0'): # не обработанные строки (в талице выделены желтым)
            not_processed[arendator_cell.value] = contract_cell.value
        if debet_cell.value == None:
            if credit_cell.value == None:
                continue
        if debet_cell.value > 0:
            rt: dict = {}
            if key_counter not in rt:
                rt[key_counter] = []
                counter = counter + 1
            rt[key_counter].append(arendator_cell.value)
            rt[key_counter].append(contract_cell.value)
            rt[key_counter].append(debet_cell.value)
            rt[key_counter].append(email_cell.value)
            result_table.append(rt)
            total_debet = total_debet + debet_cell.value
        if credit_cell.value > 0:
            total_credit = total_credit + credit_cell.value
        

    # AMOUNT_ROW_TOTAL = AMOUNT_A + len(arendator_without_contract) + len(not_processed)
    amount_wrong_row = len(not_processed) + len(arendator_without_contract)
    if AMOUNT_ROW != AMOUNT_A + amount_wrong_row:
        color = 31
    else:
        color = 32
    print(f"\033[1;{color};40m ===== {AMOUNT_A} обработанных строк из {AMOUNT_ROW}  ===== в том числе {amount_wrong_row} строк(а) без обработки ===== \033[0;0m\n")
    print("Обратите внимание:\n")
    print(f"\033[1;31;40m ===== Необработанные позиции ===== {not_processed}  \033[0;0m\n")
    print(f"\033[1;31;40m ===== Арендаторы без договоров ===== {arendator_without_contract}  \033[0;0m\n")


    # print(f"\033[1;{color};40m ========== {AMOUNT_A} строк в выводе из {AMOUNT_ROW} (арендаторы в файле аренда) ========== \033[0;0m\n")
    # print(f"Аредаторы без договоров____{lost_contracts}\n")
    # print(f"Аредаторы отсутствующте в фале дебеторки - {arendators_not_in_debet_list}\n")
    # # print(f"Аредаторы с некорректными договорами: {incorrect_contracts}\n")
    print(f"Обработанный файл с дебеторкой {file_name} в директории {file_path}\n")
    logging.info(f"\033[1;{color};40m ===== {AMOUNT_A} обработанных строк из {AMOUNT_ROW}  ===== в том числе {amount_wrong_row} строк(а) без обработки ===== \033[0;0m\n")
    # logging.info(f"Аредаторы без договоров____{lost_contracts}\n")
    # logging.info(f"Аредаторы отсутствующте в фале дебеторки - {arendators_not_in_debet_list}\n")
    # # logging.info(f"Аредаторы с некорректными договорами: {incorrect_contracts}\n")
    logging.info(f"Обработанный файл с дебеторкой {file_name} в директории {file_path}\n")

    total_credit = int(total_credit)
    total_debet = int(total_debet)
    query_params = {
        "arendator_without_contract": arendator_without_contract,
        "not_processed": not_processed,
        "file_name": file_name,
        "file_path": file_path,
        "result_table": result_table,
        "total_debet": total_debet,
        "total_credit": total_credit,
    }

    return query_params



# if not 'style_normal' in book_arenda.named_styles:
#     style_normal = NamedStyle(name="style_normal")
#     style_normal.font = Font(name='Times New Roman', bold=False, size=11, color="00000000")
#     style_normal.alignment = Alignment(horizontal='center', vertical='center')
#     style_normal.fill = PatternFill(fgColor="00FFFFFF")
#     bd = Side(style='thin', color="00000000")
#     style_normal.border = Border(left=bd, top=bd, right=bd, bottom=bd)
# else:
#     book_arenda.named_styles(name="style_normal")


# book_arenda.add_named_style(style_normal)

# for index,cur_style in enumerate(book_arenda._named_styles):
#     if cur_style.name == 'my_new_style':
#         book_arenda._named_styles[index] = style_normal
#         style_normal.bind(book_arenda)
#         break
# else:
#     book_arenda.add_named_style(style_normal)



# bg_red = PatternFill(fill_type='solid', fgColor="FF0000")
# diff_style = DifferentialStyle(fill=bg_red)
# rule = Rule(type="expression", dxf=diff_style)
# rule.formula = ["$B3>0"]
# new_sheet.conditional_formatting.add("C3:C100", rule)

# if 'style_normal' in book_arenda.named_styles:
#     del book_arenda.named_styles.del  = style_normal



# title = f"{now.strftime(DATE_NOW)}_auto"
# book_arenda.create_sheet(title)
# source = book_arenda.worksheets[-1]
# new_sheet = book_arenda.copy_worksheet(source)
# with ExcelWriter(PATH, mode="a", if_sheet_exists="new") as writer:
#     book_arenda.
# sheet = source.get_sheet_by_name()
# sheet.title = title
# book_arenda.save(PATH)


# for row in sheet_debet.iter_rows(min_row=10, max_row=3000, min_col=1, max_col=3):
    # if row[0].value == None:
    #     continue