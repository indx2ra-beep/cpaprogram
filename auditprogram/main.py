import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import webbrowser
import platform
import uuid


# -------------------------
# "SERVER" SIMULATION
# -------------------------

SERVER = {
    "latest_version": "1.1",
    "dev_message": "Welcome developer. System running normally.",
    "force_update": False
}


def get_device_id():
    return f"{uuid.getnode()}-{platform.node()}"


class AuditApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Audit Program")
        self.geometry("800x500")

        self.version = "1.0"
        self.device_id = get_device_id()

        self.data = {}

        self.create_widgets()

        self.after(1000, self.startup_checks)

    # -------------------------
    # STARTUP CHECKS
    # -------------------------

    def startup_checks(self):
        self.check_updates()
        self.check_dev_message()

    def is_developer(self):
        # Replace this with YOUR real device ID after printing it once
        DEVICES = [
            "123456789-your-device-name"
        ]
        return self.device_id in DEVICES

    def check_updates(self):
        latest = SERVER["latest_version"]

        if latest != self.version:
            msg = f"Update available: v{latest}\nCurrent version: v{self.version}"

            if SERVER["force_update"]:
                messagebox.showwarning("Update Required", msg)
            else:
                messagebox.showinfo("Update Available", msg)

    def check_dev_message(self):
        if self.is_developer():
            msg = SERVER.get("dev_message")
            if msg:
                messagebox.showinfo("Developer Message", msg)

    # -------------------------
    # UI
    # -------------------------

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=10)

        ttk.Button(top, text="Load 401(k)", command=self.load_401k).pack(side="left", padx=5)
        ttk.Button(top, text="Load Payroll YTD", command=self.load_payroll_ytd).pack(side="left", padx=5)
        ttk.Button(top, text="Load Weekly", command=self.load_weekly).pack(side="left", padx=5)
        ttk.Button(top, text="Load TEST DATA", command=self.load_test_data).pack(side="left", padx=5)
        ttk.Button(top, text="Export CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(top, text="Clear", command=self.clear_data).pack(side="left", padx=5)

        ttk.Label(self, text=f"Device ID: {self.device_id}").pack()

        self.status = ttk.Label(self, text="Ready")
        self.status.pack()

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
        self.tree.pack(fill="both", expand=True)

    # -------------------------
    # DATA MODEL
    # -------------------------

    def get_row(self, name):
        name = str(name).strip().lower()

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

        self.refresh()
        self.status.config(text="Test data loaded")

    # -------------------------
    # PLACEHOLDER LOADERS
    # -------------------------

    def load_401k(self):
        self.status.config(text="401(k) loader not implemented yet")

    def load_payroll_ytd(self):
        self.status.config(text="Payroll loader not implemented yet")

    def load_weekly(self):
        self.status.config(text="Weekly loader not implemented yet")

    # -------------------------
    # TABLE
    # -------------------------

    def refresh(self):
        self.tree.delete(*self.tree.get_children())

        df = pd.DataFrame(self.data.values())

        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    # -------------------------
    # EXPORT
    # -------------------------

    def export_csv(self):
        if not self.data:
            messagebox.showwarning("No data", "No data to export")
            return

        file = filedialog.asksaveasfilename(defaultextension=".csv")

        if file:
            pd.DataFrame(self.data.values()).to_csv(file, index=False)
            messagebox.showinfo("Success", "Export complete")

    def clear_data(self):
        self.data = {}
        self.refresh()
        self.status.config(text="Cleared")


if __name__ == "__main__":
    app = AuditApp()
    app.mainloop()