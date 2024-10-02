import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from src.configs import configure_logging
from fastapi.responses import RedirectResponse
# from fastapi.staticfiles import StaticFiles

app = FastAPI()

configure_logging()

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
    if exc.status_code == 403:
        logging.warning("Unauthorized access attempt")
        return RedirectResponse(url="/t_login")
    else:
        logging.error(f"HTTP Exception: {exc.detail}")
        return templates.TemplateResponse("upload_files.html", {
            "request": request,
            "error_message": exc.detail,
            "color": "red"
        }, status_code=exc.status_code)
