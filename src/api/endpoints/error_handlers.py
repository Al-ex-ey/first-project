import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from src.configs import configure_logging
from fastapi.responses import RedirectResponse
# from fastapi.staticfiles import StaticFiles

app = FastAPI()

configure_logging()

templates = Jinja2Templates(directory="src/templates")

   
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        logging.warning(f"================= http_exception_handler === Вход неавторизированного пользователя ================")
        return RedirectResponse(url="/t_login")
    elif exc.status_code == 500:
        logging.warning(f"================= {exc.detail} Что то пошло не так :( ================")
        return RedirectResponse(url="/")
    else:
        logging.error(f"HTTP Exception: {exc.detail}")
        return templates.TemplateResponse("upload_files.html", {
            "request": request,
            "error_message": exc.detail,
            "color": "red"
        }, status_code=exc.status_code)
