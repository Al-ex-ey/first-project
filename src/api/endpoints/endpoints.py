from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
# from ssl import create_default_context
# from email.mime.text import MIMEText
import smtplib
from email.message import EmailMessage
from src.configs import *
from src.constants import MAIL_HOST, MAIL_USERNAME, MAIL_PASSWORD, MAIL_PORT, MAIL_TO, TEXT_REPLACEMENTS
from src.utils import template_processing


configure_logging()

router = APIRouter()

MAIL_TEXT = "Тестовое письмо"
MAIL_SUBJECT = "Тема письма"

file = "XXXX.pdf"
lease_contract_nomber = "1"
lessee = "АвагянВО"
lease_contract_date = "01.02.2021"

@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post('/mail')
async def send_mail():
    file = await template_processing(lessee, lease_contract_nomber, lease_contract_date)
    msg = EmailMessage()
    msg['Subject'] = MAIL_SUBJECT
    msg['From'] = MAIL_HOST
    msg['To'] = MAIL_TO
    msg.set_content(MAIL_TEXT)

    downloads_dir = BASE_DIR/"send_files"
    with open(downloads_dir/file, 'rb') as f:
        file_data = f.read()
    msg.add_attachment(file_data, maintype="application", subtype="application/pdf", filename=file)

    with smtplib.SMTP_SSL('smtp.mail.ru', MAIL_PORT) as smtp:
        smtp.login(MAIL_HOST, MAIL_PASSWORD)
        smtp.send_message(msg)
 
    return RedirectResponse(url=router.url_path_for("index"), status_code=status.HTTP_303_SEE_OTHER)
