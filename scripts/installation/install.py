"""
Script d'installation et de lancement de PostCorrectionHTR
Vérifie et installe uniquement ce qui est nécessaire
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

from pathlib import Path
import time

# Configuration
REPO_URL = "https://github.com/CERES-Sorbonne/PostCorrectionHTR/archive/refs/heads/main.zip"
REPO_DIR = "PostCorrectionHTR"
VENV_DIR = "post_correction_env"
PYTHON_VERSION = "3.13"

# Couleurs pour les messages (Windows)
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    
    @staticmethod
    def enable_windows_colors():
        """Active les couleurs ANSI sur Windows"""
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def print_info(message):
    print(f"{Colors.CYAN}{message}{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}{message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}{message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}{message}{Colors.RESET}")

def run_command(command, shell=True, check=True, capture_output=False):
    """Exécute une commande et retourne le résultat"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
            return result
        else:
            result = subprocess.run(command, shell=shell, check=check)
            return result
    except subprocess.CalledProcessError as e:
        return None

def check_uv_installed():
    """Vérifie si uv est installé"""
    result = run_command("uv --version", capture_output=True, check=False)
    return result is not None and result.returncode == 0

def install_uv():
    """Installe uv via PowerShell"""
    print_info("Installation de uv...")
    
    # Commande PowerShell pour installer uv
    ps_command = 'irm https://astral.sh/uv/install.ps1 | iex'
    command = f'powershell -Command "{ps_command}"'
    
    result = run_command(command, check=False)
    
    if result and result.returncode == 0:
        print_success("✓ uv installé avec succès")
        
        # Ajouter le chemin de uv au PATH pour cette session
        user_profile = os.environ.get('USERPROFILE', '')
        uv_path = os.path.join(user_profile, '.cargo', 'bin')
        if os.path.exists(uv_path):
            os.environ['PATH'] = uv_path + os.pathsep + os.environ['PATH']
        
        return True
    else:
        print_error("✗ Échec de l'installation de uv")
        return False

