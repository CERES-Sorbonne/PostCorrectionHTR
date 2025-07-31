import html
from contextlib import asynccontextmanager
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from models import WordContext
from core import DataManager

manager = DataManager()
iterator = manager.generate_sample_from_xml()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    manager.save_data()
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    wc: WordContext
    for wc in iterator:
        word = wc.word
        line = wc.current_line
        corrections = manager.get_most_similar_words(word)
        line = html.escape(line)
        cleaned_word = html.escape(word)
        line = line.replace(cleaned_word, f'<mark>{cleaned_word}</mark>')
        return templates.TemplateResponse("index.html", {
            "request": request,
            "mot": word,
            "previous": wc.previous_line,
            "ligne": line,
            "next": wc.next_line,
            "image": wc.cropped_image.decode(),
            "corrections": corrections,
        })


@app.post("/add")
async def add_to_dictionary(mot: str = Form(...)):
    print(f"Ajout au dictionnaire : {mot}")
    manager.add_to_dico(mot)
    return RedirectResponse("/", status_code=303)

@app.post("/correct")
async def correct_word(mot: str = Form(...), correction: str = Form(...), save_rule: bool = True):
    print(f"Correction sélectionnée : {correction}")
    manager.add_correction(mot, correction, save_rule)
    return RedirectResponse("/", status_code=303)

