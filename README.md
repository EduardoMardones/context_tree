# Generador de Contexto para Proyectos

Esta herramienta permite cargar un proyecto, seleccionar archivos específicos y generar un archivo consolidado de texto ideal para ser usado como contexto en modelos de lenguaje (LLMs).

## Guía de Uso

### 1. Cargar el proyecto
Ingresa la ruta raíz de tu proyecto en el campo superior izquierdo y presiona el botón **Cargar**. 
El árbol de archivos se generará automáticamente, omitiendo carpetas irrelevantes como `node_modules`, `__pycache__`, `.git`, `dist`, entre otras.

### 2. Selección de archivos
Navegar y seleccionar archivos es intuitivo:
- **Click en un archivo**: Lo marca o desmarca con `[x]`.
- **Click en una carpeta**: Selecciona o deselecciona toda la carpeta de forma recursiva.
- **Click en la flecha (▸)**: Expande o colapsa el directorio sin alterar la selección actual.

### 3. Búsqueda rápida
Existen dos métodos para localizar archivos sin navegar manualmente:
- **`Ctrl + P` (Command Palette)**: Al estilo VSCode. Escribe parte del nombre, navega con las flechas y presiona `Enter` para saltar al archivo en el árbol.
- **Panel lateral**: Buscador permanente con resultados en tiempo real. Haz **doble click** en un resultado para desplazarte automáticamente hasta el archivo.

> **Nota:** En ambos casos, el sistema resalta el archivo para que decidas si incluirlo con un click, pero no lo marca automáticamente.

### 4. Generación del contexto
Una vez seleccionado el código, utiliza el panel derecho para procesarlo. Verás una estimación previa de **tokens, número de archivos, líneas y peso en KB**.

| Botón | Acción |
| :--- | :--- |
| **Generar .txt** | Guarda el contenido en `~/textos_intranet/[nombre_del_archivo].txt` |
| **Copiar** | Copia el contenido directamente al portapapeles |
| **Bash** | Muestra el comando bash equivalente para obtener el mismo resultado |

### 5. Gestión de Lista Negra (Blacklist)
Puedes excluir archivos o carpetas permanentemente para que no aparezcan en futuras cargas:
- **Click derecho** sobre cualquier ítem → Selecciona `[BLOQUEAR] Agregar a lista negra`. El elemento desaparecerá inmediatamente.
- **Botón "Lista negra (N)"**: Ubicado en el footer, permite ver todos los elementos bloqueados y eliminarlos de la lista si es necesario.

*La lista negra se guarda en `~/textos_intranet/.blacklist.json` y persiste entre sesiones.*

---

## Archivos ignorados por defecto

Para optimizar el rendimiento y la limpieza del contexto, se ignoran:

**Carpetas:**  
`node_modules`, `__pycache__`, `.git`, `env`, `dist`, `migrations`, `.next`, `build`, `.venv`, `media`

**Extensiones:**  
`.pyc`, `.zip`, `.png`, `.jpg`, `.jpeg`, `.svg`, `.ico`, `.woff`, `.woff2`, `.ttf`, `.map`, `.lock`

---

## Estructura del Output

El resultado final concatena los archivos seleccionados, separándolos con un encabezado claro que indica la ruta del archivo, facilitando la lectura para el usuario o el análisis por parte de una IA.
