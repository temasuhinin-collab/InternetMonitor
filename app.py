import csv
import os
import shutil
import sqlite3
import webbrowser
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# ============================================================
# CAR MANAGER
# ============================================================

APP_NAME = "Car Manager"
VERSION = "3.2.0"
AUTHOR = "Artem Sukhinin"
TELEGRAM_URL = "https://t.me/artem_sukhinin"

APP_DIR = Path.home() / "CarManager"
DB_FILE = APP_DIR / "CarManager.db"
PHOTOS_DIR = APP_DIR / "photos"
BACKUP_DIR = APP_DIR / "backups"
SETTINGS_FILE = APP_DIR / "settings.txt"

APP_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# TRANSLATIONS
# ============================================================

LANG = {
    "ru": {
        "dashboard": "Главная",
        "garage": "Гараж",
        "service": "Обслуживание",
        "fuel": "Заправки",
        "expenses": "Расходы",
        "reminders": "Напоминания",
        "settings": "Настройки",
        "about": "О программе",

        "add_car": "＋ Добавить автомобиль",
        "edit": "Изменить",
        "delete": "Удалить",
        "save": "Сохранить",
        "cancel": "Отмена",
        "close": "Закрыть",
        "add": "Добавить",

        "search": "Поиск...",
        "search_garage": "Поиск автомобиля...",

        "cars": "Автомобили",
        "total_cars": "Всего автомобилей",
        "service_count": "Обслуживаний",
        "fuel_count": "Заправок",
        "expense_total": "Расходы",
        "recent_cars": "Последние автомобили",
        "no_cars": "В гараже пока нет автомобилей",
        "no_photo": "НЕТ ФОТО",

        "car_name": "Название",
        "make": "Марка",
        "model": "Модель",
        "year": "Год",
        "mileage": "Пробег",
        "vin": "VIN",
        "plate": "Госномер",
        "color": "Цвет",
        "engine": "Двигатель",
        "transmission": "КПП",
        "drive": "Привод",
        "fuel_type": "Топливо",
        "notes": "Заметки",
        "photo": "Фото автомобиля",
        "choose_photo": "Выбрать фото",
        "remove_photo": "Удалить фото",
        "change_photo": "Изменить фото",

        "petrol": "Бензин",
        "diesel": "Дизель",
        "hybrid": "Гибрид",
        "electric": "Электро",
        "gas": "Газ",

        "manual": "Механика",
        "automatic": "Автомат",
        "cvt": "CVT",
        "robot": "Робот",

        "fwd": "Передний",
        "rwd": "Задний",
        "awd": "Полный",

        "service_title": "Работа",
        "category": "Категория",
        "cost": "Стоимость",
        "date": "Дата",
        "station": "АЗС",
        "liters": "Литры",
        "price": "Цена за литр",
        "amount": "Сумма",
        "expense_title": "Расход",
        "due_date": "Дата",
        "due_mileage": "Пробег",
        "done": "Выполнено",

        "export_csv": "Экспорт CSV",
        "open_folder": "Открыть папку данных",
        "theme": "Тема",
        "dark": "Тёмная",
        "light": "Светлая",
        "language": "Язык",
        "russian": "Русский",
        "english": "English",

        "welcome": "Добро пожаловать в Car Manager",
        "manage_cars": "Управляйте автомобилями, обслуживанием и расходами в одном месте.",
        "quick_actions": "Быстрые действия",
        "add_first_car": "Добавьте первый автомобиль",
        "photo_hint": "Поддерживаются JPG, JPEG, PNG, WEBP",

        "delete_confirm": "Удалить этот автомобиль?",
        "delete_warning": "Все связанные записи обслуживания, заправок, расходов и напоминаний также будут удалены.",
        "saved": "Автомобиль сохранён",
        "deleted": "Автомобиль удалён",
        "error": "Ошибка",

        "service_empty": "Записей об обслуживании пока нет",
        "fuel_empty": "Заправок пока нет",
        "expenses_empty": "Расходов пока нет",
        "reminders_empty": "Напоминаний пока нет",

        "about_text": "Car Manager\n\nУправление автомобилями, обслуживанием, расходами и заправками.\n\nРазработчик:\nArtem Sukhinin",
        "telegram": "Telegram разработчика",

        "select_car": "Автомобиль",
        "all_cars": "Все автомобили",

        "confirm_delete": "Подтверждение",
        "invalid_year": "Введите корректный год.",
        "invalid_mileage": "Введите корректный пробег.",
        "required_name": "Введите название автомобиля.",
        "photo_error": "Не удалось сохранить фотографию.",

        "language_changed": "Язык изменён. Интерфейс обновлён.",
    },

    "en": {
        "dashboard": "Dashboard",
        "garage": "Garage",
        "service": "Service",
        "fuel": "Fuel",
        "expenses": "Expenses",
        "reminders": "Reminders",
        "settings": "Settings",
        "about": "About",

        "add_car": "＋ Add vehicle",
        "edit": "Edit",
        "delete": "Delete",
        "save": "Save",
        "cancel": "Cancel",
        "close": "Close",
        "add": "Add",

        "search": "Search...",
        "search_garage": "Search vehicle...",

        "cars": "Vehicles",
        "total_cars": "Total vehicles",
        "service_count": "Service records",
        "fuel_count": "Fuel records",
        "expense_total": "Expenses",
        "recent_cars": "Recent vehicles",
        "no_cars": "Your garage is empty",
        "no_photo": "NO PHOTO",

        "car_name": "Name",
        "make": "Make",
        "model": "Model",
        "year": "Year",
        "mileage": "Mileage",
        "vin": "VIN",
        "plate": "License plate",
        "color": "Color",
        "engine": "Engine",
        "transmission": "Transmission",
        "drive": "Drive",
        "fuel_type": "Fuel",
        "notes": "Notes",
        "photo": "Vehicle photo",
        "choose_photo": "Choose photo",
        "remove_photo": "Remove photo",
        "change_photo": "Change photo",

        "petrol": "Petrol",
        "diesel": "Diesel",
        "hybrid": "Hybrid",
        "electric": "Electric",
        "gas": "Gas",

        "manual": "Manual",
        "automatic": "Automatic",
        "cvt": "CVT",
        "robot": "DCT",

        "fwd": "FWD",
        "rwd": "RWD",
        "awd": "AWD",

        "service_title": "Work",
        "category": "Category",
        "cost": "Cost",
        "date": "Date",
        "station": "Station",
        "liters": "Liters",
        "price": "Price / liter",
        "amount": "Amount",
        "expense_title": "Expense",
        "due_date": "Date",
        "due_mileage": "Mileage",
        "done": "Completed",

        "export_csv": "Export CSV",
        "open_folder": "Open data folder",
        "theme": "Theme",
        "dark": "Dark",
        "light": "Light",
        "language": "Language",
        "russian": "Русский",
        "english": "English",

        "welcome": "Welcome to Car Manager",
        "manage_cars": "Manage vehicles, maintenance, fuel and expenses in one place.",
        "quick_actions": "Quick actions",
        "add_first_car": "Add your first vehicle",
        "photo_hint": "JPG, JPEG, PNG and WEBP supported",

        "delete_confirm": "Delete this vehicle?",
        "delete_warning": "All related service, fuel, expense and reminder records will also be deleted.",
        "saved": "Vehicle saved",
        "deleted": "Vehicle deleted",
        "error": "Error",

        "service_empty": "No service records yet",
        "fuel_empty": "No fuel records yet",
        "expenses_empty": "No expenses yet",
        "reminders_empty": "No reminders yet",

        "about_text": "Car Manager\n\nManage vehicles, maintenance, expenses and fuel in one place.\n\nDeveloper:\nArtem Sukhinin",
        "telegram": "Developer Telegram",

        "select_car": "Vehicle",
        "all_cars": "All vehicles",

        "confirm_delete": "Confirmation",
        "invalid_year": "Enter a valid year.",
        "invalid_mileage": "Enter a valid mileage.",
        "required_name": "Enter vehicle name.",
        "photo_error": "Could not save the photo.",

        "language_changed": "Language changed. Interface updated.",
    },
}


