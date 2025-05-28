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

