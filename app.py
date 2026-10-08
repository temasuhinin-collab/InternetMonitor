import csv
import shutil
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import date, datetime
import webbrowser


# ============================================================
# CAR MANAGER 3.1
# Developed by Artem Sukhinin
# Telegram: https://t.me/artem_sukhinin
# ============================================================

APP_NAME = "Car Manager"
VERSION = "3.1.0"
AUTHOR = "Artem Sukhinin"
TELEGRAM_URL = "https://t.me/artem_sukhinin"

DB_FILE = Path.home() / "CarManager.db"
BACKUP_DIR = Path.home() / "CarManagerBackups"


# ============================================================
# THEMES
# ============================================================

THEMES = {
    "dark": {
        "bg": "#07111F",
        "surface": "#0D1929",
        "surface2": "#132238",
        "surface3": "#172A43",
        "border": "#223A59",
        "text": "#F5F8FC",
        "muted": "#879AB3",
        "accent": "#4DA3FF",
        "accent2": "#725CFF",
        "success": "#35D39A",
        "warning": "#FFB95E",
        "danger": "#FF5F76",
        "input": "#091625",
    },
    "light": {
        "bg": "#F3F6FA",
        "surface": "#FFFFFF",
        "surface2": "#EEF3F9",
        "surface3": "#E5ECF5",
        "border": "#D7E0EB",
        "text": "#162236",
        "muted": "#6D7C91",
        "accent": "#277FEA",
        "accent2": "#6757E8",
        "success": "#159A70",
        "warning": "#D78B19",
        "danger": "#E45068",
        "input": "#F8FAFC",
    },
}


# ============================================================
# DATABASE
# ============================================================

