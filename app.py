import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import socket
import urllib.request
import time
from datetime import datetime
from collections import deque
import webbrowser
import sys
import re


# ============================================================
# INTERNET MONITOR
# Author: Artem Sukhinin
# Telegram: https://t.me/artem_sukhinin
# ============================================================

APP_NAME = "Internet Monitor"
VERSION = "1.0.0"

AUTHOR = "Artem Sukhinin"
TELEGRAM_URL = "https://t.me/artem_sukhinin"

CHECK_INTERVAL = 5
HISTORY_LIMIT = 60

# Сервисы, которые будем проверять
SERVICES = [
    ("Google", "https://www.google.com/generate_204"),
    ("Cloudflare", "https://www.cloudflare.com/cdn-cgi/trace"),
    ("Telegram", "https://telegram.org"),
    ("GitHub", "https://github.com"),
]

history = deque(maxlen=HISTORY_LIMIT)
running = True


# ============================================================
# NETWORK FUNCTIONS
# ============================================================

def ping_host(host="1.1.1.1"):
    """
    Проверка ping.
    Возвращает миллисекунды или None.
    """

    try:
        if sys.platform.startswith("win"):
            command = [
                "ping",
                "-n",
                "1",
                "-w",
                "1800",
                host
            ]
        else:
            command = [
                "ping",
                "-c",
                "1",
                "-W",
                "2",
                host
            ]

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=4
        )

        if process.returncode != 0:
            return None

        match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*ms",
            process.stdout,
            re.IGNORECASE
        )

        if match:
            return float(
                match.group(1).replace(",", ".")
            )

        return None

    except Exception:
        return None


def check_http(url):
    """
    Проверяет доступность сайта.
    Возвращает:
        status_code, response_time
    """

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "InternetMonitor/1.0"
            }
        )

        started = time.perf_counter()

        with urllib.request.urlopen(
            request,
            timeout=5
        ) as response:

            response.read(1)

            elapsed = (
                time.perf_counter() - started
            ) * 1000

            return (
                response.status,
                round(elapsed, 1)
            )

    except Exception:
        return None, None


def check_dns():
    """
    Проверяет DNS через разрешение google.com.
    """

    try:

        started = time.perf_counter()

        socket.gethostbyname(
            "google.com"
        )

        elapsed = (
            time.perf_counter() - started
        ) * 1000

        return round(elapsed, 1)

    except Exception:
        return None


def get_local_ip():
    """
    Получает локальный IPv4.
    """

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(
            ("1.1.1.1", 80)
        )

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except Exception:
        return "Недоступен"


# ============================================================
# MAIN APPLICATION
# ============================================================

