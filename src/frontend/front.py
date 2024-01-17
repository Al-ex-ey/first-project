from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import List
import shutil


app = FastAPI()
templates = Jinja2Templates(directory="src/frontend/templates")

app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# app.post('/upload')
# async def load_files(upload_file: UploadFile = File(...)):
#     path = f"src/front/static/{upload_file.filename}"
#     with open(path,"wb+") as buffer:
#         shutil.copyfileobj(upload_file.file, buffer)
#     return {           
#             "filename": upload_file.filename,
#             "path": path,
#             "type": upload_file.content_type
#         }


# app = FastAPI()
# # staticfiles = StaticFiles(directory="src/front/static")
# app.mount("/static", StaticFiles(directory="src/front/static"), name="static")
# templates = Jinja2Templates(directory="src/front/templates")


# @app.post('/', response_class=HTMLResponse)
# async def index(request: Request, upload_file: UploadFile = File(...)):
#     path = f"static/{upload_file.filename}"
#     with open(path,"wb+") as buffer:
#         shutil.copyfileobj(upload_file.file, buffer)
#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "filename": upload_file.filename,
#             "path": path,
#             "type": upload_file.content_type
#         }
#     )

# if __name__ == "__main__":
#     uvicorn.run("front:app", host='127.0.0.1', port=8000, reload=True)