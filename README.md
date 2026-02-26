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

```bash
sudo apt install python3-tk
pip install customtkinter
