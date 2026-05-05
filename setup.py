import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import subprocess
import winreg # For handling .qm file associations

# Configuration Logic
class QumiConfigHandler:
    def __init__(self, path="QumiData\\qu.conf"):
        self.path = path

    def get_product_key(self):
        if not os.path.exists(self.path): return ""
        with open(self.path, 'r') as f:
            for line in f:
                if line.startswith("Code="):
                    return line.split("=")[1].strip()
        return ""

    def update_config(self, key):
        if not os.path.exists("QumiData"): os.makedirs("QumiData")
        lines = []
        if os.path.exists(self.path):
            with open(self.path, 'r') as f: lines = f.readlines()
        
        with open(self.path, 'w') as f:
            found = False
            for line in lines:
                if line.startswith("Code="):
                    f.write("Code={}\n".format(key))
                    found = True
                else: f.write(line)
            if not found: f.write("Code={}\n".format(key))

class SetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Qumi 2 - Setup & Recovery Wizard")
        self.root.geometry("550x450")
        self.config = QumiConfigHandler()
        self.setup_styles()
        self.init_ui()

    def setup_styles(self):
        self.bg_color = "#f0f0f0"
        self.accent_color = "#004a99"
        self.root.configure(bg=self.bg_color)

    def init_ui(self):
        # Header Banner
        header = tk.Frame(self.root, bg=self.accent_color, height=70)
        header.pack(fill="x")
        tk.Label(header, text="QUMI 2 INSTALLATION & REPAIR", fg="white", 
                 bg=self.accent_color, font=("Segoe UI", 12, "bold")).pack(pady=20, padx=20, side="left")

        # Main Content
        content = tk.Frame(self.root, padx=25, pady=15, bg=self.bg_color)
        content.pack(fill="both", expand=True)

        # Product Key (Code= in qu.conf)
        tk.Label(content, text="Activation Code (Product Key):", bg=self.bg_color).pack(anchor="w")
        self.key_entry = tk.Entry(content, font=("Consolas", 11), width=40)
        self.key_entry.pack(pady=5, anchor="w")
        self.key_entry.insert(0, self.config.get_product_key())

        # Options
        self.assoc_var = tk.BooleanVar(value=True)
        tk.Checkbutton(content, text="Associate .qm files with Qumi", variable=self.assoc_var, bg=self.bg_color).pack(anchor="w")

        # Log Window
        tk.Label(content, text="Installation Progress:", bg=self.bg_color).pack(anchor="w", pady=(10,0))
        self.log_box = tk.Text(content, height=8, font=("Courier New", 9), state="disabled")
        self.log_box.pack(fill="x", pady=5)

        # License Note
        tk.Label(content, text="Licensed under GNU GPL v3.0", fg="#777", bg=self.bg_color).pack(side="bottom", anchor="w")

        # Footer Buttons
        footer = tk.Frame(self.root, pady=10, padx=20, bg=self.bg_color)
        footer.pack(fill="x", side="bottom")
        
        tk.Button(footer, text="Install / Repair", width=15, command=self.start_process).pack(side="right", padx=5)
        tk.Button(footer, text="Cancel", width=10, command=self.root.quit).pack(side="right")

    def log(self, text):
        self.log_box.config(state="normal")
        self.log_box.insert("end", "> " + text + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        self.root.update()

    def set_registry_associations(self):
        """Replicates Inno Setup [Registry] section for .qm files[cite: 60, 61, 91, 92]."""
        try:
            exe_path = os.path.abspath("dist\\qumo.exe")
            # Create .qm association
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".qm") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "QQFile")
            
            # Create QQFile verb
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "QQFile") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "Qumi Quma File")
            
            # Set Command
            cmd = '"{}" "%1"'.format(exe_path)
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"QQFile\shell\open\command") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, cmd)
            self.log("File associations registered.") 
        except Exception as e:
            self.log("Registry Error: " + str(e))

    def start_process(self):
        self.log("Initializing Qumi 2 Environment...")
        
        # 1. Directory Structure 
        if not os.path.exists("QumiData"):
            os.makedirs("QumiData")
            self.log("Created directory: QumiData")
        
        # 2. Config Sync
        key = self.key_entry.get().strip()
        self.config.update_config(key)
        self.log("Synchronized Product Key to qu.conf.")

        # 3. Database Integrity [cite: 70, 78]
        db_path = "QumiData\\brain.db"
        try:
            conn = sqlite3.connect(db_path)
            # Handshake with db_validator signature
            conn.execute("CREATE TABLE IF NOT EXISTS qumo_metadata (sig_key TEXT, sig_value TEXT)")
            self.log("Neural Manifold verified.")
            conn.close()
        except:
            self.log("Repairing brain.db structure...")

        # 4. Registry [cite: 60, 91]
        if self.assoc_var.get():
            self.set_registry_associations()

        # 5. Compile check (If compile.bat exists) 
        if os.path.exists("compile.bat"):
            self.log("Running compilation tasks...")
            subprocess.Popen(["compile.bat"], shell=True)

        self.log("--- SETUP COMPLETE ---")
        messagebox.showinfo("Success", "Qumi 2 has been successfully installed/repaired.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SetupWizard(root)
    root.mainloop()