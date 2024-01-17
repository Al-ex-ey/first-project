from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.routers import main_router


app = FastAPI()
app.include_router(main_router)
app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")
# templates = Jinja2Templates(directory="src/frontend/templates")

# app.get('/', response_class=HTMLResponse)
# def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# if __name__ == "__main__":
#     uvicorn.run("index:app", host='127.0.0.1', port=8000, reload=True)