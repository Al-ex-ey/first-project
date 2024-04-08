from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.configs import *

configure_logging()

router = APIRouter()

@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except:
        raise HTTPException(status_code=404, detail=" Page not found")
