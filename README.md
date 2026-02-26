# Context Tree

Herramienta de escritorio para generar archivos de contexto para IAs (Claude, ChatGPT, etc.) a partir de tu proyecto. 
En vez de copiar archivos uno por uno, seleccionas carpetas y archivos desde un explorador visual y generas un `.txt` listo para pegar.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-informational)
![Linux](https://img.shields.io/badge/OS-Linux-lightgrey)

---

## El problema que resuelve

Cuando trabajas con una IA en un proyecto de código, necesitas darle contexto: modelos, vistas, tipos, servicios, etc. 
El método manual es abrir cada archivo, copiar el contenido y pegarlo. Con proyectos grandes esto es lento y propenso a errores.

**Context Tree** te da un explorador visual de tu proyecto donde seleccionas exactamente lo que quieres incluir y genera el contexto en un click.

---

## Instalación

### Requisitos:

\`\`\`bash
sudo apt install python3-tk
pip install customtkinter
\`\`\`

### Clonar y ejecutar:

\`\`\`bash
git clone https://github.com/tu-usuario/context-tree.git
cd context-tree
python3 context_tree.py
\`\`\`

### Alias opcional (para llamarlo desde cualquier lugar):

Con un editor de texto, abre el archivo \`.bashrc\` que se encuentra oculto en la carpeta principal de usuario:

\`\`\`bash
# Agregar al final de ~/.bashrc
alias contree='python3 ~/ruta/context-tree/context_tree.py'
\`\`\`

Aplica los cambios ingresando en la terminal:

\`\`\`bash
source ~/.bashrc
\`\`\`

Ahora puedes usar el siguiente comando para iniciar el programa:

\`\`\`bash
contree
\`\`\`

---

## Uso

### 1. Cargar el proyecto
Escribe la ruta raíz de tu proyecto en el campo superior izquierdo y presiona **Cargar**. 
El árbol se popula automáticamente ignorando carpetas como \`node_modules\`, \`__pycache__\`, \`.git\`, \`dist\`, etc.

### 2. Seleccionar archivos
*   **Click en un archivo**: lo marca con \`[x]\`
*   **Click en una carpeta**: marca toda la carpeta recursivamente.
*   **Click en la flecha**: solo expande/colapsa, no selecciona.

### 3. Buscar archivos rápido
Dos formas de buscar sin navegar el árbol manualmente:
*   **\`Ctrl+P\`**: abre el *Command Palette* (estilo VSCode). Escribe parte del nombre, navega con flechas y presiona \`Enter\` para ir al archivo en el árbol.
*   **Panel lateral**: búsqueda permanente con resultados en tiempo real. Doble click en un resultado para navegar al archivo en el árbol.

En ambos casos, el árbol **salta al archivo y lo resalta** sin marcarlo automáticamente; tú decides si lo incluyes con un click.

### 4. Generar el contexto
Con los archivos seleccionados, en el panel derecho:

| Botón | Acción |
| :--- | :--- |
| **Generar .txt** | Guarda el contenido en \`~/textos_intranet/nombre.txt\` |
| **Copiar** | Copia el contenido directo al portapapeles |
| **Bash** | Muestra el comando bash equivalente |

El panel muestra una estimación de tokens, número de archivos, líneas y peso en KB antes de generar.

### 5. Lista negra
Para excluir archivos o carpetas permanentemente del árbol:
*   **Click derecho** sobre cualquier ítem → \`[BLOQUEAR] Agregar a lista negra\`: desaparece del árbol inmediatamente.
*   **Botón "Lista negra (N)"** en el footer: abre el panel de gestión donde puedes ver todo lo bloqueado y quitar entradas.

La lista negra se guarda en \`~/textos_intranet/.blacklist.json\` y persiste entre sesiones.

---

## Archivos ignorados por defecto

*   **Carpetas:** \`node_modules\`, \`__pycache__\`, \`.git\`, \`env\`, \`dist\`, \`migrations\`, \`.next\`, \`build\`, \`.venv\`, \`media\`.
*   **Extensiones:** \`.pyc\`, \`.zip\`, \`.png\`, \`.jpg\`, \`.jpeg\`, \`.svg\`, \`.ico\`, \`.woff\`, \`.woff2\`, \`.ttf\`, \`.map\`, \`.lock\`.

---

## Estructura del output

Cada archivo seleccionado se concatena con un header identificador:

\`\`\`text
==>> ARCHIVO: /ruta/completa/al/archivo.py
------------------------------------------------------------
# contenido del archivo
...

==>> ARCHIVO: /ruta/completa/otro/archivo.ts
------------------------------------------------------------
// contenido del archivo
...
\`\`\`

---

## Notas para Linux

Si el programa no arranca, verifica que tienes \`python3-tk\` instalado:

\`\`\`bash
sudo apt install python3-tk
\`\`\`

Si ves errores de \`LC_ALL\` o locale, la app está diseñada para funcionar con \`LC_ALL=POSIX\` sin problemas.

---

## Licencia

MIT
