from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
# staticfiles = StaticFiles(directory="src/front/static")
app.mount("/static", StaticFiles(directory="src/front/static"), name="static")
templates = Jinja2Templates(directory="src/front/templates")


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("front:app", host='127.0.0.1', port=8000, reload=True)