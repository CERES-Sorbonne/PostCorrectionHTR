from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from core import DataManager

manager = DataManager()
iterator = manager.generate_sample()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    manager.save_data()
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    for word, prevl, line, nextl in iterator:
        corrections = manager.get_most_similar_words(word)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "mot": word,
            "previous": prevl,
            "ligne": line,
            "next": nextl,
            "corrections": corrections,
        })


@app.post("/add")
async def add_to_dictionary(mot: str = Form(...)):
    print(f"Ajout au dictionnaire : {mot}")
    manager.add_to_dico(mot)
    return RedirectResponse("/", status_code=303)

@app.post("/correct")
async def correct_word(mot: str = Form(...), correction: str = Form(...)):
    print(f"Correction sélectionnée : {correction}")
    manager.add_correction(mot, correction)
    return RedirectResponse("/", status_code=303)