class Database:

    SCHEMA_VERSION = 4

    def __init__(self):

        self.connection = sqlite3.connect(
            DB_FILE,
            timeout=10
        )

        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        self.connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        self.initialize()

    # --------------------------------------------------------
    # INITIALIZE
    # --------------------------------------------------------

    def initialize(self):

        self.create_base_tables()
        self.migrate_database()

    # --------------------------------------------------------
    # BASE TABLES
    # --------------------------------------------------------

    def create_base_tables(self):

        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            make TEXT,
            model TEXT,
            year INTEGER,
            mileage INTEGER DEFAULT 0,
            vin TEXT,
            plate TEXT,
            color TEXT,
            engine TEXT,
            transmission TEXT,
            drive TEXT,
            fuel TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS service (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            title TEXT,
            category TEXT,
            mileage INTEGER DEFAULT 0,
            cost REAL DEFAULT 0,
            date TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS fuel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            liters REAL DEFAULT 0,
            price REAL DEFAULT 0,
            mileage INTEGER DEFAULT 0,
            date TEXT,
            station TEXT
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            title TEXT,
            category TEXT,
            amount REAL DEFAULT 0,
            date TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            title TEXT,
            due_date TEXT,
            due_mileage INTEGER DEFAULT 0,
            done INTEGER DEFAULT 0,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS database_info (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            version INTEGER NOT NULL DEFAULT 1
        );
        """)

        self.connection.commit()

    # --------------------------------------------------------
    # BACKUP
    # --------------------------------------------------------

    def create_backup(self):

        if not DB_FILE.exists():
            return None

        try:

            BACKUP_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            backup = (
                BACKUP_DIR /
                f"CarManager_backup_{timestamp}.db"
            )

            self.connection.commit()

            shutil.copy2(
                DB_FILE,
                backup
            )

            return backup

        except Exception as error:

            print(
                f"[DATABASE] Backup error: {error}"
            )

            return None

    # --------------------------------------------------------
    # COLUMNS
    # --------------------------------------------------------

    def get_columns(self, table):

        rows = self.connection.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()

        return {
            row["name"]
            for row in rows
        }

    # --------------------------------------------------------
    # ADD COLUMN
    # --------------------------------------------------------

    def ensure_column(
        self,
        table,
        column,
        definition
    ):

        columns = self.get_columns(table)

        if column in columns:
            return False

        try:

            self.connection.execute(
                f"""
                ALTER TABLE {table}
                ADD COLUMN {column} {definition}
                """
            )

            return True

        except sqlite3.OperationalError as error:

            print(
                f"[DATABASE] "
                f"Cannot add {table}.{column}: {error}"
            )

            return False

    # --------------------------------------------------------
    # MIGRATION
    # --------------------------------------------------------

    def migrate_database(self):

        try:

            # Backup BEFORE modifications.
            current_version_row = self.connection.execute(
                """
                SELECT version
                FROM database_info
                WHERE id=1
                """
            ).fetchone()

            current_version = (
                current_version_row["version"]
                if current_version_row
                else 0
            )

            # Only create a backup for existing databases.
            if DB_FILE.exists() and current_version < self.SCHEMA_VERSION:
                backup = self.create_backup()

                if backup:
                    print(
                        f"[DATABASE] Backup created: {backup}"
                    )

            # =================================================
            # CARS
            # =================================================

            cars = {
                "name": "TEXT",
                "make": "TEXT",
                "model": "TEXT",
                "year": "INTEGER",
                "mileage": "INTEGER DEFAULT 0",
                "vin": "TEXT",
                "plate": "TEXT",
                "color": "TEXT",
                "engine": "TEXT",
                "transmission": "TEXT",
                "drive": "TEXT",
                "fuel": "TEXT",
                "notes": "TEXT",
                "created_at": "TEXT"
            }

            for column, definition in cars.items():

                self.ensure_column(
                    "cars",
                    column,
                    definition
                )

            # =================================================
            # SERVICE
            # =================================================

            service = {
                "car_id": "INTEGER",
                "title": "TEXT",
                "category": "TEXT",
                "mileage": "INTEGER DEFAULT 0",
                "cost": "REAL DEFAULT 0",
                "date": "TEXT",
                "notes": "TEXT"
            }

            for column, definition in service.items():

                self.ensure_column(
                    "service",
                    column,
                    definition
                )

            # =================================================
            # FUEL
            # =================================================

            fuel = {
                "car_id": "INTEGER",
                "liters": "REAL DEFAULT 0",
                "price": "REAL DEFAULT 0",
                "mileage": "INTEGER DEFAULT 0",
                "date": "TEXT",
                "station": "TEXT"
            }

            for column, definition in fuel.items():

                self.ensure_column(
                    "fuel",
                    column,
                    definition
                )

            # =================================================
            # EXPENSES
            # =================================================

            expenses = {
                "car_id": "INTEGER",
                "title": "TEXT",
                "category": "TEXT",
                "amount": "REAL DEFAULT 0",
                "date": "TEXT",
                "notes": "TEXT"
            }

            for column, definition in expenses.items():

                self.ensure_column(
                    "expenses",
                    column,
                    definition
                )

            # =================================================
            # REMINDERS
            # =================================================

            reminders = {
                "car_id": "INTEGER",
                "title": "TEXT",
                "due_date": "TEXT",
                "due_mileage": "INTEGER DEFAULT 0",
                "done": "INTEGER DEFAULT 0",
                "notes": "TEXT"
            }

            for column, definition in reminders.items():

                self.ensure_column(
                    "reminders",
                    column,
                    definition
                )

            # =================================================
            # NORMALIZE NULL VALUES
            # =================================================

            self.connection.execute(
                """
                UPDATE cars
                SET mileage=0
                WHERE mileage IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE service
                SET mileage=0
                WHERE mileage IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE service
                SET cost=0
                WHERE cost IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE fuel
                SET liters=0
                WHERE liters IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE fuel
                SET price=0
                WHERE price IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE fuel
                SET mileage=0
                WHERE mileage IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE expenses
                SET amount=0
                WHERE amount IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE reminders
                SET done=0
                WHERE done IS NULL
                """
            )

            self.connection.execute(
                """
                UPDATE reminders
                SET due_mileage=0
                WHERE due_mileage IS NULL
                """
            )

            # =================================================
            # DATABASE VERSION
            # =================================================

            self.connection.execute(
                """
                INSERT INTO database_info
                (id, version)
                VALUES (1, ?)
                ON CONFLICT(id)
                DO UPDATE SET version=excluded.version
                """,
                (self.SCHEMA_VERSION,)
            )

            self.connection.commit()

            print(
                f"[DATABASE] Schema version: "
                f"{self.SCHEMA_VERSION}"
            )

        except Exception:

            self.connection.rollback()

            raise

    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    def execute(
        self,
        query,
        params=(),
        fetch=False
    ):

        cursor = self.connection.execute(
            query,
            params
        )

        self.connection.commit()

        if fetch:
            return cursor.fetchall()

        return cursor

    # --------------------------------------------------------
    # ONE
    # --------------------------------------------------------

    def one(
        self,
        query,
        params=()
    ):

        return self.connection.execute(
            query,
            params
        ).fetchone()

    # --------------------------------------------------------
    # SCALAR
    # --------------------------------------------------------

    def scalar(
        self,
        query,
        params=()
    ):

        row = self.one(
            query,
            params
        )

        if row is None:
            return 0

        try:

            value = row[0]

            return 0 if value is None else value

        except Exception:

            return 0

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    def close(self):

        try:
            self.connection.close()
        except Exception:
            pass


# ============================================================
# APPLICATION
# ============================================================

class CarManager(tk.Tk):

    def __init__(self):

        super().__init__()

        self.theme_name = "dark"
        self.colors = THEMES[self.theme_name]

        try:

            self.database = Database()

        except Exception as error:

            messagebox.showerror(
                "Car Manager — Database error",
                (
                    "Не удалось открыть базу данных.\n\n"
                    f"{error}\n\n"
                    f"Файл:\n{DB_FILE}"
                )
            )

            self.destroy()

            raise

        self.title(
            f"{APP_NAME} {VERSION}"
        )

        self.geometry(
            "1380x850"
        )

        self.minsize(
            1100,
            700
        )

        self.configure(
            bg=self.c("bg")
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        self.style = ttk.Style(self)

        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.configure_styles()

        self.build_menu()
        self.build_interface()

        self.show_dashboard()

    # ========================================================
    # COLORS
    # ========================================================

    def c(self, key):
        return self.colors[key]

    # ========================================================
    # STYLES
    # ========================================================

    def configure_styles(self):

        self.style.configure(
            "TCombobox",
            fieldbackground=self.c("input"),
            background=self.c("input"),
            foreground=self.c("text"),
            borderwidth=0
        )

    # ========================================================
    # FORMAT
    # ========================================================

    def money(self, value):

        try:

            return (
                f"₽ {float(value):,.0f}"
                .replace(",", " ")
            )

        except Exception:

            return "₽ 0"

    def number(self, value):

        try:

            return f"{int(float(value)):,}".replace(
                ",",
                " "
            )

        except Exception:

            return "0"

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_content(self):

        if not hasattr(self, "content"):
            return

        for widget in self.content.winfo_children():
            widget.destroy()

    # ========================================================
    # MENU
    # ========================================================

    def build_menu(self):

        menu = tk.Menu(
            self
        )

        file_menu = tk.Menu(
            menu,
            tearoff=0
        )

        file_menu.add_command(
            label="Export all data to CSV",
            command=self.export_all
        )

        file_menu.add_command(
            label="Open database folder",
            command=self.open_database_folder
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit",
            command=self.on_close
        )

        menu.add_cascade(
            label="File",
            menu=file_menu
        )

        theme_menu = tk.Menu(
            menu,
            tearoff=0
        )

        theme_menu.add_command(
            label="Dark",
            command=lambda: self.set_theme("dark")
        )

        theme_menu.add_command(
            label="Light",
            command=lambda: self.set_theme("light")
        )

        menu.add_cascade(
            label="Theme",
            menu=theme_menu
        )

        help_menu = tk.Menu(
            menu,
            tearoff=0
        )

        help_menu.add_command(
            label="About",
            command=self.show_about
        )

        menu.add_cascade(
            label="Help",
            menu=help_menu
        )

        self.config(
            menu=menu
        )

    # ========================================================
    # MAIN INTERFACE
    # ========================================================

    def build_interface(self):

        self.sidebar = tk.Frame(
            self,
            bg=self.c("surface"),
            width=245
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.build_sidebar()

        self.main = tk.Frame(
            self,
            bg=self.c("bg")
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.header = tk.Frame(
            self.main,
            bg=self.c("bg"),
            height=75
        )

        self.header.pack(
            fill="x",
            padx=30,
            pady=(20, 0)
        )

        self.header.pack_propagate(False)

        self.page_title = tk.Label(
            self.header,
            text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            fg=self.c("text"),
            bg=self.c("bg")
        )

        self.page_title.pack(
            side="left",
            anchor="center"
        )

        self.search_entry = tk.Entry(
            self.header,
            relief="flat",
            bg=self.c("surface"),
            fg=self.c("muted"),
            insertbackground=self.c("text"),
            font=("Segoe UI", 10)
        )

        self.search_entry.insert(
            0,
            "Search garage..."
        )

        self.search_entry.pack(
            side="right",
            ipadx=14,
            ipady=10
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.show_garage()
        )

        self.content = tk.Frame(
            self.main,
            bg=self.c("bg")
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

    # ========================================================
    # SIDEBAR
    # ========================================================

    def build_sidebar(self):

        brand = tk.Frame(
            self.sidebar,
            bg=self.c("surface")
        )

        brand.pack(
            fill="x",
            padx=20,
            pady=(25, 30)
        )

        tk.Label(
            brand,
            text="CM",
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg=self.c("accent"),
            padx=12,
            pady=8
        ).pack(side="left")

        info = tk.Frame(
            brand,
            bg=self.c("surface")
        )

        info.pack(
            side="left",
            padx=10
        )

        tk.Label(
            info,
            text="CAR MANAGER",
            font=("Segoe UI", 12, "bold"),
            fg=self.c("text"),
            bg=self.c("surface")
        ).pack(anchor="w")

        tk.Label(
            info,
            text="VERSION 3.1",
            font=("Segoe UI", 8, "bold"),
            fg=self.c("accent"),
            bg=self.c("surface")
        ).pack(anchor="w")

        navigation = [
            ("⌂   Dashboard", self.show_dashboard),
            ("🚗   Garage", self.show_garage),
            ("🔧   Service", self.show_service),
            ("⛽   Fuel", self.show_fuel),
            ("💳   Expenses", self.show_expenses),
            ("◷   Reminders", self.show_reminders),
        ]

        for text, command in navigation:

            tk.Button(
                self.sidebar,
                text=text,
                command=command,
                relief="flat",
                bd=0,
                anchor="w",
                cursor="hand2",
                bg=self.c("surface"),
                fg=self.c("muted"),
                activebackground=self.c("surface2"),
                activeforeground=self.c("text"),
                font=("Segoe UI", 10, "bold"),
                padx=22,
                pady=12
            ).pack(
                fill="x",
                pady=2
            )

        tk.Frame(
            self.sidebar,
            bg=self.c("surface")
        ).pack(
            fill="both",
            expand=True
        )

        tk.Button(
            self.sidebar,
            text="☼   Switch theme",
            command=self.toggle_theme,
            relief="flat",
            bd=0,
            anchor="w",
            cursor="hand2",
            bg=self.c("surface"),
            fg=self.c("muted"),
            activebackground=self.c("surface2"),
            activeforeground=self.c("text"),
            font=("Segoe UI", 10),
            padx=22,
            pady=11
        ).pack(fill="x")

        tk.Button(
            self.sidebar,
            text="ⓘ   About",
            command=self.show_about,
            relief="flat",
            bd=0,
            anchor="w",
            cursor="hand2",
            bg=self.c("surface"),
            fg=self.c("muted"),
            activebackground=self.c("surface2"),
            activeforeground=self.c("text"),
            font=("Segoe UI", 10),
            padx=22,
            pady=11
        ).pack(
            fill="x",
            pady=(0, 15)
        )

    # ========================================================
    # BUTTON
    # ========================================================

    def button(
        self,
        parent,
        text,
        command,
        primary=True
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            bg=(
                self.c("accent")
                if primary
                else self.c("surface2")
            ),
            fg=(
                "#FFFFFF"
                if primary
                else self.c("text")
            ),
            activebackground=self.c("accent2"),
            activeforeground="#FFFFFF",
            padx=18,
            pady=10
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        self.clear_content()

        self.page_title.config(
            text="Dashboard"
        )

        cars = self.database.execute(
            """
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
                created_at
            FROM cars
            ORDER BY id DESC
            """,
            fetch=True
        )

        total_service = self.database.scalar(
            """
            SELECT COALESCE(SUM(cost),0)
            FROM service
            """
        )

        total_fuel = self.database.scalar(
            """
            SELECT COALESCE(SUM(liters * price),0)
            FROM fuel
            """
        )

        total_expenses = self.database.scalar(
            """
            SELECT COALESCE(SUM(amount),0)
            FROM expenses
            """
        )

        reminders = self.database.scalar(
            """
            SELECT COUNT(*)
            FROM reminders
            WHERE done=0
            """
        )

        # ----------------------------------------------------
        # HERO
        # ----------------------------------------------------

        hero = tk.Frame(
            self.content,
            bg=self.c("surface"),
            highlightthickness=1,
            highlightbackground=self.c("border"),
            padx=28,
            pady=24
        )

        hero.pack(
            fill="x",
            pady=(5, 18)
        )

        tk.Label(
            hero,
            text="Your garage. Your data. Your control.",
            font=("Segoe UI", 24, "bold"),
            fg=self.c("text"),
            bg=self.c("surface")
        ).pack(anchor="w")

        tk.Label(
            hero,
            text=(
                "Manage vehicles, maintenance, fuel, expenses "
                "and reminders from one modern workspace."
            ),
            font=("Segoe UI", 10),
            fg=self.c("muted"),
            bg=self.c("surface")
        ).pack(
            anchor="w",
            pady=(5, 18)
        )

        actions = tk.Frame(
            hero,
            bg=self.c("surface")
        )

        actions.pack(anchor="w")

        self.button(
            actions,
            "+ Add vehicle",
            self.add_car
        ).pack(side="left")

        self.button(
            actions,
            "＋ Service",
            self.add_service,
            False
        ).pack(
            side="left",
            padx=8
        )

        self.button(
            actions,
            "＋ Fuel",
            self.add_fuel,
            False
        ).pack(side="left")

        # ----------------------------------------------------
        # STATS
        # ----------------------------------------------------

        cards = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        cards.pack(
            fill="x",
            pady=(0, 18)
        )

        values = [
            (
                "VEHICLES",
                str(len(cars)),
                "cars in garage",
                self.c("accent")
            ),
            (
                "SERVICE",
                self.money(total_service),
                "maintenance costs",
                self.c("success")
            ),
            (
                "FUEL",
                self.money(total_fuel),
                "fuel spending",
                self.c("warning")
            ),
            (
                "EXPENSES",
                self.money(total_expenses),
                "additional expenses",
                self.c("accent2")
            ),
            (
                "REMINDERS",
                str(reminders),
                "open tasks",
                self.c("danger")
            )
        ]

        for i, item in enumerate(values):

            cards.grid_columnconfigure(
                i,
                weight=1
            )

            self.create_stat_card(
                cards,
                *item
            ).grid(
                row=0,
                column=i,
                sticky="nsew",
                padx=5
            )

        # ----------------------------------------------------
        # LOWER
        # ----------------------------------------------------

        lower = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        lower.pack(
            fill="both",
            expand=True
        )

        left = self.panel(
            lower,
            "Garage overview"
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        if not cars:

            tk.Label(
                left,
                text="Your garage is empty",
                font=("Segoe UI", 16, "bold"),
                fg=self.c("text"),
                bg=self.c("surface")
            ).pack(
                anchor="w",
                pady=(30, 5)
            )

            tk.Label(
                left,
                text="Add your first vehicle to start tracking it.",
                font=("Segoe UI", 10),
                fg=self.c("muted"),
                bg=self.c("surface")
            ).pack(anchor="w")

        else:

            for car in cars[:5]:

                row = tk.Frame(
                    left,
                    bg=self.c("surface")
                )

                row.pack(
                    fill="x",
                    pady=8
                )

                tk.Label(
                    row,
                    text="🚗",
                    font=("Segoe UI", 18),
                    bg=self.c("surface")
                ).pack(side="left")

                details = tk.Frame(
                    row,
                    bg=self.c("surface")
                )

                details.pack(
                    side="left",
                    padx=12
                )

                tk.Label(
                    details,
                    text=car["name"] or "Vehicle",
                    font=("Segoe UI", 11, "bold"),
                    fg=self.c("text"),
                    bg=self.c("surface")
                ).pack(anchor="w")

                make = car["make"] or ""
                model = car["model"] or ""

                tk.Label(
                    details,
                    text=(
                        f"{make} {model}  •  "
                        f"{self.number(car['mileage'])} km"
                    ),
                    font=("Segoe UI", 9),
                    fg=self.c("muted"),
                    bg=self.c("surface")
                ).pack(anchor="w")

        right = self.panel(
            lower,
            "Upcoming reminders"
        )

        right.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0)
        )

        upcoming = self.database.execute(
            """
            SELECT
                reminders.id,
                reminders.car_id,
                reminders.title,
                reminders.due_date,
                reminders.due_mileage,
                reminders.done,
                reminders.notes,
                cars.name AS car_name
            FROM reminders
            LEFT JOIN cars
                ON cars.id = reminders.car_id
            WHERE reminders.done=0
            ORDER BY
                CASE
                    WHEN reminders.due_date IS NULL
                    OR reminders.due_date=''
                    THEN 1
                    ELSE 0
                END,
                reminders.due_date ASC
            LIMIT 5
            """,
            fetch=True
        )

        if not upcoming:

            tk.Label(
                right,
                text="Everything is up to date ✓",
                font=("Segoe UI", 11, "bold"),
                fg=self.c("success"),
                bg=self.c("surface")
            ).pack(
                anchor="w",
                pady=30
            )

        else:

            for reminder in upcoming:

                car_name = (
                    reminder["car_name"]
                    or
                    "Vehicle"
                )

                tk.Label(
                    right,
                    text=(
                        f"• {reminder['title'] or 'Reminder'} "
                        f"— {car_name}"
                    ),
                    font=("Segoe UI", 10),
                    fg=self.c("text"),
                    bg=self.c("surface")
                ).pack(
                    anchor="w",
                    pady=6
                )

    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat_card(
        self,
        parent,
        title,
        value,
        subtitle,
        accent
    ):

        frame = tk.Frame(
            parent,
            bg=self.c("surface"),
            highlightthickness=1,
            highlightbackground=self.c("border"),
            padx=17,
            pady=15
        )

        tk.Frame(
            frame,
            bg=accent,
            height=3
        ).pack(
            fill="x",
            pady=(0, 13)
        )

        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 8, "bold"),
            fg=self.c("muted"),
            bg=self.c("surface")
        ).pack(anchor="w")

        tk.Label(
            frame,
            text=value,
            font=("Segoe UI", 20, "bold"),
            fg=self.c("text"),
            bg=self.c("surface")
        ).pack(
            anchor="w",
            pady=4
        )

        tk.Label(
            frame,
            text=subtitle,
            font=("Segoe UI", 8),
            fg=self.c("muted"),
            bg=self.c("surface")
        ).pack(anchor="w")

        return frame

    # ========================================================
    # PANEL
    # ========================================================

    def panel(
        self,
        parent,
        title
    ):

        frame = tk.Frame(
            parent,
            bg=self.c("surface"),
            highlightthickness=1,
            highlightbackground=self.c("border"),
            padx=20,
            pady=18
        )

        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            fg=self.c("text"),
            bg=self.c("surface")
        ).pack(
            anchor="w",
            pady=(0, 12)
        )

        return frame

    # ========================================================
    # GARAGE
    # ========================================================

    def show_garage(self):

        self.clear_content()

        self.page_title.config(
            text="Garage"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        toolbar.pack(
            fill="x",
            pady=(5, 12)
        )

        self.button(
            toolbar,
            "+ Add vehicle",
            self.add_car
        ).pack(side="right")

        query = (
            self.search_entry.get()
            .strip()
            .lower()
        )

        cars = self.database.execute(
            """
            SELECT *
            FROM cars
            ORDER BY id DESC
            """,
            fetch=True
        )

        if query and query != "search garage...":

            filtered = []

            for car in cars:

                text = " ".join(
                    str(
                        car[key]
                        if key in car.keys()
                        else ""
                    )
                    for key in (
                        "name",
                        "make",
                        "model",
                        "vin",
                        "plate",
                        "engine"
                    )
                ).lower()

                if query in text:
                    filtered.append(car)

            cars = filtered

        if not cars:

            tk.Label(
                self.content,
                text="No vehicles found",
                font=("Segoe UI", 16, "bold"),
                fg=self.c("muted"),
                bg=self.c("bg")
            ).pack(
                pady=80
            )

            return

        grid = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        grid.pack(
            fill="both",
            expand=True
        )

        grid.grid_columnconfigure(
            0,
            weight=1
        )

        grid.grid_columnconfigure(
            1,
            weight=1
        )

        for index, car in enumerate(cars):

            self.vehicle_card(
                grid,
                car
            ).grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=7,
                pady=7
            )

    # ========================================================
    # VEHICLE CARD
    # ========================================================

    def vehicle_card(
        self,
        parent,
        car
    ):

        frame = tk.Frame(
            parent,
            bg=self.c("surface"),
            highlightthickness=1,
            highlightbackground=self.c("border"),
            padx=20,
            pady=18
        )

        header = tk.Frame(
            frame,
            bg=self.c("surface")
        )

        header.pack(
            fill="x"
        )

        tk.Label(
            header,
            text="🚗",
            font=("Segoe UI", 25),
            bg=self.c("surface")
        ).pack(side="left")

        tk.Label(
            header,
            text=car["name"] or "Vehicle",
            font=("Segoe UI", 15, "bold"),
            fg=self.c("text"),
            bg=self.c("surface")
        ).pack(
            side="left",
            padx=12
        )

        tk.Button(
            header,
            text="•••",
            command=lambda c=car: self.vehicle_menu(c),
            relief="flat",
            bd=0,
            bg=self.c("surface"),
            fg=self.c("muted"),
            cursor="hand2"
        ).pack(side="right")

        tk.Label(
            frame,
            text=(
                f'{car["make"] or ""} '
                f'{car["model"] or ""} '
                f'{car["year"] or ""}'
            ),
            font=("Segoe UI", 10),
            fg=self.c("muted"),
            bg=self.c("surface")
        ).pack(
            anchor="w",
            pady=(7, 12)
        )

        tk.Label(
            frame,
            text=(
                f'ODO  {self.number(car["mileage"])} km'
                f'     •     '
                f'{car["engine"] or "Engine —"}'
                f'     •     '
                f'{car["transmission"] or "Transmission —"}'
            ),
            font=("Segoe UI", 9, "bold"),
            fg=self.c("text"),
            bg=self.c("surface")
        ).pack(anchor="w")

        service = self.database.scalar(
            """
            SELECT COALESCE(SUM(cost),0)
            FROM service
            WHERE car_id=?
            """,
            (car["id"],)
        )

        fuel = self.database.scalar(
            """
            SELECT COALESCE(SUM(liters * price),0)
            FROM fuel
            WHERE car_id=?
            """,
            (car["id"],)
        )

        tk.Label(
            frame,
            text=(
                f"Maintenance {self.money(service)}"
                f"   •   "
                f"Fuel {self.money(fuel)}"
            ),
            font=("Segoe UI", 9),
            fg=self.c("muted"),
            bg=self.c("surface")
        ).pack(
            anchor="w",
            pady=(7, 0)
        )

        return frame

    # ========================================================
    # VEHICLE MENU
    # ========================================================

    def vehicle_menu(
        self,
        car
    ):

        menu = tk.Menu(
            self,
            tearoff=0,
            bg=self.c("surface"),
            fg=self.c("text")
        )

        menu.add_command(
            label="Edit vehicle",
            command=lambda c=car: self.add_car(c)
        )

        menu.add_command(
            label="Delete vehicle",
            command=lambda c=car: self.delete_car(c)
        )

        menu.tk_popup(
            self.winfo_pointerx(),
            self.winfo_pointery()
        )

    # ========================================================
    # ADD / EDIT CAR
    # ========================================================

    def add_car(
        self,
        car=None
    ):

        window = tk.Toplevel(self)

        window.title(
            "Edit vehicle"
            if car
            else
            "Add vehicle"
        )

        window.geometry(
            "520x700"
        )

        window.configure(
            bg=self.c("bg")
        )

        window.transient(self)
        window.grab_set()

        tk.Label(
            window,
            text="Vehicle details",
            font=("Segoe UI", 20, "bold"),
            fg=self.c("text"),
            bg=self.c("bg")
        ).pack(
            anchor="w",
            padx=28,
            pady=(25, 5)
        )

        tk.Label(
            window,
            text="Keep your vehicle information in one place.",
            font=("Segoe UI", 9),
            fg=self.c("muted"),
            bg=self.c("bg")
        ).pack(
            anchor="w",
            padx=28
        )

        container = tk.Frame(
            window,
            bg=self.c("bg")
        )

        container.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=15
        )

        fields = [
            ("Name", "name"),
            ("Make", "make"),
            ("Model", "model"),
            ("Year", "year"),
            ("Mileage, km", "mileage"),
            ("VIN", "vin"),
            ("Plate", "plate"),
            ("Color", "color"),
            ("Engine", "engine"),
            ("Transmission", "transmission"),
            ("Drive", "drive"),
            ("Fuel", "fuel"),
        ]

        entries = {}

        for label, key in fields:

            tk.Label(
                container,
                text=label,
                font=("Segoe UI", 8, "bold"),
                fg=self.c("muted"),
                bg=self.c("bg")
            ).pack(
                anchor="w",
                pady=(5, 2)
            )

            entry = tk.Entry(
                container,
                relief="flat",
                bg=self.c("input"),
                fg=self.c("text"),
                insertbackground=self.c("text")
            )

            entry.pack(
                fill="x",
                ipady=7
            )

            entries[key] = entry

            if car:

                try:

                    value = car[key]

                    if value is not None:
                        entry.insert(
                            0,
                            str(value)
                        )

                except (KeyError, IndexError):
                    pass

        def save():

            values = {
                key: entry.get().strip()
                for key, entry in entries.items()
            }

            if not values["name"]:

                messagebox.showwarning(
                    "Car Manager",
                    "Enter a vehicle name.",
                    parent=window
                )

                return

            try:

                year = int(
                    values["year"] or 0
                )

                mileage = int(
                    values["mileage"] or 0
                )

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Year and mileage must be numbers.",
                    parent=window
                )

                return

            params = (
                values["name"],
                values["make"],
                values["model"],
                year,
                mileage,
                values["vin"],
                values["plate"],
                values["color"],
                values["engine"],
                values["transmission"],
                values["drive"],
                values["fuel"]
            )

            if car:

                self.database.execute(
                    """
                    UPDATE cars
                    SET
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
                        fuel=?
                    WHERE id=?
                    """,
                    params + (car["id"],)
                )

            else:

                self.database.execute(
                    """
                    INSERT INTO cars
                    (
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
                        fuel
                    )
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    params
                )

            window.destroy()

            self.show_garage()

        self.button(
            window,
            "Save vehicle",
            save
        ).pack(
            fill="x",
            padx=28,
            pady=20
        )

    # ========================================================
    # DELETE CAR
    # ========================================================

    def delete_car(
        self,
        car
    ):

        if not messagebox.askyesno(
            "Delete vehicle",
            (
                f'Delete "{car["name"]}" '
                "and all related records?"
            )
        ):
            return

        for table in (
            "service",
            "fuel",
            "expenses",
            "reminders"
        ):

            self.database.execute(
                f"DELETE FROM {table} WHERE car_id=?",
                (car["id"],)
            )

        self.database.execute(
            "DELETE FROM cars WHERE id=?",
            (car["id"],)
        )

        self.show_garage()

    # ========================================================
    # SERVICE
    # ========================================================

    def show_service(self):

        self.clear_content()

        self.page_title.config(
            text="Service & repairs"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        toolbar.pack(
            fill="x"
        )

        self.button(
            toolbar,
            "+ Add service",
            self.add_service
        ).pack(side="right")

        rows = self.database.execute(
            """
            SELECT
                service.id,
                service.car_id,
                service.title,
                service.category,
                service.mileage,
                service.cost,
                service.date,
                service.notes,
                cars.name AS car_name
            FROM service
            LEFT JOIN cars
                ON cars.id=service.car_id
            ORDER BY service.date DESC
            """,
            fetch=True
        )

        self.create_table(
            self.content,
            [
                "Date",
                "Vehicle",
                "Work",
                "Category",
                "Mileage",
                "Cost"
            ],
            rows,
            "service"
        )

    # ========================================================
    # FUEL
    # ========================================================

    def show_fuel(self):

        self.clear_content()

        self.page_title.config(
            text="Fuel & consumption"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        toolbar.pack(
            fill="x"
        )

        self.button(
            toolbar,
            "+ Add fuel",
            self.add_fuel
        ).pack(side="right")

        rows = self.database.execute(
            """
            SELECT
                fuel.id,
                fuel.car_id,
                fuel.liters,
                fuel.price,
                fuel.mileage,
                fuel.date,
                fuel.station,
                cars.name AS car_name
            FROM fuel
            LEFT JOIN cars
                ON cars.id=fuel.car_id
            ORDER BY fuel.date DESC
            """,
            fetch=True
        )

        self.create_table(
            self.content,
            [
                "Date",
                "Vehicle",
                "Liters",
                "Price/L",
                "Mileage",
                "Station"
            ],
            rows,
            "fuel"
        )

    # ========================================================
    # EXPENSES
    # ========================================================

    def show_expenses(self):

        self.clear_content()

        self.page_title.config(
            text="Expenses"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        toolbar.pack(
            fill="x"
        )

        self.button(
            toolbar,
            "+ Add expense",
            self.add_expense
        ).pack(side="right")

        rows = self.database.execute(
            """
            SELECT
                expenses.id,
                expenses.car_id,
                expenses.title,
                expenses.category,
                expenses.amount,
                expenses.date,
                expenses.notes,
                cars.name AS car_name
            FROM expenses
            LEFT JOIN cars
                ON cars.id=expenses.car_id
            ORDER BY expenses.date DESC
            """,
            fetch=True
        )

        self.create_table(
            self.content,
            [
                "Date",
                "Vehicle",
                "Expense",
                "Category",
                "Amount"
            ],
            rows,
            "expenses"
        )

    # ========================================================
    # REMINDERS
    # ========================================================

    def show_reminders(self):

        self.clear_content()

        self.page_title.config(
            text="Reminders"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.c("bg")
        )

        toolbar.pack(
            fill="x"
        )

        self.button(
            toolbar,
            "+ Add reminder",
            self.add_reminder
        ).pack(side="right")

        rows = self.database.execute(
            """
            SELECT
                reminders.id,
                reminders.car_id,
                reminders.title,
                reminders.due_date,
                reminders.due_mileage,
                reminders.done,
                reminders.notes,
                cars.name AS car_name
            FROM reminders
            LEFT JOIN cars
                ON cars.id=reminders.car_id
            ORDER BY
                reminders.done ASC,
                reminders.due_date ASC
            """,
            fetch=True
        )

        self.create_table(
            self.content,
            [
                "Status",
                "Vehicle",
                "Task",
                "Due date",
                "Due mileage"
            ],
            rows,
            "reminders"
        )

    # ========================================================
    # TABLE
    # ========================================================

    def create_table(
        self,
        parent,
        headers,
        rows,
        table
    ):

        wrapper = tk.Frame(
            parent,
            bg=self.c("surface"),
            highlightthickness=1,
            highlightbackground=self.c("border")
        )

        wrapper.pack(
            fill="both",
            expand=True,
            pady=15
        )

        for index, header in enumerate(headers):

            wrapper.grid_columnconfigure(
                index,
                weight=1
            )

            tk.Label(
                wrapper,
                text=header.upper(),
                font=("Segoe UI", 8, "bold"),
                fg=self.c("muted"),
                bg=self.c("surface"),
                anchor="w"
            ).grid(
                row=0,
                column=index,
                sticky="ew",
                padx=15,
                pady=14
            )

        for row_index, row in enumerate(rows, 1):

            if table == "service":

                values = [
                    row["date"] or "—",
                    row["car_name"] or "—",
                    row["title"] or "—",
                    row["category"] or "—",
                    f'{self.number(row["mileage"])} km',
                    self.money(row["cost"])
                ]

            elif table == "fuel":

                values = [
                    row["date"] or "—",
                    row["car_name"] or "—",
                    f'{float(row["liters"] or 0):.1f} L',
                    self.money(row["price"]),
                    f'{self.number(row["mileage"])} km',
                    row["station"] or "—"
                ]

            elif table == "expenses":

                values = [
                    row["date"] or "—",
                    row["car_name"] or "—",
                    row["title"] or "—",
                    row["category"] or "—",
                    self.money(row["amount"])
                ]

            else:

                values = [
                    "✓ Done"
                    if row["done"]
                    else "○ Open",
                    row["car_name"] or "—",
                    row["title"] or "—",
                    row["due_date"] or "—",
                    (
                        f'{self.number(row["due_mileage"])} km'
                        if row["due_mileage"]
                        else "—"
                    )
                ]

            for column, value in enumerate(values):

                fg = self.c("text")

                if (
                    table == "reminders"
                    and column == 0
                ):

                    fg = (
                        self.c("success")
                        if row["done"]
                        else self.c("warning")
                    )

                tk.Label(
                    wrapper,
                    text=str(value),
                    font=("Segoe UI", 9),
                    fg=fg,
                    bg=self.c("surface"),
                    anchor="w"
                ).grid(
                    row=row_index,
                    column=column,
                    sticky="ew",
                    padx=15,
                    pady=11
                )

            if table == "reminders":

                command = (
                    lambda r=row:
                    self.toggle_reminder(r)
                )

                symbol = "✓"

            else:

                command = (
                    lambda r=row, t=table:
                    self.delete_record(
                        t,
                        r["id"]
                    )
                )

                symbol = "×"

            tk.Button(
                wrapper,
                text=symbol,
                command=command,
                relief="flat",
                bd=0,
                bg=self.c("surface2"),
                fg=self.c("muted"),
                cursor="hand2"
            ).grid(
                row=row_index,
                column=len(headers),
                padx=8
            )

    # ========================================================
    # SELECT CAR
    # ========================================================

    def select_car(self):

        cars = self.database.execute(
            """
            SELECT id, name
            FROM cars
            ORDER BY name
            """,
            fetch=True
        )

        if not cars:

            messagebox.showinfo(
                "Car Manager",
                "Add a vehicle first."
            )

            return None

        window = tk.Toplevel(self)

        window.title(
            "Select vehicle"
        )

        window.geometry(
            "400x230"
        )

        window.configure(
            bg=self.c("bg")
        )

        window.transient(self)
        window.grab_set()

        tk.Label(
            window,
            text="Select vehicle",
            font=("Segoe UI", 18, "bold"),
            fg=self.c("text"),
            bg=self.c("bg")
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 15)
        )

        names = {
            car["name"]: car["id"]
            for car in cars
        }

        variable = tk.StringVar(
            value=cars[0]["name"]
        )

        combo = ttk.Combobox(
            window,
            textvariable=variable,
            values=list(names.keys()),
            state="readonly"
        )

        combo.pack(
            fill="x",
            padx=25,
            pady=10
        )

        result = [None]

        def confirm():

            result[0] = names[
                variable.get()
            ]

            window.destroy()

        self.button(
            window,
            "Continue",
            confirm
        ).pack(
            fill="x",
            padx=25,
            pady=15
        )

        self.wait_window(window)

        return result[0]

    # ========================================================
    # GENERIC FORM
    # ========================================================

    def open_form(
        self,
        title,
        fields,
        callback
    ):

        window = tk.Toplevel(self)

        window.title(title)
        window.geometry("500x600")

        window.configure(
            bg=self.c("bg")
        )

        window.transient(self)
        window.grab_set()

        tk.Label(
            window,
            text=title,
            font=("Segoe UI", 19, "bold"),
            fg=self.c("text"),
            bg=self.c("bg")
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 15)
        )

        entries = {}

        for label, key in fields:

            tk.Label(
                window,
                text=label,
                font=("Segoe UI", 8, "bold"),
                fg=self.c("muted"),
                bg=self.c("bg")
            ).pack(
                anchor="w",
                padx=25,
                pady=(6, 2)
            )

            entry = tk.Entry(
                window,
                relief="flat",
                bg=self.c("input"),
                fg=self.c("text"),
                insertbackground=self.c("text")
            )

            entry.pack(
                fill="x",
                padx=25,
                ipady=8
            )

            entries[key] = entry

        self.button(
            window,
            "Save",
            lambda: self.submit_form(
                window,
                entries,
                callback
            )
        ).pack(
            fill="x",
            padx=25,
            pady=25
        )

    def submit_form(
        self,
        window,
        entries,
        callback
    ):

        values = {
            key: entry.get().strip()
            for key, entry in entries.items()
        }

        if callback(values) is False:
            return

        window.destroy()

    # ========================================================
    # SERVICE FORM
    # ========================================================

    def add_service(self):

        car_id = self.select_car()

        if not car_id:
            return

        def save(values):

            try:

                mileage = int(
                    values["mileage"] or 0
                )

                cost = float(
                    values["cost"] or 0
                )

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Mileage and cost must be numbers."
                )

                return False

            self.database.execute(
                """
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
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    car_id,
                    values["title"],
                    values["category"],
                    mileage,
                    cost,
                    values["date"] or str(date.today()),
                    values["notes"]
                )
            )

            self.show_service()

            return True

        self.open_form(
            "Add service record",
            [
                ("Work performed", "title"),
                ("Category", "category"),
                ("Mileage", "mileage"),
                ("Cost", "cost"),
                ("Date (YYYY-MM-DD)", "date"),
                ("Notes", "notes")
            ],
            save
        )

    # ========================================================
    # FUEL FORM
    # ========================================================

    def add_fuel(self):

        car_id = self.select_car()

        if not car_id:
            return

        def save(values):

            try:

                liters = float(
                    values["liters"] or 0
                )

                price = float(
                    values["price"] or 0
                )

                mileage = int(
                    values["mileage"] or 0
                )

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Liters, price and mileage must be numbers."
                )

                return False

            self.database.execute(
                """
                INSERT INTO fuel
                (
                    car_id,
                    liters,
                    price,
                    mileage,
                    date,
                    station
                )
                VALUES (?,?,?,?,?,?)
                """,
                (
                    car_id,
                    liters,
                    price,
                    mileage,
                    values["date"] or str(date.today()),
                    values["station"]
                )
            )

            self.show_fuel()

            return True

        self.open_form(
            "Add fuel record",
            [
                ("Liters", "liters"),
                ("Price per liter", "price"),
                ("Mileage", "mileage"),
                ("Date (YYYY-MM-DD)", "date"),
                ("Station", "station")
            ],
            save
        )

    # ========================================================
    # EXPENSE FORM
    # ========================================================

    def add_expense(self):

        car_id = self.select_car()

        if not car_id:
            return

        def save(values):

            try:

                amount = float(
                    values["amount"] or 0
                )

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Amount must be a number."
                )

                return False

            self.database.execute(
                """
                INSERT INTO expenses
                (
                    car_id,
                    title,
                    category,
                    amount,
                    date,
                    notes
                )
                VALUES (?,?,?,?,?,?)
                """,
                (
                    car_id,
                    values["title"],
                    values["category"],
                    amount,
                    values["date"] or str(date.today()),
                    values["notes"]
                )
            )

            self.show_expenses()

            return True

        self.open_form(
            "Add expense",
            [
                ("Expense", "title"),
                ("Category", "category"),
                ("Amount", "amount"),
                ("Date (YYYY-MM-DD)", "date"),
                ("Notes", "notes")
            ],
            save
        )

    # ========================================================
    # REMINDER FORM
    # ========================================================

    def add_reminder(self):

        car_id = self.select_car()

        if not car_id:
            return

        def save(values):

            try:

                mileage = int(
                    values["mileage"] or 0
                )

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Mileage must be a number."
                )

                return False

            self.database.execute(
                """
                INSERT INTO reminders
                (
                    car_id,
                    title,
                    due_date,
                    due_mileage,
                    done,
                    notes
                )
                VALUES (?,?,?,?,?,?)
                """,
                (
                    car_id,
                    values["title"],
                    values["date"],
                    mileage,
                    0,
                    values["notes"]
                )
            )

            self.show_reminders()

            return True

        self.open_form(
            "Add reminder",
            [
                ("Task", "title"),
                ("Due date (YYYY-MM-DD)", "date"),
                ("Due mileage", "mileage"),
                ("Notes", "notes")
            ],
            save
        )

    # ========================================================
    # DELETE RECORD
    # ========================================================

    def delete_record(
        self,
        table,
        record_id
    ):

        if not messagebox.askyesno(
            "Confirm",
            "Delete this record?"
        ):
            return

        self.database.execute(
            f"DELETE FROM {table} WHERE id=?",
            (record_id,)
        )

        pages = {
            "service": self.show_service,
            "fuel": self.show_fuel,
            "expenses": self.show_expenses
        }

        pages[table]()

    # ========================================================
    # REMINDER TOGGLE
    # ========================================================

    def toggle_reminder(
        self,
        reminder
    ):

        self.database.execute(
            """
            UPDATE reminders
            SET done=?
            WHERE id=?
            """,
            (
                0
                if reminder["done"]
                else
                1,
                reminder["id"]
            )
        )

        self.show_reminders()

    # ========================================================
    # EXPORT
    # ========================================================

    def export_all(self):

        folder = filedialog.askdirectory(
            title="Choose export folder"
        )

        if not folder:
            return

        tables = [
            "cars",
            "service",
            "fuel",
            "expenses",
            "reminders"
        ]

        exported = 0

        for table in tables:

            rows = self.database.execute(
                f"SELECT * FROM {table}",
                fetch=True
            )

            if not rows:
                continue

            path = (
                Path(folder)
                /
                f"{table}.csv"
            )

            with path.open(
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)

                writer.writerow(
                    rows[0].keys()
                )

                for row in rows:

                    writer.writerow(
                        list(row)
                    )

            exported += 1

        messagebox.showinfo(
            "Export complete",
            (
                f"Exported {exported} tables.\n\n"
                f"Folder:\n{folder}"
            )
        )

    # ========================================================
    # OPEN DATABASE FOLDER
    # ========================================================

    def open_database_folder(self):

        folder = DB_FILE.parent

        try:

            webbrowser.open(
                folder.as_uri()
            )

        except Exception:

            messagebox.showinfo(
                "Database",
                f"Database location:\n{DB_FILE}"
            )

    # ========================================================
    # THEME
    # ========================================================

    def toggle_theme(self):

        self.set_theme(
            "light"
            if self.theme_name == "dark"
            else "dark"
        )

    def set_theme(
        self,
        theme
    ):

        self.theme_name = theme
        self.colors = THEMES[theme]

        for widget in self.winfo_children():
            widget.destroy()

        self.configure(
            bg=self.c("bg")
        )

        self.configure_styles()

        self.build_menu()
        self.build_interface()

        self.show_dashboard()

    # ========================================================
    # ABOUT
    # ========================================================

    def show_about(self):

        window = tk.Toplevel(self)

        window.title(
            "About Car Manager"
        )

        window.geometry(
            "470x350"
        )

        window.configure(
            bg=self.c("bg")
        )

        window.transient(self)

        tk.Label(
            window,
            text="CAR MANAGER",
            font=("Segoe UI", 24, "bold"),
            fg=self.c("text"),
            bg=self.c("bg")
        ).pack(
            pady=(40, 5)
        )

        tk.Label(
            window,
            text=f"Version {VERSION}",
            font=("Segoe UI", 10, "bold"),
            fg=self.c("accent"),
            bg=self.c("bg")
        ).pack()

        tk.Label(
            window,
            text="Modern vehicle management for Windows",
            font=("Segoe UI", 10),
            fg=self.c("muted"),
            bg=self.c("bg")
        ).pack(
            pady=18
        )

        tk.Label(
            window,
            text=f"Developed by {AUTHOR}",
            font=("Segoe UI", 11, "bold"),
            fg=self.c("text"),
            bg=self.c("bg")
        ).pack()

        link = tk.Label(
            window,
            text=TELEGRAM_URL,
            font=("Segoe UI", 10, "underline"),
            fg=self.c("accent"),
            bg=self.c("bg"),
            cursor="hand2"
        )

        link.pack(
            pady=7
        )

        link.bind(
            "<Button-1>",
            lambda event: webbrowser.open(
                TELEGRAM_URL
            )
        )

        self.button(
            window,
            "Close",
            window.destroy,
            False
        ).pack(
            pady=25
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(self):

        try:

            self.database.close()

        except Exception:
            pass

        self.destroy()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app = CarManager()

    app.mainloop()
