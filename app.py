import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import webbrowser
from datetime import datetime, date
from pathlib import Path


# ============================================================
# CAR MANAGER
# Author: Artem Sukhinin
# Telegram: https://t.me/artem_sukhinin
# ============================================================

APP_NAME = "Car Manager"
VERSION = "1.0.0"

AUTHOR = "Artem Sukhinin"
TELEGRAM_URL = "https://t.me/artem_sukhinin"

DB_FILE = Path.home() / "CarManager.db"


# ============================================================
# THEMES
# ============================================================

THEMES = {
    "dark": {
        "bg": "#0b1220",
        "surface": "#111a2b",
        "surface2": "#17233a",
        "border": "#263650",
        "text": "#f4f7fb",
        "muted": "#8fa1ba",
        "accent": "#4a90c2",
        "accent_hover": "#5da4d8",
        "success": "#35d07f",
        "danger": "#ff5f6d",
        "warning": "#f5b942",
        "input": "#0e1727",
        "selected": "#1e4f8a",
    },

    "light": {
        "bg": "#f3f6fa",
        "surface": "#ffffff",
        "surface2": "#e9eef5",
        "border": "#d7dfeb",
        "text": "#182230",
        "muted": "#68778d",
        "accent": "#2878b5",
        "accent_hover": "#3a8bc8",
        "success": "#159957",
        "danger": "#dc3545",
        "warning": "#c88900",
        "input": "#ffffff",
        "selected": "#dcecf9",
    }
}


# ============================================================
# DATABASE
# ============================================================

class Database:

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER,
                mileage INTEGER DEFAULT 0,
                vin TEXT,
                plate TEXT,
                engine TEXT,
                transmission TEXT,
                drive TEXT,
                color TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                mileage INTEGER DEFAULT 0,
                category TEXT,
                description TEXT,
                cost REAL DEFAULT 0,
                workshop TEXT,
                FOREIGN KEY(car_id) REFERENCES cars(id)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fuel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                mileage INTEGER DEFAULT 0,
                liters REAL DEFAULT 0,
                price REAL DEFAULT 0,
                total REAL DEFAULT 0,
                station TEXT,
                FOREIGN KEY(car_id) REFERENCES cars(id)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                due_date TEXT,
                due_mileage INTEGER,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY(car_id) REFERENCES cars(id)
            )
        """)

        self.conn.commit()

    # --------------------------------------------------------
    # Cars
    # --------------------------------------------------------

    def get_cars(self):
        return self.conn.execute(
            "SELECT * FROM cars ORDER BY id DESC"
        ).fetchall()

    def get_car(self, car_id):
        return self.conn.execute(
            "SELECT * FROM cars WHERE id=?",
            (car_id,)
        ).fetchone()

    def add_car(self, data):

        cursor = self.conn.execute("""
            INSERT INTO cars (
                make,
                model,
                year,
                mileage,
                vin,
                plate,
                engine,
                transmission,
                drive,
                color,
                notes,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["make"],
            data["model"],
            data["year"],
            data["mileage"],
            data["vin"],
            data["plate"],
            data["engine"],
            data["transmission"],
            data["drive"],
            data["color"],
            data["notes"],
            datetime.now().isoformat()
        ))

        self.conn.commit()

        return cursor.lastrowid

    def update_car(self, car_id, data):

        self.conn.execute("""
            UPDATE cars SET
                make=?,
                model=?,
                year=?,
                mileage=?,
                vin=?,
                plate=?,
                engine=?,
                transmission=?,
                drive=?,
                color=?,
                notes=?
            WHERE id=?
        """, (
            data["make"],
            data["model"],
            data["year"],
            data["mileage"],
            data["vin"],
            data["plate"],
            data["engine"],
            data["transmission"],
            data["drive"],
            data["color"],
            data["notes"],
            car_id
        ))

        self.conn.commit()

    def delete_car(self, car_id):

        self.conn.execute(
            "DELETE FROM service WHERE car_id=?",
            (car_id,)
        )

        self.conn.execute(
            "DELETE FROM fuel WHERE car_id=?",
            (car_id,)
        )

        self.conn.execute(
            "DELETE FROM reminders WHERE car_id=?",
            (car_id,)
        )

        self.conn.execute(
            "DELETE FROM cars WHERE id=?",
            (car_id,)
        )

        self.conn.commit()

    # --------------------------------------------------------
    # Service
    # --------------------------------------------------------

    def add_service(self, data):

        self.conn.execute("""
            INSERT INTO service (
                car_id,
                date,
                mileage,
                category,
                description,
                cost,
                workshop
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["car_id"],
            data["date"],
            data["mileage"],
            data["category"],
            data["description"],
            data["cost"],
            data["workshop"]
        ))

        self.conn.commit()

    def get_service(self, car_id=None):

        if car_id:
            return self.conn.execute("""
                SELECT service.*, cars.make, cars.model
                FROM service
                JOIN cars ON cars.id = service.car_id
                WHERE car_id=?
                ORDER BY service.date DESC, service.id DESC
            """, (car_id,)).fetchall()

        return self.conn.execute("""
            SELECT service.*, cars.make, cars.model
            FROM service
            JOIN cars ON cars.id = service.car_id
            ORDER BY service.date DESC, service.id DESC
        """).fetchall()

    def delete_service(self, service_id):

        self.conn.execute(
            "DELETE FROM service WHERE id=?",
            (service_id,)
        )

        self.conn.commit()

    # --------------------------------------------------------
    # Fuel
    # --------------------------------------------------------

    def add_fuel(self, data):

        self.conn.execute("""
            INSERT INTO fuel (
                car_id,
                date,
                mileage,
                liters,
                price,
                total,
                station
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["car_id"],
            data["date"],
            data["mileage"],
            data["liters"],
            data["price"],
            data["total"],
            data["station"]
        ))

        self.conn.commit()

    def get_fuel(self, car_id=None):

        if car_id:
            return self.conn.execute("""
                SELECT fuel.*, cars.make, cars.model
                FROM fuel
                JOIN cars ON cars.id = fuel.car_id
                WHERE car_id=?
                ORDER BY fuel.date DESC, fuel.id DESC
            """, (car_id,)).fetchall()

        return self.conn.execute("""
            SELECT fuel.*, cars.make, cars.model
            FROM fuel
            JOIN cars ON cars.id = fuel.car_id
            ORDER BY fuel.date DESC, fuel.id DESC
        """).fetchall()

    # --------------------------------------------------------
    # Reminders
    # --------------------------------------------------------

    def add_reminder(self, data):

        self.conn.execute("""
            INSERT INTO reminders (
                car_id,
                title,
                due_date,
                due_mileage
            )
            VALUES (?, ?, ?, ?)
        """, (
            data["car_id"],
            data["title"],
            data["due_date"],
            data["due_mileage"]
        ))

        self.conn.commit()

    def get_reminders(self, car_id=None):

        if car_id:
            return self.conn.execute("""
                SELECT reminders.*, cars.make, cars.model
                FROM reminders
                JOIN cars ON cars.id = reminders.car_id
                WHERE car_id=? AND completed=0
                ORDER BY due_date ASC
            """, (car_id,)).fetchall()

        return self.conn.execute("""
            SELECT reminders.*, cars.make, cars.model
            FROM reminders
            JOIN cars ON cars.id = reminders.car_id
            WHERE completed=0
            ORDER BY due_date ASC
        """).fetchall()

    def complete_reminder(self, reminder_id):

        self.conn.execute(
            "UPDATE reminders SET completed=1 WHERE id=?",
            (reminder_id,)
        )

        self.conn.commit()

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def total_service_cost(self):

        row = self.conn.execute(
            "SELECT COALESCE(SUM(cost), 0) AS total FROM service"
        ).fetchone()

        return row["total"]

    def total_fuel_cost(self):

        row = self.conn.execute(
            "SELECT COALESCE(SUM(total), 0) AS total FROM fuel"
        ).fetchone()

        return row["total"]

    def close(self):
        self.conn.close()


