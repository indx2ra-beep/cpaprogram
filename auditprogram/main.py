import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import webbrowser
import requests
import hashlib
import os
import platform
import uuid


class AuditApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Audit Program")
        self.geometry("800x500")

        self.data = {}

        # -------------------------
        # VERSION + UPDATE SYSTEM
        # -------------------------
        self.version = "1.0"

        self.GITHUB_URL = "https://raw.githubusercontent.com/indx2ra-beep/cpaprogram/main/README.md"
        self.LOCAL_HASH_FILE = "github_hash.txt"

        self.device_id = f"{uuid.getnode()}-{platform.node()}"

        self.create_widgets()

        # run update check after UI loads (non-blocking)
        self.after(1000, self.check_github_update)

    # -------------------------
    # GITHUB UPDATE SYSTEM
    # -------------------------

    def get_remote_hash(self):
        try:
            r = requests.get(self.GITHUB_URL, timeout=5)
            r.raise_for_status()
            return hashlib.sha256(r.text.encode()).hexdigest()
        except:
            return None

    def get_local_hash(self):
        if not os.path.exists(self.LOCAL_HASH_FILE):
            return None
        with open(self.LOCAL_HASH_FILE, "r") as f:
            return f.read().strip()

    def save_local_hash(self, value):
        with open(self.LOCAL_HASH_FILE, "w") as f:
            f.write(value)

    def check_github_update(self):
        remote_hash = self.get_remote_hash()
        local_hash = self.get_local_hash()

        if not remote_hash:
            return

        # first run setup
        if local_hash is None:
            self.save_local_hash(remote_hash)
            return

        if remote_hash != local_hash:
            self.prompt_update()
            self.save_local_hash(remote_hash)

    def prompt_update(self):
        messagebox.showinfo(
            "Update Available",
            "The application has been updated on GitHub (README.md changed)."
        )

    def contact_developer(self):
        webbrowser.open_new_tab("mailto:indx.2ra@gmail.com")
        
    # -------------------------
    # UI
    # -------------------------

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=10)

        ttk.Button(top, text="Load 401(k) PDF", command=self.load_401k).pack(side="left", padx=5)
        ttk.Button(top, text="Load Payroll YTD", command=self.load_payroll_ytd).pack(side="left", padx=5)
        ttk.Button(top, text="Load Weekly Payroll", command=self.load_weekly).pack(side="left", padx=5)
        ttk.Button(top, text="Load TEST DATA", command=self.load_test_data).pack(side="left", padx=5)
        ttk.Button(top, text="Export Excel", command=self.export_excel).pack(side="left", padx=5)
        ttk.Button(top, text="Clear", command=self.clear_data).pack(side="left", padx=5)
        ttk.Button(top, text="Contact Developer", command=self.contact_developer).pack(side="left", padx=5)

        self.status = ttk.Label(self, text=f"Ready | Device: {self.device_id}")
        self.status.pack(pady=5)

        preview = ttk.Label(
            self,
            text="developer preview 1.0",
            foreground="blue",
            cursor="hand2"
        )
        preview.pack(anchor="ne")
        preview.bind("<Button-1>", lambda e: webbrowser.open_new_tab(
            "https://github.com/indx2ra-beep/cpaprogram"
        ))

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # -------------------------
    # DATA MODEL
    # -------------------------

    def normalize(self, name):
        return str(name).strip().lower()

    def get_row(self, name):
        name = self.normalize(name)

        if name not in self.data:
            self.data[name] = {
                "Employee Name": name,
                "401k Employee Contributions": 0,
                "401k Employer Contributions": 0,
                "Payroll Employee Contributions YTD": 0,
                "Payroll Wages YTD": 0,
                "Weekly Employee Contributions": 0,
                "Weekly Wages": 0,
            }

        return self.data[name]

    # -------------------------
    # LOADERS
    # -------------------------

    def load_401k(self):
        file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file:
            for row in self.parse_401k(file):
                r = self.get_row(row["Employee Name"])
                r["401k Employee Contributions"] = row.get("401k Employee Contributions", 0)
                r["401k Employer Contributions"] = row.get("401k Employer Contributions", 0)

            self.refresh_table()
            self.status.config(text="Loaded 401(k)")

    def load_payroll_ytd(self):
        file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file:
            for row in self.parse_payroll_ytd(file):
                r = self.get_row(row["Employee Name"])
                r["Payroll Employee Contributions YTD"] = row.get("Payroll Employee Contributions YTD", 0)
                r["Payroll Wages YTD"] = row.get("Payroll Wages YTD", 0)

            self.refresh_table()
            self.status.config(text="Loaded Payroll YTD")

    def load_weekly(self):
        file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file:
            for row in self.parse_weekly(file):
                r = self.get_row(row["Employee Name"])
                r["Weekly Employee Contributions"] += row.get("Weekly Employee Contributions", 0)
                r["Weekly Wages"] += row.get("Weekly Wages", 0)

            self.refresh_table()
            self.status.config(text="Loaded Weekly Payroll")

    # -------------------------
    # TEST DATA
    # -------------------------

    def load_test_data(self):
        test = [
            ("John Doe", 5000, 2500, 5000, 80000, 100, 1500),
            ("Jane Smith", 3200, 1600, 3200, 62000, 80, 1400),
        ]

        for name, c1, c2, py, wage, wc, ww in test:
            r = self.get_row(name)
            r["401k Employee Contributions"] = c1
            r["401k Employer Contributions"] = c2
            r["Payroll Employee Contributions YTD"] = py
            r["Payroll Wages YTD"] = wage
            r["Weekly Employee Contributions"] += wc
            r["Weekly Wages"] += ww

        self.refresh_table()
        self.status.config(text="Loaded TEST DATA")

    # -------------------------
    # PLACEHOLDERS
    # -------------------------

    def parse_401k(self, file):
        return []

    def parse_payroll_ytd(self, file):
        return []

    def parse_weekly(self, file):
        return []

    # -------------------------
    # TABLE
    # -------------------------

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())

        df = pd.DataFrame(self.data.values())

        if df.empty:
            return

        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    # -------------------------
    # EXPORT
    # -------------------------

    def export_excel(self):
        if not self.data:
            messagebox.showwarning("No data", "Nothing to export")
            return

        file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if file:
            df = pd.DataFrame(self.data.values())
            df.to_excel(file, index=False, engine="openpyxl")
            messagebox.showinfo("Success", "Excel export complete")

    def clear_data(self):
        self.data = {}
        self.refresh_table()
        self.status.config(text="Cleared")


if __name__ == "__main__":
    app = AuditApp()
    app.mainloop()
