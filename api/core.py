import json
import re
from collections import defaultdict
from functools import partial, wraps, partialmethod

from Levenshtein import distance


DICO_PATH = '../resources/dico.json'
RULES_PATH = '../resources/correct_rules.json'
TO_CORRECT_PATH = "../resources/to_correct.txt"
CORRECTED_PATH = "../resources/corrected.txt"


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

    def generate_sample(self):
        try:
            with open(TO_CORRECT_PATH, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                for line_index, line in enumerate(all_lines):
                    previous_line = "" if line_index == 0 else all_lines[line_index - 1]
                    self.current_line = line_index
                    next_line = "" if line_index == len(all_lines) - 1 else all_lines[line_index + 1]

                    if line_index % 10 == 0:
                        self.save_data()
                    for word in line.split():
                        if self.is_word_in_dico(word):
                            self.correction[line_index].append(word)
                            continue
                        regex_match = False
                        for regex in self.regex_rules:
                            if regex.match(word.lower()):
                                regex_match = True
                                break
                        if regex_match:
                            self.correction[line_index].append(word)
                            continue
                        if self.is_word_in_rules(word):
                            self.correction[line_index].append(self.rules[self.clean_word(word).lower()])
                            continue
                        previous_line = self.correct_line(previous_line)
                        corrected_line = self.correct_line(line)
                        yield word, previous_line, corrected_line, next_line
        except Exception as e:
            print(e)
            self.save_data()
            raise e

    def add_correction(self, word, correction):
        word = self.clean_word(word)
        self.correction[self.current_line].append(correction)
        self.rules[word.lower()] = correction

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

    def correct_line(self, line):
        res = []
        for word in line.split():
            if self.is_word_in_rules(word):
                res.append(self.rules[self.clean_word(word).lower()])
            else:
                res.append(word)
        return " ".join(res)