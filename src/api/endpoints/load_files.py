from fastapi import APIRouter, FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
from .validators import load_validate
import shutil


router = APIRouter()

app = FastAPI()

# staticfiles = StaticFiles(directory="src/front/static")
# app.mount("/static", StaticFiles(directory="src/front/static"), name="static")
templates = Jinja2Templates(directory="src/frontend/templates")


# @router.post('/', response_class=HTMLResponse)
# def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


@router.post('/upload')
async def upload_files(files: list[UploadFile]):
    load_validate(files)
    result = []
    for file in files:
        path = f"src/frontend/static/{file.filename}"
        with open(path,"wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result.append(file)
    return result

    # result = {"file": [file.filename for file in files]}
    # for file in result:
    #     path = f"src/frontend/static/{file.filename}"
    #     with open(path,"wb+") as buffer:
    #         shutil.copyfileobj(files.file, buffer)
    # return result
    
    # path = f"src/frontend/static/{files.filename}"
    # with open(path,"wb+") as buffer:
    #     shutil.copyfileobj(files.file, buffer)
    
    # return {
    #         "file": file,
    #         "filename": file.filename,
    #         "path": path,
    #         "type": file.content_type,
    #     }


    # result = []
    # for file in files:
    #     path = f"src/frontend/static/{files.filename}"
    #     with open(path,"wb+") as buffer:
    #         shutil.copyfileobj(files.file, buffer)
    #     result.append(file)
    # return result

@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
