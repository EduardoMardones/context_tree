#!/usr/bin/env python3
"""
Context Tree - Generador de contexto para IA
v4: Lista negra con click derecho + panel de gestion + persistencia JSON
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import threading
from pathlib import Path
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OUTPUT_DIR = Path.home() / "textos_intranet"
OUTPUT_DIR.mkdir(exist_ok=True)
BLACKLIST_FILE = OUTPUT_DIR / ".blacklist.json"

IGNORE_EXTENSIONS = {
    ".pyc",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".map",
    ".lock",
}
IGNORE_DIRS = {
    "node_modules",
    "__pycache__",
    ".git",
    "env",
    "dist",
    "migrations",
    ".next",
    "build",
    ".venv",
    "media",
}

C = {
    "bg_dark": "#0d1117",
    "bg_panel": "#161b22",
    "bg_item": "#1c2128",
    "bg_hover": "#21262d",
    "bg_select": "#1f3a5f",
    "accent": "#58a6ff",
    "accent2": "#3fb950",
    "red": "#f85149",
    "red_dim": "#3d1a1a",
    "red_hover": "#5a1f1f",
    "text": "#e6edf3",
    "text_dim": "#8b949e",
    "text_muted": "#484f58",
    "border": "#30363d",
    "highlight": "#ffa657",
}


# ─── Persistencia de lista negra ─────────────────────────────────────────────


def load_blacklist() -> set[str]:
    try:
        if BLACKLIST_FILE.exists():
            data = json.loads(BLACKLIST_FILE.read_text())
            return set(data.get("paths", []))
    except Exception:
        pass
    return set()


def save_blacklist(bl: set[str]):
    try:
        BLACKLIST_FILE.write_text(json.dumps({"paths": sorted(bl)}, indent=2))
    except Exception:
        pass


# ─── Utilidades ─────────────────────────────────────────────────────────────


def should_ignore(name: str, is_dir: bool) -> bool:
    if is_dir:
        return name in IGNORE_DIRS or name.startswith(".")
    return Path(name).suffix.lower() in IGNORE_EXTENSIONS or name.startswith(".")


def collect_files(path: Path, blacklist: set[str] = None) -> list[Path]:
    bl = blacklist or set()
    if path.is_file():
        return [] if str(path) in bl else [path]
    files = []
    for root, dirs, filenames in os.walk(path):
        # Filtrar dirs ignorados y en lista negra
        dirs[:] = [
            d
            for d in sorted(dirs)
            if not should_ignore(d, True) and str(Path(root) / d) not in bl
        ]
        for f in sorted(filenames):
            if not should_ignore(f, False):
                full = Path(root) / f
                if str(full) not in bl:
                    files.append(full)
    return files


def generate_content(
    paths: list[Path], blacklist: set[str] = None
) -> tuple[str, list[Path]]:
    all_files = []
    for p in paths:
        all_files.extend(collect_files(p, blacklist))
    seen, unique = set(), []
    for f in all_files:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            unique.append(f)
    parts = []
    for f in unique:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            parts.append(f"==>> ARCHIVO: {f}\n{'─' * 60}\n{content}\n")
        except Exception as e:
            parts.append(f"==>> ARCHIVO: {f}\n[ERROR: {e}]\n")
    return "\n".join(parts), unique


def generate_bash_command(paths: list[Path], output_file: Path) -> str:
    if not paths:
        return ""
    cmds = []
    for i, p in enumerate(paths):
        op = ">" if i == 0 else ">>"
        if p.is_file():
            cmds.append(
                f'echo "==>> ARCHIVO: {p}" {op} "{output_file}" && '
                f'cat "{p}" >> "{output_file}"'
            )
        else:
            cmds.append(
                f'find "{p}" -type f | sort | while read f; do\n'
                f'  echo "==>> ARCHIVO: $f" >> "{output_file}"\n'
                f'  cat "$f" >> "{output_file}"\n'
                f"done"
            )
    return " && \\\n\n".join(cmds)


def file_icon(path: Path) -> str:
    return {
        ".py": "[py]",
        ".ts": "[ts]",
        ".tsx": "[tsx]",
        ".js": "[js]",
        ".jsx": "[tsx]",
        ".json": "[json]",
        ".md": "[md]",
        ".txt": "[txt]",
        ".css": "[css]",
        ".html": "[html]",
        ".sql": "[sql]",
        ".sh": "[sh]",
    }.get(path.suffix.lower(), "[txt]")


def index_all_files(root: Path, blacklist: set[str] = None) -> list[dict]:
    bl = blacklist or set()
    result = []
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [
            d
            for d in sorted(dirs)
            if not should_ignore(d, True) and str(Path(root_dir) / d) not in bl
        ]
        for f in sorted(files):
            if not should_ignore(f, False):
                full = Path(root_dir) / f
                if str(full) not in bl:
                    try:
                        rel = str(full.relative_to(root))
                    except ValueError:
                        rel = str(full)
                    result.append({"path": full, "name": f, "rel": rel})
    return result


# ─── Setup centralizado de estilos ttk ──────────────────────────────────────
# Se llama UNA sola vez al inicio para evitar conflictos y posibles segfaults


def setup_ttk_styles():
    style = ttk.Style()
    # Usar 'clam' si esta disponible, si no el default
    if "clam" in style.theme_names():
        style.theme_use("clam")

    base = dict(
        background=C["bg_dark"],
        foreground=C["text"],
        rowheight=26,
        fieldbackground=C["bg_dark"],
        borderwidth=0,
        font=("Consolas", 11),
    )
    sel = [("selected", C["bg_select"])]
    sel_fg = [("selected", "#ffffff")]

    # Arbol principal
    style.configure("CT.Treeview", **base)
    style.map("CT.Treeview", background=sel, foreground=sel_fg)

    # Panel de busqueda lateral
    style.configure(
        "SP.Treeview", **{**base, "rowheight": 30, "font": ("Consolas", 10)}
    )
    style.map("SP.Treeview", background=sel, foreground=sel_fg)

    # Modal lista negra
    style.configure(
        "BL.Treeview",
        **{
            **base,
            "background": C["bg_panel"],
            "fieldbackground": C["bg_panel"],
            "foreground": C["red"],
            "rowheight": 28,
        },
    )
    style.map(
        "BL.Treeview",
        background=[("selected", C["red_dim"])],
        foreground=[("selected", C["red"])],
    )


# ─── Command Palette ─────────────────────────────────────────────────────────


class CommandPalette(tk.Toplevel):
    def __init__(self, master, index: list[dict], on_select):
        super().__init__(master)
        self.index = index
        self.on_select = on_select
        self.results: list[dict] = []

        px = master.winfo_x() + master.winfo_width() // 2
        py = master.winfo_y() + 80
        self.geometry(f"640x420+{px - 320}+{py}")
        # overrideredirect removido -- causa crashes en algunos window managers Linux
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(bg=C["border"])

        self._build()
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(60, self.search_entry.focus_set)

    def _build(self):
        wrap = tk.Frame(self, bg=C["bg_panel"], padx=1, pady=1)
        wrap.pack(fill="both", expand=True)

        top = tk.Frame(wrap, bg=C["bg_panel"])
        top.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(
            top,
            text="Command Palette",
            bg=C["bg_panel"],
            fg=C["text_dim"],
            font=("Consolas", 10, "bold"),
        ).pack(side="left")
        tk.Label(
            top,
            text="ESC para cerrar  .  Enter para seleccionar",
            bg=C["bg_panel"],
            fg=C["text_muted"],
            font=("Consolas", 9),
        ).pack(side="right")

        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x", pady=(8, 0))

        ef = tk.Frame(wrap, bg=C["bg_item"])
        ef.pack(fill="x")
        tk.Label(
            ef,
            text="  >",
            bg=C["bg_item"],
            fg=C["accent"],
            font=("Consolas", 14, "bold"),
        ).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_type)
        self.search_entry = tk.Entry(
            ef,
            textvariable=self.search_var,
            bg=C["bg_item"],
            fg=C["text"],
            insertbackground=C["accent"],
            font=("Consolas", 13),
            relief="flat",
            bd=10,
        )
        self.search_entry.pack(fill="x", expand=True)
        self.search_entry.bind("<Down>", self._focus_list)
        self.search_entry.bind("<Return>", self._select_first)

        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x")

        lf = tk.Frame(wrap, bg=C["bg_panel"])
        lf.pack(fill="both", expand=True, pady=4)
        self.listbox = tk.Listbox(
            lf,
            bg=C["bg_panel"],
            fg=C["text"],
            selectbackground=C["bg_select"],
            selectforeground=C["text"],
            font=("Consolas", 11),
            relief="flat",
            activestyle="none",
            bd=0,
        )
        sb = tk.Scrollbar(
            lf,
            command=self.listbox.yview,
            bg=C["bg_panel"],
            troughcolor=C["bg_dark"],
            relief="flat",
        )
        self.listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.listbox.pack(fill="both", expand=True, padx=4)
        self.listbox.bind("<Return>", self._on_lb_enter)
        self.listbox.bind("<Double-Button-1>", self._on_lb_enter)
        self.listbox.bind("<Up>", self._on_lb_up)
        self.listbox.bind("<Escape>", lambda e: self.destroy())

        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x")
        self.footer = tk.Label(
            wrap,
            text="Escribe para buscar...",
            bg=C["bg_panel"],
            fg=C["text_muted"],
            font=("Consolas", 9),
            anchor="w",
            padx=12,
            pady=5,
        )
        self.footer.pack(fill="x")

    def _on_type(self, *_):
        query = self.search_var.get().strip().lower()
        self.listbox.delete(0, "end")
        if not query:
            self.results = []
            self.footer.configure(text="Escribe para buscar...")
            return
        terms = query.split()
        matches = [
            it for it in self.index if all(t in it["rel"].lower() for t in terms)
        ][:40]
        self.results = matches
        if not matches:
            self.listbox.insert("end", f'  Sin resultados para "{query}"')
            self.listbox.itemconfig(0, fg=C["text_muted"])
            self.footer.configure(text="0 resultados")
            return
        for it in matches:
            parent = str(Path(it["rel"]).parent)
            self.listbox.insert(
                "end", f"  {file_icon(it['path'])}  {it['name']:<40}  {parent}"
            )
        for i in range(len(matches)):
            self.listbox.itemconfig(i, fg=C["text"])
        self.footer.configure(text=f"{len(matches)} resultado(s)")

    def _focus_list(self, _):
        if self.listbox.size() > 0:
            self.listbox.focus_set()
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(0)
            self.listbox.activate(0)

    def _select_first(self, _):
        if self.results:
            self._emit(self.results[0])

    def _on_lb_enter(self, _):
        sel = self.listbox.curselection()
        if sel and sel[0] < len(self.results):
            self._emit(self.results[sel[0]])

    def _on_lb_up(self, _):
        if self.listbox.curselection() == (0,):
            self.search_entry.focus_set()

    def _emit(self, item: dict):
        self.destroy()
        self.on_select(item["path"])


# ─── Panel lateral de busqueda ───────────────────────────────────────────────


class SearchPanel(ctk.CTkFrame):
    def __init__(self, master, on_select_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_select = on_select_callback
        self.index: list[dict] = []
        self.results: list[dict] = []
        self._job = None
        self._build()

    def _build(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        ctk.CTkLabel(
            title_row,
            text="Busqueda rapida",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["text"],
        ).pack(side="left")
        ctk.CTkLabel(
            title_row,
            text="busca y navega",
            font=ctk.CTkFont(size=9),
            text_color=C["text_muted"],
        ).pack(side="right")

        ef = ctk.CTkFrame(self, fg_color=C["bg_item"], corner_radius=8)
        ef.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        ef.grid_columnconfigure(0, weight=1)
        self.sv = tk.StringVar()
        self.sv.trace_add("write", self._schedule)
        self.entry = ctk.CTkEntry(
            ef,
            textvariable=self.sv,
            placeholder_text="nombre o ruta parcial...",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="transparent",
            border_width=0,
            height=32,
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=8, pady=4)
        ctk.CTkButton(
            ef,
            text="X",
            width=26,
            height=26,
            fg_color="transparent",
            hover_color=C["bg_hover"],
            text_color=C["text_dim"],
            command=lambda: self.sv.set(""),
        ).grid(row=0, column=1, padx=4)

        self.count_lbl = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=10), text_color=C["text_muted"]
        )
        self.count_lbl.grid(row=2, column=0, sticky="w", padx=14)

        lc = ctk.CTkFrame(self, fg_color=C["bg_dark"], corner_radius=8)
        lc.grid(row=3, column=0, sticky="nsew", padx=10, pady=(2, 10))
        lc.grid_rowconfigure(0, weight=1)
        lc.grid_columnconfigure(0, weight=1)

        self.tv = ttk.Treeview(
            lc, style="SP.Treeview", show="tree", selectmode="browse"
        )
        self.tv.tag_configure("sub", foreground=C["text_muted"])
        sb2 = ctk.CTkScrollbar(lc, command=self.tv.yview)
        self.tv.configure(yscrollcommand=sb2.set)
        sb2.grid(row=0, column=1, sticky="ns")
        self.tv.grid(row=0, column=0, sticky="nsew")
        self.tv.bind("<Double-Button-1>", self._click)
        self.tv.bind("<Return>", self._click)
        self._hint()

    def _hint(self):
        self.tv.delete(*self.tv.get_children())
        self.tv.insert("", "end", text="  Escribe para buscar...", tags=("sub",))

    def set_index(self, idx):
        self.index = idx
        self._hint()

    def _schedule(self, *_):
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(160, self._search)

    def _search(self):
        q = self.sv.get().strip().lower()
        self.tv.delete(*self.tv.get_children())
        if not q or len(q) < 2:
            self._hint()
            self.count_lbl.configure(text="")
            return
        terms = q.split()
        hits = [it for it in self.index if all(t in it["rel"].lower() for t in terms)][
            :50
        ]
        self.results = hits
        if not hits:
            self.tv.insert(
                "", "end", text=f'  Sin resultados para "{q}"', tags=("sub",)
            )
            self.count_lbl.configure(text="")
            return
        self.count_lbl.configure(
            text=f"{len(hits)} resultado{'s' if len(hits) != 1 else ''}"
        )
        for it in hits:
            parent_dir = str(Path(it["rel"]).parent)
            iid = self.tv.insert(
                "",
                "end",
                text=f"  {file_icon(it['path'])}  {it['name']}",
                values=(str(it["path"]),),
            )
            self.tv.insert(iid, "end", text=f"     [{parent_dir}]", tags=("sub",))

    def _click(self, _):
        sel = self.tv.selection()
        if not sel:
            return
        vals = self.tv.item(sel[0], "values")
        if vals:
            self.on_select(Path(vals[0]))
        else:
            parent = self.tv.parent(sel[0])
            if parent:
                vals = self.tv.item(parent, "values")
                if vals:
                    self.on_select(Path(vals[0]))


# ─── Modal de gestion de lista negra ────────────────────────────────────────


class BlacklistManager(ctk.CTkToplevel):
    """Modal que muestra la lista negra actual y permite quitar entradas."""

    def __init__(self, master, blacklist: set[str], on_save):
        super().__init__(master)
        self.blacklist = set(blacklist)
        self.on_save = on_save
        self.title("Lista negra")
        self.geometry("680x500")
        self.configure(fg_color=C["bg_dark"])
        self._build()
        self.after(100, self._safe_grab)

    def _safe_grab(self):
        try:
            self.grab_set()
        except Exception:
            pass

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color=C["bg_panel"], corner_radius=10)
        hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        ctk.CTkLabel(
            hdr,
            text="[x] Rutas en lista negra",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C["text"],
        ).pack(side="left", padx=14, pady=10)
        ctk.CTkLabel(
            hdr,
            text="Estas rutas no aparecen en el arbol ni en el contexto generado",
            font=ctk.CTkFont(size=10),
            text_color=C["text_muted"],
        ).pack(side="left", padx=4)

        # Lista
        lc = ctk.CTkFrame(self, fg_color=C["bg_panel"], corner_radius=10)
        lc.grid(row=1, column=0, sticky="nsew", padx=14, pady=6)
        lc.grid_rowconfigure(0, weight=1)
        lc.grid_columnconfigure(0, weight=1)

        self.tv = ttk.Treeview(
            lc, style="BL.Treeview", show="tree", selectmode="extended"
        )
        sb = ctk.CTkScrollbar(lc, command=self.tv.yview)
        self.tv.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")
        self.tv.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self._refresh_list()

        # Acciones
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=2, column=0, sticky="ew", padx=14, pady=(4, 14))

        ctk.CTkButton(
            foot,
            text="Quitar seleccionados",
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color="#1a3a1a",
            hover_color="#2d5c47",
            command=self._remove_selected,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            foot,
            text="Limpiar todo",
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color=C["red_dim"],
            hover_color=C["red_hover"],
            text_color=C["red"],
            command=self._clear_all,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            foot,
            text="Cerrar",
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color=C["bg_item"],
            hover_color=C["bg_hover"],
            text_color=C["text_dim"],
            command=self.destroy,
        ).pack(side="right", padx=4)

        self.count_lbl = ctk.CTkLabel(
            foot, text="", font=ctk.CTkFont(size=11), text_color=C["text_muted"]
        )
        self.count_lbl.pack(side="right", padx=12)
        self._update_count()

    def _refresh_list(self):
        self.tv.delete(*self.tv.get_children())
        for path_str in sorted(self.blacklist):
            p = Path(path_str)
            icon = "[+]" if p.is_dir() else file_icon(p)
            self.tv.insert(
                "", "end", text=f"  [x] {icon}  {path_str}", values=(path_str,)
            )
        if not self.blacklist:
            self.tv.insert(
                "",
                "end",
                text="  Lista negra vacia -- no hay nada bloqueado",
                tags=("empty",),
            )
            self.tv.tag_configure("empty", foreground=C["text_muted"])

    def _update_count(self):
        n = len(self.blacklist)
        self.count_lbl.configure(
            text=f"{n} entrada{'s' if n != 1 else ''} bloqueada{'s' if n != 1 else ''}"
        )

    def _remove_selected(self):
        sel = self.tv.selection()
        if not sel:
            return
        to_remove = set()
        for iid in sel:
            vals = self.tv.item(iid, "values")
            if vals:
                to_remove.add(vals[0])
        self.blacklist -= to_remove
        save_blacklist(self.blacklist)
        self.on_save(self.blacklist)
        self._refresh_list()
        self._update_count()

    def _clear_all(self):
        if not self.blacklist:
            return
        if messagebox.askyesno(
            "Confirmar", "Limpiar toda la lista negra?", parent=self
        ):
            self.blacklist.clear()
            save_blacklist(self.blacklist)
            self.on_save(self.blacklist)
            self._refresh_list()
            self._update_count()


# ─── CheckableTree ───────────────────────────────────────────────────────────


class CheckableTree(ctk.CTkFrame):
    def __init__(self, master, root_path: Path, blacklist: set[str] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.root_path = root_path
        self.blacklist: set[str] = blacklist or set()
        self.checked_items: dict[str, tk.BooleanVar] = {}
        self.item_paths: dict[str, Path] = {}
        self.path_to_item: dict[Path, str] = {}
        self._highlighted: str | None = None
        self._context_menu: tk.Menu | None = None
        self._ctx_item: str | None = (
            None  # item bajo el cursor en el momento del clic derecho
        )

        self._build_ui()
        self._populate(root_path)

    def set_blacklist(self, bl: set[str]):
        self.blacklist = bl
        self._populate(self.root_path)

    def _build_ui(self):
        c = ctk.CTkFrame(self, fg_color=C["bg_dark"], corner_radius=8)
        c.pack(fill="both", expand=True, padx=2, pady=2)

        self.tree = ttk.Treeview(c, style="CT.Treeview", show="tree", selectmode="none")
        self.tree.tag_configure("hl", background="#2d2200", foreground=C["highlight"])
        self.tree.tag_configure("chk", foreground=C["accent2"])

        vsb = ctk.CTkScrollbar(c, command=self.tree.yview)
        hsb = ctk.CTkScrollbar(c, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Button-1>", self._on_click)
        self.tree.bind("<Button-3>", self._on_right_click)

        # Menu contextual (sin emojis -- causan segfault con LC_ALL=POSIX en Linux)
        self._context_menu = tk.Menu(
            self.tree,
            tearoff=0,
            bg=C["bg_panel"],
            fg=C["red"],
            activebackground=C["red_dim"],
            activeforeground="#ffffff",
            font=("Consolas", 11),
            relief="flat",
            bd=1,
        )
        self._context_menu.add_command(
            label="  [BLOQUEAR]  Agregar a lista negra",
            command=self._ctx_add_to_blacklist,
        )

    def _populate(self, path: Path):
        self.tree.delete(*self.tree.get_children())
        self.checked_items.clear()
        self.item_paths.clear()
        self.path_to_item.clear()
        self._highlighted = None
        self._insert_node("", path, is_root=True)

    def _is_blacklisted(self, path: Path) -> bool:
        """True si la ruta o algun ancestro esta en la lista negra."""
        s = str(path)
        if s in self.blacklist:
            return True
        for bl in self.blacklist:
            if s.startswith(bl + os.sep):
                return True
        return False

    def _insert_node(self, parent: str, path: Path, is_root=False):
        if not is_root and self._is_blacklisted(path):
            return

        name = path.name if not is_root else str(path)
        icon = "[+]" if path.is_dir() else file_icon(path)
        iid = self.tree.insert(
            parent, "end", text=f"  [ ] {icon}  {name}", open=is_root
        )
        self.checked_items[iid] = tk.BooleanVar(value=False)
        self.item_paths[iid] = path
        self.path_to_item[path.resolve()] = iid

        if path.is_dir():
            try:
                children = sorted(
                    path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
                )
                for child in children:
                    if not should_ignore(child.name, child.is_dir()):
                        self._insert_node(iid, child)
            except PermissionError:
                pass

    # ── Click izquierdo ──────────────────────────────────────────────

    def _on_click(self, e):
        element = self.tree.identify_element(e.x, e.y)
        if element == "Treeitem.indicator":
            return
        if self.tree.identify_region(e.x, e.y) != "tree":
            return
        item = self.tree.identify_row(e.y)
        if item and item in self.checked_items:
            self._toggle(item)

    # ── Click derecho -> menu contextual ─────────────────────────────

    def _on_right_click(self, e):
        item = self.tree.identify_row(e.y)
        if not item or item not in self.item_paths:
            return
        self._ctx_item = item
        # Seleccionar visualmente el item
        self.tree.selection_set(item)
        try:
            self._context_menu.tk_popup(e.x_root, e.y_root)
        finally:
            self._context_menu.grab_release()

    def _ctx_add_to_blacklist(self):
        if not self._ctx_item or self._ctx_item not in self.item_paths:
            return
        path = self.item_paths[self._ctx_item]
        self.blacklist.add(str(path))
        save_blacklist(self.blacklist)
        # Notificar a la app para que actualice el badge del boton
        self.event_generate("<<BlacklistChanged>>")
        # Quitar el nodo del arbol
        self.tree.delete(self._ctx_item)
        # Limpiar referencias
        del self.checked_items[self._ctx_item]
        del self.item_paths[self._ctx_item]
        if path.resolve() in self.path_to_item:
            del self.path_to_item[path.resolve()]
        self._ctx_item = None

    # ── Toggle / redraw ─────────────────────────────────────────────

    def _toggle(self, iid: str, state: bool = None):
        var = self.checked_items[iid]
        new = not var.get() if state is None else state
        var.set(new)
        self._redraw(iid)
        p = self.item_paths[iid]
        if p.is_dir():
            for child in self.tree.get_children(iid):
                self._toggle(child, state=new)

    def _redraw(self, iid: str):
        path = self.item_paths[iid]
        name = path.name if path != self.root_path else str(path)
        icon = "[+]" if path.is_dir() else file_icon(path)
        cb = "[x]" if self.checked_items[iid].get() else "[ ]"
        self.tree.item(iid, text=f"  {cb} {icon}  {name}")
        tags = []
        if iid == self._highlighted:
            tags.append("hl")
        if self.checked_items[iid].get():
            tags.append("chk")
        self.tree.item(iid, tags=tags)

    def navigate_to(self, file_path: Path) -> bool:
        resolved = file_path.resolve()
        iid = self.path_to_item.get(resolved)
        if iid is None:
            return False
        if self._highlighted and self._highlighted in self.item_paths:
            prev = self._highlighted
            self._highlighted = None
            self._redraw(prev)
        parent = self.tree.parent(iid)
        chain = []
        while parent:
            chain.append(parent)
            parent = self.tree.parent(parent)
        for p in reversed(chain):
            self.tree.item(p, open=True)
        self._highlighted = iid
        self._redraw(iid)
        self.tree.see(iid)
        self.tree.selection_set(iid)
        return True

    def get_selected_paths(self) -> list[Path]:
        selected = [
            p for iid, p in self.item_paths.items() if self.checked_items[iid].get()
        ]
        result = []
        for p in selected:
            dominated = any(
                other != p and str(p).startswith(str(other) + os.sep)
                for other in selected
                if other.is_dir()
            )
            if not dominated:
                result.append(p)
        return result

    def clear_selection(self):
        for iid in list(self.checked_items):
            if self.checked_items[iid].get():
                self.checked_items[iid].set(False)
                self._redraw(iid)
        self._highlighted = None


# ─── App principal ───────────────────────────────────────────────────────────


class ContextTreeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Context Tree  .  Generador de contexto IA")
        self.geometry("1380x820")
        self.minsize(1000, 640)
        self.configure(fg_color=C["bg_dark"])
        self._file_index: list[dict] = []
        self.blacklist: set[str] = load_blacklist()
        setup_ttk_styles()
        self._build_ui()
        self.bind("<Control-p>", self._open_palette)
        self.bind("<Control-P>", self._open_palette)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # ── Arbol ──────────────────────────────────────────
        tp = ctk.CTkFrame(self, corner_radius=12, fg_color=C["bg_panel"])
        tp.grid(row=0, column=0, sticky="nsew", padx=(10, 4), pady=10)
        tp.grid_rowconfigure(2, weight=1)
        tp.grid_columnconfigure(0, weight=1)

        h = ctk.CTkFrame(tp, fg_color="transparent")
        h.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        ctk.CTkLabel(
            h,
            text="Proyecto",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C["text"],
        ).pack(side="left")
        ctk.CTkLabel(
            h,
            text="Ctrl+P",
            font=ctk.CTkFont(size=9),
            text_color=C["text_muted"],
            fg_color=C["bg_item"],
            corner_radius=4,
        ).pack(side="right")

        pf = ctk.CTkFrame(tp, fg_color=C["bg_item"], corner_radius=6)
        pf.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        pf.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(pf, text=">", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=8
        )
        self.root_var = tk.StringVar(
            value=str(Path.home() / "workspace" / "intranet-pi")
        )
        ctk.CTkEntry(
            pf,
            textvariable=self.root_var,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="transparent",
            border_width=0,
            height=28,
        ).grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkButton(
            pf,
            text="Cargar",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            command=self._reload,
        ).grid(row=0, column=2, padx=6, pady=4)

        self.tree_w = CheckableTree(
            tp,
            Path(self.root_var.get()),
            blacklist=self.blacklist,
            fg_color="transparent",
        )
        self.tree_w.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)
        # Escuchar cuando el arbol cambia la lista negra por click derecho
        self.tree_w.bind("<<BlacklistChanged>>", self._on_blacklist_changed)

        # Footer arbol
        foot = ctk.CTkFrame(tp, fg_color="transparent")
        foot.grid(row=3, column=0, sticky="ew", padx=8, pady=(4, 10))

        ctk.CTkButton(
            foot,
            text="Limpiar seleccion",
            height=28,
            width=150,
            fg_color=C["bg_item"],
            hover_color=C["bg_hover"],
            font=ctk.CTkFont(size=11),
            text_color=C["text_dim"],
            command=self.tree_w.clear_selection,
        ).pack(side="left", padx=4)

        # Boton lista negra con badge de conteo
        self.bl_btn = ctk.CTkButton(
            foot,
            text=self._bl_label(),
            height=28,
            width=130,
            fg_color=C["red_dim"],
            hover_color=C["red_hover"],
            font=ctk.CTkFont(size=11),
            text_color=C["red"],
            command=self._open_blacklist_manager,
        )
        self.bl_btn.pack(side="left", padx=4)

        self.sel_lbl = ctk.CTkLabel(
            foot,
            text="0 seleccionados",
            font=ctk.CTkFont(size=11),
            text_color=C["text_muted"],
        )
        self.sel_lbl.pack(side="right", padx=8)
        self._tick()

        # ── Panel busqueda lateral ──────────────────────────
        self.sp = SearchPanel(
            self,
            on_select_callback=self._go_to,
            fg_color=C["bg_panel"],
            corner_radius=12,
        )
        self.sp.grid(row=0, column=1, sticky="nsew", padx=4, pady=10)

        # ── Panel derecho ────────────────────────────────────
        rp = ctk.CTkFrame(self, corner_radius=12, fg_color=C["bg_panel"])
        rp.grid(row=0, column=2, sticky="nsew", padx=(4, 10), pady=10)
        rp.grid_rowconfigure(3, weight=1)
        rp.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            rp,
            text="Generar contexto",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C["text"],
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        opts = ctk.CTkFrame(rp, fg_color=C["bg_item"], corner_radius=8)
        opts.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        opts.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            opts, text="Nombre:", font=ctk.CTkFont(size=11), text_color=C["text_dim"]
        ).grid(row=0, column=0, padx=10, pady=8)
        self.out_name = tk.StringVar(value="contexto")
        ctk.CTkEntry(
            opts,
            textvariable=self.out_name,
            placeholder_text="nombre_sin_extension",
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
        ).grid(row=0, column=1, sticky="ew", padx=6)
        ctk.CTkLabel(
            opts, text=".txt", text_color=C["text_muted"], font=ctk.CTkFont(size=12)
        ).grid(row=0, column=2, padx=(0, 8))
        ctk.CTkLabel(
            opts,
            text="Directorio:",
            font=ctk.CTkFont(size=11),
            text_color=C["text_dim"],
        ).grid(row=1, column=0, padx=10, pady=(0, 8))
        self.out_dir = tk.StringVar(value=str(OUTPUT_DIR))
        ctk.CTkEntry(
            opts,
            textvariable=self.out_dir,
            height=28,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=C["text_muted"],
            fg_color="transparent",
        ).grid(row=1, column=1, columnspan=2, sticky="ew", padx=6, pady=(0, 6))

        actions = ctk.CTkFrame(rp, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=10, pady=6)
        self.gen_btn = ctk.CTkButton(
            actions,
            text="Generar .txt",
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0d3b7a",
            hover_color="#1a5fa8",
            command=self._generate,
        )
        self.gen_btn.pack(side="left", padx=3, expand=True, fill="x")
        ctk.CTkButton(
            actions,
            text="Copiar",
            height=38,
            font=ctk.CTkFont(size=12),
            fg_color="#1a3a1a",
            hover_color="#2d5c47",
            command=self._copy,
        ).pack(side="left", padx=3, expand=True, fill="x")
        ctk.CTkButton(
            actions,
            text="Bash",
            height=38,
            font=ctk.CTkFont(size=12),
            fg_color="#2a1a3a",
            hover_color="#4a3060",
            command=self._bash,
        ).pack(side="left", padx=3, expand=True, fill="x")

        pw = ctk.CTkFrame(rp, fg_color="transparent")
        pw.grid(row=3, column=0, sticky="nsew", padx=10, pady=(2, 6))
        pw.grid_rowconfigure(1, weight=1)
        pw.grid_columnconfigure(0, weight=1)
        self.token_lbl = ctk.CTkLabel(
            pw, text="", font=ctk.CTkFont(size=10), text_color=C["text_muted"]
        )
        self.token_lbl.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.preview = ctk.CTkTextbox(
            pw,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=C["bg_dark"],
            text_color="#d1d5db",
            wrap="none",
            corner_radius=8,
        )
        self.preview.grid(row=1, column=0, sticky="nsew")

        self.status = tk.StringVar(
            value="Listo | Ctrl+P buscar | Click derecho = lista negra"
        )
        ctk.CTkLabel(
            rp,
            textvariable=self.status,
            font=ctk.CTkFont(size=10),
            text_color=C["text_muted"],
            anchor="w",
        ).grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 8))

        self._rebuild_index()

    # ── Lista negra ──────────────────────────────────────────────────

    def _bl_label(self) -> str:
        n = len(self.blacklist)
        return f"Lista negra ({n})" if n > 0 else "Lista negra"

    def _on_blacklist_changed(self, _=None):
        """Llamado cuando el arbol agrega algo a la lista negra por click derecho."""
        self.blacklist = self.tree_w.blacklist
        self.bl_btn.configure(text=self._bl_label())
        self._rebuild_index()
        self._set_status(
            f"[x] Bloqueado: {len(self.blacklist)} entradas en lista negra"
        )

    def _open_blacklist_manager(self):
        def on_save(new_bl: set[str]):
            self.blacklist = new_bl
            self.tree_w.set_blacklist(new_bl)
            self.bl_btn.configure(text=self._bl_label())
            self._rebuild_index()
            self._set_status(f"Lista negra: {len(new_bl)} entradas")

        BlacklistManager(self, self.blacklist, on_save)

    # ── Indice / navegacion ──────────────────────────────────────────

    def _rebuild_index(self):
        root = Path(self.root_var.get())
        if not root.exists():
            return
        bl = set(self.blacklist)

        def w():
            idx = index_all_files(root, bl)
            self.after(0, lambda: self._set_idx(idx))

        threading.Thread(target=w, daemon=True).start()

    def _set_idx(self, idx):
        self._file_index = idx
        self.sp.set_index(idx)

    def _open_palette(self, _=None):
        if not self._file_index:
            self._set_status("Indexando...")
            return
        CommandPalette(self, self._file_index, self._go_to)

    def _go_to(self, file_path: Path):
        found = self.tree_w.navigate_to(file_path)
        if found:
            self._set_status(f">> {file_path.name}   ->   {file_path.parent}")
        else:
            self._set_status(
                f"WARN: {file_path.name} no encontrado -- en lista negra o recarga con <->?"
            )

    # ── Arbol ────────────────────────────────────────────────────────

    def _reload(self):
        path = Path(self.root_var.get())
        if not path.exists():
            self._set_status("ERROR: Ruta no existe")
            return
        self.tree_w._populate(path)
        self._rebuild_index()
        self._set_status(f"Arbol cargado: {path}")

    def _tick(self):
        try:
            n = len(self.tree_w.get_selected_paths())
            self.sel_lbl.configure(
                text=f"{n} seleccionado{'s' if n != 1 else ''}",
                text_color=C["accent"] if n > 0 else C["text_muted"],
            )
        except Exception:
            pass
        self.after(400, self._tick)

    # ── Generar ──────────────────────────────────────────────────────

    def _sel_or_warn(self):
        p = self.tree_w.get_selected_paths()
        if not p:
            messagebox.showwarning(
                "Sin seleccion", "Selecciona al menos un archivo o carpeta."
            )
            return None
        return p

    def _generate(self):
        paths = self._sel_or_warn()
        if not paths:
            return
        name = self.out_name.get().strip() or "contexto"
        od = Path(self.out_dir.get().strip())
        od.mkdir(parents=True, exist_ok=True)
        of = od / f"{name}.txt"
        self._set_status("Generando...")
        self.gen_btn.configure(state="disabled")
        bl = set(self.blacklist)

        def w():
            try:
                content, files = generate_content(paths, bl)
                of.write_text(content, encoding="utf-8")
                lines = content.count("\n")
                kb = of.stat().st_size / 1024
                tk_est = len(content) // 4
                self.after(
                    0, lambda: self._after_gen(content, files, of, lines, kb, tk_est)
                )
            except Exception as e:
                self.after(0, lambda: self._set_status(f"ERROR: {e}"))
            finally:
                self.after(0, lambda: self.gen_btn.configure(state="normal"))

        threading.Thread(target=w, daemon=True).start()

    def _after_gen(self, content, files, of, lines, kb, tk_est):
        self.preview.delete("1.0", "end")
        pv = content[:10000] + (
            "\n\n[... preview truncado -- archivo completo guardado ...]"
            if len(content) > 10000
            else ""
        )
        self.preview.insert("1.0", pv)
        self.token_lbl.configure(
            text=f"~{tk_est:,} tokens  .  {len(files)} archivos  .  {lines:,} lineas  .  {kb:.1f} KB"
        )
        self._set_status(f"Guardado: {of}")
        self.out_name.set(f"contexto_{datetime.now().strftime('%H%M')}")

    def _copy(self):
        paths = self._sel_or_warn()
        if not paths:
            return
        self._set_status("Copiando...")
        bl = set(self.blacklist)

        def w():
            try:
                content, files = generate_content(paths, bl)
                self.clipboard_clear()
                self.clipboard_append(content)
                self.update()
                tk_est = len(content) // 4
                kb = len(content.encode()) / 1024
                self.after(
                    0,
                    lambda: self._set_status(
                        f"Copiado: {len(files)} archivos . ~{tk_est:,} tokens . {kb:.1f} KB"
                    ),
                )
            except Exception as e:
                self.after(0, lambda: self._set_status(f"ERROR: {e}"))

        threading.Thread(target=w, daemon=True).start()

    def _bash(self):
        paths = self._sel_or_warn()
        if not paths:
            return
        name = self.out_name.get().strip() or "contexto"
        of = Path(self.out_dir.get().strip()) / f"{name}.txt"
        cmd = generate_bash_command(paths, of)

        win = ctk.CTkToplevel(self)
        win.title("Comando Bash")
        win.geometry("860x340")
        win.configure(fg_color=C["bg_dark"])
        win.grab_set()
        ctk.CTkLabel(
            win,
            text="Comando bash equivalente",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["text"],
        ).pack(padx=14, pady=(14, 4), anchor="w")
        txt = ctk.CTkTextbox(
            win,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=C["bg_dark"],
            text_color="#98fb98",
            corner_radius=8,
        )
        txt.pack(fill="both", expand=True, padx=14, pady=4)
        txt.insert("1.0", cmd)
        txt.configure(state="disabled")

        def cp():
            self.clipboard_clear()
            self.clipboard_append(cmd)
            self.update()
            btn.configure(text="Copiado!")

        btn = ctk.CTkButton(
            win, text="Copiar comando", command=cp, height=36, font=ctk.CTkFont(size=12)
        )
        btn.pack(padx=14, pady=(4, 14))

    def _set_status(self, msg: str):
        self.status.set(msg)
        self.update_idletasks()


if __name__ == "__main__":
    app = ContextTreeApp()
    app.mainloop()