# ============================================================
# DATABASE
# ============================================================

class Database:

    SCHEMA_VERSION = 5

    def __init__(self):
        self.connection = sqlite3.connect(DB_FILE)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.create_base_tables()
        self.migrate_database()

    def execute(self, sql, params=()):
        cur = self.connection.cursor()
        cur.execute(sql, params)
        self.connection.commit()
        return cur

    def executemany(self, sql, data):
        cur = self.connection.cursor()
        cur.executemany(sql, data)
        self.connection.commit()
        return cur

    def one(self, sql, params=()):
        return self.connection.execute(sql, params).fetchone()

    def all(self, sql, params=()):
        return self.connection.execute(sql, params).fetchall()

    def scalar(self, sql, params=()):
        row = self.one(sql, params)
        if row is None:
            return None
        return row[0]

    def create_base_tables(self):
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT '',
            make TEXT DEFAULT '',
            model TEXT DEFAULT '',
            year INTEGER DEFAULT 0,
            mileage INTEGER DEFAULT 0,
            vin TEXT DEFAULT '',
            plate TEXT DEFAULT '',
            color TEXT DEFAULT '',
            engine TEXT DEFAULT '',
            transmission TEXT DEFAULT '',
            drive TEXT DEFAULT '',
            fuel TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            photo TEXT DEFAULT '',
            created_at TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS service (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER DEFAULT 0,
            title TEXT DEFAULT '',
            category TEXT DEFAULT '',
            mileage INTEGER DEFAULT 0,
            cost REAL DEFAULT 0,
            date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS fuel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER DEFAULT 0,
            liters REAL DEFAULT 0,
            price REAL DEFAULT 0,
            mileage INTEGER DEFAULT 0,
            date TEXT DEFAULT '',
            station TEXT DEFAULT '',
            FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER DEFAULT 0,
            title TEXT DEFAULT '',
            category TEXT DEFAULT '',
            amount REAL DEFAULT 0,
            date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER DEFAULT 0,
            title TEXT DEFAULT '',
            due_date TEXT DEFAULT '',
            due_mileage INTEGER DEFAULT 0,
            done INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS database_info (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            version INTEGER DEFAULT 1
        );

        INSERT OR IGNORE INTO database_info(id, version)
        VALUES(1, 1);
        """)
        self.connection.commit()

    def create_backup(self):
        try:
            self.connection.commit()
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = BACKUP_DIR / f"CarManager_backup_{stamp}.db"

            backup_connection = sqlite3.connect(backup)
            with backup_connection:
                self.connection.backup(backup_connection)
            backup_connection.close()

            return backup
        except Exception:
            return None

    def migrate_database(self):
        current = self.scalar(
            "SELECT version FROM database_info WHERE id=1"
        ) or 1

        if current < self.SCHEMA_VERSION:
            self.create_backup()

        required = {
            "cars": {
                "name": "TEXT DEFAULT ''",
                "make": "TEXT DEFAULT ''",
                "model": "TEXT DEFAULT ''",
                "year": "INTEGER DEFAULT 0",
                "mileage": "INTEGER DEFAULT 0",
                "vin": "TEXT DEFAULT ''",
                "plate": "TEXT DEFAULT ''",
                "color": "TEXT DEFAULT ''",
                "engine": "TEXT DEFAULT ''",
                "transmission": "TEXT DEFAULT ''",
                "drive": "TEXT DEFAULT ''",
                "fuel": "TEXT DEFAULT ''",
                "notes": "TEXT DEFAULT ''",
                "photo": "TEXT DEFAULT ''",
                "created_at": "TEXT DEFAULT ''",
            },
            "service": {
                "car_id": "INTEGER DEFAULT 0",
                "title": "TEXT DEFAULT ''",
                "category": "TEXT DEFAULT ''",
                "mileage": "INTEGER DEFAULT 0",
                "cost": "REAL DEFAULT 0",
                "date": "TEXT DEFAULT ''",
                "notes": "TEXT DEFAULT ''",
            },
            "fuel": {
                "car_id": "INTEGER DEFAULT 0",
                "liters": "REAL DEFAULT 0",
                "price": "REAL DEFAULT 0",
                "mileage": "INTEGER DEFAULT 0",
                "date": "TEXT DEFAULT ''",
                "station": "TEXT DEFAULT ''",
            },
            "expenses": {
                "car_id": "INTEGER DEFAULT 0",
                "title": "TEXT DEFAULT ''",
                "category": "TEXT DEFAULT ''",
                "amount": "REAL DEFAULT 0",
                "date": "TEXT DEFAULT ''",
                "notes": "TEXT DEFAULT ''",
            },
            "reminders": {
                "car_id": "INTEGER DEFAULT 0",
                "title": "TEXT DEFAULT ''",
                "due_date": "TEXT DEFAULT ''",
                "due_mileage": "INTEGER DEFAULT 0",
                "done": "INTEGER DEFAULT 0",
                "notes": "TEXT DEFAULT ''",
            },
        }

        for table, columns in required.items():
            existing = {
                row["name"]
                for row in self.connection.execute(
                    f"PRAGMA table_info({table})"
                ).fetchall()
            }

            for column, definition in columns.items():
                if column not in existing:
                    self.connection.execute(
                        f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
                    )

        self.connection.execute(
            "UPDATE database_info SET version=? WHERE id=1",
            (self.SCHEMA_VERSION,)
        )

        self.connection.commit()

    def close(self):
        try:
            self.connection.commit()
            self.connection.close()
        except Exception:
            pass


# ============================================================
# APPLICATION
# ============================================================

class CarManager(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("1450x900")
        self.minsize(1100, 700)

        self.db = Database()

        self.language = self.load_setting("language", "ru")
        self.theme = self.load_setting("theme", "dark")

        if self.language not in LANG:
            self.language = "ru"

        self.colors = {}
        self.current_page = "dashboard"
        self.photo_preview = None
        self.current_photo_path = ""

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.configure_theme()
        self.build_interface()
        self.show_dashboard()

    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    def load_setting(self, key, default):
        try:
            if SETTINGS_FILE.exists():
                data = {}
                for line in SETTINGS_FILE.read_text(
                    encoding="utf-8"
                ).splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        data[k] = v
                return data.get(key, default)
        except Exception:
            pass

        return default

    def save_settings(self):
        try:
            SETTINGS_FILE.write_text(
                f"language={self.language}\n"
                f"theme={self.theme}\n",
                encoding="utf-8"
            )
        except Exception:
            pass

    def t(self, key):
        return LANG.get(self.language, LANG["ru"]).get(key, key)

    # --------------------------------------------------------
    # THEME
    # --------------------------------------------------------

    def configure_theme(self):

        if self.theme == "dark":
            self.colors = {
                "bg": "#0B1120",
                "sidebar": "#0F172A",
                "card": "#111827",
                "card2": "#172033",
                "border": "#263247",
                "text": "#F8FAFC",
                "muted": "#94A3B8",
                "accent": "#4F8CFF",
                "accent2": "#6EA8FF",
                "danger": "#EF4444",
                "success": "#22C55E",
                "input": "#0F172A",
                "hover": "#1E293B",
            }
        else:
            self.colors = {
                "bg": "#F4F7FB",
                "sidebar": "#FFFFFF",
                "card": "#FFFFFF",
                "card2": "#F8FAFC",
                "border": "#DCE3ED",
                "text": "#111827",
                "muted": "#64748B",
                "accent": "#2563EB",
                "accent2": "#3B82F6",
                "danger": "#DC2626",
                "success": "#16A34A",
                "input": "#FFFFFF",
                "hover": "#EEF4FF",
            }

        self.configure(bg=self.colors["bg"])

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            ".",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10)
        )

        style.configure(
            "TFrame",
            background=self.colors["bg"]
        )

        style.configure(
            "Card.TFrame",
            background=self.colors["card"]
        )

        style.configure(
            "TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text"]
        )

        style.configure(
            "Card.TLabel",
            background=self.colors["card"],
            foreground=self.colors["text"]
        )

        style.configure(
            "Muted.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"]
        )

        style.configure(
            "CardMuted.TLabel",
            background=self.colors["card"],
            foreground=self.colors["muted"]
        )

        style.configure(
            "Title.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Segoe UI Semibold", 24)
        )

        style.configure(
            "Subtitle.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 11)
        )

        style.configure(
            "Treeview",
            background=self.colors["card"],
            foreground=self.colors["text"],
            fieldbackground=self.colors["card"],
            borderwidth=0,
            rowheight=36
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["sidebar"],
            foreground=self.colors["muted"],
            font=("Segoe UI Semibold", 9)
        )

        style.map(
            "Treeview",
            background=[
                ("selected", self.colors["accent"])
            ],
            foreground=[
                ("selected", "#FFFFFF")
            ]
        )

        style.configure(
            "TEntry",
            fieldbackground=self.colors["input"],
            foreground=self.colors["text"],
            insertcolor=self.colors["text"],
            bordercolor=self.colors["border"]
        )

        style.configure(
            "TCombobox",
            fieldbackground=self.colors["input"],
            foreground=self.colors["text"]
        )

        style.configure(
            "TButton",
            background=self.colors["card2"],
            foreground=self.colors["text"],
            borderwidth=0,
            padding=(12, 8)
        )

        style.map(
            "TButton",
            background=[
                ("active", self.colors["hover"])
            ]
        )

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def build_interface(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.sidebar = tk.Frame(
            self,
            bg=self.colors["sidebar"],
            width=245
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = tk.Frame(
            self,
            bg=self.colors["bg"]
        )
        self.main.pack(side="right", fill="both", expand=True)

        self.build_sidebar()

    def build_sidebar(self):

        logo = tk.Frame(
            self.sidebar,
            bg=self.colors["sidebar"]
        )
        logo.pack(fill="x", padx=22, pady=(25, 30))

        tk.Label(
            logo,
            text="CAR",
            bg=self.colors["sidebar"],
            fg=self.colors["accent"],
            font=("Segoe UI Black", 19)
        ).pack(anchor="w")

        tk.Label(
            logo,
            text="MANAGER",
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 19)
        ).pack(anchor="w")

        tk.Label(
            logo,
            text=f"v{VERSION}",
            bg=self.colors["sidebar"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(3, 0))

        self.nav_buttons = {}

        items = [
            ("dashboard", "⌂", "dashboard"),
            ("garage", "▣", "garage"),
            ("service", "⚙", "service"),
            ("fuel", "⛽", "fuel"),
            ("expenses", "₽", "expenses"),
            ("reminders", "◷", "reminders"),
        ]

        for key, icon, label in items:
            self.create_nav_button(key, icon, self.t(label))

        spacer = tk.Frame(
            self.sidebar,
            bg=self.colors["sidebar"]
        )
        spacer.pack(fill="both", expand=True)

        settings = tk.Frame(
            self.sidebar,
            bg=self.colors["sidebar"]
        )
        settings.pack(fill="x", padx=15, pady=15)

        self.create_nav_button(
            "settings",
            "⚙",
            self.t("settings"),
            parent=settings
        )

        self.create_nav_button(
            "about",
            "ⓘ",
            self.t("about"),
            parent=settings
        )

        author = tk.Label(
            self.sidebar,
            text="by Artem Sukhinin",
            bg=self.colors["sidebar"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8)
        )
        author.pack(pady=(0, 18))

    def create_nav_button(
        self,
        key,
        icon,
        text,
        parent=None
    ):

        if parent is None:
            parent = self.sidebar

        btn = tk.Button(
            parent,
            text=f"{icon}   {text}",
            command=lambda k=key: self.navigate(k),
            anchor="w",
            padx=18,
            bd=0,
            relief="flat",
            bg=self.colors["sidebar"],
            fg=self.colors["muted"],
            activebackground=self.colors["hover"],
            activeforeground=self.colors["text"],
            font=("Segoe UI Semibold", 10),
            cursor="hand2"
        )

        btn.pack(fill="x", pady=3)

        self.nav_buttons[key] = btn

    def navigate(self, page):
        self.current_page = page

        if page == "dashboard":
            self.show_dashboard()
        elif page == "garage":
            self.show_garage()
        elif page == "service":
            self.show_records("service")
        elif page == "fuel":
            self.show_records("fuel")
        elif page == "expenses":
            self.show_records("expenses")
        elif page == "reminders":
            self.show_records("reminders")
        elif page == "settings":
            self.show_settings()
        elif page == "about":
            self.show_about()

    def clear_main(self):

        for widget in self.main.winfo_children():
            widget.destroy()

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def page_header(
        self,
        title,
        subtitle="",
        action_text=None,
        command=None
    ):

        header = tk.Frame(
            self.main,
            bg=self.colors["bg"]
        )
        header.pack(
            fill="x",
            padx=35,
            pady=(30, 22)
        )

        left = tk.Frame(
            header,
            bg=self.colors["bg"]
        )
        left.pack(side="left")

        tk.Label(
            left,
            text=title,
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 25)
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                left,
                text=subtitle,
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(5, 0))

        if action_text:
            tk.Button(
                header,
                text=action_text,
                command=command,
                bg=self.colors["accent"],
                fg="white",
                activebackground=self.colors["accent2"],
                activeforeground="white",
                bd=0,
                relief="flat",
                padx=17,
                pady=10,
                font=("Segoe UI Semibold", 10),
                cursor="hand2"
            ).pack(side="right")

    def card(self, parent, **kwargs):

        frame = tk.Frame(
            parent,
            bg=self.colors["card"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            **kwargs
        )

        return frame

    def stat_card(self, parent, title, value, icon):

        frame = self.card(parent)
        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        top = tk.Frame(
            frame,
            bg=self.colors["card"]
        )
        top.pack(fill="x", padx=20, pady=(18, 5))

        tk.Label(
            top,
            text=icon,
            bg=self.colors["card"],
            fg=self.colors["accent"],
            font=("Segoe UI", 18)
        ).pack(side="left")

        tk.Label(
            top,
            text=title,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        ).pack(side="left", padx=10)

        tk.Label(
            frame,
            text=value,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 24)
        ).pack(anchor="w", padx=20, pady=(0, 18))

        return frame

    def safe_int(self, value, default=0):

        try:
            return int(str(value).strip())
        except Exception:
            return default

    def safe_float(self, value, default=0):

        try:
            return float(
                str(value).replace(",", ".").strip()
            )
        except Exception:
            return default

    def format_number(self, value):

        try:
            return f"{int(value):,}".replace(",", " ")
        except Exception:
            return str(value)

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    def show_dashboard(self):

        self.clear_main()

        cars_count = self.db.scalar(
            "SELECT COUNT(*) FROM cars"
        ) or 0

        service_count = self.db.scalar(
            "SELECT COUNT(*) FROM service"
        ) or 0

        fuel_count = self.db.scalar(
            "SELECT COUNT(*) FROM fuel"
        ) or 0

        expenses = self.db.scalar(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        ) or 0

        self.page_header(
            self.t("dashboard"),
            self.t("manage_cars"),
            self.t("add_car"),
            self.add_car
        )

        stats = tk.Frame(
            self.main,
            bg=self.colors["bg"]
        )
        stats.pack(
            fill="x",
            padx=35
        )

        self.stat_card(
            stats,
            self.t("total_cars"),
            cars_count,
            "🚗"
        )

        self.stat_card(
            stats,
            self.t("service_count"),
            service_count,
            "🔧"
        )

        self.stat_card(
            stats,
            self.t("fuel_count"),
            fuel_count,
            "⛽"
        )

        self.stat_card(
            stats,
            self.t("expense_total"),
            f"{expenses:,.0f}",
            "₽"
        )

        section = tk.Frame(
            self.main,
            bg=self.colors["bg"]
        )
        section.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        tk.Label(
            section,
            text=self.t("recent_cars"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 16)
        ).pack(anchor="w", pady=(0, 15))

        cars = self.db.all("""
            SELECT
                id,
                name,
                make,
                model,
                year,
                mileage,
                vin,
                plate,
                color,
                engine,
                transmission,
                drive,
                fuel,
                notes,
                photo,
                created_at
            FROM cars
            ORDER BY id DESC
            LIMIT 6
        """)

        if not cars:

            empty = self.card(section)
            empty.pack(fill="x", pady=10)

            tk.Label(
                empty,
                text="🚘",
                bg=self.colors["card"],
                fg=self.colors["accent"],
                font=("Segoe UI", 36)
            ).pack(pady=(25, 8))

            tk.Label(
                empty,
                text=self.t("no_cars"),
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=("Segoe UI", 11)
            ).pack(pady=(0, 25))

            return

        canvas = tk.Canvas(
            section,
            bg=self.colors["bg"],
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            section,
            orient="vertical",
            command=canvas.yview
        )

        container = tk.Frame(
            canvas,
            bg=self.colors["bg"]
        )

        container.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=container,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        for i, car in enumerate(cars):

            self.vehicle_card(
                container,
                car,
                column=i % 2,
                row=i // 2
            )

        for i in range(2):
            container.grid_columnconfigure(
                i,
                weight=1
            )

    # --------------------------------------------------------
    # VEHICLE PHOTO
    # --------------------------------------------------------

    def copy_photo(self, source, car_id):

        try:

            source = Path(source)

            if not source.exists():
                return ""

            extension = source.suffix.lower()

            if extension not in (
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ):
                extension = ".jpg"

            destination = PHOTOS_DIR / f"car_{car_id}{extension}"

            for old in PHOTOS_DIR.glob(
                f"car_{car_id}.*"
            ):
                try:
                    old.unlink()
                except Exception:
                    pass

            shutil.copy2(
                source,
                destination
            )

            return str(destination)

        except Exception:
            return ""

    def delete_car_photo(self, car_id):

        for path in PHOTOS_DIR.glob(
            f"car_{car_id}.*"
        ):
            try:
                path.unlink()
            except Exception:
                pass

    def load_photo(self, path, size=(250, 155)):

        if not path:
            return None

        try:
            if not Path(path).exists():
                return None

            image = tk.PhotoImage(
                file=path
            )

            width = image.width()
            height = image.height()

            target_w, target_h = size

            scale_x = max(1, width // target_w)
            scale_y = max(1, height // target_h)
            scale = max(scale_x, scale_y)

            if scale > 1:
                image = image.subsample(
                    scale,
                    scale
                )

            return image

        except Exception:

            # PNG is supported natively.
            # For JPEG/WEBP fallback to Pillow if installed.
            try:
                from PIL import Image, ImageTk

                img = Image.open(path)
                img.thumbnail(size)

                return ImageTk.PhotoImage(img)

            except Exception:
                return None

    # --------------------------------------------------------
    # VEHICLE CARD
    # --------------------------------------------------------

    def vehicle_card(
        self,
        parent,
        car,
        column=0,
        row=0
    ):

        card = self.card(parent)

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=7,
            pady=7
        )

        photo_frame = tk.Frame(
            card,
            bg=self.colors["card2"],
            width=270,
            height=165
        )

        photo_frame.pack(
            fill="x",
            padx=12,
            pady=(12, 0)
        )

        photo_frame.pack_propagate(False)

        photo = self.load_photo(
            car["photo"],
            (270, 165)
        )

        if photo:

            label = tk.Label(
                photo_frame,
                image=photo,
                bg=self.colors["card2"]
            )

            label.image = photo
            label.pack(
                fill="both",
                expand=True
            )

        else:

            tk.Label(
                photo_frame,
                text="🚘",
                bg=self.colors["card2"],
                fg=self.colors["accent"],
                font=("Segoe UI", 40)
            ).pack(
                pady=(20, 2)
            )

            tk.Label(
                photo_frame,
                text=self.t("no_photo"),
                bg=self.colors["card2"],
                fg=self.colors["muted"],
                font=("Segoe UI Semibold", 8)
            ).pack()

        body = tk.Frame(
            card,
            bg=self.colors["card"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=16
        )

        title = (
            car["name"]
            or f"{car['make']} {car['model']}"
            or self.t("cars")
        )

        tk.Label(
            body,
            text=title,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 16)
        ).pack(anchor="w")

        subtitle = " ".join(
            str(x)
            for x in [
                car["make"],
                car["model"],
                car["year"] or ""
            ]
            if x
        )

        tk.Label(
            body,
            text=subtitle,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 12))

        info = tk.Frame(
            body,
            bg=self.colors["card"]
        )

        info.pack(fill="x")

        mileage = (
            f"{self.format_number(car['mileage'])} km"
            if car["mileage"]
            else "—"
        )

        plate = car["plate"] or "—"

        engine = car["engine"] or "—"

        self.card_info(
            info,
            "Mileage",
            mileage
        )

        self.card_info(
            info,
            "Plate",
            plate
        )

        self.card_info(
            info,
            "Engine",
            engine
        )

        buttons = tk.Frame(
            body,
            bg=self.colors["card"]
        )

        buttons.pack(
            fill="x",
            pady=(15, 0)
        )

        tk.Button(
            buttons,
            text=self.t("edit"),
            command=lambda c=car: self.edit_car(c),
            bg=self.colors["card2"],
            fg=self.colors["text"],
            activebackground=self.colors["hover"],
            activeforeground=self.colors["text"],
            bd=0,
            padx=12,
            pady=7,
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            buttons,
            text=self.t("delete"),
            command=lambda cid=car["id"]: self.delete_car(cid),
            bg=self.colors["card2"],
            fg=self.colors["danger"],
            activebackground=self.colors["hover"],
            activeforeground=self.colors["danger"],
            bd=0,
            padx=12,
            pady=7,
            cursor="hand2"
        ).pack(side="right")

    def card_info(self, parent, title, value):

        box = tk.Frame(
            parent,
            bg=self.colors["card"]
        )

        box.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            box,
            text=title,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        tk.Label(
            box,
            text=value,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 9)
        ).pack(anchor="w", pady=(2, 0))

    # --------------------------------------------------------
    # GARAGE
    # --------------------------------------------------------

    def show_garage(self):

        self.clear_main()

        self.page_header(
            self.t("garage"),
            self.t("manage_cars"),
            self.t("add_car"),
            self.add_car
        )

        search_frame = tk.Frame(
            self.main,
            bg=self.colors["bg"]
        )
        search_frame.pack(
            fill="x",
            padx=35,
            pady=(0, 18)
        )

        search_var = tk.StringVar()

        entry = ttk.Entry(
            search_frame,
            textvariable=search_var,
            width=50
        )

        entry.pack(
            side="left",
            ipady=7
        )

        def refresh(*args):
            self.render_garage(
                search_var.get()
            )

        search_var.trace_add(
            "write",
            refresh
        )

        self.garage_container = tk.Frame(
            self.main,
            bg=self.colors["bg"]
        )

        self.garage_container.pack(
            fill="both",
            expand=True,
            padx=28
        )

        self.render_garage("")

    def render_garage(self, search):

        if not hasattr(
            self,
            "garage_container"
        ):
            return

        for widget in self.garage_container.winfo_children():
            widget.destroy()

        search = search.strip()

        if search:

            cars = self.db.all("""
                SELECT * FROM cars
                WHERE
                    name LIKE ?
                    OR make LIKE ?
                    OR model LIKE ?
                    OR vin LIKE ?
                    OR plate LIKE ?
                ORDER BY id DESC
            """, tuple(
                [f"%{search}%"] * 5
            ))

        else:

            cars = self.db.all("""
                SELECT * FROM cars
                ORDER BY id DESC
            """)

        if not cars:

            tk.Label(
                self.garage_container,
                text=self.t("no_cars"),
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                font=("Segoe UI", 12)
            ).pack(pady=60)

            return

        canvas = tk.Canvas(
            self.garage_container,
            bg=self.colors["bg"],
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            self.garage_container,
            orient="vertical",
            command=canvas.yview
        )

        container = tk.Frame(
            canvas,
            bg=self.colors["bg"]
        )

        container.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=container,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        for i, car in enumerate(cars):

            self.vehicle_card(
                container,
                car,
                i % 3,
                i // 3
            )

        for i in range(3):
            container.grid_columnconfigure(
                i,
                weight=1
            )

    # --------------------------------------------------------
    # ADD / EDIT CAR
    # --------------------------------------------------------

    def add_car(self):

        self.car_form()

    def edit_car(self, car):

        self.car_form(car)

    def car_form(self, car=None):

        dialog = tk.Toplevel(self)

        dialog.title(
            self.t("edit")
            if car
            else self.t("add_car")
        )

        dialog.geometry("900x760")
        dialog.minsize(820, 650)

        dialog.configure(
            bg=self.colors["bg"]
        )

        dialog.transient(self)
        dialog.grab_set()

        title = tk.Label(
            dialog,
            text=(
                self.t("edit")
                if car
                else self.t("add_car")
            ),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 22)
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(25, 20)
        )

        content = tk.Frame(
            dialog,
            bg=self.colors["bg"]
        )

        content.pack(
            fill="both",
            expand=True,
            padx=30
        )

        left = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 25)
        )

        right = tk.Frame(
            content,
            bg=self.colors["bg"],
            width=300
        )

        right.pack(
            side="right",
            fill="y"
        )

        right.pack_propagate(False)

        variables = {}

        fields = [
            ("name", self.t("car_name")),
            ("make", self.t("make")),
            ("model", self.t("model")),
            ("year", self.t("year")),
            ("mileage", self.t("mileage")),
            ("vin", self.t("vin")),
            ("plate", self.t("plate")),
            ("color", self.t("color")),
            ("engine", self.t("engine")),
        ]

        for key, label in fields:

            row = tk.Frame(
                left,
                bg=self.colors["bg"]
            )

            row.pack(
                fill="x",
                pady=5
            )

            tk.Label(
                row,
                text=label,
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                width=16,
                anchor="w"
            ).pack(side="left")

            var = tk.StringVar(
                value=(
                    str(car[key])
                    if car and car[key] is not None
                    else ""
                )
            )

            variables[key] = var

            ttk.Entry(
                row,
                textvariable=var
            ).pack(
                side="right",
                fill="x",
                expand=True,
                ipady=5
            )

        combos = [
            (
                "transmission",
                self.t("transmission"),
                [
                    self.t("manual"),
                    self.t("automatic"),
                    self.t("cvt"),
                    self.t("robot"),
                ]
            ),
            (
                "drive",
                self.t("drive"),
                [
                    self.t("fwd"),
                    self.t("rwd"),
                    self.t("awd"),
                ]
            ),
            (
                "fuel",
                self.t("fuel_type"),
                [
                    self.t("petrol"),
                    self.t("diesel"),
                    self.t("hybrid"),
                    self.t("electric"),
                    self.t("gas"),
                ]
            ),
        ]

        for key, label, values in combos:

            row = tk.Frame(
                left,
                bg=self.colors["bg"]
            )

            row.pack(
                fill="x",
                pady=5
            )

            tk.Label(
                row,
                text=label,
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                width=16,
                anchor="w"
            ).pack(side="left")

            var = tk.StringVar(
                value=(
                    str(car[key])
                    if car and car[key]
                    else ""
                )
            )

            variables[key] = var

            ttk.Combobox(
                row,
                textvariable=var,
                values=values,
                state="readonly"
            ).pack(
                side="right",
                fill="x",
                expand=True,
                ipady=4
            )

        row = tk.Frame(
            left,
            bg=self.colors["bg"]
        )

        row.pack(
            fill="both",
            expand=True,
            pady=8
        )

        tk.Label(
            row,
            text=self.t("notes"),
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            width=16,
            anchor="nw"
        ).pack(side="left")

        notes = tk.Text(
            row,
            height=6,
            bg=self.colors["input"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            bd=0,
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            font=("Segoe UI", 10)
        )

        notes.pack(
            side="right",
            fill="both",
            expand=True
        )

        if car and car["notes"]:
            notes.insert(
                "1.0",
                car["notes"]
            )

        # PHOTO
        photo_title = tk.Label(
            right,
            text=self.t("photo"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 13)
        )

        photo_title.pack(
            anchor="w"
        )

        preview = tk.Frame(
            right,
            bg=self.colors["card"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=290,
            height=220
        )

        preview.pack(
            fill="x",
            pady=(12, 10)
        )

        preview.pack_propagate(False)

        current_photo = (
            car["photo"]
            if car and car["photo"]
            else ""
        )

        selected_photo = {
            "path": current_photo,
            "remove": False
        }

        def refresh_preview():

            for widget in preview.winfo_children():
                widget.destroy()

            path = selected_photo["path"]

            photo = self.load_photo(
                path,
                (280, 210)
            )

            if photo:

                label = tk.Label(
                    preview,
                    image=photo,
                    bg=self.colors["card"]
                )

                label.image = photo

                label.pack(
                    fill="both",
                    expand=True
                )

            else:

                tk.Label(
                    preview,
                    text="🚘",
                    bg=self.colors["card"],
                    fg=self.colors["accent"],
                    font=("Segoe UI", 50)
                ).pack(
                    pady=(45, 5)
                )

                tk.Label(
                    preview,
                    text=self.t("no_photo"),
                    bg=self.colors["card"],
                    fg=self.colors["muted"],
                    font=("Segoe UI Semibold", 8)
                ).pack()

        refresh_preview()

        def choose_photo():

            filename = filedialog.askopenfilename(
                parent=dialog,
                title=self.t("choose_photo"),
                filetypes=[
                    (
                        "Images",
                        "*.jpg *.jpeg *.png *.webp"
                    ),
                    (
                        "JPEG",
                        "*.jpg *.jpeg"
                    ),
                    (
                        "PNG",
                        "*.png"
                    ),
                    (
                        "WEBP",
                        "*.webp"
                    ),
                ]
            )

            if filename:

                selected_photo["path"] = filename
                selected_photo["remove"] = False

                refresh_preview()

        def remove_photo():

            selected_photo["path"] = ""
            selected_photo["remove"] = True

            refresh_preview()

        tk.Button(
            right,
            text=self.t("choose_photo"),
            command=choose_photo,
            bg=self.colors["accent"],
            fg="white",
            activebackground=self.colors["accent2"],
            activeforeground="white",
            bd=0,
            padx=12,
            pady=9,
            cursor="hand2"
        ).pack(
            fill="x",
            pady=3
        )

        tk.Button(
            right,
            text=self.t("remove_photo"),
            command=remove_photo,
            bg=self.colors["card2"],
            fg=self.colors["danger"],
            activebackground=self.colors["hover"],
            activeforeground=self.colors["danger"],
            bd=0,
            padx=12,
            pady=9,
            cursor="hand2"
        ).pack(
            fill="x",
            pady=3
        )

        tk.Label(
            right,
            text=self.t("photo_hint"),
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            pady=(6, 0)
        )

        buttons = tk.Frame(
            dialog,
            bg=self.colors["bg"]
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=20
        )

        def save():

            name = variables["name"].get().strip()

            if not name:

                messagebox.showwarning(
                    self.t("error"),
                    self.t("required_name"),
                    parent=dialog
                )

                return

            year_text = variables["year"].get().strip()

            if year_text:

                try:
                    year = int(year_text)
                except ValueError:

                    messagebox.showwarning(
                        self.t("error"),
                        self.t("invalid_year"),
                        parent=dialog
                    )

                    return

            else:
                year = 0

            mileage_text = (
                variables["mileage"]
                .get()
                .strip()
            )

            if mileage_text:

                try:
                    mileage = int(
                        mileage_text.replace(" ", "")
                    )
                except ValueError:

                    messagebox.showwarning(
                        self.t("error"),
                        self.t("invalid_mileage"),
                        parent=dialog
                    )

                    return

            else:
                mileage = 0

            data = {
                key: variables[key].get().strip()
                for key, _ in fields
                if key in variables
            }

            data["year"] = year
            data["mileage"] = mileage
            data["notes"] = notes.get(
                "1.0",
                "end"
            ).strip()

            now = datetime.now().isoformat(
                timespec="seconds"
            )

            if car:

                self.db.execute("""
                    UPDATE cars SET
                        name=?,
                        make=?,
                        model=?,
                        year=?,
                        mileage=?,
                        vin=?,
                        plate=?,
                        color=?,
                        engine=?,
                        transmission=?,
                        drive=?,
                        fuel=?,
                        notes=?
                    WHERE id=?
                """, (
                    data["name"],
                    data["make"],
                    data["model"],
                    data["year"],
                    data["mileage"],
                    data["vin"],
                    data["plate"],
                    data["color"],
                    data["engine"],
                    variables["transmission"].get(),
                    variables["drive"].get(),
                    variables["fuel"].get(),
                    data["notes"],
                    car["id"]
                ))

                car_id = car["id"]

            else:

                cursor = self.db.execute("""
                    INSERT INTO cars (
                        name,
                        make,
                        model,
                        year,
                        mileage,
                        vin,
                        plate,
                        color,
                        engine,
                        transmission,
                        drive,
                        fuel,
                        notes,
                        photo,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["name"],
                    data["make"],
                    data["model"],
                    data["year"],
                    data["mileage"],
                    data["vin"],
                    data["plate"],
                    data["color"],
                    data["engine"],
                    variables["transmission"].get(),
                    variables["drive"].get(),
                    variables["fuel"].get(),
                    data["notes"],
                    "",
                    now
                ))

                car_id = cursor.lastrowid

            # PHOTO
            selected = selected_photo["path"]

            if selected_photo["remove"]:

                self.delete_car_photo(
                    car_id
                )

                self.db.execute(
                    "UPDATE cars SET photo='' WHERE id=?",
                    (car_id,)
                )

            elif selected:

                # If the selected file is already our stored file,
                # don't copy it unnecessarily.
                if Path(selected).resolve() != (
                    PHOTOS_DIR / f"car_{car_id}.jpg"
                ).resolve():

                    saved_photo = self.copy_photo(
                        selected,
                        car_id
                    )

                    if saved_photo:

                        self.db.execute(
                            "UPDATE cars SET photo=? WHERE id=?",
                            (
                                saved_photo,
                                car_id
                            )
                        )

            messagebox.showinfo(
                self.t("saved"),
                self.t("saved"),
                parent=dialog
            )

            dialog.destroy()

            if self.current_page == "garage":
                self.show_garage()
            else:
                self.show_dashboard()

        tk.Button(
            buttons,
            text=self.t("cancel"),
            command=dialog.destroy,
            bg=self.colors["card2"],
            fg=self.colors["text"],
            activebackground=self.colors["hover"],
            activeforeground=self.colors["text"],
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(
            side="right",
            padx=(8, 0)
        )

        tk.Button(
            buttons,
            text=self.t("save"),
            command=save,
            bg=self.colors["accent"],
            fg="white",
            activebackground=self.colors["accent2"],
            activeforeground="white",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2"
        ).pack(
            side="right"
        )

    # --------------------------------------------------------
    # DELETE CAR
    # --------------------------------------------------------

    def delete_car(self, car_id):

        result = messagebox.askyesno(
            self.t("confirm_delete"),
            self.t("delete_confirm")
            + "\n\n"
            + self.t("delete_warning")
        )

        if not result:
            return

        self.delete_car_photo(
            car_id
        )

        self.db.execute(
            "DELETE FROM cars WHERE id=?",
            (car_id,)
        )

        messagebox.showinfo(
            self.t("deleted"),
            self.t("deleted")
        )

        if self.current_page == "garage":
            self.show_garage()
        else:
            self.show_dashboard()

    # --------------------------------------------------------
    # RECORDS
    # --------------------------------------------------------

    def show_records(self, record_type):

        self.clear_main()

        titles = {
            "service": self.t("service"),
            "fuel": self.t("fuel"),
            "expenses": self.t("expenses"),
            "reminders": self.t("reminders"),
        }

        self.page_header(
            titles[record_type],
            "",
            self.t("add"),
            lambda: self.add_record(record_type)
        )

        frame = tk.Frame(
            self.main,
            bg=self.colors["bg"]
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 25)
        )

        columns = {
            "service": (
                ("id", "#", 50),
                ("car", self.t("select_car"), 180),
                ("title", self.t("service_title"), 220),
                ("category", self.t("category"), 150),
                ("mileage", self.t("mileage"), 120),
                ("cost", self.t("cost"), 120),
                ("date", self.t("date"), 120),
            ),

            "fuel": (
                ("id", "#", 50),
                ("car", self.t("select_car"), 180),
                ("liters", self.t("liters"), 120),
                ("price", self.t("price"), 120),
                ("mileage", self.t("mileage"), 120),
                ("date", self.t("date"), 120),
                ("station", self.t("station"), 180),
            ),

            "expenses": (
                ("id", "#", 50),
                ("car", self.t("select_car"), 180),
                ("title", self.t("expense_title"), 220),
                ("category", self.t("category"), 150),
                ("amount", self.t("amount"), 120),
                ("date", self.t("date"), 120),
            ),

            "reminders": (
                ("id", "#", 50),
                ("car", self.t("select_car"), 180),
                ("title", self.t("expense_title"), 240),
                ("due_date", self.t("due_date"), 140),
                ("due_mileage", self.t("due_mileage"), 140),
                ("done", self.t("done"), 120),
            ),
        }

        tree = ttk.Treeview(
            frame,
            columns=[
                x[0]
                for x in columns[record_type]
            ],
            show="headings"
        )

        for key, label, width in columns[record_type]:

            tree.heading(
                key,
                text=label
            )

            tree.column(
                key,
                width=width,
                anchor="w"
            )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.populate_records(
            tree,
            record_type
        )

        tree.bind(
            "<Double-1>",
            lambda e: self.edit_selected_record(
                tree,
                record_type
            )
        )

    def populate_records(
        self,
        tree,
        record_type
    ):

        for item in tree.get_children():
            tree.delete(item)

        if record_type == "service":

            rows = self.db.all("""
                SELECT
                    service.id,
                    COALESCE(c.name, '') AS car,
                    service.title,
                    service.category,
                    service.mileage,
                    service.cost,
                    service.date
                FROM service
                LEFT JOIN cars c
                    ON c.id = service.car_id
                ORDER BY service.id DESC
            """)

            for row in rows:
                tree.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(
                        row["id"],
                        row["car"],
                        row["title"],
                        row["category"],
                        row["mileage"],
                        f"{row['cost']:,.2f}",
                        row["date"],
                    )
                )

        elif record_type == "fuel":

            rows = self.db.all("""
                SELECT
                    fuel.id,
                    COALESCE(c.name, '') AS car,
                    fuel.liters,
                    fuel.price,
                    fuel.mileage,
                    fuel.date,
                    fuel.station
                FROM fuel
                LEFT JOIN cars c
                    ON c.id = fuel.car_id
                ORDER BY fuel.id DESC
            """)

            for row in rows:
                tree.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(
                        row["id"],
                        row["car"],
                        row["liters"],
                        f"{row['price']:,.2f}",
                        row["mileage"],
                        row["date"],
                        row["station"],
                    )
                )

        elif record_type == "expenses":

            rows = self.db.all("""
                SELECT
                    expenses.id,
                    COALESCE(c.name, '') AS car,
                    expenses.title,
                    expenses.category,
                    expenses.amount,
                    expenses.date
                FROM expenses
                LEFT JOIN cars c
                    ON c.id = expenses.car_id
                ORDER BY expenses.id DESC
            """)

            for row in rows:
                tree.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(
                        row["id"],
                        row["car"],
                        row["title"],
                        row["category"],
                        f"{row['amount']:,.2f}",
                        row["date"],
                    )
                )

        elif record_type == "reminders":

            rows = self.db.all("""
                SELECT
                    reminders.id,
                    COALESCE(c.name, '') AS car,
                    reminders.title,
                    reminders.due_date,
                    reminders.due_mileage,
                    reminders.done
                FROM reminders
                LEFT JOIN cars c
                    ON c.id = reminders.car_id
                ORDER BY reminders.id DESC
            """)

            for row in rows:
                tree.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(
                        row["id"],
                        row["car"],
                        row["title"],
                        row["due_date"],
                        row["due_mileage"],
                        self.t("done")
                        if row["done"]
                        else "—"
                    )
                )

    # --------------------------------------------------------
    # RECORD FORM
    # --------------------------------------------------------

    def add_record(self, record_type):

        self.record_form(
            record_type
        )

    def edit_selected_record(
        self,
        tree,
        record_type
    ):

        selected = tree.selection()

        if not selected:
            return

        record_id = int(
            selected[0]
        )

        row = self.db.one(
            f"SELECT * FROM {record_type} WHERE id=?",
            (record_id,)
        )

        if row:
            self.record_form(
                record_type,
                row
            )

    def record_form(
        self,
        record_type,
        record=None
    ):

        dialog = tk.Toplevel(self)

        dialog.title(
            self.t("edit")
            if record
            else self.t("add")
        )

        dialog.geometry(
            "620x600"
        )

        dialog.configure(
            bg=self.colors["bg"]
        )

        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=(
                self.t("edit")
                if record
                else self.t("add")
            ),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 21)
        ).pack(
            anchor="w",
            padx=30,
            pady=(25, 20)
        )

        form = tk.Frame(
            dialog,
            bg=self.colors["bg"]
        )

        form.pack(
            fill="both",
            expand=True,
            padx=30
        )

        cars = self.db.all(
            "SELECT id, name, make, model FROM cars ORDER BY id DESC"
        )

        car_values = []

        car_map = {}

        for car in cars:

            name = (
                car["name"]
                or f"{car['make']} {car['model']}"
            )

            car_values.append(name)
            car_map[name] = car["id"]

        variables = {}

        def add_entry(
            key,
            label,
            value=""
        ):

            row = tk.Frame(
                form,
                bg=self.colors["bg"]
            )

            row.pack(
                fill="x",
                pady=7
            )

            tk.Label(
                row,
                text=label,
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                width=18,
                anchor="w"
            ).pack(side="left")

            var = tk.StringVar(
                value=str(value or "")
            )

            variables[key] = var

            ttk.Entry(
                row,
                textvariable=var
            ).pack(
                side="right",
                fill="x",
                expand=True,
                ipady=5
            )

        current_car_id = (
            record["car_id"]
            if record
            else None
        )

        current_car_name = ""

        for car in cars:

            if car["id"] == current_car_id:
                current_car_name = (
                    car["name"]
                    or f"{car['make']} {car['model']}"
                )

        row = tk.Frame(
            form,
            bg=self.colors["bg"]
        )

        row.pack(
            fill="x",
            pady=7
        )

        tk.Label(
            row,
            text=self.t("select_car"),
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            width=18,
            anchor="w"
        ).pack(side="left")

        car_var = tk.StringVar(
            value=current_car_name
        )

        variables["car_id"] = car_var

        ttk.Combobox(
            row,
            textvariable=car_var,
            values=car_values,
            state="readonly"
        ).pack(
            side="right",
            fill="x",
            expand=True,
            ipady=4
        )

        if record_type == "service":

            add_entry(
                "title",
                self.t("service_title"),
                record["title"] if record else ""
            )

            add_entry(
                "category",
                self.t("category"),
                record["category"] if record else ""
            )

            add_entry(
                "mileage",
                self.t("mileage"),
                record["mileage"] if record else ""
            )

            add_entry(
                "cost",
                self.t("cost"),
                record["cost"] if record else ""
            )

            add_entry(
                "date",
                self.t("date"),
                record["date"]
                if record
                else date.today().isoformat()
            )

        elif record_type == "fuel":

            add_entry(
                "liters",
                self.t("liters"),
                record["liters"] if record else ""
            )

            add_entry(
                "price",
                self.t("price"),
                record["price"] if record else ""
            )

            add_entry(
                "mileage",
                self.t("mileage"),
                record["mileage"] if record else ""
            )

            add_entry(
                "date",
                self.t("date"),
                record["date"]
                if record
                else date.today().isoformat()
            )

            add_entry(
                "station",
                self.t("station"),
                record["station"] if record else ""
            )

        elif record_type == "expenses":

            add_entry(
                "title",
                self.t("expense_title"),
                record["title"] if record else ""
            )

            add_entry(
                "category",
                self.t("category"),
                record["category"] if record else ""
            )

            add_entry(
                "amount",
                self.t("amount"),
                record["amount"] if record else ""
            )

            add_entry(
                "date",
                self.t("date"),
                record["date"]
                if record
                else date.today().isoformat()
            )

        elif record_type == "reminders":

            add_entry(
                "title",
                self.t("expense_title"),
                record["title"] if record else ""
            )

            add_entry(
                "due_date",
                self.t("due_date"),
                record["due_date"] if record else ""
            )

            add_entry(
                "due_mileage",
                self.t("due_mileage"),
                record["due_mileage"] if record else ""
            )

        buttons = tk.Frame(
            dialog,
            bg=self.colors["bg"]
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=20
        )

        def save():

            car_name = variables[
                "car_id"
            ].get()

            car_id = car_map.get(
                car_name
            )

            if not car_id:
                car_id = 0

            if record_type == "service":

                values = (
                    car_id,
                    variables["title"].get(),
                    variables["category"].get(),
                    self.safe_int(
                        variables["mileage"].get()
                    ),
                    self.safe_float(
                        variables["cost"].get()
                    ),
                    variables["date"].get(),
                    "",
                )

                if record:

                    self.db.execute("""
                        UPDATE service
                        SET car_id=?,
                            title=?,
                            category=?,
                            mileage=?,
                            cost=?,
                            date=?,
                            notes=?
                        WHERE id=?
                    """, values + (
                        record["id"],
                    ))

                else:

                    self.db.execute("""
                        INSERT INTO service
                        (
                            car_id,
                            title,
                            category,
                            mileage,
                            cost,
                            date,
                            notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, values)

            elif record_type == "fuel":

                values = (
                    car_id,
                    self.safe_float(
                        variables["liters"].get()
                    ),
                    self.safe_float(
                        variables["price"].get()
                    ),
                    self.safe_int(
                        variables["mileage"].get()
                    ),
                    variables["date"].get(),
                    variables["station"].get(),
                )

                if record:

                    self.db.execute("""
                        UPDATE fuel
                        SET car_id=?,
                            liters=?,
                            price=?,
                            mileage=?,
                            date=?,
                            station=?
                        WHERE id=?
                    """, values + (
                        record["id"],
                    ))

                else:

                    self.db.execute("""
                        INSERT INTO fuel
                        (
                            car_id,
                            liters,
                            price,
                            mileage,
                            date,
                            station
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, values)

            elif record_type == "expenses":

                values = (
                    car_id,
                    variables["title"].get(),
                    variables["category"].get(),
                    self.safe_float(
                        variables["amount"].get()
                    ),
                    variables["date"].get(),
                    "",
                )

                if record:

                    self.db.execute("""
                        UPDATE expenses
                        SET car_id=?,
                            title=?,
                            category=?,
                            amount=?,
                            date=?,
                            notes=?
                        WHERE id=?
                    """, values + (
                        record["id"],
                    ))

                else:

                    self.db.execute("""
                        INSERT INTO expenses
                        (
                            car_id,
                            title,
                            category,
                            amount,
                            date,
                            notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, values)

            elif record_type == "reminders":

                values = (
                    car_id,
                    variables["title"].get(),
                    variables["due_date"].get(),
                    self.safe_int(
                        variables["due_mileage"].get()
                    ),
                    0,
                    "",
                )

                if record:

                    self.db.execute("""
                        UPDATE reminders
                        SET car_id=?,
                            title=?,
                            due_date=?,
                            due_mileage=?,
                            done=?,
                            notes=?
                        WHERE id=?
                    """, values + (
                        record["id"],
                    ))

                else:

                    self.db.execute("""
                        INSERT INTO reminders
                        (
                            car_id,
                            title,
                            due_date,
                            due_mileage,
                            done,
                            notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, values)

            dialog.destroy()

            self.show_records(
                record_type
            )

        tk.Button(
            buttons,
            text=self.t("cancel"),
            command=dialog.destroy,
            bg=self.colors["card2"],
            fg=self.colors["text"],
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(
            side="right",
            padx=5
        )

        tk.Button(
            buttons,
            text=self.t("save"),
            command=save,
            bg=self.colors["accent"],
            fg="white",
            activebackground=self.colors["accent2"],
            bd=0,
            padx=25,
            pady=9,
            cursor="hand2"
        ).pack(
            side="right"
        )

    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    def show_settings(self):

        self.clear_main()

        self.page_header(
            self.t("settings"),
            ""
        )

        content = tk.Frame(
            self.main,
            bg=self.colors["bg"]
        )

        content.pack(
            fill="both",
            expand=True,
            padx=35
        )

        language_card = self.card(
            content
        )

        language_card.pack(
            fill="x",
            pady=8
        )

        tk.Label(
            language_card,
            text=self.t("language"),
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 15)
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 8)
        )

        tk.Label(
            language_card,
            text="Русский / English",
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(
            anchor="w",
            padx=20
        )

        lang_var = tk.StringVar(
            value=self.language
        )

        combo = ttk.Combobox(
            language_card,
            textvariable=lang_var,
            values=["ru", "en"],
            state="readonly",
            width=20
        )

        combo.pack(
            anchor="w",
            padx=20,
            pady=15
        )

        def change_language(event=None):

            value = lang_var.get()

            if value not in (
                "ru",
                "en"
            ):
                return

            self.language = value
            self.save_settings()

            self.build_interface()

            self.navigate(
                self.current_page
            )

        combo.bind(
            "<<ComboboxSelected>>",
            change_language
        )

        theme_card = self.card(
            content
        )

        theme_card.pack(
            fill="x",
            pady=8
        )

        tk.Label(
            theme_card,
            text=self.t("theme"),
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 15)
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 8)
        )

        theme_var = tk.StringVar(
            value=self.theme
        )

        theme_combo = ttk.Combobox(
            theme_card,
            textvariable=theme_var,
            values=[
                "dark",
                "light"
            ],
            state="readonly",
            width=20
        )

        theme_combo.pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        def change_theme(event=None):

            self.theme = theme_var.get()
            self.save_settings()

            self.configure_theme()
            self.build_interface()
            self.navigate(
                self.current_page
            )

        theme_combo.bind(
            "<<ComboboxSelected>>",
            change_theme
        )

        tools_card = self.card(
            content
        )

        tools_card.pack(
            fill="x",
            pady=8
        )

        tk.Button(
            tools_card,
            text=self.t("export_csv"),
            command=self.export_csv,
            bg=self.colors["card2"],
            fg=self.colors["text"],
            activebackground=self.colors["hover"],
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(
            side="left",
            padx=20,
            pady=20
        )

        tk.Button(
            tools_card,
            text=self.t("open_folder"),
            command=self.open_data_folder,
            bg=self.colors["card2"],
            fg=self.colors["text"],
            activebackground=self.colors["hover"],
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(
            side="left",
            padx=0,
            pady=20
        )

    # --------------------------------------------------------
    # ABOUT
    # --------------------------------------------------------

    def show_about(self):

        self.clear_main()

        self.page_header(
            self.t("about")
        )

        card = self.card(
            self.main
        )

        card.pack(
            fill="x",
            padx=35,
            pady=10
        )

        tk.Label(
            card,
            text="CAR MANAGER",
            bg=self.colors["card"],
            fg=self.colors["accent"],
            font=("Segoe UI Black", 28)
        ).pack(
            pady=(35, 5)
        )

        tk.Label(
            card,
            text=f"Version {VERSION}",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack()

        tk.Label(
            card,
            text=self.t("about_text"),
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI", 11),
            justify="center"
        ).pack(
            pady=25
        )

        tk.Button(
            card,
            text=self.t("telegram"),
            command=lambda: webbrowser.open(
                TELEGRAM_URL
            ),
            bg=self.colors["accent"],
            fg="white",
            activebackground=self.colors["accent2"],
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2"
        ).pack(
            pady=(0, 35)
        )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    def export_csv(self):

        filename = filedialog.asksaveasfilename(
            title=self.t("export_csv"),
            defaultextension=".csv",
            filetypes=[
                (
                    "CSV",
                    "*.csv"
                )
            ]
        )

        if not filename:
            return

        try:

            cars = self.db.all(
                "SELECT * FROM cars"
            )

            with open(
                filename,
                "w",
                encoding="utf-8-sig",
                newline=""
            ) as file:

                writer = csv.writer(
                    file
                )

                if cars:

                    writer.writerow(
                        cars[0].keys()
                    )

                    for car in cars:
                        writer.writerow(
                            list(car)
                        )

            messagebox.showinfo(
                "CSV",
                "CSV exported successfully."
                if self.language == "en"
                else "CSV успешно экспортирован."
            )

        except Exception as error:

            messagebox.showerror(
                self.t("error"),
                str(error)
            )

    # --------------------------------------------------------
    # DATA FOLDER
    # --------------------------------------------------------

    def open_data_folder(self):

        try:

            if os.name == "nt":
                os.startfile(
                    APP_DIR
                )
            else:
                webbrowser.open(
                    APP_DIR.as_uri()
                )

        except Exception:

            webbrowser.open(
                APP_DIR.as_uri()
            )

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    def on_close(self):

        self.save_settings()
        self.db.close()
        self.destroy()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app = CarManager()
    app.mainloop()
