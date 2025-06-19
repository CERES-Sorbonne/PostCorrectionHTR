import json
import os
import re

from collections import defaultdict
from functools import partial, wraps, partialmethod
from pathlib import Path

from Levenshtein import distance
from PIL import Image

from api.models import WordContext
from api.utils import parse_xml_lines, crop_image_for_context, _get_xml_files

DICO_PATH = '../resources/dico.json'
RULES_PATH = '../resources/correct_rules.json'
TO_CORRECT_PATH = "../resources/to_correct.txt"
CORRECTED_PATH = "../resources/corrected.txt"
XML_FILES_PATH = "../resources/xml_files"


class DataManager:
    def __init__(self):
        self.dico = None
        self.words_by_size = defaultdict(list)
        self.rules = {}
        self.regex_rules = []
        self.correction = defaultdict(list)
        self.current_line = 0
        self.nb_actions = 0
        self.punkt = [',', ';', '!', '.']

        self._load_dico(DICO_PATH)
        self._load_rules(RULES_PATH)
        # reset file
        with open(CORRECTED_PATH, 'w') as f:
            f.write('')

    def _load_dico(self, dico_path):
        with open(dico_path, 'r', encoding='utf-8') as f:
            self.dico = set(json.load(f))

        for index, word in enumerate(self.dico):
            self.words_by_size[len(word)].append(word)


    def _load_rules(self, rules_path):
        with open(rules_path, 'r', encoding='utf-8') as f:
            all_rules = json.load(f)
            self.rules = all_rules['rules']
            self.regex_rules = [re.compile(expr) for expr in all_rules['regex_rules']]


    def save_rules(self):
        regex_rules = [e.pattern for e in self.regex_rules]
        with open(RULES_PATH, mode='w', encoding='utf-8') as f:
            json.dump(
                {
                    "rules": self.rules,
                    "regex_rules": regex_rules
                },
                f,
                ensure_ascii=False,
                indent=2
            )

    def save_dico(self):
        with open(DICO_PATH, 'w', encoding='utf-8') as f:
            json.dump(list(self.dico), f, ensure_ascii=False, indent=2)

    def save_correction(self):
        with open(CORRECTED_PATH, 'a', encoding='utf-8') as f:
            lines = [" ".join(line) for line in self.correction.values()]
            f.write("\n" + "\n".join(lines))
        del self.correction
        self.correction = defaultdict(list)

    def add_to_dico(self, word):
        word = self.clean_word(word)
        self.dico.add(word)
        if word not in self.words_by_size[len(word)]:
            self.words_by_size[len(word)].append(word)
        self.correction[self.current_line].append(word)

    def generate_sample_from_xml(self):
        all_xml = _get_xml_files(XML_FILES_PATH)
        for xml_file in all_xml:
            try:
                print(f"Traitement de {xml_file}")
                image_path = Path(xml_file).with_suffix('.jpg')
                image = Image.open(image_path)

                # Parser les lignes du XML
                lines = parse_xml_lines(xml_file)

                for line_index, current_line in enumerate(lines):
                    current_image: Image = None

                    # Sauvegarder périodiquement (si applicable)
                    if hasattr(self, 'save_data') and line_index % 10 == 0:
                        self.save_data()

                    # Déterminer les lignes précédente et suivante
                    previous_line = lines[line_index - 1] if line_index > 0 else None
                    next_line = lines[line_index + 1] if line_index < len(lines) - 1 else None

                    # Traiter chaque mot de la ligne courante
                    words = current_line.content.split()

                    for word in words:
                        if line_index % 10 == 0:
                            self.save_data()
                        if self.is_word_in_dico(word):
                            self.correction[line_index].append(word)
                            continue
                        regex_match = False
                        # for regex in self.regex_rules:
                        #     if regex.match(word.lower()):
                        #         regex_match = True
                        #         break
                        # if regex_match:
                        #     self.correction[line_index].append(word)
                        #     continue
                        if self.is_word_in_rules(word):
                            self.correction[line_index].append(self.rules[self.clean_word(word).lower()])
                            continue

                        corrected_previous_line = self.correct_line(previous_line.content.split()) if previous_line else ""
                        corrected_current_line = self.correct_line(words)
                        if not current_image:
                            # Créer l'image croppée avec le contexte des 3 lignes
                            current_image = crop_image_for_context(
                                image, current_line, previous_line, next_line
                            )

                        # Créer le contexte complet
                        context = WordContext(
                            word=word,
                            current_line=corrected_current_line,
                            previous_line=corrected_previous_line,
                            next_line=next_line.content if next_line else "",
                            cropped_image=current_image,
                            xml_file=xml_file,
                            line_index=line_index
                        )

                        yield context
            except Exception as e:
                print("error occured", e)
                self.save_dico()

            # Fermer l'image pour libérer la mémoire
            image.close()



    def add_correction(self, word, correction):
        word = self.clean_word(word)
        regex_match = self.check_regex(word)
        # on ne sauvegarde pas de règle de correction si correction est vide
        if correction:
            self.rules[word.lower()] = correction
        # si la correction est vide mais que le mot match une regex on remplace correction par le mot
        elif not correction and regex_match:
            correction = word
        self.correction[self.current_line].append(correction)

    def get_most_similar_words(self, word, nb_words=5):
        possible_results = []
        all_words = []

        for offset in [-1, 0, 1]:
            target_len = len(word) + offset
            if target_len in self.words_by_size:
                all_words.extend(self.words_by_size[target_len])

        for word_to_compare in all_words:
            dist = distance(word, word_to_compare)
            if dist < 5:
                possible_results.append((word_to_compare, dist))
        possible_results.sort(key=lambda x: x[1])
        # keep only word and not the dist
        return [x[0] for x in possible_results[:nb_words]]

    def is_word_in(self, word, dataset="dico"):
        if dataset == "dico":
            to_check = self.dico
        elif dataset == "rules":
            to_check = self.rules
        word = word.strip()

        word = self.clean_word(word)
        if word.lower() in to_check or word in to_check:
            return True

    is_word_in_dico = partialmethod(is_word_in, dataset="dico")
    is_word_in_rules = partialmethod(is_word_in, dataset="rules")

    def save_data(self):
        self.save_dico()
        self.save_rules()
        self.save_correction()

    def clean_word(self, word):
        if word in self.punkt:
            return word
        if len(word) >= 1 and word[-1] in self.punkt:
            word = word[:-1]
        if len(word) >= 1 and word[0] in self.punkt:
            word = word[1:]
        return word.strip()

    def correct_line(self, words):
        res = []
        for word in words:
            if self.is_word_in_rules(word):
                res.append(self.rules[self.clean_word(word).lower()])
            else:
                res.append(word)
        return " ".join(res)

    def check_regex(self, word):
        regex_match = False
        # si le mot est une regex alors on ne sauvegarde pas de règle non plus
        for regex in self.regex_rules:
            if regex.match(word.lower()):
                regex_match = True
                break
        return regex_match