# ============================================================
# APPLICATION
# ============================================================

class CarManager(tk.Tk):

    def __init__(self):

        super().__init__()

        self.db = Database(DB_FILE)

        self.theme_name = "dark"
        self.colors = THEMES[self.theme_name]

        self.selected_car_id = None
        self.current_page = "dashboard"

        self.title(
            f"{APP_NAME} {VERSION}"
        )

        self.geometry("1280x820")
        self.minsize(1050, 700)

        self.configure(
            bg=self.colors["bg"]
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.setup_style()
        self.create_menu()
        self.create_layout()
        self.refresh_dashboard()

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):

        style = ttk.Style(self)

        style.theme_use("clam")

        c = self.colors

        style.configure(
            "Treeview",
            background=c["surface"],
            fieldbackground=c["surface"],
            foreground=c["text"],
            borderwidth=0,
            rowheight=38,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=c["surface2"],
            foreground=c["muted"],
            borderwidth=0,
            relief="flat",
            font=("Segoe UI Semibold", 9)
        )

        style.map(
            "Treeview",
            background=[
                ("selected", c["selected"])
            ],
            foreground=[
                ("selected", c["text"])
            ]
        )

        style.configure(
            "TCombobox",
            fieldbackground=c["input"],
            background=c["input"],
            foreground=c["text"],
            borderwidth=0
        )

    # ========================================================
    # MENU
    # ========================================================

    def create_menu(self):

        menu = tk.Menu(
            self,
            tearoff=False,
            bg=self.colors["surface"],
            fg=self.colors["text"],
            activebackground=self.colors["selected"],
            activeforeground=self.colors["text"]
        )

        file_menu = tk.Menu(
            menu,
            tearoff=False,
            bg=self.colors["surface"],
            fg=self.colors["text"]
        )

        file_menu.add_command(
            label="Новый автомобиль",
            command=self.add_car_dialog
        )

        file_menu.add_command(
            label="Экспорт CSV",
            command=self.export_csv
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Выход",
            command=self.close
        )

        menu.add_cascade(
            label="Файл",
            menu=file_menu
        )

        view_menu = tk.Menu(
            menu,
            tearoff=False,
            bg=self.colors["surface"],
            fg=self.colors["text"]
        )

        view_menu.add_command(
            label="Dashboard",
            command=self.show_dashboard
        )

        view_menu.add_command(
            label="Мой гараж",
            command=self.show_garage
        )

        view_menu.add_command(
            label="Обслуживание",
            command=self.show_service
        )

        view_menu.add_command(
            label="Заправки",
            command=self.show_fuel
        )

        view_menu.add_command(
            label="Напоминания",
            command=self.show_reminders
        )

        menu.add_cascade(
            label="Разделы",
            menu=view_menu
        )

        theme_menu = tk.Menu(
            menu,
            tearoff=False,
            bg=self.colors["surface"],
            fg=self.colors["text"]
        )

        theme_menu.add_command(
            label="🌙 Тёмная",
            command=lambda: self.set_theme("dark")
        )

        theme_menu.add_command(
            label="☀ Светлая",
            command=lambda: self.set_theme("light")
        )

        menu.add_cascade(
            label="Тема",
            menu=theme_menu
        )

        help_menu = tk.Menu(
            menu,
            tearoff=False,
            bg=self.colors["surface"],
            fg=self.colors["text"]
        )

        help_menu.add_command(
            label="О программе",
            command=self.about
        )

        help_menu.add_command(
            label="Telegram автора",
            command=lambda: webbrowser.open(
                TELEGRAM_URL
            )
        )

        menu.add_cascade(
            label="Помощь",
            menu=help_menu
        )

        self.config(
            menu=menu
        )

    # ========================================================
    # LAYOUT
    # ========================================================

    def create_layout(self):

        self.sidebar = tk.Frame(
            self,
            bg=self.colors["surface"],
            width=230
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(
            self,
            bg=self.colors["bg"]
        )

        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.create_sidebar()

    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):

        c = self.colors

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        logo = tk.Frame(
            self.sidebar,
            bg=c["surface"]
        )

        logo.pack(
            fill="x",
            padx=20,
            pady=(25, 30)
        )

        tk.Label(
            logo,
            text="CAR",
            bg=c["surface"],
            fg=c["accent"],
            font=("Segoe UI Black", 20)
        ).pack(anchor="w")

        tk.Label(
            logo,
            text="MANAGER",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI Semibold", 13)
        ).pack(anchor="w")

        tk.Label(
            logo,
            text=f"v{VERSION}",
            bg=c["surface"],
            fg=c["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(3, 0))

        self.nav_button(
            "⌂",
            "Dashboard",
            self.show_dashboard
        )

        self.nav_button(
            "🚗",
            "Мой гараж",
            self.show_garage
        )

        self.nav_button(
            "🔧",
            "Обслуживание",
            self.show_service
        )

        self.nav_button(
            "⛽",
            "Заправки",
            self.show_fuel
        )

        self.nav_button(
            "🔔",
            "Напоминания",
            self.show_reminders
        )

        spacer = tk.Frame(
            self.sidebar,
            bg=c["surface"]
        )

        spacer.pack(
            fill="both",
            expand=True
        )

        author = tk.Frame(
            self.sidebar,
            bg=c["surface"]
        )

        author.pack(
            fill="x",
            padx=20,
            pady=20
        )

        tk.Label(
            author,
            text="Created by",
            bg=c["surface"],
            fg=c["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        link = tk.Label(
            author,
            text="Artem Sukhinin",
            bg=c["surface"],
            fg=c["accent"],
            cursor="hand2",
            font=("Segoe UI Semibold", 9)
        )

        link.pack(anchor="w")

        link.bind(
            "<Button-1>",
            lambda e: webbrowser.open(
                TELEGRAM_URL
            )
        )

    def nav_button(self, icon, title, command):

        c = self.colors

        frame = tk.Frame(
            self.sidebar,
            bg=c["surface"]
        )

        frame.pack(
            fill="x",
            padx=12,
            pady=3
        )

        button = tk.Button(
            frame,
            text=f"  {icon}   {title}",
            command=command,
            anchor="w",
            relief="flat",
            bd=0,
            bg=c["surface"],
            fg=c["text"],
            activebackground=c["selected"],
            activeforeground=c["text"],
            font=("Segoe UI Semibold", 10),
            padx=12,
            pady=10,
            cursor="hand2"
        )

        button.pack(fill="x")

    # ========================================================
    # COMMON UI
    # ========================================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def page_title(self, title, subtitle=""):

        c = self.colors

        header = tk.Frame(
            self.content,
            bg=c["bg"]
        )

        header.pack(
            fill="x",
            padx=32,
            pady=(28, 20)
        )

        tk.Label(
            header,
            text=title,
            bg=c["bg"],
            fg=c["text"],
            font=("Segoe UI Semibold", 26)
        ).pack(anchor="w")

        if subtitle:

            tk.Label(
                header,
                text=subtitle,
                bg=c["bg"],
                fg=c["muted"],
                font=("Segoe UI", 10)
            ).pack(
                anchor="w",
                pady=(4, 0)
            )

    def card(
        self,
        parent,
        title,
        value,
        subtitle="",
        width=None
    ):

        c = self.colors

        frame = tk.Frame(
            parent,
            bg=c["surface"],
            highlightbackground=c["border"],
            highlightthickness=1
        )

        if width:
            frame.configure(width=width)

        tk.Label(
            frame,
            text=title.upper(),
            bg=c["surface"],
            fg=c["muted"],
            font=("Segoe UI Semibold", 8)
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 4)
        )

        tk.Label(
            frame,
            text=value,
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI Semibold", 23)
        ).pack(
            anchor="w",
            padx=18
        )

        if subtitle:

            tk.Label(
                frame,
                text=subtitle,
                bg=c["surface"],
                fg=c["muted"],
                font=("Segoe UI", 9)
            ).pack(
                anchor="w",
                padx=18,
                pady=(2, 14)
            )

        return frame

    def primary_button(
        self,
        parent,
        text,
        command
    ):

        c = self.colors

        return tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            bd=0,
            bg=c["accent"],
            fg="#ffffff",
            activebackground=c["accent_hover"],
            activeforeground="#ffffff",
            font=("Segoe UI Semibold", 9),
            padx=16,
            pady=9,
            cursor="hand2"
        )

    def danger_button(
        self,
        parent,
        text,
        command
    ):

        c = self.colors

        return tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            bd=0,
            bg=c["danger"],
            fg="#ffffff",
            activebackground="#ff7180",
            font=("Segoe UI Semibold", 9),
            padx=14,
            pady=8,
            cursor="hand2"
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        self.current_page = "dashboard"
        self.refresh_dashboard()

    def refresh_dashboard(self):

        self.clear_content()

        self.page_title(
            "Dashboard",
            "Состояние вашего автопарка"
        )

        c = self.colors

        cars = self.db.get_cars()

        total_service = self.db.total_service_cost()
        total_fuel = self.db.total_fuel_cost()

        row = tk.Frame(
            self.content,
            bg=c["bg"]
        )

        row.pack(
            fill="x",
            padx=27
        )

        for title, value, subtitle in [
            (
                "Автомобили",
                str(len(cars)),
                "в вашем гараже"
            ),
            (
                "Обслуживание",
                f"{total_service:,.0f} ₽",
                "всего расходов"
            ),
            (
                "Топливо",
                f"{total_fuel:,.0f} ₽",
                "всего расходов"
            ),
            (
                "Напоминания",
                str(len(self.db.get_reminders())),
                "активных задач"
            )
        ]:

            box = self.card(
                row,
                title,
                value,
                subtitle
            )

            box.pack(
                side="left",
                fill="x",
                expand=True,
                padx=5
            )

        # ----------------------------------------------------
        # Cars preview
        # ----------------------------------------------------

        tk.Label(
            self.content,
            text="Ваши автомобили",
            bg=c["bg"],
            fg=c["text"],
            font=("Segoe UI Semibold", 15)
        ).pack(
            anchor="w",
            padx=32,
            pady=(30, 10)
        )

        if not cars:

            empty = tk.Frame(
                self.content,
                bg=c["surface"],
                highlightbackground=c["border"],
                highlightthickness=1
            )

            empty.pack(
                fill="x",
                padx=32
            )

            tk.Label(
                empty,
                text="🚗",
                bg=c["surface"],
                fg=c["text"],
                font=("Segoe UI", 30)
            ).pack(pady=(25, 5))

            tk.Label(
                empty,
                text="Гараж пока пуст",
                bg=c["surface"],
                fg=c["text"],
                font=("Segoe UI Semibold", 14)
            ).pack()

            tk.Label(
                empty,
                text="Добавьте первый автомобиль, чтобы начать вести историю.",
                bg=c["surface"],
                fg=c["muted"],
                font=("Segoe UI", 10)
            ).pack(pady=5)

            self.primary_button(
                empty,
                "＋ Добавить автомобиль",
                self.add_car_dialog
            ).pack(pady=(10, 25))

        else:

            container = tk.Frame(
                self.content,
                bg=c["bg"]
            )

            container.pack(
                fill="both",
                expand=True,
                padx=27
            )

            for car in cars[:4]:

                car_frame = tk.Frame(
                    container,
                    bg=c["surface"],
                    highlightbackground=c["border"],
                    highlightthickness=1
                )

                car_frame.pack(
                    fill="x",
                    padx=5,
                    pady=5
                )

                title = (
                    f"{car['make']} {car['model']}"
                )

                tk.Label(
                    car_frame,
                    text=title,
                    bg=c["surface"],
                    fg=c["text"],
                    font=("Segoe UI Semibold", 13)
                ).pack(
                    side="left",
                    padx=18,
                    pady=15
                )

                info = (
                    f"{car['year'] or '—'}  •  "
                    f"{car['mileage']:,} км  •  "
                    f"{car['engine'] or 'Двигатель —'}"
                )

                tk.Label(
                    car_frame,
                    text=info,
                    bg=c["surface"],
                    fg=c["muted"],
                    font=("Segoe UI", 9)
                ).pack(
                    side="left",
                    padx=10
                )

                tk.Button(
                    car_frame,
                    text="Открыть",
                    command=lambda x=car["id"]:
                    self.open_car(x),
                    relief="flat",
                    bd=0,
                    bg=c["surface2"],
                    fg=c["text"],
                    activebackground=c["selected"],
                    font=("Segoe UI Semibold", 9),
                    padx=12,
                    pady=7,
                    cursor="hand2"
                ).pack(
                    side="right",
                    padx=15
                )

    # ========================================================
    # GARAGE
    # ========================================================

    def show_garage(self):

        self.current_page = "garage"

        self.clear_content()

        self.page_title(
            "Мой гараж",
            "Все автомобили и их основные параметры"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.colors["bg"]
        )

        toolbar.pack(
            fill="x",
            padx=32,
            pady=(0, 12)
        )

        self.primary_button(
            toolbar,
            "＋ Добавить автомобиль",
            self.add_car_dialog
        ).pack(side="left")

        search_var = tk.StringVar()

        search = tk.Entry(
            toolbar,
            textvariable=search_var,
            bg=self.colors["input"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            font=("Segoe UI", 10)
        )

        search.pack(
            side="right",
            ipady=8,
            ipadx=10
        )

        tk.Label(
            toolbar,
            text="Поиск:",
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        ).pack(
            side="right",
            padx=8
        )

        table_frame = tk.Frame(
            self.content,
            bg=self.colors["surface"]
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(0, 25)
        )

        columns = (
            "car",
            "year",
            "mileage",
            "engine",
            "transmission",
            "drive",
            "plate"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "car": "Автомобиль",
            "year": "Год",
            "mileage": "Пробег",
            "engine": "Двигатель",
            "transmission": "КПП",
            "drive": "Привод",
            "plate": "Номер"
        }

        widths = {
            "car": 220,
            "year": 70,
            "mileage": 110,
            "engine": 140,
            "transmission": 120,
            "drive": 100,
            "plate": 120
        }

        for col in columns:

            tree.heading(
                col,
                text=headings[col]
            )

            tree.column(
                col,
                width=widths[col]
            )

        tree.pack(
            fill="both",
            expand=True
        )

        def populate():

            tree.delete(
                *tree.get_children()
            )

            query = search_var.get().lower()

            for car in self.db.get_cars():

                full = (
                    f"{car['make']} "
                    f"{car['model']} "
                    f"{car['engine'] or ''} "
                    f"{car['plate'] or ''}"
                ).lower()

                if query and query not in full:
                    continue

                tree.insert(
                    "",
                    "end",
                    iid=str(car["id"]),
                    values=(
                        f"{car['make']} {car['model']}",
                        car["year"] or "—",
                        f"{car['mileage']:,} км",
                        car["engine"] or "—",
                        car["transmission"] or "—",
                        car["drive"] or "—",
                        car["plate"] or "—"
                    )
                )

        populate()

        search_var.trace_add(
            "write",
            lambda *args: populate()
        )

        def open_selected():

            selection = tree.selection()

            if not selection:
                return

            self.open_car(
                int(selection[0])
            )

        tree.bind(
            "<Double-1>",
            lambda e: open_selected()
        )

    # ========================================================
    # CAR DETAILS
    # ========================================================

    def open_car(self, car_id):

        car = self.db.get_car(car_id)

        if not car:
            return

        self.clear_content()

        self.selected_car_id = car_id

        self.page_title(
            f"{car['make']} {car['model']}",
            "Карточка автомобиля"
        )

        c = self.colors

        toolbar = tk.Frame(
            self.content,
            bg=c["bg"]
        )

        toolbar.pack(
            fill="x",
            padx=32
        )

        self.primary_button(
            toolbar,
            "✎ Редактировать",
            lambda: self.edit_car_dialog(car_id)
        ).pack(side="left")

        self.danger_button(
            toolbar,
            "Удалить",
            lambda: self.delete_car(car_id)
        ).pack(
            side="left",
            padx=8
        )

        info = tk.Frame(
            self.content,
            bg=c["surface"],
            highlightbackground=c["border"],
            highlightthickness=1
        )

        info.pack(
            fill="x",
            padx=32,
            pady=20
        )

        fields = [
            ("Год", car["year"] or "—"),
            ("Пробег", f"{car['mileage']:,} км"),
            ("Двигатель", car["engine"] or "—"),
            ("КПП", car["transmission"] or "—"),
            ("Привод", car["drive"] or "—"),
            ("Цвет", car["color"] or "—"),
            ("Госномер", car["plate"] or "—"),
            ("VIN", car["vin"] or "—"),
        ]

        for i, (title, value) in enumerate(fields):

            box = tk.Frame(
                info,
                bg=c["surface"]
            )

            box.grid(
                row=i // 4,
                column=i % 4,
                sticky="ew",
                padx=15,
                pady=12
            )

            info.columnconfigure(
                i % 4,
                weight=1
            )

            tk.Label(
                box,
                text=title.upper(),
                bg=c["surface"],
                fg=c["muted"],
                font=("Segoe UI Semibold", 8)
            ).pack(anchor="w")

            tk.Label(
                box,
                text=value,
                bg=c["surface"],
                fg=c["text"],
                font=("Segoe UI Semibold", 11)
            ).pack(anchor="w", pady=(3, 0))

        if car["notes"]:

            tk.Label(
                self.content,
                text="Заметки",
                bg=c["bg"],
                fg=c["text"],
                font=("Segoe UI Semibold", 13)
            ).pack(
                anchor="w",
                padx=32,
                pady=(0, 7)
            )

            tk.Label(
                self.content,
                text=car["notes"],
                bg=c["surface"],
                fg=c["muted"],
                justify="left",
                anchor="w",
                padx=15,
                pady=12,
                font=("Segoe UI", 9)
            ).pack(
                fill="x",
                padx=32
            )

    # ========================================================
    # ADD / EDIT CAR
    # ========================================================

    def add_car_dialog(self):

        self.car_dialog()

    def edit_car_dialog(self, car_id):

        car = self.db.get_car(car_id)

        self.car_dialog(car)

    def car_dialog(self, car=None):

        c = self.colors

        dialog = tk.Toplevel(self)

        dialog.title(
            "Новый автомобиль"
            if not car
            else "Редактировать автомобиль"
        )

        dialog.geometry("620x650")
        dialog.configure(
            bg=c["bg"]
        )

        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=(
                "Новый автомобиль"
                if not car
                else "Редактирование"
            ),
            bg=c["bg"],
            fg=c["text"],
            font=("Segoe UI Semibold", 20)
        ).pack(
            anchor="w",
            padx=30,
            pady=(25, 20)
        )

        form = tk.Frame(
            dialog,
            bg=c["bg"]
        )

        form.pack(
            fill="both",
            expand=True,
            padx=30
        )

        entries = {}

        fields = [
            ("make", "Марка", ""),
            ("model", "Модель", ""),
            ("year", "Год", ""),
            ("mileage", "Пробег, км", "0"),
            ("engine", "Двигатель", ""),
            ("transmission", "КПП", ""),
            ("drive", "Привод", ""),
            ("color", "Цвет", ""),
            ("plate", "Госномер", ""),
            ("vin", "VIN", ""),
        ]

        for index, (
            key,
            label,
            default
        ) in enumerate(fields):

            row = index // 2
            column = index % 2

            wrapper = tk.Frame(
                form,
                bg=c["bg"]
            )

            wrapper.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=6,
                pady=7
            )

            form.columnconfigure(
                column,
                weight=1
            )

            tk.Label(
                wrapper,
                text=label,
                bg=c["bg"],
                fg=c["muted"],
                font=("Segoe UI", 9)
            ).pack(anchor="w")

            value = default

            if car:
                value = car[key] or ""

            var = tk.StringVar(
                value=str(value)
            )

            entry = tk.Entry(
                wrapper,
                textvariable=var,
                bg=c["input"],
                fg=c["text"],
                insertbackground=c["text"],
                relief="flat",
                font=("Segoe UI", 10)
            )

            entry.pack(
                fill="x",
                ipady=8,
                pady=(4, 0)
            )

            entries[key] = var

        notes_wrapper = tk.Frame(
            form,
            bg=c["bg"]
        )

        notes_wrapper.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=6,
            pady=8
        )

        form.rowconfigure(
            5,
            weight=1
        )

        tk.Label(
            notes_wrapper,
            text="Заметки",
            bg=c["bg"],
            fg=c["muted"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        notes = tk.Text(
            notes_wrapper,
            height=5,
            bg=c["input"],
            fg=c["text"],
            insertbackground=c["text"],
            relief="flat",
            font=("Segoe UI", 10)
        )

        notes.pack(
            fill="both",
            expand=True,
            pady=(4, 0)
        )

        if car and car["notes"]:
            notes.insert(
                "1.0",
                car["notes"]
            )

        buttons = tk.Frame(
            dialog,
            bg=c["bg"]
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=20
        )

        def save():

            if not entries["make"].get().strip():
                messagebox.showwarning(
                    "Car Manager",
                    "Введите марку автомобиля.",
                    parent=dialog
                )
                return

            if not entries["model"].get().strip():
                messagebox.showwarning(
                    "Car Manager",
                    "Введите модель автомобиля.",
                    parent=dialog
                )
                return

            try:
                year = int(
                    entries["year"].get()
                    or 0
                )

                mileage = int(
                    entries["mileage"].get()
                    or 0
                )

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Год и пробег должны быть числами.",
                    parent=dialog
                )

                return

            data = {
                key: entries[key].get().strip()
                for key, _, _ in fields
            }

            data["year"] = year
            data["mileage"] = mileage
            data["notes"] = notes.get(
                "1.0",
                "end"
            ).strip()

            if car:

                self.db.update_car(
                    car["id"],
                    data
                )

            else:

                self.db.add_car(
                    data
                )

            dialog.destroy()

            if self.current_page == "garage":
                self.show_garage()
            else:
                self.show_dashboard()

        self.primary_button(
            buttons,
            "Сохранить",
            save
        ).pack(side="right")

        tk.Button(
            buttons,
            text="Отмена",
            command=dialog.destroy,
            relief="flat",
            bd=0,
            bg=c["surface2"],
            fg=c["text"],
            font=("Segoe UI Semibold", 9),
            padx=16,
            pady=9,
            cursor="hand2"
        ).pack(
            side="right",
            padx=8
        )

    # ========================================================
    # DELETE CAR
    # ========================================================

    def delete_car(self, car_id):

        car = self.db.get_car(car_id)

        if not car:
            return

        result = messagebox.askyesno(
            "Удаление",
            f"Удалить {car['make']} {car['model']}?\n\n"
            "Все записи обслуживания, заправок и напоминаний "
            "этого автомобиля также будут удалены."
        )

        if result:

            self.db.delete_car(
                car_id
            )

            self.show_garage()

    # ========================================================
    # SERVICE
    # ========================================================

    def show_service(self):

        self.current_page = "service"

        self.clear_content()

        self.page_title(
            "Обслуживание",
            "История ремонтов, ТО и расходов"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.colors["bg"]
        )

        toolbar.pack(
            fill="x",
            padx=32,
            pady=(0, 12)
        )

        self.primary_button(
            toolbar,
            "＋ Добавить запись",
            self.add_service_dialog
        ).pack(side="left")

        table = tk.Frame(
            self.content,
            bg=self.colors["surface"]
        )

        table.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(0, 25)
        )

        columns = (
            "date",
            "car",
            "mileage",
            "category",
            "description",
            "cost",
            "workshop"
        )

        tree = ttk.Treeview(
            table,
            columns=columns,
            show="headings"
        )

        headings = {
            "date": "Дата",
            "car": "Автомобиль",
            "mileage": "Пробег",
            "category": "Категория",
            "description": "Работа",
            "cost": "Стоимость",
            "workshop": "Сервис"
        }

        for col in columns:

            tree.heading(
                col,
                text=headings[col]
            )

            tree.column(
                col,
                width=130
            )

        tree.pack(
            fill="both",
            expand=True
        )

        for row in self.db.get_service():

            tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["date"],
                    f"{row['make']} {row['model']}",
                    f"{row['mileage']:,}",
                    row["category"] or "—",
                    row["description"] or "—",
                    f"{row['cost']:,.0f} ₽",
                    row["workshop"] or "—"
                )
            )

    # ========================================================
    # SERVICE DIALOG
    # ========================================================

    def add_service_dialog(self):

        cars = self.db.get_cars()

        if not cars:

            messagebox.showinfo(
                "Car Manager",
                "Сначала добавьте автомобиль."
            )

            return

        self.record_dialog(
            mode="service"
        )

    # ========================================================
    # FUEL
    # ========================================================

    def show_fuel(self):

        self.current_page = "fuel"

        self.clear_content()

        self.page_title(
            "Заправки",
            "История топлива и затрат"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.colors["bg"]
        )

        toolbar.pack(
            fill="x",
            padx=32,
            pady=(0, 12)
        )

        self.primary_button(
            toolbar,
            "＋ Добавить заправку",
            self.add_fuel_dialog
        ).pack(side="left")

        table = tk.Frame(
            self.content,
            bg=self.colors["surface"]
        )

        table.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(0, 25)
        )

        columns = (
            "date",
            "car",
            "mileage",
            "liters",
            "price",
            "total",
            "station"
        )

        tree = ttk.Treeview(
            table,
            columns=columns,
            show="headings"
        )

        headings = {
            "date": "Дата",
            "car": "Автомобиль",
            "mileage": "Пробег",
            "liters": "Литры",
            "price": "Цена/л",
            "total": "Сумма",
            "station": "АЗС"
        }

        for col in columns:

            tree.heading(
                col,
                text=headings[col]
            )

            tree.column(
                col,
                width=130
            )

        tree.pack(
            fill="both",
            expand=True
        )

        for row in self.db.get_fuel():

            tree.insert(
                "",
                "end",
                values=(
                    row["date"],
                    f"{row['make']} {row['model']}",
                    f"{row['mileage']:,}",
                    f"{row['liters']:.1f} л",
                    f"{row['price']:.2f} ₽",
                    f"{row['total']:,.0f} ₽",
                    row["station"] or "—"
                )
            )

    def add_fuel_dialog(self):

        if not self.db.get_cars():

            messagebox.showinfo(
                "Car Manager",
                "Сначала добавьте автомобиль."
            )

            return

        self.record_dialog(
            mode="fuel"
        )

    # ========================================================
    # RECORD DIALOG
    # ========================================================

    def record_dialog(self, mode):

        c = self.colors

        dialog = tk.Toplevel(self)

        dialog.title(
            "Добавить обслуживание"
            if mode == "service"
            else "Добавить заправку"
        )

        dialog.geometry("560x540")

        dialog.configure(
            bg=c["bg"]
        )

        dialog.transient(self)
        dialog.grab_set()

        title = (
            "Добавить обслуживание"
            if mode == "service"
            else "Добавить заправку"
        )

        tk.Label(
            dialog,
            text=title,
            bg=c["bg"],
            fg=c["text"],
            font=("Segoe UI Semibold", 19)
        ).pack(
            anchor="w",
            padx=30,
            pady=(25, 20)
        )

        form = tk.Frame(
            dialog,
            bg=c["bg"]
        )

        form.pack(
            fill="both",
            expand=True,
            padx=30
        )

        cars = self.db.get_cars()

        car_map = {
            f"{car['make']} {car['model']}":
                car["id"]
            for car in cars
        }

        tk.Label(
            form,
            text="Автомобиль",
            bg=c["bg"],
            fg=c["muted"]
        ).pack(anchor="w")

        car_var = tk.StringVar(
            value=list(car_map.keys())[0]
        )

        combo = ttk.Combobox(
            form,
            textvariable=car_var,
            values=list(car_map.keys()),
            state="readonly"
        )

        combo.pack(
            fill="x",
            pady=(4, 12)
        )

        def field(label, default=""):

            tk.Label(
                form,
                text=label,
                bg=c["bg"],
                fg=c["muted"]
            ).pack(anchor="w")

            var = tk.StringVar(
                value=default
            )

            entry = tk.Entry(
                form,
                textvariable=var,
                bg=c["input"],
                fg=c["text"],
                insertbackground=c["text"],
                relief="flat"
            )

            entry.pack(
                fill="x",
                ipady=7,
                pady=(4, 10)
            )

            return var

        date_var = field(
            "Дата",
            date.today().isoformat()
        )

        mileage_var = field(
            "Пробег",
            "0"
        )

        if mode == "service":

            category_var = field(
                "Категория",
                "ТО"
            )

            description_var = field(
                "Работа",
                ""
            )

            cost_var = field(
                "Стоимость",
                "0"
            )

            workshop_var = field(
                "Сервис",
                ""
            )

        else:

            liters_var = field(
                "Количество литров",
                "0"
            )

            price_var = field(
                "Цена за литр",
                "0"
            )

            station_var = field(
                "АЗС",
                ""
            )

        def save():

            try:

                car_id = car_map[
                    car_var.get()
                ]

                mileage = int(
                    mileage_var.get() or 0
                )

                if mode == "service":

                    cost = float(
                        cost_var.get() or 0
                    )

                    self.db.add_service({
                        "car_id": car_id,
                        "date": date_var.get(),
                        "mileage": mileage,
                        "category": category_var.get(),
                        "description": description_var.get(),
                        "cost": cost,
                        "workshop": workshop_var.get()
                    })

                else:

                    liters = float(
                        liters_var.get() or 0
                    )

                    price = float(
                        price_var.get() or 0
                    )

                    self.db.add_fuel({
                        "car_id": car_id,
                        "date": date_var.get(),
                        "mileage": mileage,
                        "liters": liters,
                        "price": price,
                        "total": liters * price,
                        "station": station_var.get()
                    })

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Проверьте числовые значения.",
                    parent=dialog
                )

                return

            dialog.destroy()

            if mode == "service":
                self.show_service()
            else:
                self.show_fuel()

        buttons = tk.Frame(
            dialog,
            bg=c["bg"]
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=20
        )

        self.primary_button(
            buttons,
            "Сохранить",
            save
        ).pack(side="right")

        tk.Button(
            buttons,
            text="Отмена",
            command=dialog.destroy,
            relief="flat",
            bd=0,
            bg=c["surface2"],
            fg=c["text"],
            padx=15,
            pady=8
        ).pack(
            side="right",
            padx=8
        )

    # ========================================================
    # REMINDERS
    # ========================================================

    def show_reminders(self):

        self.current_page = "reminders"

        self.clear_content()

        self.page_title(
            "Напоминания",
            "Не забывайте о важных работах"
        )

        toolbar = tk.Frame(
            self.content,
            bg=self.colors["bg"]
        )

        toolbar.pack(
            fill="x",
            padx=32,
            pady=(0, 12)
        )

        self.primary_button(
            toolbar,
            "＋ Добавить напоминание",
            self.add_reminder_dialog
        ).pack(side="left")

        table = tk.Frame(
            self.content,
            bg=self.colors["surface"]
        )

        table.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(0, 25)
        )

        columns = (
            "car",
            "title",
            "date",
            "mileage",
            "status"
        )

        tree = ttk.Treeview(
            table,
            columns=columns,
            show="headings"
        )

        headings = {
            "car": "Автомобиль",
            "title": "Задача",
            "date": "Дата",
            "mileage": "Пробег",
            "status": "Статус"
        }

        for col in columns:

            tree.heading(
                col,
                text=headings[col]
            )

            tree.column(
                col,
                width=160
            )

        tree.pack(
            fill="both",
            expand=True
        )

        for row in self.db.get_reminders():

            status = "Просрочено"

            if row["due_date"]:

                try:

                    if row["due_date"] >= date.today().isoformat():
                        status = "Запланировано"

                except Exception:
                    pass

            tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    f"{row['make']} {row['model']}",
                    row["title"],
                    row["due_date"] or "—",
                    (
                        f"{row['due_mileage']:,} км"
                        if row["due_mileage"]
                        else "—"
                    ),
                    status
                )
            )

    def add_reminder_dialog(self):

        cars = self.db.get_cars()

        if not cars:

            messagebox.showinfo(
                "Car Manager",
                "Сначала добавьте автомобиль."
            )

            return

        c = self.colors

        dialog = tk.Toplevel(self)

        dialog.title(
            "Новое напоминание"
        )

        dialog.geometry(
            "500x420"
        )

        dialog.configure(
            bg=c["bg"]
        )

        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Новое напоминание",
            bg=c["bg"],
            fg=c["text"],
            font=("Segoe UI Semibold", 19)
        ).pack(
            anchor="w",
            padx=30,
            pady=(25, 20)
        )

        form = tk.Frame(
            dialog,
            bg=c["bg"]
        )

        form.pack(
            fill="both",
            expand=True,
            padx=30
        )

        car_map = {
            f"{car['make']} {car['model']}":
                car["id"]
            for car in cars
        }

        tk.Label(
            form,
            text="Автомобиль",
            bg=c["bg"],
            fg=c["muted"]
        ).pack(anchor="w")

        car_var = tk.StringVar(
            value=list(car_map)[0]
        )

        combo = ttk.Combobox(
            form,
            textvariable=car_var,
            values=list(car_map),
            state="readonly"
        )

        combo.pack(
            fill="x",
            pady=(4, 12)
        )

        def make_field(
            label,
            default=""
        ):

            tk.Label(
                form,
                text=label,
                bg=c["bg"],
                fg=c["muted"]
            ).pack(anchor="w")

            var = tk.StringVar(
                value=default
            )

            tk.Entry(
                form,
                textvariable=var,
                bg=c["input"],
                fg=c["text"],
                insertbackground=c["text"],
                relief="flat"
            ).pack(
                fill="x",
                ipady=7,
                pady=(4, 10)
            )

            return var

        title_var = make_field(
            "Что сделать?",
            "Замена масла"
        )

        date_var = make_field(
            "Дата",
            date.today().isoformat()
        )

        mileage_var = make_field(
            "Пробег",
            "0"
        )

        def save():

            try:

                mileage = int(
                    mileage_var.get() or 0
                )

            except ValueError:

                messagebox.showwarning(
                    "Car Manager",
                    "Пробег должен быть числом.",
                    parent=dialog
                )

                return

            self.db.add_reminder({
                "car_id": car_map[
                    car_var.get()
                ],
                "title": title_var.get(),
                "due_date": date_var.get(),
                "due_mileage": mileage
            })

            dialog.destroy()

            self.show_reminders()

        buttons = tk.Frame(
            dialog,
            bg=c["bg"]
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=20
        )

        self.primary_button(
            buttons,
            "Создать",
            save
        ).pack(side="right")

        tk.Button(
            buttons,
            text="Отмена",
            command=dialog.destroy,
            relief="flat",
            bd=0,
            bg=c["surface2"],
            fg=c["text"],
            padx=15,
            pady=8
        ).pack(
            side="right",
            padx=8
        )

    # ========================================================
    # CSV EXPORT
    # ========================================================

    def export_csv(self):

        filename = filedialog.asksaveasfilename(
            title="Экспорт автомобилей",
            defaultextension=".csv",
            filetypes=[
                (
                    "CSV files",
                    "*.csv"
                )
            ]
        )

        if not filename:
            return

        cars = self.db.get_cars()

        try:

            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(
                    file,
                    delimiter=";"
                )

                writer.writerow([
                    "Марка",
                    "Модель",
                    "Год",
                    "Пробег",
                    "Двигатель",
                    "КПП",
                    "Привод",
                    "Цвет",
                    "Госномер",
                    "VIN",
                    "Заметки"
                ])

                for car in cars:

                    writer.writerow([
                        car["make"],
                        car["model"],
                        car["year"],
                        car["mileage"],
                        car["engine"],
                        car["transmission"],
                        car["drive"],
                        car["color"],
                        car["plate"],
                        car["vin"],
                        car["notes"]
                    ])

            messagebox.showinfo(
                "Car Manager",
                "Данные успешно экспортированы."
            )

        except Exception as error:

            messagebox.showerror(
                "Ошибка",
                str(error)
            )

    # ========================================================
    # THEME
    # ========================================================

    def set_theme(self, theme):

        if theme not in THEMES:
            return

        self.theme_name = theme
        self.colors = THEMES[theme]

        self.configure(
            bg=self.colors["bg"]
        )

        self.setup_style()

        self.create_menu()
        self.create_sidebar()

        if self.current_page == "dashboard":
            self.refresh_dashboard()

        elif self.current_page == "garage":
            self.show_garage()

        elif self.current_page == "service":
            self.show_service()

        elif self.current_page == "fuel":
            self.show_fuel()

        elif self.current_page == "reminders":
            self.show_reminders()

    # ========================================================
    # ABOUT
    # ========================================================

    def about(self):

        messagebox.showinfo(
            "Car Manager",
            "Car Manager\n\n"
            f"Версия {VERSION}\n\n"
            "Современный менеджер автомобиля "
            "для обслуживания, расходов, топлива "
            "и напоминаний.\n\n"
            "Автор:\n"
            "Artem Sukhinin\n\n"
            "Telegram:\n"
            "https://t.me/artem_sukhinin"
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        try:
            self.db.close()
        except Exception:
            pass

        self.destroy()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app = CarManager()

    app.mainloop()
