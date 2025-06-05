# PostCorrectionHTR

Scripts de posts correction d'HTR du corpus d'académie française.
L'idée est de checker avec un Levenshtein tous les mots n'étant pas dans un dictionnaire et de proposer des corrections basées sur le dico.
On enrichit le dico au fur et à mesure avec des inputs utilisateurs et on construit des règles de correction. 

## Installation

`pip install levenshtein`

## Utilisation 

Executer toutes les cellules de scripts/test_levenstein.ipynb c'est la dernière qui contient la boucle principale

## Logique

- On check si un mot est dans le dico
- Si il ne l'est pas on execute dans l'ordre:
  - Y a t il une règle de correction associée à ce mot ? Les règles sont stockées dans resources/rules.json
  - Y a t il une règle regex permettant d'ignorer ce mot ? Stockées aussi dans rules.json
  - Doit on ajouter ce mot au dictionnaire ? 
  - On cherche des corrections possibles dans le dictionnaire avec Levenshtein et on les propose
  - Si il y en a des pertinentes on peut ajouter une nouvelle règle de correction avec la correction choisie. 

## Utilisation de l'API

- Installer les requirements avec pip install -r requirements.txt
- Lancer avec `python -m uvicorn main:app --reload`

## Améliorations à faire

- Pouvoir sélectionner une zone à corriger, (si par exemple l'OCR a donné "A bsans" actuellement le programme va nous proposer de corriger "bsans" en "absent" alors que c'est "A" et "bsans" qu'il faudrait corriger)
- Afficher un bout d'image originale si on a le fichier et la hbox
- Pouvoir revenir en arrière après avoir corrigé
- Nettoyer le code en utilisant une classe gérant un state
- Tenter de faire d'autres corrections en utilisant mistral api