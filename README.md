# PostCorrectionHTR

Scripts de posts correction d'HTR des comités de la Comédie-française.
L'idée est de checker avec un Levenshtein tous les mots n'étant pas dans un dictionnaire et de proposer des corrections basées sur le dico.
On enrichit le dico au fur et à mesure avec des inputs utilisateurs et on construit des règles de correction. 

## Installation

`pip install levenshtein`

## Utilisation 

Prérequis: avoir téléchargé dans eScriptorium à la fois le txt des transcriptions et l'ALTO (dossier zip).
Dans le dossier "resources": 
- mettre dans le dossier "to_correct" le fichier txt
- mettre dans le xml_files le dossier zip décompressé (supprimer le fichier "METS").

Ensuite, aller dans le dossier "api" et ouvrir le fichier "core.py", modifier :
- TO_CORRECT_PATH = "../resources/to_correct/nom_du_fichier.txt" pour mettre le chemin vers le fichier txt ;
- CORRECTED_PATH = "../resources/nom_fichier_corrigé" renseigné le nom des transcriptions corrigées (idéalement: cote_post_corrige);
- XML_FILES_PATH = "../resources/xml_files/nom_dossier_alto" pour mettre le chemin vers le dossier alto


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
- Pouvoir revenir en arrière après avoir corrigé
- Nettoyer le code en utilisant une classe gérant un state
- Tenter de faire d'autres corrections en utilisant mistral api
