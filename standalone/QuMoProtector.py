import os
import hashlib
import platform
import subprocess
from PySide import QtCore, QtGui

class QuMoProtector:
    """Handles HWID generation and Product Key validation."""
    
    @staticmethod
    def get_hwid():
        """Generates a unique hardware hash based on CPU and OS info."""
        # Using platform info + processor ID for a classic 'Product ID' feel
        raw_id = platform.processor() + platform.node() + platform.machine()
        # On Windows, we can try to get the Volume Serial of C:
        try:
            vol = subprocess.check_output("vol c:", shell=True).decode()
            raw_id += vol.strip().split()[-1]
        except:
            pass
        
        return hashlib.md5(raw_id.encode()).hexdigest().upper()[:16]

    @staticmethod
    def generate_key(hwid):
        """The 'Server-Side' logic to create a key for a specific HWID."""
        # Simple algorithm: Hash the HWID with a secret salt
        salt = "WIMNI_SECRET_2026"
        full_hash = hashlib.sha256((hwid + salt).encode()).hexdigest().upper()
        # Format as XXXX-XXXX-XXXX-XXXX
        print("-".join([full_hash[i:i+4] for i in range(0, 16, 4)]))
        return "-".join([full_hash[i:i+4] for i in range(0, 16, 4)])

    @staticmethod
    def check_activation(config_path="QuMo.config"):
        """Checks if the system is activated or in Dev Mode."""
        if not os.path.exists(config_path):
            return False, "MISSING_CONFIG"

        config = {}
        with open(config_path, "r") as f:
            for line in f:
                if "=" in line:
                    name, val = line.strip().split("=")
                    config[name] = val

        # 1. Developer Soft-Lock Override
        if config.get("MODE") == "OPEN-SOFT":
            return True, "DEVELOPER_MODE"

        # 2. Hard-Lock Validation
        user_key = config.get("ProductKey", "")
        hwid = QuMoProtector.get_hwid()
        valid_key = QuMoProtector.generate_key(hwid)

        if user_key == valid_key:
            return True, "ACTIVATED"
        
        return False, "NOT_ACTIVATED"

class ActivationUI(QtGui.QDialog):
    """The 'Windows Activation' style popup."""
    def __init__(self):
        super(ActivationUI, self).__init__()
        self.hwid = QuMoProtector.get_hwid()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QuMo Product Activation")
        self.setFixedSize(400, 250)
        layout = QtGui.QVBoxLayout(self)

        layout.addWidget(QtGui.QLabel("<b>Your Installation ID (HWID):</b>"))
        self.txt_hwid = QtGui.QLineEdit(self.hwid)
        self.txt_hwid.setReadOnly(True)
        layout.addWidget(self.txt_hwid)

        layout.addWidget(QtGui.QLabel("<b>Enter Product Key:</b>"))
        self.txt_key = QtGui.QLineEdit()
        self.txt_key.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        layout.addWidget(self.txt_key)

        self.btn_activate = QtGui.QPushButton("Activate Advanced Features")
        self.btn_activate.clicked.connect(self.do_activate)
        layout.addWidget(self.btn_activate)
        
        self.lbl_status = QtGui.QLabel("Advanced features are currently locked.")
        layout.addWidget(self.lbl_status)

    def do_activate(self):
        key = self.txt_key.text().strip()
        expected = QuMoProtector.generate_key(self.hwid)
        
        if key == expected:
            with open("QuMo.config", "w") as f:
                f.write("MODE=PRODUCTION\n")
                f.write("ProductKey={0}\n".format(key))
            QtGui.QMessageBox.information(self, "Success", "Product Activated! Restart the application.")
            self.accept()
        else:
            QtGui.QMessageBox.critical(self, "Invalid Key", "The key entered does not match this hardware.")

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setStyle("Plastique")
    
    # Check status
    active, status = QuMoProtector.check_activation()
    if not active:
        ui = ActivationUI()
        ui.exec_()
    else:
        print("Running in mode: " + status)