class InternetMonitor(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(
            f"{APP_NAME} {VERSION}"
        )

        self.geometry(
            "1000x720"
        )

        self.minsize(
            850,
            620
        )

        self.configure(
            bg="#0b1220"
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        # ----------------------------------------------------
        # Variables
        # ----------------------------------------------------

        self.status_var = tk.StringVar(
            value="Проверка..."
        )

        self.ping_var = tk.StringVar(
            value="—"
        )

        self.dns_var = tk.StringVar(
            value="—"
        )

        self.ip_var = tk.StringVar(
            value=get_local_ip()
        )

        self.checks_var = tk.StringVar(
            value="0"
        )

        self.last_check_var = tk.StringVar(
            value="Последняя проверка: —"
        )

        self.service_vars = {}

        for name, _ in SERVICES:
            self.service_vars[name] = tk.StringVar(
                value="Проверка..."
            )

        self.create_styles()
        self.create_interface()

        # Запускаем первую проверку
        self.after(
            500,
            self.start_check
        )

    # ========================================================
    # STYLES
    # ========================================================

    def create_styles(self):

        style = ttk.Style(self)

        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#111a2b",
            fieldbackground="#111a2b",
            foreground="#e7edf7",
            borderwidth=0,
            rowheight=36,
            font=(
                "Segoe UI",
                10
            )
        )

        style.configure(
            "Treeview.Heading",
            background="#17233a",
            foreground="#9fb1ca",
            relief="flat",
            font=(
                "Segoe UI Semibold",
                9
            )
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#1e4f8a")
            ]
        )

    # ========================================================
    # UI HELPERS
    # ========================================================

    def create_card(
        self,
        parent,
        title,
        variable
    ):

        frame = tk.Frame(
            parent,
            bg="#111a2b",
            highlightbackground="#1e2b43",
            highlightthickness=1
        )

        frame.pack_propagate(False)

        tk.Label(
            frame,
            text=title,
            bg="#111a2b",
            fg="#91a3bd",
            font=(
                "Segoe UI",
                9
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 3)
        )

        tk.Label(
            frame,
            textvariable=variable,
            bg="#111a2b",
            fg="#f2f6fb",
            font=(
                "Segoe UI Semibold",
                21
            )
        ).pack(
            anchor="w",
            padx=18
        )

        return frame

    # ========================================================
    # INTERFACE
    # ========================================================

    def create_interface(self):

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = tk.Frame(
            self,
            bg="#0b1220"
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(25, 5)
        )

        tk.Label(
            header,
            text="Internet Monitor",
            bg="#0b1220",
            fg="#f4f7fb",
            font=(
                "Segoe UI Semibold",
                28
            )
        ).pack(
            anchor="w"
        )

        tk.Label(
            header,
            text="Мониторинг стабильности интернет-соединения",
            bg="#0b1220",
            fg="#8293ad",
            font=(
                "Segoe UI",
                11
            )
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status_frame = tk.Frame(
            header,
            bg="#111a2b",
            highlightbackground="#1e2b43",
            highlightthickness=1
        )

        status_frame.place(
            relx=1.0,
            x=-5,
            y=10,
            anchor="ne"
        )

        self.status_dot = tk.Label(
            status_frame,
            text="●",
            bg="#111a2b",
            fg="#f59e0b",
            font=(
                "Segoe UI",
                18
            )
        )

        self.status_dot.pack(
            side="left",
            padx=(14, 5),
            pady=8
        )

        tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg="#111a2b",
            fg="#dce6f4",
            font=(
                "Segoe UI Semibold",
                10
            )
        ).pack(
            side="left",
            padx=(0, 14)
        )

        # ----------------------------------------------------
        # Cards
        # ----------------------------------------------------

        cards = tk.Frame(
            self,
            bg="#0b1220"
        )

        cards.pack(
            fill="x",
            padx=30,
            pady=20
        )

        cards.columnconfigure(
            0,
            weight=1
        )

        cards.columnconfigure(
            1,
            weight=1
        )

        cards.columnconfigure(
            2,
            weight=1
        )

        cards.columnconfigure(
            3,
            weight=1
        )

        card_data = [
            (
                "PING • 1.1.1.1",
                self.ping_var
            ),
            (
                "DNS • google.com",
                self.dns_var
            ),
            (
                "LOCAL IP",
                self.ip_var
            ),
            (
                "CHECKS",
                self.checks_var
            )
        ]

        for index, (
            title,
            variable
        ) in enumerate(card_data):

            card = self.create_card(
                cards,
                title,
                variable
            )

            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=5
            )

            card.configure(
                height=105
            )

        # ----------------------------------------------------
        # Services
        # ----------------------------------------------------

        services_title = tk.Label(
            self,
            text="Доступность сервисов",
            bg="#0b1220",
            fg="#f4f7fb",
            font=(
                "Segoe UI Semibold",
                14
            )
        )

        services_title.pack(
            anchor="w",
            padx=30,
            pady=(0, 8)
        )

        services_frame = tk.Frame(
            self,
            bg="#111a2b",
            highlightbackground="#1e2b43",
            highlightthickness=1
        )

        services_frame.pack(
            fill="x",
            padx=30
        )

        for name, _ in SERVICES:

            row = tk.Frame(
                services_frame,
                bg="#111a2b"
            )

            row.pack(
                fill="x",
                padx=18,
                pady=6
            )

            tk.Label(
                row,
                text=name,
                width=15,
                anchor="w",
                bg="#111a2b",
                fg="#dce6f4",
                font=(
                    "Segoe UI Semibold",
                    10
                )
            ).pack(
                side="left"
            )

            tk.Label(
                row,
                textvariable=self.service_vars[name],
                bg="#111a2b",
                fg="#91a3bd",
                font=(
                    "Segoe UI",
                    10
                )
            ).pack(
                side="left"
            )

        # ----------------------------------------------------
        # History
        # ----------------------------------------------------

        tk.Label(
            self,
            text="История проверок",
            bg="#0b1220",
            fg="#f4f7fb",
            font=(
                "Segoe UI Semibold",
                14
            )
        ).pack(
            anchor="w",
            padx=30,
            pady=(20, 8)
        )

        table_frame = tk.Frame(
            self,
            bg="#111a2b"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=30
        )

        columns = (
            "time",
            "ping",
            "dns",
            "internet"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading(
            "time",
            text="Время"
        )

        self.tree.heading(
            "ping",
            text="Ping"
        )

        self.tree.heading(
            "dns",
            text="DNS"
        )

        self.tree.heading(
            "internet",
            text="Интернет"
        )

        self.tree.column(
            "time",
            width=130
        )

        self.tree.column(
            "ping",
            width=150
        )

        self.tree.column(
            "dns",
            width=150
        )

        self.tree.column(
            "internet",
            width=180
        )

        self.tree.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        footer = tk.Frame(
            self,
            bg="#0b1220"
        )

        footer.pack(
            fill="x",
            padx=30,
            pady=15
        )

        tk.Label(
            footer,
            textvariable=self.last_check_var,
            bg="#0b1220",
            fg="#64758f",
            font=(
                "Segoe UI",
                9
            )
        ).pack(
            side="left"
        )

        telegram = tk.Label(
            footer,
            text="© Artem Sukhinin  •  Telegram: @artem_sukhinin",
            bg="#0b1220",
            fg="#4a90c2",
            cursor="hand2",
            font=(
                "Segoe UI",
                9,
                "underline"
            )
        )

        telegram.pack(
            side="right"
        )

        telegram.bind(
            "<Button-1>",
            lambda event: webbrowser.open(
                TELEGRAM_URL
            )
        )

    # ========================================================
    # NETWORK CHECK
    # ========================================================

    def start_check(self):

        if not running:
            return

        thread = threading.Thread(
            target=self.network_worker,
            daemon=True
        )

        thread.start()

    def network_worker(self):

        ping = ping_host()

        dns = check_dns()

        service_results = {}

        for name, url in SERVICES:

            status, response_time = check_http(
                url
            )

            online = (
                status is not None
                and 200 <= status < 500
            )

            service_results[name] = (
                online,
                response_time
            )

        internet_online = (
            ping is not None
            or any(
                result[0]
                for result in service_results.values()
            )
        )

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.after(
            0,
            lambda: self.update_interface(
                current_time,
                ping,
                dns,
                service_results,
                internet_online
            )
        )

    # ========================================================
    # UPDATE UI
    # ========================================================

    def update_interface(
        self,
        current_time,
        ping,
        dns,
        services,
        internet_online
    ):

        # Ping
        if ping is None:
            self.ping_var.set("—")
        else:
            self.ping_var.set(
                f"{ping:.0f} ms"
            )

        # DNS
        if dns is None:
            self.dns_var.set("—")
        else:
            self.dns_var.set(
                f"{dns:.0f} ms"
            )

        # Checks
        self.checks_var.set(
            str(len(history) + 1)
        )

        # Last check
        self.last_check_var.set(
            f"Последняя проверка: {current_time}"
        )

        # Status
        if internet_online:

            self.status_var.set(
                "Интернет работает"
            )

            self.status_dot.configure(
                fg="#35d07f"
            )

        else:

            self.status_var.set(
                "Интернет недоступен"
            )

            self.status_dot.configure(
                fg="#ff5f6d"
            )

        # Services
        for name, (
            online,
            response_time
        ) in services.items():

            if online:

                if response_time is not None:

                    text = (
                        f"● Online   "
                        f"{response_time:.0f} ms"
                    )

                else:

                    text = "● Online"

                self.service_vars[name].set(
                    text
                )

            else:

                self.service_vars[name].set(
                    "● Offline / timeout"
                )

        # Save history
        history.appendleft(
            (
                current_time,
                ping,
                dns,
                internet_online
            )
        )

        # Refresh table
        self.tree.delete(
            *self.tree.get_children()
        )

        for (
            current_time,
            ping,
            dns,
            online
        ) in history:

            self.tree.insert(
                "",
                "end",
                values=(
                    current_time,

                    "—"
                    if ping is None
                    else f"{ping:.0f} ms",

                    "—"
                    if dns is None
                    else f"{dns:.0f} ms",

                    "ONLINE"
                    if online
                    else "OFFLINE"
                )
            )

        # Schedule next check
        self.after(
            CHECK_INTERVAL * 1000,
            self.start_check
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close_app(self):

        global running

        running = False

        self.destroy()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app = InternetMonitor()

    app.mainloop()
