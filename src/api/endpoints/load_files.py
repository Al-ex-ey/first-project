# from fastapi import APIRouter, FastAPI, Request, UploadFile, HTTPException, File, Form, status
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
# from .validators import load_validate
# import shutil
# import datetime as dt
# from src.parsing_excel.parsing_excel import parsing_excel 
# import os
# from src.configs import *
# from src.constants import (
#     AMOUNT_ROW,
#     AMOUNT_A,
#     AMOUNT_ROW_TOTAL,
#     AMOUNT_A_TOTAL,
#     ARENDA_AMOUNT_ROW,
#     BASE_DIR,
#     DEBIT_AMOUNT_ROW,
#     DT_FORMAT
# )


# configure_logging()

# router = APIRouter()

# app = FastAPI()





# @router.get('/load_file')
# def load_file():
#     path = BASE_DIR/"downloads"
#     files_dir = os.listdir(path)
#     if "Arenda_2024.xlsx" in files_dir:
#        return FileResponse(f"{path}/Arenda_2024.xlsx", media_type = "xlsx", filename="Arenda_2024.xlsx")
#     else:
#         raise HTTPException(status_code=404, detail="File not found")
