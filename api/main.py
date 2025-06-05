import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from core import add_to_dico, load_dico, load_rules, generate_sample, get_most_similar_words, \
    save_rules

dico, words_by_size = load_dico()
rules, regex_rules = load_rules()
word_gen = generate_sample()
OUTPUT = [[]]
CURRENT_LINE = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global OUTPUT
    yield
    save_all_data()

def save_all_data():
    with open('../resources/corrected', 'w', encoding='utf-8') as f:
        lines = [" ".join(line) for line in OUTPUT]
        f.write("\n".join(lines))
    save_rules(rules, regex_rules)
    with open('../resources/dico.json', 'w', encoding='utf-8') as f:
        json.dump(list(dico), f, ensure_ascii=False, indent=4)
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    global CURRENT_LINE, OUTPUT
    try:
        for word, line, line_index in word_gen:
            if CURRENT_LINE != line_index:
                OUTPUT.append([])
                CURRENT_LINE = line_index
            if word.lower() in dico or word in dico:
                OUTPUT[line_index].append(word)
                continue
            regex_match = False
            for regex in regex_rules:
                if regex.match(word.lower()):
                    regex_match = True
                    break
            if regex_match:
                OUTPUT[line_index].append(word)
                continue
            if word.lower() in rules or word in rules:
                OUTPUT[line_index].append(rules[word])
                continue
            corrections = [c[0] for c in get_most_similar_words(word, words_by_size)][:5]
            return templates.TemplateResponse("index.html", {
                "request": request,
                "mot": word,
                "ligne": line,
                "corrections": corrections,
            })
    except Exception as e:
        save_all_data()


@app.post("/add")
async def add_to_dictionary(mot: str = Form(...)):
    global dico, words_by_size, OUTPUT
    print(f"Ajout au dictionnaire : {mot}")
    add_to_dico(mot, dico, words_by_size)
    OUTPUT[-1].append(mot)
    return RedirectResponse("/", status_code=303)

@app.post("/correct")
async def correct_word(mot: str = Form(...), correction: str = Form(...)):
    global OUTPUT
    print(f"Correction sélectionnée : {correction}")
    OUTPUT[-1].append(correction)
    rules[mot] = correction
    return RedirectResponse("/", status_code=303)

