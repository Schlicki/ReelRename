import os
import re
import sys
import json
import threading
import io
import shutil
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import urllib.request
import urllib.parse
from urllib.error import HTTPError

# Optional: Pillow für Bildanzeige
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# --- KONFIGURATION ---
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w200' # Kleineres Bild für Vorschau
TMDB_IMAGE_ORIGINAL = 'https://image.tmdb.org/t/p/original' # Für Downloads
CONFIG_FILE = os.path.join(os.path.expanduser("~"), 'cinematch_config.json')

# --- ÜBERSETZUNGEN ---
TRANSLATIONS = {
    "de": {
        "title": "ReelRename",
        "settings": "1. Einstellungen",
        "api_label": "TMDB API Key:",
        "save": "Speichern",
        "btn_change": "Ändern",
        "lbl_stored": "Key hinterlegt",
        "get_key_link": "Kostenlosen API-Key bei TMDB erhalten",
        "folder_select": "2. Ordner wählen",
        "no_folder": "Kein Ordner gewählt",
        "open_folder": "Ordner öffnen...",
        "search_show": "3. Suchen",
        "mode_tv": "TV-Serie",
        "mode_movie": "Film",
        "search_btn": "Suchen",
        "no_image": "Kein Bild",
        "loading": "Lade...",
        "preview": "4. Vorschau & Ausführen",
        "format": "Format:",
        "update": "Aktualisieren",
        "placeholders": "Platzhalter: {show}, {s}, {e}, {title}, {year}",
        "chk_extras": "Extras (.nfo, .srt, etc.) umbenennen",
        "chk_sample": "'Sample' löschen",
        "chk_links": "Web-Links löschen",
        "chk_ren_folder": "Ordner umbenennen",
        "ready": "Bereit",
        "btn_artwork": "Artwork...",
        "btn_cleanup": "Nur Bereinigen",
        "start_rename": "UMBENENNEN STARTEN",
        "col_file": "Original Datei",
        "col_new": "Neuer Name (Doppelklick zum Ändern)",
        "col_status": "Status",
        "msg_confirm": "Bestätigen",
        "msg_start": "Vorgang starten?",
        "msg_done": "Fertig",
        "msg_success": "Dateien umbenannt.",
        "msg_saved": "Einstellungen gespeichert.",
        "msg_cleanup_desc": "Nur markierte Elemente (Samples/Links) löschen?\nEs werden KEINE Dateien umbenannt.",
        "msg_cleanup_res": "Bereinigung abgeschlossen.",
        "status_wait": "Warte auf Suche...",
        "status_ready": "Bereit",
        "status_manual": "Manuell",
        "status_ignored": "Ignoriert",
        "status_no_match": "Kein Match",
        "err_no_key": "Bitte API Key eingeben!",
        "log_search": "Suche läuft...",
        "log_no_results": "Keine Ergebnisse gefunden.",
        "log_select": "Bitte Eintrag auswählen.",
        "log_load_ep": "Lade Details für:",
        "log_found": "Dateien gefunden (inkl. Unterordner).",
        "log_preview": "Vorschau erstellt.",
        "err_api": "API Fehler",
        "err_read": "Fehler beim Lesen",
        "donate": "☕ Spenden",
        # Artwork Dialog
        "art_title": "Artwork Downloader",
        "art_select": "Bilder auswählen:",
        "art_poster": "Poster (Aktuelle Auswahl)",
        "art_fanart": "Fanart (fanart.jpg)",
        "art_logo": "Logo (logo.png)",
        "art_banner": "Banner (banner.jpg)",
        "art_clearart": "Clearart (clearart.png)",
        "art_btn_load": "Laden",
        "art_msg_ok": "Bilder gespeichert!"
    },
    "en": {
        "title": "ReelRename",
        "settings": "1. Settings",
        "api_label": "TMDB API Key:",
        "save": "Save",
        "btn_change": "Change",
        "lbl_stored": "Key stored",
        "get_key_link": "Get free API Key from TMDB",
        "folder_select": "2. Select Folder",
        "no_folder": "No folder selected",
        "open_folder": "Open Folder...",
        "search_show": "3. Search",
        "mode_tv": "TV Series",
        "mode_movie": "Movie",
        "search_btn": "Search",
        "no_image": "No Image",
        "loading": "Loading...",
        "preview": "4. Preview & Execute",
        "format": "Format:",
        "update": "Update",
        "placeholders": "Placeholders: {show}, {s}, {e}, {title}, {year}",
        "chk_extras": "Rename extras (.nfo, .srt, etc.)",
        "chk_sample": "Delete 'Sample' files",
        "chk_links": "Delete Web-Links",
        "chk_ren_folder": "Rename folder",
        "ready": "Ready",
        "btn_artwork": "Artwork...",
        "btn_cleanup": "Cleanup Only",
        "start_rename": "START RENAME",
        "col_file": "Original File",
        "col_new": "New Name (Double click to edit)",
        "col_status": "Status",
        "msg_confirm": "Confirm",
        "msg_start": "Start process?",
        "msg_done": "Done",
        "msg_success": "Files renamed.",
        "msg_saved": "Settings saved.",
        "msg_cleanup_desc": "Delete selected items (Samples/Links) only?\nNO files will be renamed.",
        "msg_cleanup_res": "Cleanup finished.",
        "status_wait": "Waiting for search...",
        "status_ready": "Ready",
        "status_manual": "Manual",
        "status_ignored": "Ignored",
        "status_no_match": "No Match",
        "err_no_key": "Please enter API Key!",
        "log_search": "Searching...",
        "log_no_results": "No results found.",
        "log_select": "Please select an entry.",
        "log_load_ep": "Loading details for:",
        "log_found": "Files found (incl. subfolders).",
        "log_preview": "Preview created.",
        "err_api": "API Error",
        "err_read": "Read Error",
        "donate": "☕ Donate",
        # Artwork Dialog
        "art_title": "Artwork Downloader",
        "art_select": "Select images:",
        "art_poster": "Poster (Current selection)",
        "art_fanart": "Fanart (fanart.jpg)",
        "art_logo": "Logo (logo.png)",
        "art_banner": "Banner (banner.jpg)",
        "art_clearart": "Clearart (clearart.png)",
        "art_btn_load": "Download",
        "art_msg_ok": "Images saved!"
    },
    "es": {
        "title": "ReelRename",
        "settings": "1. Configuración",
        "api_label": "Clave API TMDB:",
        "save": "Guardar",
        "btn_change": "Cambiar",
        "lbl_stored": "Clave guardada",
        "get_key_link": "Obtener clave API gratuita de TMDB",
        "folder_select": "2. Seleccionar carpeta",
        "no_folder": "Ninguna carpeta seleccionada",
        "open_folder": "Abrir carpeta...",
        "search_show": "3. Buscar",
        "mode_tv": "Serie TV",
        "mode_movie": "Película",
        "search_btn": "Buscar",
        "no_image": "Sin imagen",
        "loading": "Cargando...",
        "preview": "4. Vista previa y Ejecutar",
        "format": "Formato:",
        "update": "Actualizar",
        "placeholders": "Marcadores: {show}, {s}, {e}, {title}, {year}",
        "chk_extras": "Renombrar extras (.nfo, .srt, etc.)",
        "chk_sample": "Borrar 'Sample'",
        "chk_links": "Borrar enlaces web",
        "chk_ren_folder": "Renombrar carpeta",
        "ready": "Listo",
        "btn_artwork": "Arte...",
        "btn_cleanup": "Solo Limpiar",
        "start_rename": "INICIAR RENOMBRADO",
        "col_file": "Archivo original",
        "col_new": "Nuevo nombre (Doble clic para editar)",
        "col_status": "Estado",
        "msg_confirm": "Confirmar",
        "msg_start": "¿Iniciar proceso?",
        "msg_done": "Hecho",
        "msg_success": "Archivos renombrados.",
        "msg_saved": "Configuración guardada.",
        "msg_cleanup_desc": "¿Eliminar solo elementos seleccionados (Samples/Links)?\nNO se renombrarán archivos.",
        "msg_cleanup_res": "Limpieza finalizada.",
        "status_wait": "Esperando búsqueda...",
        "status_ready": "Listo",
        "status_manual": "Manual",
        "status_ignored": "Ignorado",
        "status_no_match": "Sin coincidencia",
        "err_no_key": "¡Por favor ingrese la clave API!",
        "log_search": "Buscando...",
        "log_no_results": "No se encontraron resultados.",
        "log_select": "Por favor seleccione una entrada.",
        "log_load_ep": "Cargando detalles para:",
        "log_found": "Archivos encontrados (incl. subcarpetas).",
        "log_preview": "Vista previa creada.",
        "err_api": "Error API",
        "err_read": "Error de lectura",
        "donate": "☕ Donar",
        # Artwork Dialog
        "art_title": "Descargador de Arte",
        "art_select": "Seleccionar imágenes:",
        "art_poster": "Póster (Selección actual)",
        "art_fanart": "Fanart (fanart.jpg)",
        "art_logo": "Logo (logo.png)",
        "art_banner": "Banner (banner.jpg)",
        "art_clearart": "Clearart (clearart.png)",
        "art_btn_load": "Descargar",
        "art_msg_ok": "¡Imágenes guardadas!"
    },
    "fr": {
        "title": "ReelRename",
        "settings": "1. Paramètres",
        "api_label": "Clé API TMDB :",
        "save": "Enregistrer",
        "btn_change": "Modifier",
        "lbl_stored": "Clé enregistrée",
        "get_key_link": "Obtenir une clé API gratuite sur TMDB",
        "folder_select": "2. Sélectionner le dossier",
        "no_folder": "Aucun dossier sélectionné",
        "open_folder": "Ouvrir dossier...",
        "search_show": "3. Rechercher",
        "mode_tv": "Série TV",
        "mode_movie": "Film",
        "search_btn": "Rechercher",
        "no_image": "Pas d'image",
        "loading": "Chargement...",
        "preview": "4. Aperçu et Exécution",
        "format": "Format :",
        "update": "Mettre à jour",
        "placeholders": "Espaces réservés : {show}, {s}, {e}, {title}, {year}",
        "chk_extras": "Renommer les extras (.nfo, .srt, etc.)",
        "chk_sample": "Supprimer 'Sample'",
        "chk_links": "Supprimer les liens Web",
        "chk_ren_folder": "Renommer le dossier",
        "ready": "Prêt",
        "btn_artwork": "Illustrations...",
        "btn_cleanup": "Nettoyer",
        "start_rename": "LANCER LE RENOMMAGE",
        "col_file": "Fichier original",
        "col_new": "Nouveau nom (Double-clic pour modifier)",
        "col_status": "État",
        "msg_confirm": "Confirmer",
        "msg_start": "Lancer le processus ?",
        "msg_done": "Terminé",
        "msg_success": "Fichiers renommés.",
        "msg_saved": "Paramètres enregistrés.",
        "msg_cleanup_desc": "Supprimer uniquement les éléments sélectionnés (Samples/Links) ?\nAUCUN fichier ne sera renommé.",
        "msg_cleanup_res": "Nettoyage terminé.",
        "status_wait": "En attente de recherche...",
        "status_ready": "Prêt",
        "status_manual": "Manuel",
        "status_ignored": "Ignoré",
        "status_no_match": "Aucune corresp.",
        "err_no_key": "Veuillez saisir la clé API !",
        "log_search": "Recherche en cours...",
        "log_no_results": "Aucun résultat trouvé.",
        "log_select": "Veuillez sélectionner une entrée.",
        "log_load_ep": "Chargement des détails pour :",
        "log_found": "Fichiers trouvés (y compris sous-dossiers).",
        "log_preview": "Aperçu créé.",
        "err_api": "Erreur API",
        "err_read": "Erreur de lecture",
        "donate": "☕ Faire un don",
        # Artwork Dialog
        "art_title": "Téléchargeur d'illustrations",
        "art_select": "Sélectionner les images :",
        "art_poster": "Affiche (Sélection actuelle)",
        "art_fanart": "Fanart (fanart.jpg)",
        "art_logo": "Logo (logo.png)",
        "art_banner": "Bannière (banner.jpg)",
        "art_clearart": "Clearart (clearart.png)",
        "art_btn_load": "Télécharger",
        "art_msg_ok": "Images enregistrées !"
    }
}

