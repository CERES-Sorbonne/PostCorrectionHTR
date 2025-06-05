import json
import re
from Levenshtein import distance


DICO_PATH = '../resources/dico.json'
RULES_PATH = '../resources/correct_rules.json'
TO_CORRECT_PATH = "../resources/to_correct.txt"

def load_dico():
    with open(DICO_PATH, 'r', encoding='utf-8') as f:
        dico = set(json.load(f))
    words_by_size = {}
    dico_list = list(dico)
    dico_list.sort(key=len, reverse=True)
    current_length = len(dico_list[0])
    words_by_size[current_length] = [dico_list[0]]

    for index, word in enumerate(dico_list):
        if len(word) == current_length:
            words_by_size[current_length].append(word)
            continue
        current_length = len(word)
        words_by_size[current_length] = [word]

    return dico, words_by_size


def load_rules():
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        all_rules = json.load(f)
        rules = all_rules['rules']
        regex_rules = [re.compile(expr) for expr in all_rules['regex_rules']]
        return rules, regex_rules


def save_rules(rules, regex_rules):
    regex_rules = [e.pattern for e in regex_rules]
    with open(RULES_PATH, mode='w', encoding='utf-8') as f:
        json.dump(
            {
                "rules": rules,
                "regex_rules": regex_rules
            },
            f,
            ensure_ascii=False,
            indent=2
        )

def save_dico(dico):
    with open(DICO_PATH, 'w', encoding='utf-8') as f:
        json.dump(dico, f, ensure_ascii=False, indent=2)


def add_to_dico(word, dico, words_by_size):
    dico.add(word)
    words_by_size[len(word)].append(word)
    return dico, words_by_size

def generate_sample():
    with open(TO_CORRECT_PATH, 'r', encoding='utf-8') as f:
        for line_index, line in enumerate(f):
            for word in line.split():
                yield word, line, line_index


def get_most_similar_words(word, words_by_size):
    possible_results = []
    all_words = words_by_size[len(word)]
    if len(word) + 1 in words_by_size:
        all_words += words_by_size[len(word) + 1]
    if len(word) - 1 in words_by_size:
        all_words += words_by_size[len(word) - 1]
    for word_to_compare in all_words:
        dist = distance(word, word_to_compare)
        if dist < 5:
            possible_results.append((word_to_compare, dist))
    possible_results.sort(key=lambda x: x[1])
    return possible_results
