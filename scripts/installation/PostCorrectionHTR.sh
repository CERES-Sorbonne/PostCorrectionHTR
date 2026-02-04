#!/bin/bash

# Script d'installation et de lancement de PostCorrectionHTR pour macOS/Linux
# Vérifie et installe uniquement ce qui est nécessaire

set -e  # Arrêter en cas d'erreur

# Configuration
REPO_URL="https://github.com/CERES-Sorbonne/PostCorrectionHTR/archive/refs/heads/main.zip"
REPO_DIR="PostCorrectionHTR"
VENV_DIR=".venv"
PYTHON_VERSION="3.13"

# Couleurs pour les messages
CYAN='\033[96m'
GREEN='\033[92m'
RED='\033[91m'
YELLOW='\033[93m'
RESET='\033[0m'

print_info() {
    echo -e "${CYAN}$1${RESET}"
}

print_success() {
    echo -e "${GREEN}$1${RESET}"
}

print_error() {
    echo -e "${RED}$1${RESET}"
}

print_warning() {
    echo -e "${YELLOW}$1${RESET}"
}

# Fonction pour gérer les erreurs
handle_error() {
    print_error "✗ Erreur à l'étape : $1"
    echo ""
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
}

print_info "=== Installation et lancement de PostCorrectionHTR ==="
echo ""

# 1. Vérifier et installer uv
print_info "[1/6] Vérification de uv..."
if command -v uv &> /dev/null; then
    print_success "✓ uv est déjà installé"
    uv --version
else
    print_info "Installation de uv..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        print_success "✓ uv installé avec succès"
        # Ajouter uv au PATH pour cette session
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        handle_error "Installation de uv"
    fi
fi
echo ""

# 2. Télécharger le repository
print_info "[2/6] Vérification du repository..."
if [ -d "$REPO_DIR" ]; then
    print_success "✓ Le repository existe déjà dans $REPO_DIR"
else
    print_info "Téléchargement du repository..."

    # Télécharger le ZIP
    print_info "Téléchargement depuis GitHub..."
    if curl -L "$REPO_URL" -o PostCorrectionHTR.zip; then
        # Extraire le ZIP
        print_info "Extraction du fichier..."
        unzip -q PostCorrectionHTR.zip

        # Renommer le dossier
        mv PostCorrectionHTR-main "$REPO_DIR"

        # Supprimer le fichier ZIP
        rm PostCorrectionHTR.zip

        print_success "✓ Repository téléchargé et extrait avec succès"
    else
        handle_error "Téléchargement du repository"
    fi
fi
echo ""

# Se déplacer dans le dossier du repository
cd "$REPO_DIR" || handle_error "Impossible d'accéder au dossier $REPO_DIR"

# 3. Créer l'environnement virtuel
print_info "[3/6] Vérification de l'environnement virtuel..."
if [ -d "$VENV_DIR" ]; then
    print_success "✓ L'environnement virtuel existe déjà"
else
    print_info "Création de l'environnement virtuel avec Python $PYTHON_VERSION..."
    if uv venv --python "$PYTHON_VERSION" "$VENV_DIR"; then
        print_success "✓ Environnement virtuel créé"
    else
        handle_error "Création de l'environnement virtuel"
    fi
fi
echo ""

# 4. Vérifier si les dépendances sont installées
print_info "[4/6] Vérification des dépendances..."
dependencies_installed=false

if [ -d "$VENV_DIR/lib" ]; then
    # Chercher fastapi et uvicorn dans site-packages
    if find "$VENV_DIR/lib" -name "*fastapi*" -o -name "*uvicorn*" | grep -q .; then
        print_success "✓ Les dépendances semblent déjà installées"
        dependencies_installed=true
    fi
fi
echo ""

# 5. Installer les dépendances si nécessaire
if [ "$dependencies_installed" = false ]; then
    print_info "[5/6] Installation des dépendances depuis requirements.txt..."
    if [ -f "requirements.txt" ]; then
        if uv pip install -r requirements.txt; then
            print_success "✓ Dépendances installées avec succès"
        else
            handle_error "Installation des dépendances"
        fi
    else
        print_error "✗ Fichier requirements.txt introuvable"
        handle_error "Fichier requirements.txt manquant"
    fi
else
    print_info "[5/6] Les dépendances sont déjà installées, passage à l'étape suivante..."
fi
echo ""

# 6. Vérifier si les dossiers de données contiennent des fichiers
print_info "[6/6] Vérification des données..."

xml_files_exist=false
to_correct_exist=false

# Vérifier les fichiers .xml
if [ -d "resources/xml_files" ]; then
    if find resources/xml_files -maxdepth 1 -type f -name "*.xml" | grep -q .; then
        xml_files_exist=true
    fi
fi

# Vérifier les fichiers .txt
if [ -d "resources/to_correct" ]; then
    if find resources/to_correct -maxdepth 1 -type f -name "*.txt" | grep -q .; then
        to_correct_exist=true
    fi
fi

if [ "$xml_files_exist" = false ] || [ "$to_correct_exist" = false ]; then
    echo ""
    print_warning "======================================================================"
    print_warning "ATTENTION : Données manquantes"
    print_warning "======================================================================"
    echo ""
    print_info "L'installation est terminée, mais vous devez ajouter vos fichiers :"
    echo ""

    if [ "$xml_files_exist" = false ]; then
        print_info "  1. Placez vos fichiers XML (.xml) dans :"
        echo "     $(pwd)/resources/xml_files"
        echo ""
    fi

    if [ "$to_correct_exist" = false ]; then
        print_info "  2. Placez vos fichiers texte (.txt) à corriger dans :"
        echo "     $(pwd)/resources/to_correct"
        echo ""
    fi

    print_warning "Une fois les fichiers ajoutés, relancez ce programme."
    print_warning "======================================================================"
    echo ""
    read -p "Appuyez sur Entrée pour quitter..."
    exit 0
fi

print_success "✓ Les dossiers de données contiennent des fichiers (.xml et .txt)"
echo ""

# Lancer l'API
print_info "Lancement de l'API..."
if [ -f "api/main.py" ]; then
    print_success "✓ Fichier api/main.py trouvé"
    echo ""
    print_info "Démarrage du serveur uvicorn..."
    print_info "L'API sera accessible à l'adresse: http://127.0.0.1:8000"
    print_info "Documentation interactive: http://127.0.0.1:8000/docs"
    echo ""
    print_info "Appuyez sur Ctrl+C pour arrêter le serveur"
    print_info "----------------------------------------"
    echo ""

    # Lancer uvicorn avec uv run
    uv run uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
else
    print_error "✗ Fichier api/main.py introuvable"
    handle_error "Fichier api/main.py manquant"
fi