LANG_MAP = {
    "de": "de-DE",
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR"
}

class CineMatchApp:
    def __init__(self, root):
        self.root = root
        
        # UI Elements Cache for Translation
        self.ui_elements = {}
        
        # State
        self.lang_var = tk.StringVar(value="de")
        self.api_key = tk.StringVar()
        self.format_var = tk.StringVar(value="{show} - S{s}E{e} - {title}")
        self.mode_var = tk.StringVar(value="tv") # "tv" or "movie"
        self.files = []
        self.search_results = []
        self.selected_show = None
        self.episodes_cache = []
        self.rename_plan = []
        self.current_poster_image = None
        self.tree = None  # Initiale Definition, um Absturz zu verhindern
        
        # Poster Navigation State
        self.available_posters = []
        self.current_poster_idx = 0
        
        # Options
        self.rename_others_var = tk.BooleanVar(value=True)
        self.delete_samples_var = tk.BooleanVar(value=False)
        self.delete_links_var = tk.BooleanVar(value=False)
        self.rename_folder_var = tk.BooleanVar(value=False) # NEU: Ordner umbenennen
        
        self.load_config()
        
        # Styles
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except:
            pass # Fallback to default if clam not available
            
        self.style.configure('TButton', padding=6, font=('Segoe UI', 10))
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('TRadiobutton', font=('Segoe UI', 10))
        
        self.root.geometry("1000x850")
        self.create_widgets()
        self.update_ui_text() # Initial Text Set

    def create_widgets(self):
        # --- Footer (Zuerst packen, damit er immer unten sichtbar bleibt) ---
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(side="bottom", fill="x", pady=5)
        
        # Developer Label (Links)
        ttk.Label(footer_frame, text="ReelRename developed by Schlicki", font=("Segoe UI", 8), foreground="gray").pack(side="left", padx=10)
        
        # Donate Link (Rechts)
        self.lbl_donate = ttk.Label(footer_frame, text="☕ Spenden", font=("Segoe UI", 8, "bold"), foreground="#F5A623", cursor="hand2")
        self.lbl_donate.pack(side="right", padx=10)
        self.lbl_donate.bind("<Button-1>", lambda e: webbrowser.open_new("https://coindrop.to/reelrename"))
        self.ui_elements['lbl_donate'] = self.lbl_donate

        # --- Settings Area ---
        settings_frame = ttk.LabelFrame(self.root, padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        self.ui_elements['settings_frame'] = settings_frame
        
        # Language Selection
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(lang_frame, text="Sprache/Language: ").pack(side="left")
        
        langs = [("🇩🇪 Deutsch", "de"), ("🇬🇧 English", "en"), ("🇪🇸 Español", "es"), ("🇫🇷 Français", "fr")]
        for text, val in langs:
            ttk.Radiobutton(lang_frame, text=text, variable=self.lang_var, value=val, command=self.on_language_change).pack(side="left", padx=5)

        # Input Container
        input_container = ttk.Frame(settings_frame)
        input_container.pack(fill="x", anchor="w")
        
        lbl_api = ttk.Label(input_container)
        lbl_api.pack(side="left")
        self.ui_elements['lbl_api'] = lbl_api
        
        # --- API Edit Frame (Entry + Save) ---
        self.api_edit_frame = ttk.Frame(input_container)
        self.api_entry = ttk.Entry(self.api_edit_frame, textvariable=self.api_key, width=40)
        self.api_entry.pack(side="left", padx=5)
        
        btn_save = ttk.Button(self.api_edit_frame, command=self.save_config_ui)
        btn_save.pack(side="left")
        self.ui_elements['btn_save'] = btn_save

        # --- API View Frame (Stored Label + Change) ---
        self.api_view_frame = ttk.Frame(input_container)
        
        # Grünes Häkchen Label
        lbl_check = ttk.Label(self.api_view_frame, text="✔", foreground="green")
        lbl_check.pack(side="left", padx=(5, 5))
        
        lbl_stored = ttk.Label(self.api_view_frame)
        lbl_stored.pack(side="left", padx=(0, 10))
        self.ui_elements['lbl_stored'] = lbl_stored
        
        btn_change = ttk.Button(self.api_view_frame, command=lambda: self.set_api_mode(edit=True))
        btn_change.pack(side="left")
        self.ui_elements['btn_change'] = btn_change

        # Hyperlink (Created BEFORE Initial Mode Check)
        link_url = "https://www.themoviedb.org/settings/api"
        link_label = tk.Label(settings_frame, fg="blue", cursor="hand2", font=('Segoe UI', 9, 'underline'))
        link_label.pack(anchor="w", pady=(2, 0))
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new(link_url))
        self.ui_elements['link_label'] = link_label

        # Initial Mode Check
        if self.api_key.get():
            self.set_api_mode(edit=False)
        else:
            self.set_api_mode(edit=True)
        
        # --- File Selection ---
        files_frame = ttk.LabelFrame(self.root, padding=10)
        files_frame.pack(fill="x", padx=10, pady=5)
        self.ui_elements['files_frame'] = files_frame
        
        self.path_label = ttk.Label(files_frame)
        self.path_label.pack(side="left", fill="x", expand=True)
        self.ui_elements['path_label'] = self.path_label
        
        btn_open = ttk.Button(files_frame, command=self.open_directory)
        btn_open.pack(side="right")
        self.ui_elements['btn_open'] = btn_open

        # --- Search Area ---
        search_frame = ttk.LabelFrame(self.root, padding=10)
        search_frame.pack(fill="x", padx=10, pady=5)
        self.ui_elements['search_frame'] = search_frame
        
        # Mode Selection (TV / Movie)
        mode_frame = ttk.Frame(search_frame)
        mode_frame.pack(fill="x", pady=(0, 5))
        
        rb_tv = ttk.Radiobutton(mode_frame, variable=self.mode_var, value="tv", command=self.on_mode_change)
        rb_tv.pack(side="left", padx=(0, 10))
        self.ui_elements['rb_tv'] = rb_tv
        
        rb_movie = ttk.Radiobutton(mode_frame, variable=self.mode_var, value="movie", command=self.on_mode_change)
        rb_movie.pack(side="left")
        self.ui_elements['rb_movie'] = rb_movie
        
        # Search Bar
        search_bar = ttk.Frame(search_frame)
        search_bar.pack(fill="x", pady=(0, 5))
        
        self.search_var = tk.StringVar()
        entry = ttk.Entry(search_bar, textvariable=self.search_var)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        entry.bind("<Return>", lambda e: self.search_show())
        
        btn_search = ttk.Button(search_bar, command=self.search_show)
        btn_search.pack(side="right")
        self.ui_elements['btn_search'] = btn_search
        
        results_container = ttk.Frame(search_frame)
        results_container.pack(fill="x", expand=True)
        
        list_frame = ttk.Frame(results_container)
        list_frame.pack(side="left", fill="both", expand=True)
        
        scrollbar_search = ttk.Scrollbar(list_frame, orient="vertical")
        self.result_list = tk.Listbox(list_frame, height=8, width=80, yscrollcommand=scrollbar_search.set)
        scrollbar_search.config(command=self.result_list.yview)
        
        self.result_list.pack(side="left", fill="both", expand=True)
        scrollbar_search.pack(side="right", fill="y")
        self.result_list.bind('<<ListboxSelect>>', self.on_select_show)

        # Poster Area (Frame with Image + Navigation)
        self.poster_container = ttk.Frame(results_container)
        self.poster_container.pack(side="right", padx=(10, 0), fill="y")

        self.poster_label = ttk.Label(self.poster_container, relief="sunken", anchor="center")
        self.poster_label.config(width=25)
        self.poster_label.pack(side="top", fill="y", expand=True)
        if not HAS_PIL:
            self.poster_label.config(text="Pillow fehlt")
            
        # Navigation Controls
        nav_frame = ttk.Frame(self.poster_container)
        nav_frame.pack(side="bottom", fill="x", pady=5)
        
        self.btn_prev = ttk.Button(nav_frame, text="◄", width=3, command=lambda: self.change_poster(-1), state="disabled")
        self.btn_prev.pack(side="left")
        
        self.lbl_poster_count = ttk.Label(nav_frame, text="0 / 0", anchor="center")
        self.lbl_poster_count.pack(side="left", fill="x", expand=True)
        
        self.btn_next = ttk.Button(nav_frame, text="►", width=3, command=lambda: self.change_poster(1), state="disabled")
        self.btn_next.pack(side="right")

        # --- Preview & Action ---
        preview_frame = ttk.LabelFrame(self.root, padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.ui_elements['preview_frame'] = preview_frame
        
        format_frame = ttk.Frame(preview_frame)
        format_frame.pack(fill="x", pady=(0, 5))
        
        lbl_fmt = ttk.Label(format_frame)
        lbl_fmt.pack(side="left")
        self.ui_elements['lbl_fmt'] = lbl_fmt
        
        self.format_entry = ttk.Entry(format_frame, textvariable=self.format_var)
        self.format_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.format_entry.bind("<Return>", lambda e: self.generate_plan())
        
        btn_update = ttk.Button(format_frame, command=self.generate_plan)
        btn_update.pack(side="left", padx=(0, 10))
        self.ui_elements['btn_update'] = btn_update
        
        lbl_ph = ttk.Label(format_frame, font=("Segoe UI", 8), foreground="gray")
        lbl_ph.pack(side="left")
        self.ui_elements['lbl_ph'] = lbl_ph

        # Options
        options_frame = ttk.Frame(preview_frame)
        options_frame.pack(fill="x", pady=(0, 10))
        
        chk_extras = ttk.Checkbutton(options_frame, variable=self.rename_others_var)
        chk_extras.pack(side="left", padx=(0, 15))
        self.ui_elements['chk_extras'] = chk_extras
        
        chk_sample = ttk.Checkbutton(options_frame, variable=self.delete_samples_var)
        chk_sample.pack(side="left", padx=(0, 15))
        self.ui_elements['chk_sample'] = chk_sample
        
        chk_links = ttk.Checkbutton(options_frame, variable=self.delete_links_var)
        chk_links.pack(side="left", padx=(0, 15))
        self.ui_elements['chk_links'] = chk_links

        chk_ren_folder = ttk.Checkbutton(options_frame, variable=self.rename_folder_var)
        chk_ren_folder.pack(side="left") # Am Ende der Zeile
        self.ui_elements['chk_ren_folder'] = chk_ren_folder

        # Toolbar
        toolbar = ttk.Frame(preview_frame)
        toolbar.pack(fill="x", pady=(0, 5))
        
        self.status_label = ttk.Label(toolbar, foreground="blue")
        self.status_label.pack(side="left")
        self.ui_elements['status_label'] = self.status_label
        
        self.btn_download_art = ttk.Button(toolbar, command=self.open_artwork_dialog, state="disabled")
        self.btn_download_art.pack(side="right", padx=5)
        self.ui_elements['btn_download_art'] = self.btn_download_art

        self.btn_cleanup = ttk.Button(toolbar, command=self.execute_cleanup, state="disabled")
        self.btn_cleanup.pack(side="right", padx=5)
        self.ui_elements['btn_cleanup'] = self.btn_cleanup
        
        self.btn_rename = ttk.Button(toolbar, command=self.execute_rename, state="disabled")
        self.btn_rename.pack(side="right")
        self.ui_elements['btn_rename'] = self.btn_rename

        # Treeview
        columns = ("file", "arrow", "new_name", "status")
        self.tree = ttk.Treeview(preview_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.column("file", width=250)
        self.tree.column("arrow", width=30, anchor="center")
        self.tree.column("new_name", width=350)
        self.tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self.on_tree_double_click)

    def set_api_mode(self, edit=True):
        if edit:
            self.api_view_frame.pack_forget()
            self.api_edit_frame.pack(side="left", fill="x")
            if 'link_label' in self.ui_elements:
                self.ui_elements['link_label'].pack(anchor="w", pady=(2, 0))
        else:
            self.api_edit_frame.pack_forget()
            self.api_view_frame.pack(side="left", fill="x")
            if 'link_label' in self.ui_elements:
                self.ui_elements['link_label'].pack_forget()

    def save_config_ui(self):
        self.save_config()
        if self.api_key.get().strip():
            self.set_api_mode(edit=False)
            messagebox.showinfo(self.get_text('msg_done'), self.get_text('msg_saved'))

    def on_language_change(self):
        if not hasattr(self, 'tree') or self.tree is None: return
        self.update_ui_text()
        self.save_config(silent=True)
        if self.selected_show:
            self.fetch_details()
            
    def on_mode_change(self):
        if not hasattr(self, 'tree') or self.tree is None: return
        if self.mode_var.get() == "tv":
            self.format_var.set("{show} - S{s}E{e} - {title}")
        else:
            self.format_var.set("{show} ({year})")
        
        # UI Reset
        self.result_list.delete(0, tk.END)
        self.poster_label.config(image='', text=self.get_text('no_image'))
        self.selected_show = None
        self.search_results = []
        self.available_posters = []
        self.current_poster_idx = 0
        self.lbl_poster_count.config(text="0 / 0")
        self.btn_prev.config(state="disabled")
        self.btn_next.config(state="disabled")
        
        self.tree.delete(*self.tree.get_children())
        self.scan_files() # Refresh Preview

    def get_text(self, key):
        lang = self.lang_var.get()
        return TRANSLATIONS.get(lang, TRANSLATIONS['de']).get(key, key)

    def update_ui_text(self):
        # Schutz gegen frühen Aufruf
        if not hasattr(self, 'tree') or self.tree is None: return

        t = lambda k: self.get_text(k)
        
        self.root.title(t('title'))
        self.ui_elements['settings_frame'].config(text=t('settings'))
        self.ui_elements['lbl_api'].config(text=t('api_label'))
        self.ui_elements['btn_save'].config(text=t('save'))
        self.ui_elements['btn_change'].config(text=t('btn_change'))
        self.ui_elements['lbl_stored'].config(text=t('lbl_stored'))
        self.ui_elements['link_label'].config(text=t('get_key_link'))
        self.ui_elements['files_frame'].config(text=t('folder_select'))
        
        if not self.files:
            self.ui_elements['path_label'].config(text=t('no_folder'))
        
        self.ui_elements['btn_open'].config(text=t('open_folder'))
        self.ui_elements['search_frame'].config(text=t('search_show'))
        self.ui_elements['rb_tv'].config(text=t('mode_tv'))
        self.ui_elements['rb_movie'].config(text=t('mode_movie'))
        self.ui_elements['btn_search'].config(text=t('search_btn'))
        
        if not self.current_poster_image:
            self.poster_label.config(text=t('no_image'))
            
        self.ui_elements['preview_frame'].config(text=t('preview'))
        self.ui_elements['lbl_fmt'].config(text=t('format'))
        self.ui_elements['btn_update'].config(text=t('update'))
        self.ui_elements['lbl_ph'].config(text=t('placeholders'))
        self.ui_elements['chk_extras'].config(text=t('chk_extras'))
        self.ui_elements['chk_sample'].config(text=t('chk_sample'))
        self.ui_elements['chk_links'].config(text=t('chk_links'))
        self.ui_elements['chk_ren_folder'].config(text=t('chk_ren_folder'))
        self.ui_elements['status_label'].config(text=t('ready'))
        self.ui_elements['btn_download_art'].config(text=t('btn_artwork'))
        self.ui_elements['btn_cleanup'].config(text=t('btn_cleanup'))
        self.ui_elements['btn_rename'].config(text=t('start_rename'))
        self.ui_elements['lbl_donate'].config(text=t('donate'))
        
        self.tree.heading("file", text=t('col_file'))
        self.tree.heading("arrow", text="->")
        self.tree.heading("new_name", text=t('col_new'))
        self.tree.heading("status", text=t('col_status'))

    def log(self, message_key, error=False, literal=False):
        text = message_key if literal else self.get_text(message_key)
        self.status_label.config(text=text, foreground="red" if error else "blue")
        self.root.update_idletasks()

    def open_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.current_dir = folder_selected
            self.path_label.config(text=folder_selected)
            
            self.result_list.delete(0, tk.END)
            self.search_results = []
            self.selected_show = None
            self.poster_label.config(image='', text=self.get_text('no_image'))
            self.current_poster_image = None
            self.available_posters = []
            self.current_poster_idx = 0
            self.lbl_poster_count.config(text="0 / 0")
            
            self.search_var.set("")
            folder_name = os.path.basename(folder_selected)
            if folder_name:
                clean_name = folder_name.replace('.', ' ').replace('_', ' ')
                clean_name = re.sub(r'(?i)\s+s(?:eason)?\s*\d+.*$', '', clean_name).strip()
                clean_name = re.sub(r'\(\d{4}\)|\d{4}', '', clean_name).strip()
                self.search_var.set(clean_name)
                if self.api_key.get():
                     self.search_show()
            self.scan_files()
        
    def scan_files(self):
        self.files = []
        self.tree.delete(*self.tree.get_children())
        self.rename_plan = []
        valid_extensions = ('.mkv', '.mp4', '.avi', '.mov', '.wmv')
        
        try:
            for root, dirs, files in os.walk(self.current_dir):
                for f in files:
                    if f.lower().endswith(valid_extensions):
                        size = os.path.getsize(os.path.join(root, f))
                        parsed = self.parse_filename(f)
                        self.files.append({
                            'name': f,
                            'path': os.path.join(root, f),
                            'dir': root,
                            'size': size,
                            'parsed': parsed
                        })
            self.files.sort(key=lambda x: x['name'])
            
            for i, f in enumerate(self.files):
                self.tree.insert("", "end", iid=i, values=(f['name'], "->", "", self.get_text('status_wait')))
            
            if self.files:
                self.btn_cleanup.config(state="normal")
            else:
                self.btn_cleanup.config(state="disabled")
                
            self.log(self.get_text('log_found'), literal=True)
        except Exception as e:
            self.log(f"{self.get_text('err_read')}: {e}", True, literal=True)

    def parse_filename(self, filename):
        match = re.search(r'(?:s|season)\s?(\d{1,2}).*?(?:e|episode)\s?(\d{1,2})', filename, re.IGNORECASE)
        if match: return {'season': int(match.group(1)), 'episode': int(match.group(2))}
        
        match = re.search(r'(\d{1,2})x(\d{1,2})', filename, re.IGNORECASE)
        if match: return {'season': int(match.group(1)), 'episode': int(match.group(2))}
             
        match = re.search(r'(?<!\d)(\d{1,2})(\d{2})(?!\d)', filename)
        if match:
            s, e = int(match.group(1)), int(match.group(2))
            if s <= 50 and e <= 99: return {'season': s, 'episode': e}
        
        match = re.search(r'(?:^|[\s._\-])(?:e|ep|episode)\.?\s?(\d{1,2})(?!\d)', filename, re.IGNORECASE)
        if match: return {'season': 1, 'episode': int(match.group(1))}
        return None

    def search_show(self):
        query = self.search_var.get()
        key = self.api_key.get()
        lang_code = LANG_MAP.get(self.lang_var.get(), "de-DE")
        mode = self.mode_var.get()
        
        if not key:
            messagebox.showerror(self.get_text('msg_confirm'), self.get_text('err_no_key'))
            return
            
        self.log('log_search')
        self.result_list.delete(0, tk.END)
        self.poster_label.config(image='', text=self.get_text('loading'))
        
        def run_search():
            try:
                endpoint = "tv" if mode == "tv" else "movie"
                url = f"{TMDB_BASE_URL}/search/{endpoint}?api_key={key}&language={lang_code}&query={urllib.parse.quote(query)}"
                
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                    self.search_results = data.get('results', [])
                    self.root.after(0, self.update_search_ui)
            except Exception as e:
                self.root.after(0, lambda: self.log(f"{self.get_text('err_api')}: {e}", True, literal=True))

        threading.Thread(target=run_search, daemon=True).start()

    def update_search_ui(self):
        self.result_list.delete(0, tk.END)
        self.poster_label.config(text=self.get_text('no_image'))
        
        if not self.search_results:
            self.log('log_no_results')
            return
            
        for item in self.search_results:
            title = item.get('name') if self.mode_var.get() == "tv" else item.get('title')
            date = item.get('first_air_date') if self.mode_var.get() == "tv" else item.get('release_date')
            year = date.split('-')[0] if date else "N/A"
            self.result_list.insert(tk.END, f"{title} ({year})")
        
        self.log('log_select')

    def on_select_show(self, event):
        selection = self.result_list.curselection()
        if not selection: return
            
        index = selection[0]
        self.selected_show = self.search_results[index]
        
        title = self.selected_show.get('name') if self.mode_var.get() == "tv" else self.selected_show.get('title')
        self.log(f"{self.get_text('log_load_ep')} {title}...", literal=True)
        
        # Start fetching all posters instead of just one
        threading.Thread(target=self.fetch_all_posters, daemon=True).start()
        threading.Thread(target=self.fetch_details, daemon=True).start()

    def fetch_all_posters(self):
        key = self.api_key.get()
        show_id = self.selected_show['id']
        mode = self.mode_var.get()
        endpoint = "tv" if mode == "tv" else "movie"
        lang = LANG_MAP.get(self.lang_var.get(), "de-DE")
        
        self.available_posters = []
        try:
            url = f"{TMDB_BASE_URL}/{endpoint}/{show_id}/images?api_key={key}&include_image_language={lang.split('-')[0]},en,null"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                self.available_posters = data.get('posters', [])
        except Exception as e:
            print("Error fetching images list:", e)
        
        # Fallback to the single poster from search result if images endpoint fails or returns empty
        if not self.available_posters and self.selected_show.get('poster_path'):
            self.available_posters = [{'file_path': self.selected_show['poster_path']}]
            
        self.current_poster_idx = 0
        self.root.after(0, self.update_poster_view)

    def update_poster_view(self):
        # Update Nav Buttons
        count = len(self.available_posters)
        if count > 1:
            self.btn_prev.config(state="normal")
            self.btn_next.config(state="normal")
            self.lbl_poster_count.config(text=f"{self.current_poster_idx + 1} / {count}")
        else:
            self.btn_prev.config(state="disabled")
            self.btn_next.config(state="disabled")
            self.lbl_poster_count.config(text=f"{1 if count else 0} / {count}")

        if not self.available_posters:
            self.poster_label.config(image='', text=self.get_text('no_image'))
            return

        # Fetch current image
        path = self.available_posters[self.current_poster_idx]['file_path']
        
        def fetch_and_display():
            try:
                url = TMDB_IMAGE_BASE + path
                with urllib.request.urlopen(url) as response:
                    img_data = response.read()
                
                if not HAS_PIL:
                    self.root.after(0, lambda: self.poster_label.config(text="Pillow fehlt"))
                    return

                image = Image.open(io.BytesIO(img_data))
                basewidth = 150
                wpercent = (basewidth / float(image.size[0]))
                hsize = int((float(image.size[1]) * float(wpercent)))
                image = image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                def update_ui():
                    self.current_poster_image = photo 
                    self.poster_label.config(image=photo, text="")
                self.root.after(0, update_ui)
            except Exception as e:
                print("Image load error:", e)

        threading.Thread(target=fetch_and_display, daemon=True).start()

    def change_poster(self, delta):
        if not self.available_posters: return
        new_idx = self.current_poster_idx + delta
        # Loop around
        if new_idx < 0: new_idx = len(self.available_posters) - 1
        if new_idx >= len(self.available_posters): new_idx = 0
        
        self.current_poster_idx = new_idx
        self.update_poster_view()

    def fetch_details(self):
        key = self.api_key.get()
        show_id = self.selected_show['id']
        lang_code = LANG_MAP.get(self.lang_var.get(), "de-DE")
        mode = self.mode_var.get()

        if mode == "movie":
            self.root.after(0, self.generate_plan)
            return

        seasons = set(f['parsed']['season'] for f in self.files if f['parsed'])
        if not seasons: seasons = {1}
        
        all_episodes = []
        try:
            for season_num in seasons:
                url = f"{TMDB_BASE_URL}/tv/{show_id}/season/{season_num}?api_key={key}&language={lang_code}"
                try:
                    with urllib.request.urlopen(url) as response:
                        data = json.loads(response.read().decode())
                        all_episodes.extend(data.get('episodes', []))
                except HTTPError:
                    pass 
            self.episodes_cache = all_episodes
            self.root.after(0, self.generate_plan)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"{self.get_text('err_api')}: {e}", True, literal=True))

    def generate_plan(self):
        if not self.selected_show: return
        self.rename_plan = [None] * len(self.files)
        self.tree.delete(*self.tree.get_children())
        
        mode = self.mode_var.get()
        fmt = self.format_var.get()
        
        title = self.selected_show.get('name') if mode == "tv" else self.selected_show.get('title')
        clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
        
        date = self.selected_show.get('first_air_date') if mode == "tv" else self.selected_show.get('release_date')
        year = date.split('-')[0] if date else "N/A"

        has_matches = False

        if mode == "movie":
            max_size = 0
            if self.files:
                max_size = max(f['size'] for f in self.files)
            
            for i, f in enumerate(self.files):
                new_name = ""
                status = self.get_text('status_ignored')
                is_main_movie = (f['size'] == max_size)
                
                if is_main_movie:
                    ext = os.path.splitext(f['name'])[1]
                    try:
                        new_name = fmt.replace("{show}", clean_title)\
                                      .replace("{title}", clean_title)\
                                      .replace("{year}", year)
                        new_name = new_name.replace("S{s}E{e}", "").replace("{s}", "").replace("{e}", "")
                        new_name = re.sub(r'\s{2,}', ' ', new_name).strip()
                        new_name = re.sub(r' - \.', '.', new_name)
                        new_name += ext
                    except:
                        new_name = "Format Error"
                    
                    status = self.get_text('status_ready')
                    has_matches = True
                    self.rename_plan[i] = {
                        'original_path': f['path'],
                        'new_name': new_name,
                        'dir': f['dir']
                    }
                
                self.tree.insert("", "end", iid=i, values=(f['name'], "->", new_name, status))

        else:
            for i, f in enumerate(self.files):
                new_name = ""
                status = self.get_text('status_no_match')
                matched_ep = None
                if f['parsed']:
                    matched_ep = next((ep for ep in self.episodes_cache 
                                       if ep['season_number'] == f['parsed']['season'] 
                                       and ep['episode_number'] == f['parsed']['episode']), None)
                if matched_ep:
                    ext = os.path.splitext(f['name'])[1]
                    clean_ep_name = re.sub(r'[\\/*?:"<>|]', "", matched_ep['name'])
                    s = str(matched_ep['season_number']).zfill(2)
                    e = str(matched_ep['episode_number']).zfill(2)
                    try:
                        new_name = fmt.replace("{show}", clean_title)\
                                      .replace("{s}", s)\
                                      .replace("{e}", e)\
                                      .replace("{title}", clean_ep_name)\
                                      .replace("{year}", year)
                        new_name += ext
                    except Exception:
                        new_name = "Format Error"
                    status = self.get_text('status_ready')
                    has_matches = True
                    self.rename_plan[i] = {
                        'original_path': f['path'],
                        'new_name': new_name,
                        'dir': f['dir']
                    }
                self.tree.insert("", "end", iid=i, values=(f['name'], "->", new_name, status))
        
        if has_matches:
            self.btn_rename.config(state="normal")
            self.btn_download_art.config(state="normal")
            self.log('log_preview')
        else:
            self.log('log_no_results', True)

    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        idx = int(item_id)
        current_values = self.tree.item(item_id, 'values')
        original_name = current_values[0]
        current_new_name = current_values[2]
        new_val = simpledialog.askstring("Edit", f"New name for:\n{original_name}", 
                                       initialvalue=current_new_name or original_name, parent=self.root)
        if new_val is not None:
            status = self.get_text('status_manual') if new_val != original_name else self.get_text('status_ignored')
            self.tree.item(item_id, values=(original_name, "->", new_val, status))
            if new_val.strip() == "" or new_val == original_name:
                self.rename_plan[idx] = None
            else:
                self.rename_plan[idx] = {
                    'original_path': self.files[idx]['path'],
                    'new_name': new_val,
                    'dir': self.files[idx]['dir']
                }
            if any(p is not None for p in self.rename_plan):
                self.btn_rename.config(state="normal")

    def execute_cleanup(self):
        if not messagebox.askyesno(self.get_text('msg_confirm'), self.get_text('msg_cleanup_desc')): return
        deleted_samples = 0
        deleted_links = 0
        if self.delete_links_var.get():
            link_extensions = ('.url', '.lnk', '.html', '.htm', '.webloc')
            for root, dirs, files in os.walk(self.current_dir):
                for name in files:
                    if name.lower().endswith(link_extensions):
                        try: os.remove(os.path.join(root, name))
                        except: pass
                        else: deleted_links += 1
        if self.delete_samples_var.get():
            for root, dirs, files in os.walk(self.current_dir, topdown=False):
                for name in files:
                    if "sample" in name.lower():
                        try: os.remove(os.path.join(root, name))
                        except: pass
                        else: deleted_samples += 1
                for name in dirs:
                    if "sample" in name.lower():
                        try: shutil.rmtree(os.path.join(root, name))
                        except: pass
                        else: deleted_samples += 1
        msg = self.get_text('msg_cleanup_res')
        if deleted_links > 0: msg += f"\n- {deleted_links} Links"
        if deleted_samples > 0: msg += f"\n- {deleted_samples} Samples"
        messagebox.showinfo(self.get_text('msg_done'), msg)
        self.scan_files()

    def execute_rename(self):
        if not messagebox.askyesno(self.get_text('msg_confirm'), self.get_text('msg_start')): return
        count = 0
        errors = 0
        renamed_extras = 0
        if self.delete_links_var.get():
            link_extensions = ('.url', '.lnk', '.html', '.htm', '.webloc')
            for root, dirs, files in os.walk(self.current_dir):
                for name in files:
                    if name.lower().endswith(link_extensions):
                        try: os.remove(os.path.join(root, name))
                        except: pass
        if self.delete_samples_var.get():
            for root, dirs, files in os.walk(self.current_dir, topdown=False):
                for name in files:
                    if "sample" in name.lower():
                        try: os.remove(os.path.join(root, name))
                        except: pass
                for name in dirs:
                    if "sample" in name.lower():
                        try: shutil.rmtree(os.path.join(root, name))
                        except: pass
        valid_items = [p for p in self.rename_plan if p is not None]
        for item in valid_items:
            old_path = item['original_path']
            if not os.path.exists(old_path): continue
            new_path = os.path.join(item['dir'], item['new_name'])
            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    count += 1
                    if self.rename_others_var.get():
                        old_dir = os.path.dirname(old_path)
                        old_base = os.path.splitext(os.path.basename(old_path))[0]
                        new_base = os.path.splitext(os.path.basename(new_path))[0]
                        if os.path.exists(old_dir):
                            for f in os.listdir(old_dir):
                                f_path = os.path.join(old_dir, f)
                                if f_path == old_path or f_path == new_path: continue
                                if f.startswith(old_base + "."):
                                    suffix = f[len(old_base):]
                                    try: os.rename(f_path, os.path.join(old_dir, new_base + suffix))
                                    except: pass
                                    else: renamed_extras += 1
                except Exception as e:
                    print(e); errors += 1
        
        msg = f"{count} {self.get_text('msg_success')}"
        if renamed_extras > 0: msg += f"\n+ {renamed_extras} Extras"
        if errors > 0: msg += f"\n{errors} Errors"

        # 3. ORDNER UMBENENNEN (Ganz am Ende)
        if self.rename_folder_var.get() and self.selected_show:
            try:
                # Info aus selected_show holen
                mode = self.mode_var.get()
                title = self.selected_show.get('name') if mode == "tv" else self.selected_show.get('title')
                date = self.selected_show.get('first_air_date') if mode == "tv" else self.selected_show.get('release_date')
                year = date.split('-')[0] if date else "0000"
                
                clean_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
                new_folder_name = f"{clean_title} ({year})"
                
                # Zielpfad bauen
                # self.current_dir ist der aktuelle Ordner
                parent_dir = os.path.dirname(self.current_dir)
                new_folder_path = os.path.join(parent_dir, new_folder_name)
                
                # Nur umbenennen wenn nötig
                if self.current_dir != new_folder_path:
                    os.rename(self.current_dir, new_folder_path)
                    self.current_dir = new_folder_path # Update internal state
                    self.path_label.config(text=self.current_dir) # Update UI
                    msg += f"\nOrdner umbenannt zu: {new_folder_name}"
            except Exception as e:
                msg += f"\nFehler beim Ordner-Umbenennen: {e}"

        messagebox.showinfo(self.get_text('msg_done'), msg)
        self.scan_files()
        self.btn_rename.config(state="disabled")

    def open_artwork_dialog(self):
        if not self.selected_show or not self.current_dir: return
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text('art_title'))
        dialog.geometry("350x300")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text=self.get_text('art_select'), font=('Segoe UI', 10, 'bold')).pack(pady=10)
        vars = {
            'poster': tk.BooleanVar(value=True),
            'fanart': tk.BooleanVar(value=True),
            'logo': tk.BooleanVar(value=False),
            'banner': tk.BooleanVar(value=False),
            'clearart': tk.BooleanVar(value=False)
        }
        ttk.Checkbutton(dialog, text=self.get_text('art_poster'), variable=vars['poster']).pack(anchor='w', padx=20)
        ttk.Checkbutton(dialog, text=self.get_text('art_fanart'), variable=vars['fanart']).pack(anchor='w', padx=20)
        ttk.Checkbutton(dialog, text=self.get_text('art_logo'), variable=vars['logo']).pack(anchor='w', padx=20)
        ttk.Checkbutton(dialog, text=self.get_text('art_banner'), variable=vars['banner']).pack(anchor='w', padx=20)
        ttk.Checkbutton(dialog, text=self.get_text('art_clearart'), variable=vars['clearart']).pack(anchor='w', padx=20)

        def run_download():
            dialog.destroy()
            threading.Thread(target=self.download_selected_artwork, args=(vars,), daemon=True).start()
        ttk.Button(dialog, text=self.get_text('art_btn_load'), command=run_download).pack(pady=20)

    def download_selected_artwork(self, vars):
        key = self.api_key.get()
        show_id = self.selected_show['id']
        lang = LANG_MAP.get(self.lang_var.get(), "de-DE")
        mode = self.mode_var.get()
        endpoint = "tv" if mode == "tv" else "movie"
        
        images_data = {}
        try:
            url = f"{TMDB_BASE_URL}/{endpoint}/{show_id}/images?api_key={key}&include_image_language={lang.split('-')[0]},en,null"
            with urllib.request.urlopen(url) as response:
                images_data = json.loads(response.read().decode())
        except Exception as e:
            print("Error fetching images:", e)
        
        targets = []
        
        # POSTER (Use specifically selected one if available)
        if vars['poster'].get():
            path = None
            # Check if we have a currently selected poster in view
            if self.available_posters and len(self.available_posters) > self.current_poster_idx:
                 path = self.available_posters[self.current_poster_idx]['file_path']
            
            # Fallback (should normally not happen if UI is active)
            if not path:
                path = self.selected_show.get('poster_path')
            
            if path: targets.append((path, "poster.jpg"))

        # FANART
        if vars['fanart'].get():
            path = self.selected_show.get('backdrop_path')
            if not path and images_data.get('backdrops'):
                path = images_data['backdrops'][0]['file_path']
            if path: targets.append((path, "fanart.jpg"))

        # LOGO
        if vars['logo'].get():
            if images_data.get('logos'):
                path = images_data['logos'][0]['file_path']
                targets.append((path, "logo.png"))

        # CLEARART
        if vars['clearart'].get():
            if images_data.get('logos'):
                path = images_data['logos'][0]['file_path']
                targets.append((path, "clearart.png"))

        count = 0
        for path, filename in targets:
            url = TMDB_IMAGE_ORIGINAL + path
            save_path = os.path.join(self.current_dir, filename)
            try:
                urllib.request.urlretrieve(url, save_path)
                count += 1
            except Exception as e:
                print(f"Error downloading {filename}: {e}")

        if count > 0:
            messagebox.showinfo(self.get_text('msg_done'), self.get_text('art_msg_ok'))
        else:
            messagebox.showwarning(self.get_text('msg_done'), "Keine Bilder gefunden/geladen.")

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.api_key.set(data.get('api_key', ''))
                        self.format_var.set(data.get('format', '{show} - S{s}E{e} - {title}'))
                        self.lang_var.set(data.get('language', 'de'))
        except: pass

    def save_config(self, silent=False):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    'api_key': self.api_key.get(),
                    'format': self.format_var.get(),
                    'language': self.lang_var.get()
                }, f)
        except: pass

if __name__ == "__main__":
    try:
        root = tk.Tk()
        # Optional: Catch errors during app initialization
        try:
            app = CineMatchApp(root)
        except Exception as e:
            messagebox.showerror("Fehler beim Starten", f"Fehler beim Initialisieren der App:\n{e}")
            sys.exit(1)
            
        root.mainloop()
    except Exception as e:
        # Fallback if Tkinter itself fails or messagebox fails
        print(f"Kritischer Fehler: {e}")
