import os
import re
import openpyxl
import logging
# import pandas as pd
import datetime as dt

# from openpyxl.styles import PatternFill
# from openpyxl.styles.differential import DifferentialStyle
# from openpyxl.formatting.rule import Rule
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

# data = sheet_arenda.values
# df = pd.DataFrame(data)
# df.to_excel('C:/Users/user/Desktop/Arenda_df.xlsx', index=False, header=False, sheet_name=f"{now.strftime(DATE_NOW)}_auto")


def parsing_excel(AMOUNT_ROW_TOTAL, AMOUNT_ROW, AMOUNT_A, AMOUNT_A_TOTAL, ARENDA_AMOUNT_ROW, DEBIT_AMOUNT_ROW):
    # global AMOUNT_ROW, AMOUNT_ROW_TOTAL
    now = dt.datetime.now()

    try:
        pattern = re.compile(r"debet\_\d\d\.\d\d\.\d\d\d\d\_\d\d\-\d\d\.xlsx$")
        downloads_dir = BASE_DIR/"downloads"
        files_dir = os.listdir(downloads_dir)
        files_list = []
        for file in files_dir:
            if  re.search(pattern, file):
                files_list.append(file)
        # print(f"========== files_dir ========{files_dir}========== files_list ========{files_list}=========={downloads_dir}\n")
        if len(files_list) > 0:
            files = [os.path.join(downloads_dir, file) for file in files_list]
            files = [file for file in files if os.path.isfile(file)]
            file_path = max(files, key=os.path.getctime)
            file_name = file_path.split('\\')[-1]
            check_pattern = re.search(pattern, file_name)
            # print(f"============= file_path ======{file_path}============= file_name ======{file_name}======= check_pattern ====={check_pattern}\n")
            if check_pattern:
                arenda_dir = downloads_dir/"Arenda_2024.xlsx"
                debet_dir = file_path
                # print(f"============================= arenda_dir =========={arenda_dir}=========================\n")
                # print(f"============================ debet_dir ==========={debet_dir}===========================\n")
            else:
                logging.ERROR(f"___{now.strftime(DT_FORMAT)}___There are no necessary files in the directory")
                raise
    except:
        logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when chose files")
        raise
    
    try:
        # print(f"================================arenda_dir======={arenda_dir}=================================\n")
        book_arenda = openpyxl.load_workbook(filename=arenda_dir)
        # print(f"===============================debet_dir========{debet_dir}====file_path==={file_path}==========================\n")
        book_debet = openpyxl.load_workbook(filename=debet_dir)
    except:
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
    # pattern2 = re.compile(r'[\"|\(|\)]')

    for i in tqdm(range(1, AMOUNT_ROW_TOTAL), desc="Wait a going process"):
        arendator_cell = sheet_arenda.cell(row=i, column=1)
        if arendator_cell.value == "КОНТАКТЫ":
            break
        if arendator_cell.value == None or arendator_cell.font.bold == True:
            continue
        AMOUNT_ROW = AMOUNT_ROW + 1
        arendator_value = arendator_cell.value
        arendator_pattern = pattern.findall(arendator_value)
        # print(f"============================== arendator_value ===== {arendator_value} ==================\n")
        if len(arendator_pattern) < 2:
            print(f"============================== arendator_value ===== {arendator_value} ==================\n")
            arendator = pattern.findall(arendator_value)[0]
        else:
            print(f"============================== arendator_value ===== {arendator_value} ==================\n")
            arendator = pattern.findall(arendator_value)[0] + " " + pattern.findall(arendator_value)[1]
        for d in sheet_debet.iter_rows(min_row=10, max_row=DEBIT_AMOUNT_ROW, min_col=1, max_col=3):
            debet_arendator_cell = d[0]
            arendator_d = debet_arendator_cell.value
            if arendator_d == None or debet_arendator_cell.alignment.indent > 0:
                continue
    
            pattern = re.compile(r'[\"|\(|\)]')
            # print(f"========= arendator ===== {arendator} ============ debet_arendator_cell.value ===== {arendator_d} ==={type(arendator_d)}===\n")
            comparison = re.search(re.sub(pattern, '', arendator.lower()), re.sub(pattern, '', arendator_d.lower()))
            # comparison = re.search(arendator.lower(), arendator_d.lower())

            cell_arenda_contract = sheet_arenda.cell(row=i, column=2)
            if cell_arenda_contract.value == None:
                if arendator not in lost_contracts:
                    lost_contracts.append(arendator)
                continue

            for contract in range(1, 20): 
                cell_debet_contract = debet_arendator_cell.offset(row=contract)
                try:
                    if comparison and (cell_arenda_contract.value == cell_debet_contract.value):
                        # print(f"===== cell_arenda_contract.value ===== {cell_arenda_contract.value} ========= cell_debet_contract.value ===== {cell_debet_contract.value} =====\n")
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
    if AMOUNT_ROW != AMOUNT_A_TOTAL or AMOUNT_A != AMOUNT_A_TOTAL:
        color = 31
    else:
        color = 32
    print(f"\033[1;{color};40m ========== {AMOUNT_ROW} строк обработано из {AMOUNT_A_TOTAL} расчетных в файле аренда ========== {AMOUNT_A} строк в выводе из {AMOUNT_A_TOTAL} расчетных (арендаторы в файле аренда) ========== \033[0;0m\n")
    print(f"Аредаторы без договоров____{lost_contracts}\n")
    print(f"Аредаторы отсутствующте в фале дебеторки - {arendators_not_in_debet_list}\n")
    print(f"Обработанный файл с дебеторкой {file_name} в директории {file_path}\n")



# def find_debit(arendator, i, sheet_debet, sheet_arenda, lost_contracts, AMOUNT_A, book_arenda):




# if __name__ == '__main__':
    # parsing_excel()
# def save_excel(book_arenda, PATH_A, lost_contracts, arendators_not_in_debet_list):
#     book_arenda.save(PATH_A)

#     if AMOUNT_ROW != AMOUNT_A_TOTAL or AMOUNT_A != AMOUNT_A_TOTAL:
#         color = 31
#     else:
#         color = 32
#     print(f"\033[1;{color};40m ========== {AMOUNT_ROW} строк обработано из {AMOUNT_A_TOTAL} расчетных в файле аренда ========== {AMOUNT_A} строк в выводе из {AMOUNT_A_TOTAL} расчетных (арендаторы в файле аренда) ========== \033[0;0m\n")
#     print(f"Аредаторы без договоров____{lost_contracts}\n")
#     print(f"Аредаторы отсутствующте в фале дебеторки - {arendators_not_in_debet_list}\n")
    # print(f"{arendator_pattern_list}")



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