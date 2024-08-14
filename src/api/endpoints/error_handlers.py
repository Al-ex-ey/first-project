from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles

app = FastAPI()

# staticfiles = StaticFiles(directory="src/frontend/static")
# app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# class File_not_found(Exception):
#     def __init__(self, name: str):
#         self.name = name


# @app.exception_handler(404)
# async def file_exception_handler(request: Request, exc: Exception):
#     return templates.TemplateResponse("404.html", {"request": request})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("upload_files.html", {
        "request": request,
        "error_message": exc.detail,
        "color": "red"
    }, status_code=exc.status_code)
