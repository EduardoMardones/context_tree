#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Context Tree — Instalador para Linux / macOS
#  Uso: bash install.sh
# ─────────────────────────────────────────────────────────────

set -e

INSTALL_DIR="$HOME/.context-tree"
REPO_URL="https://raw.githubusercontent.com/EduardoMardones/context_tree/main/context_tree.py"
BIN_NAME="contree"

GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

step()  { echo -e "${CYAN}▶  $1${NC}"; }
ok()    { echo -e "${GREEN}✔  $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠  $1${NC}"; }
error() { echo -e "${RED}✖  $1${NC}"; exit 1; }

echo ""
echo -e "${CYAN}╔══════════════════════════════════════╗"
echo -e "║       Context Tree  —  Instalador    ║"
echo -e "╚══════════════════════════════════════╝${NC}"
echo ""

# ── 1. Detectar OS ───────────────────────────────────────────
OS="$(uname -s)"
step "Sistema detectado: $OS"

# ── 2. Verificar Python 3.10+ ────────────────────────────────
step "Verificando Python..."
if ! command -v python3 &>/dev/null; then
    error "Python 3 no encontrado. Instálalo desde https://www.python.org/downloads/"
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    error "Se requiere Python 3.10+. Versión encontrada: $PY_VER"
fi
ok "Python $PY_VER encontrado"

# ── 3. Instalar python3-tk si es Linux ───────────────────────
if [ "$OS" = "Linux" ]; then
    step "Verificando tkinter..."
    if ! python3 -c "import tkinter" &>/dev/null; then
        warn "tkinter no encontrado. Intentando instalar..."
        if command -v apt &>/dev/null; then
            sudo apt install -y python3-tk
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3-tkinter
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm tk
        else
            error "No se pudo instalar tkinter automáticamente. Instálalo manualmente para tu distribución."
        fi
    fi
    ok "tkinter disponible"
fi

# ── 4. Crear carpeta de instalacion ──────────────────────────
step "Creando directorio de instalación en $INSTALL_DIR ..."
mkdir -p "$INSTALL_DIR"
ok "Directorio listo"

# ── 5. Descargar o copiar el script ──────────────────────────
SCRIPT_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/context_tree.py"

if [ -f "$SCRIPT_SRC" ]; then
    step "Copiando context_tree.py desde directorio local..."
    cp "$SCRIPT_SRC" "$INSTALL_DIR/context_tree.py"
    ok "Archivo copiado"
else
    step "Descargando context_tree.py desde GitHub..."
    if command -v curl &>/dev/null; then
        curl -fsSL "$REPO_URL" -o "$INSTALL_DIR/context_tree.py" || error "No se pudo descargar el archivo"
    elif command -v wget &>/dev/null; then
        wget -q "$REPO_URL" -O "$INSTALL_DIR/context_tree.py" || error "No se pudo descargar el archivo"
    else
        error "curl o wget no encontrados. Instala uno de ellos e intenta de nuevo."
    fi
    ok "Descarga completa"
fi

# ── 6. Crear entorno virtual ──────────────────────────────────
step "Creando entorno virtual en $INSTALL_DIR/.venv ..."
python3 -m venv "$INSTALL_DIR/.venv" --system-site-packages
ok "Entorno virtual creado"

# ── 7. Instalar dependencias ──────────────────────────────────
step "Instalando dependencias (customtkinter, Pillow)..."
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet customtkinter Pillow
ok "Dependencias instaladas"

# ── 8. Crear script lanzador ──────────────────────────────────
step "Creando comando '$BIN_NAME'..."

LAUNCHER="$INSTALL_DIR/contree"
cat > "$LAUNCHER" << EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/context_tree.py" "\$@"
EOF
chmod +x "$LAUNCHER"
ok "Lanzador creado"

# ── 9. Agregar al PATH en el shell rc ────────────────────────
step "Agregando $INSTALL_DIR al PATH..."

add_to_rc() {
    local RC="$1"
    local LINE="export PATH=\"\$PATH:$INSTALL_DIR\""
    if [ -f "$RC" ] && grep -qF "$INSTALL_DIR" "$RC"; then
        warn "Ya estaba en $RC, omitido"
    else
        echo "" >> "$RC"
        echo "# Context Tree" >> "$RC"
        echo "$LINE" >> "$RC"
        ok "Agregado a $RC"
    fi
}

ADDED=0

if [ -f "$HOME/.zshrc" ]; then
    add_to_rc "$HOME/.zshrc"
    ADDED=1
fi
if [ -f "$HOME/.bashrc" ]; then
    add_to_rc "$HOME/.bashrc"
    ADDED=1
fi
if [ -f "$HOME/.bash_profile" ] && [ "$ADDED" -eq 0 ]; then
    add_to_rc "$HOME/.bash_profile"
fi

# ── 10. Listo ─────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗"
echo -e "║   ✔  Context Tree instalado con éxito   ║"
echo -e "╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Reinicia tu terminal o ejecuta:"
echo -e "    ${CYAN}source ~/.bashrc${NC}   (o ~/.zshrc si usas zsh)"
echo ""
echo -e "  Luego inicia el programa con:"
echo -e "    ${CYAN}contree${NC}"
echo ""
