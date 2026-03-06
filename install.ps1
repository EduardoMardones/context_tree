# ─────────────────────────────────────────────────────────────────────────────
#  Context Tree — Instalador para Windows (PowerShell)
#  Uso: Clic derecho sobre este archivo → "Ejecutar con PowerShell"
#       o desde PowerShell:  .\install.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

$INSTALL_DIR = "$env:USERPROFILE\.context-tree"
$REPO_URL    = "https://raw.githubusercontent.com/EduardoMardones/context_tree/main/context_tree.py"
$BIN_NAME    = "contree"

function Write-Step  { param($msg) Write-Host ">>  $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "OK  $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "!!  $msg" -ForegroundColor Yellow }
function Write-Fail  { param($msg) Write-Host "ERR $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Context Tree  --  Instalador       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Verificar Python 3.10+ ────────────────────────────────────────────────
Write-Step "Verificando Python..."
try {
    $pyVer = & python --version 2>&1
} catch {
    Write-Fail "Python no encontrado. Descárgalo en https://www.python.org/downloads/ (marca 'Add Python to PATH')"
}

if ($pyVer -match "Python (\d+)\.(\d+)") {
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        Write-Fail "Se requiere Python 3.10+. Versión encontrada: $pyVer"
    }
    Write-Ok "$pyVer encontrado"
} else {
    Write-Fail "No se pudo determinar la versión de Python."
}

# ── 2. Crear carpeta de instalación ──────────────────────────────────────────
Write-Step "Creando directorio de instalación en $INSTALL_DIR ..."
New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null
Write-Ok "Directorio listo"

# ── 3. Copiar o descargar context_tree.py ────────────────────────────────────
$scriptSrc = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "context_tree.py"

if (Test-Path $scriptSrc) {
    Write-Step "Copiando context_tree.py desde directorio local..."
    Copy-Item $scriptSrc "$INSTALL_DIR\context_tree.py" -Force
    Write-Ok "Archivo copiado"
} else {
    Write-Step "Descargando context_tree.py desde GitHub..."
    try {
        Invoke-WebRequest -Uri $REPO_URL -OutFile "$INSTALL_DIR\context_tree.py" -UseBasicParsing
        Write-Ok "Descarga completa"
    } catch {
        Write-Fail "No se pudo descargar el archivo. Verifica tu conexión o el repositorio."
    }
}

# ── 4. Crear entorno virtual ──────────────────────────────────────────────────
Write-Step "Creando entorno virtual en $INSTALL_DIR\.venv ..."
& python -m venv "$INSTALL_DIR\.venv"
Write-Ok "Entorno virtual creado"

# ── 5. Instalar dependencias ──────────────────────────────────────────────────
Write-Step "Instalando dependencias (customtkinter, Pillow)..."
& "$INSTALL_DIR\.venv\Scripts\pip.exe" install --quiet --upgrade pip
& "$INSTALL_DIR\.venv\Scripts\pip.exe" install --quiet customtkinter Pillow
Write-Ok "Dependencias instaladas"

# ── 6. Crear lanzador .bat ────────────────────────────────────────────────────
Write-Step "Creando comando '$BIN_NAME'..."
$batPath = "$INSTALL_DIR\contree.bat"
$batContent = "@echo off`r`n`"$INSTALL_DIR\.venv\Scripts\pythonw.exe`" `"$INSTALL_DIR\context_tree.py`" %*"
Set-Content -Path $batPath -Value $batContent -Encoding ASCII
Write-Ok "Lanzador creado en $batPath"

# ── 7. Agregar al PATH del usuario ────────────────────────────────────────────
Write-Step "Agregando $INSTALL_DIR al PATH del usuario..."
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$INSTALL_DIR*") {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$INSTALL_DIR", "User")
    Write-Ok "Agregado al PATH del usuario"
} else {
    Write-Warn "Ya estaba en el PATH, omitido"
}

# ── 8. Listo ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   OK  Context Tree instalado con exito  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Abre una terminal NUEVA y ejecuta:" -ForegroundColor White
Write-Host "    contree" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Nota: si ves un error de 'ejecución de scripts deshabilitada'," -ForegroundColor Yellow
Write-Host "  ejecuta primero en PowerShell (como administrador):" -ForegroundColor Yellow
Write-Host "    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
Write-Host ""