def download_and_extract_repo():
    """Télécharge et extrait le repository"""
    print_info("Téléchargement du repository...")
    
    zip_file = "PostCorrectionHTR.zip"
    
    try:
        # Télécharger le fichier
        print_info("Téléchargement depuis GitHub...")
        urllib.request.urlretrieve(REPO_URL, zip_file)
        
        # Extraire le ZIP
        print_info("Extraction du fichier...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Renommer le dossier (GitHub ajoute -main au nom)
        if os.path.exists("PostCorrectionHTR-main"):
            if os.path.exists(REPO_DIR):
                shutil.rmtree(REPO_DIR)
            os.rename("PostCorrectionHTR-main", REPO_DIR)
        
        # Supprimer le fichier ZIP
        os.remove(zip_file)
        
        print_success("✓ Repository téléchargé et extrait avec succès")
        return True
        
    except Exception as e:
        print_error(f"✗ Échec du téléchargement: {e}")
        if os.path.exists(zip_file):
            os.remove(zip_file)
        return False

def create_venv():
    """Crée l'environnement virtuel avec uv"""
    print_info(f"Création de l'environnement virtuel avec Python {PYTHON_VERSION}...")
    
    result = run_command(f"uv venv --python {PYTHON_VERSION} {VENV_DIR}", check=False)
    
    if result and result.returncode == 0:
        print_success("✓ Environnement virtuel créé")
        return True
    else:
        print_error("✗ Échec de la création de l'environnement virtuel")
        return False

def check_dependencies_installed():
    """Vérifie si les dépendances sont déjà installées"""
    site_packages = Path(VENV_DIR) / "Lib" / "site-packages"
    
    if not site_packages.exists():
        return False
    
    # Vérifier si fastapi et uvicorn sont installés
    packages = [d.name for d in site_packages.iterdir() if d.is_dir()]
    has_fastapi = any("fastapi" in p.lower() for p in packages)
    has_uvicorn = any("uvicorn" in p.lower() for p in packages)
    
    return has_fastapi and has_uvicorn

def install_dependencies():
    """Installe les dépendances depuis requirements.txt"""
    print_info("Installation des dépendances depuis requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        print_error("✗ Fichier requirements.txt introuvable")
        return False
    
    result = run_command("uv pip install -r requirements.txt", check=False)
    
    if result and result.returncode == 0:
        print_success("✓ Dépendances installées avec succès")
        return True
    else:
        print_error("✗ Échec de l'installation des dépendances")
        return False

def launch_api():
    """Lance l'API FastAPI avec uvicorn"""
    print_info("Lancement de l'API FastAPI...")
    
    if not os.path.exists("api/main.py") and not os.path.exists("api\\main.py"):
        print_error("✗ Fichier api/main.py introuvable")
        return False
    
    print_success("✓ Fichier api/main.py trouvé")
    print()
    print_info("Démarrage du serveur uvicorn...")
    print_info("L'API sera accessible à l'adresse: http://127.0.0.1:8000")
    print_info("Documentation interactive: http://127.0.0.1:8000/docs")
    print()
    print_info("Appuyez sur Ctrl+C pour arrêter le serveur")
    print_info("----------------------------------------")
    print()
    
    # Lancer uvicorn avec uv run
    try:
        subprocess.run("uv run uvicorn api.main:app --reload --host 127.0.0.1 --port 8000", 
                      shell=True, check=True)
    except KeyboardInterrupt:
        print()
        print_warning("Serveur arrêté par l'utilisateur")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"✗ Erreur lors du lancement de l'API: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    # Activer les couleurs sur Windows
    Colors.enable_windows_colors()
    
    print_info("=== Installation et lancement de PostCorrectionHTR ===")
    print()
    
    # Sauvegarder le répertoire de départ
    start_dir = os.getcwd()
    
    try:
        # 1. Vérifier et installer uv
        print_info("[1/6] Vérification de uv...")
        if check_uv_installed():
            print_success("✓ uv est déjà installé")
            result = run_command("uv --version", capture_output=True)
            if result:
                print(result.stdout.strip())
        else:
            if not install_uv():
                print_error("Installation de uv requise. Veuillez réessayer.")
                input("\nAppuyez sur Entrée pour quitter...")
                return
        print()
        
        # 2. Télécharger le repository
        print_info("[2/6] Vérification du repository...")
        if os.path.exists(REPO_DIR):
            print_success(f"✓ Le repository existe déjà dans {REPO_DIR}")
        else:
            if not download_and_extract_repo():
                input("\nAppuyez sur Entrée pour quitter...")
                return
        print()
        
        # Se déplacer dans le dossier du repository
        os.chdir(REPO_DIR)
        
        # 3. Créer l'environnement virtuel
        print_info("[3/6] Vérification de l'environnement virtuel...")
        if os.path.exists(VENV_DIR):
            print_success("✓ L'environnement virtuel existe déjà")
        else:
            if not create_venv():
                os.chdir(start_dir)
                input("\nAppuyez sur Entrée pour quitter...")
                return
        print()
        
        # 4. Vérifier les dépendances
        print_info("[4/6] Vérification des dépendances...")
        dependencies_installed = check_dependencies_installed()
        
        if dependencies_installed:
            print_success("✓ Les dépendances semblent déjà installées")
        print()
        
        # 5. Installer les dépendances si nécessaire
        if not dependencies_installed:
            print_info("[5/6] Installation des dépendances...")
            if not install_dependencies():
                os.chdir(start_dir)
                input("\nAppuyez sur Entrée pour quitter...")
                return
        else:
            print_info("[5/6] Les dépendances sont déjà installées, passage à l'étape suivante...")
        print()
        
        # 6. Lancer l'API
        print_info("[6/6] Lancement de l'API...")
        launch_api()
        
    except Exception as e:
        print_error(f"\n✗ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour quitter...")
    finally:
        # Revenir au répertoire de départ
        os.chdir(start_dir)

if __name__ == "__main__":
    main()