# Context Tree

Herramienta de escritorio para generar archivos de contexto para IAs (Claude, ChatGPT, etc.) a partir de tu proyecto. 
En vez de copiar archivos uno por uno, seleccionas carpetas y archivos desde un explorador visual y generates un `.txt` listo para pegar.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-informational)
![Linux](https://img.shields.io/badge/OS-Linux-lightgrey)

---

## El problema que resuelve

Cuando trabajas con una IA en un proyecto de codigo, necesitas darle contexto: modelos, vistas, tipos, servicios, etc. 
El metodo manual es abrir cada archivo, copiar el contenido y pegarlo. Con proyectos grandes esto es lento y propenso a errores.

**Context Tree** te da un explorador visual de tu proyecto donde seleccionas exactamente lo que quieres incluir y genera el contexto en un click.

---

## Instalacion

**Requisitos:**

sudo apt install python3-tk
pip install customtkinter

**Clonar y ejecutar:**

git clone https://github.com/tu-usuario/context-tree.git
cd context-tree
python3 context_tree.py


**Alias opcional** (para llamarlo desde cualquier lugar):

Con un editor de texto abrir el archivo ./bashrc que se encuentra oculto en la caperta principal de usuario

# Agregar al final de ~/.bashrc
alias contree='python3 ~/ruta/context-tree/context_tree.py'

# Aplicar cambios ingresando en la terminal:
source ~/.bashrc

# Usar en la terminal el siguiente comando para inciar el programa
contree
```

---

## Uso

### 1. Cargar el proyecto

Escribe la ruta raiz de tu proyecto en el campo superior izquierdo y presiona **Cargar**. 
El arbol se popula automaticamente ignorando carpetas como `node_modules`, `__pycache__`, `.git`, `dist`, etc.

### 2. Seleccionar archivos

- **Click en un archivo** — lo marca con `[x]`
- **Click en una carpeta** — marca toda la carpeta recursivamente
- **Click en la flecha** — solo expande/colapsa, no selecciona

### 3. Buscar archivos rapido

Dos formas de buscar sin navegar el arbol manualmente:

- **`Ctrl+P`** — abre el Command Palette (estilo VSCode). Escribe parte del nombre, navega con flechas, Enter para ir al archivo en el arbol
- **Panel lateral** — busqueda permanente con resultados en tiempo real. Doble click en un resultado para navegar al archivo en el arbol

En ambos casos, el arbol **salta al archivo y lo resalta** sin marcarlo automaticamente — tu decides si lo incluyes con un click.

### 4. Generar el contexto

Con los archivos seleccionados, en el panel derecho:

| Boton | Accion |
|-------|--------|
| **Generar .txt** | Guarda el contenido en `~/textos_intranet/nombre.txt` |
| **Copiar** | Copia el contenido directo al portapapeles |
| **Bash** | Muestra el comando bash equivalente |

El panel muestra una estimacion de tokens, numero de archivos, lineas y peso en KB antes de generar.

### 5. Lista negra

Para excluir archivos o carpetas permanentemente del arbol:

- **Click derecho** sobre cualquier item → `[BLOQUEAR] Agregar a lista negra` — desaparece del arbol inmediatamente
- **Boton "Lista negra (N)"** en el footer — abre el panel de gestion donde puedes ver todo lo bloqueado y quitar entradas

La lista negra se guarda en `~/textos_intranet/.blacklist.json` y persiste entre sesiones.

---

## Archivos ignorados por defecto

**Carpetas:**
`node_modules`, `__pycache__`, `.git`, `env`, `dist`, `migrations`, `.next`, `build`, `.venv`, `media`

**Extensiones:**
`.pyc`, `.zip`, `.png`, `.jpg`, `.jpeg`, `.svg`, `.ico`, `.woff`, `.woff2`, `.ttf`, `.map`, `.lock`

---

## Estructura del output

Cada archivo seleccionado se concatena con un header identificador:

```
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

## Notas para Linux

Si el programa no arranca, verifica que tienes `python3-tk` instalado:

```bash
sudo apt install python3-tk
```

Si ves errores de `LC_ALL` o locale, no hay problema — la app esta disenada para funcionar con `LC_ALL=POSIX`.

---

## Licencia

MIT
