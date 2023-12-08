import re
import openpyxl
import logging
# import pandas as pd
import datetime as dt

from openpyxl.styles import PatternFill
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import Rule
from openpyxl.styles import NamedStyle, Alignment, Font, Border, Side
from src.configs import configure_logging
from src.constants import AMOUNT_RAW, AMOUNT_A, AMOUNT_RAW_TOTAL, AMOUNT_A_TOTAL, PATH_A, PATH_D, DT_FORMAT

configure_logging()
now = dt.datetime.now()

try:
    book_arenda = openpyxl.load_workbook(filename=PATH_A)
    book_debet = openpyxl.load_workbook(filename=PATH_D)
except:
    logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when open and reed files")
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
    logging.ERROR(f"___{now.strftime(DT_FORMAT)}___Something went wrong when delete columns")
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
                    logging.info(f"___{now.strftime(DT_FORMAT)}___{cell_debet[0].value}-----{cell[0].value} /// {cell_debet_downcell.value}-----{cell_downlow.value}-----{debet_amount.value}-----{credit_amount.value}\n")
                    if not debet_amount.value:
                        style_bad = "Normal"
                    else:
                        style_bad = "Bad"
                    if credit_amount.value:
                        style_good = "Good"
                    else:
                        style_good = "Normal"
                    new_sheet.cell(cell[2].row, cell[2].column, value=debet_amount.value).style = style_bad
                    new_sheet.cell(cell[3].row, cell[3].column, value=credit_amount.value).style = style_good
                    AMOUNT_A = AMOUNT_A + 1
            except:
                raise
        
source = book_arenda.worksheets[-1]
new_sheet = book_arenda.copy_worksheet(source)

# if not 'style_normal' in book_arenda.named_styles:
#     style_normal = NamedStyle(name="style_normal")
#     style_normal.font = Font(name='Times New Roman', bold=True, size=11, color="00000000")
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


for cell in sheet_arenda.iter_rows(min_row=1, max_row=50, min_col=1, max_col=5):
    if cell[0].value == None:
        continue
    find_debet(cell)
    AMOUNT_RAW = AMOUNT_RAW + 1

# bg_red = PatternFill(fill_type='solid', fgColor="FF0000")
# diff_style = DifferentialStyle(fill=bg_red)
# rule = Rule(type="expression", dxf=diff_style)
# rule.formula = ["$B3>0"]
# new_sheet.conditional_formatting.add("C3:C100", rule)

# if 'style_normal' in book_arenda.named_styles:
#     del book_arenda.named_styles.del  = style_normal

book_arenda.save(PATH_A)

# title = f"{now.strftime(DATE_NOW)}_auto"
# book_arenda.create_sheet(title)
# source = book_arenda.worksheets[-1]
# new_sheet = book_arenda.copy_worksheet(source)
# with ExcelWriter(PATH, mode="a", if_sheet_exists="new") as writer:
#     book_arenda.
# sheet = source.get_sheet_by_name()
# sheet.title = title
# book_arenda.save(PATH)

if AMOUNT_RAW < AMOUNT_RAW_TOTAL or AMOUNT_A < AMOUNT_A_TOTAL: 
    color = 31
else:
    color = 32
print (f"\033[1;{color};40m ========== {AMOUNT_RAW} строк обработано из 28 расчетных в файле аренда ========== {AMOUNT_A} строк в выводе из 24 расчетных (арендаторы в файле аренда) ========== \033[0;0m")
