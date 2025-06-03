from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Exemple temporaire de mots à corriger
liste_mots = [
    {"mot": "motfautif", "ligne": "Voici une phrase avec un motfautif.", "corrections": ["motif", "motifatif", "motifautif", "motifotif", "mou fautif"]},
    # Ajouter plus de mots ici
]
index = 0

@app.get("/")
async def root(request: Request):
    global index
    if index >= len(liste_mots):
        index = 0  # recommencer
    data = liste_mots[index]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mot": data["mot"],
        "ligne": data["ligne"],
        "corrections": data["corrections"]
    })

@app.post("/add")
async def add_to_dictionary(mot: str = Form(...)):
    print(f"Ajout au dictionnaire : {mot}")
    # Traitement ici...
    return RedirectResponse("/", status_code=303)

@app.post("/correct")
async def correct_word(correction: str = Form(...)):
    print(f"Correction sélectionnée : {correction}")
    # Traitement ici...
    global index
    index += 1
    return RedirectResponse("/", status_code=303)
