# Context Tree

Herramienta de escritorio para generar archivos de contexto para IAs (Claude, ChatGPT, etc.) a partir de tu proyecto.
En vez de copiar archivos uno por uno, seleccionas carpetas y archivos desde un explorador visual y generas un `.txt` listo para pegar.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-informational)
![Linux](https://img.shields.io/badge/OS-Linux-lightgrey)
![Windows](https://img.shields.io/badge/OS-Windows-blue)

---

## El problema que resuelve

Cuando trabajas con una IA en un proyecto de código, necesitas darle contexto: modelos, vistas, tipos, servicios, etc.
El método manual es abrir cada archivo, copiar el contenido y pegarlo. Con proyectos grandes esto es lento y propenso a errores.

**Context Tree** te da un explorador visual de tu proyecto donde seleccionas exactamente lo que quieres incluir y genera el contexto en un click.

---

## Instalación

### Requisito único: Python 3.10+

- **Linux**: normalmente ya viene instalado. Verificá con `python3 --version`.
- **Windows**: descargalo desde [python.org](https://www.python.org/downloads/) — al instalarlo, **marcá la opción "Add Python to PATH"**.

---

### Linux / macOS — un solo comando

```bash
git clone https://github.com/EduardoMardones/context_tree.git
cd context_tree
bash install.sh
```

El script automáticamente:
- Detecta tu sistema operativo
- Instala `tkinter` si falta (en Linux)
- Crea `~/.context-tree/` con el programa y un entorno virtual aislado
- Instala `customtkinter` y `Pillow` dentro del entorno virtual
- Agrega el comando `contree` a tu PATH

Luego abrí una terminal nueva y ejecutá:

```bash
contree
```

---

### Windows — un solo comando (PowerShell)

```powershell
git clone https://github.com/EduardoMardones/context_tree.git
cd context_tree
.\install.ps1
```

> Si ves un error de *"ejecución de scripts deshabilitada"*, ejecutá esto primero en PowerShell como administrador:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

El script automáticamente:
- Crea `%USERPROFILE%\.context-tree\` con el programa y un entorno virtual aislado
- Instala `customtkinter` y `Pillow` dentro del entorno virtual
- Crea un comando `contree.bat` y lo agrega a tu PATH

Luego abre una terminal nueva y ejecuta:

```powershell
contree
```

---

## Uso

### 1. Cargar el proyecto
Al abrir el programa aparece un selector de carpeta. Elegí la raíz de tu proyecto y presioná **Confirmar**.
El árbol se popula automáticamente ignorando carpetas como `node_modules`, `__pycache__`, `.git`, `dist`, etc.

### 2. Seleccionar archivos
- **Click en un archivo**: lo marca con `[x]`
- **Click en una carpeta**: marca toda la carpeta recursivamente.
- **Click en la flecha**: solo expande/colapsa, no selecciona.

### 3. Buscar archivos rápido
Dos formas de buscar sin navegar el árbol manualmente:
- **`Ctrl+P`**: abre el *Command Palette* (estilo VSCode). Escribí parte del nombre, navegá con flechas y presioná `Enter` para ir al archivo en el árbol.
- **Panel lateral**: búsqueda permanente con resultados en tiempo real. Doble click en un resultado para navegar al archivo en el árbol.

En ambos casos, el árbol **salta al archivo y lo resalta** sin marcarlo automáticamente; vos decidís si lo incluís con un click.

### 4. Generar el contexto
Con los archivos seleccionados, en el panel derecho:

| Botón | Acción |
| :--- | :--- |
| **Generar .txt** | Guarda el contenido en `~/textos_intranet/nombre.txt` |
| **Copiar** | Copia el contenido directo al portapapeles |
| **Bash** | Muestra el comando bash equivalente |

El panel muestra una estimación de tokens, número de archivos, líneas y peso en KB antes de generar.

### 5. Lista negra
Para excluir archivos o carpetas permanentemente del árbol:
- **Click derecho** sobre cualquier ítem → `[BLOQUEAR] Agregar a lista negra`: desaparece del árbol inmediatamente.
- **Botón "Lista negra (N)"** en el footer: abre el panel de gestión donde podés ver todo lo bloqueado y quitar entradas.

La lista negra se guarda en `~/textos_intranet/.blacklist.json` y persiste entre sesiones.

---

## Archivos ignorados por defecto

- **Carpetas:** `node_modules`, `__pycache__`, `.git`, `env`, `dist`, `migrations`, `.next`, `build`, `.venv`, `media`.
- **Extensiones:** `.pyc`, `.zip`, `.png`, `.jpg`, `.jpeg`, `.svg`, `.ico`, `.woff`, `.woff2`, `.ttf`, `.map`, `.lock`.

---

## Estructura del output

Cada archivo seleccionado se concatena con un header identificador:

```text
==>> ARCHIVO: /ruta/completa/al/archivo.py
------------------------------------------------------------
# contenido del archivo
...

==>> ARCHIVO: /ruta/completa/otro/archivo.ts
------------------------------------------------------------
// contenido del archivo
...
```

---

## Desinstalar

### Linux / macOS
```bash
rm -rf ~/.context-tree
```
Luego eliminá la línea `# Context Tree` y la siguiente de tu `~/.bashrc` o `~/.zshrc`.

### Windows
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.context-tree"
```
Y eliminá la entrada del PATH en: `Panel de control → Variables de entorno`.

---

## Licencia

MIT