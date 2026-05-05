import sys
import os
import time
import subprocess
from PySide import QtCore, QtGui

# Core Imports
from API import process, shutdown_core
from API.QuTensors.Configure import Configure

class QumiNotification(QtGui.QWidget):
    """Sliding notification that moves from off-screen right to left."""
    def __init__(self, title, message, parent=None):
        super(QumiNotification, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.ToolTip | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Layout & Style
        self.main_layout = QtGui.QVBoxLayout(self)
        self.bg = QtGui.QFrame()
        self.bg.setObjectName("NotifyBG")
        self.bg.setStyleSheet("""
            #NotifyBG { 
                background-color: #252526; 
                border: 1px solid #007acc; 
                border-radius: 4px; 
            }
        """)
        
        bg_layout = QtGui.QVBoxLayout(self.bg)
        title_lbl = QtGui.QLabel(title.upper())
        title_lbl.setStyleSheet("color: #007acc; font-weight: bold; font-family: 'Segoe UI', Arial; font-size: 9pt;")
        
        msg_lbl = QtGui.QLabel(message)
        msg_lbl.setStyleSheet("color: #d4d4d4; font-family: 'Segoe UI', Arial; font-size: 10pt;")
        msg_lbl.setWordWrap(True)
        
        bg_layout.addWidget(title_lbl)
        bg_layout.addWidget(msg_lbl)
        self.main_layout.addWidget(self.bg)
        
        self.setFixedSize(280, 90)
        
        # Setup Animation
        #self.anim = QtCore.QPropertyAnimation(self, "pos")
        #self.anim.setDuration(600)
        #self.anim.setEasingCurve()
        # Commented Out Due To Easing Curves Invalid.
    def slide_in(self):
        screen = QtGui.QApplication.desktop().screenGeometry()
        self.start_pos = QtCore.QPoint(screen.width(), screen.height() - 140)
        self.end_pos = QtCore.QPoint(screen.width() - 300, screen.height() - 140)
        
        self.move(self.start_pos)
        self.show()
        
        self.anim.setStartValue(self.start_pos)
        self.anim.setEndValue(self.end_pos)
        self.anim.start()
        
        # Auto-slide out after 4 seconds
        QtCore.QTimer.singleShot(4000, self.slide_out)
    def slide_out(self):
        screen = QtGui.QApplication.desktop().screenGeometry()
        exit_pos = QtCore.QPoint(screen.width(), self.y())
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(exit_pos)
        self.anim.finished.connect(self.close)
        self.anim.start()
    def visibility(self, boolean : bool):
        if boolean == False:
            self.setVisible(False)
        else:
            self.setVisible(True)


class ChatUI(QtGui.QMainWindow):
    def __init__(self):
        super(ChatUI, self).__init__()
        self.config = Configure()
        self.init_ui()
        
        # Boot-up Notification
        QtCore.QTimer.singleShot(800, lambda: self.notify("Neural Link", "Qumi Q3 character-stream active."))

    def init_ui(self):
        self.setWindowTitle("Qumi Q3 - Neural IDE")
        self.resize(1150, 750)
        self.apply_theme()

        # --- MENU BAR ---
        menubar = self.menuBar()
        file_m = menubar.addMenu("&File")
        db_act = QtGui.QAction("Select Brain (.db)", self)
        db_act.triggered.connect(self.select_db)
        file_m.addAction(db_act)
        file_m.addSeparator()
        file_m.addAction(QtGui.QAction("Exit", self, triggered=self.close))

        # --- MAIN SPLITTER ---
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # --- SIDEBAR ---
        self.sidebar = QtGui.QTabWidget()
        self.sidebar.setTabPosition(QtGui.QTabWidget.West)
        self.sidebar.setFixedWidth(320)

        # 1. Telemetry / Profile Panel
        self.prof_panel = QtGui.QWidget()
        p_layout = QtGui.QVBoxLayout(self.prof_panel)
        p_layout.addWidget(QtGui.QLabel("<b>SENSORY TELEMETRY</b>"))

        # Detailed data from qu.conf
        name = self.config.get_config_value("Displayname") or "Operator"
        q_name = self.config.get_config_value("QQName") or "Qumi"
        q_age = self.config.get_config_value("QQAge") or "0"
        q_dob = self.config.get_config_value("QQDOB") or "N/A"
        
        p_layout.addWidget(QtGui.QLabel("Operator: " + name))
        p_layout.addWidget(QtGui.QLabel("Entity: " + q_name))
        p_layout.addWidget(QtGui.QLabel("Entity Age: " + q_age))
        p_layout.addWidget(QtGui.QLabel("DOB: " + q_dob))

        line = QtGui.QFrame(); line.setFrameShape(QtGui.QFrame.HLine); p_layout.addWidget(line)

        p_layout.addWidget(QtGui.QLabel("<b>TENSOR CONFIG</b>"))
        in_s = self.config.get_config_value("NeuralNetInputSize") or "3"
        hid_s = self.config.get_config_value("NeuralNetHiddenSize") or "6"
        p_layout.addWidget(QtGui.QLabel("Input Resolution: " + in_s))
        p_layout.addWidget(QtGui.QLabel("Hidden Layer: " + hid_s))

        # Tension Meter (ToPT)
        topt = int(self.config.get_config_value("ToPT") or 1)
        self.tension_bar = QtGui.QProgressBar()
        self.tension_bar.setValue(topt * 10)
        self.tension_bar.setFormat("Manifold Tension: %p%")
        p_layout.addWidget(self.tension_bar)
        
        p_layout.addStretch()
        self.sidebar.addTab(self.prof_panel, "User")

        # 2. External Programs Panel
        self.tools_panel = QtGui.QWidget()
        t_layout = QtGui.QVBoxLayout(self.tools_panel)
        t_layout.addWidget(QtGui.QLabel("<b>PROGRAM EXPLORER</b>"))
        self.tool_list = QtGui.QListWidget()
        self.tool_list.itemDoubleClicked.connect(self.launch_tool)
        t_layout.addWidget(self.tool_list)
        self.scan_tools()
        self.sidebar.addTab(self.tools_panel, "Tools")

        # 3. File Upload Panel
        self.up_panel = QtGui.QWidget()
        u_layout = QtGui.QVBoxLayout(self.up_panel)
        u_layout.addWidget(QtGui.QLabel("<b>FILE STREAMER</b>"))
        self.btn_up = QtGui.QPushButton("Upload & Feed Brain")
        self.btn_up.clicked.connect(self.upload_and_feed)
        u_layout.addWidget(self.btn_up)
        u_layout.addStretch()
        self.sidebar.addTab(self.up_panel, "Upload")

        # --- CHAT AREA ---
        chat_container = QtGui.QWidget()
        chat_layout = QtGui.QVBoxLayout(chat_container)
        
        self.chat_log = QtGui.QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setHtml("<body style='color:#d4d4d4;'><i>Awaiting input signals...</i></body>")
        chat_layout.addWidget(self.chat_log)

        input_row = QtGui.QHBoxLayout()
        self.input_field = QtGui.QLineEdit()
        self.input_field.setPlaceholderText("Send signal to Qumi manifold...")
        self.input_field.returnPressed.connect(self.send_msg)
        
        btn_send = QtGui.QPushButton("SEND")
        btn_send.setFixedWidth(80)
        btn_send.clicked.connect(self.send_msg)
        
        input_row.addWidget(self.input_field)
        input_row.addWidget(btn_send)
        chat_layout.addLayout(input_row)

        # Assemble Splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(chat_container)
        self.setCentralWidget(self.splitter)

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QTextEdit { background-color: #1e1e1e; border: 1px solid #333; color: #9cdcfe; font-family: 'Consolas', monospace; }
            QLineEdit { background-color: #3c3c3c; border: 1px solid #555; color: white; padding: 6px; }
            QPushButton { background-color: #0e639c; color: white; border: none; padding: 8px; }
            QPushButton:hover { background-color: #1177bb; }
            QProgressBar { border: 1px solid #444; background: #252526; text-align: center; color: white; height: 15px; }
            QProgressBar::chunk { background-color: #007acc; }
            QTabBar::tab { background: #2d2d2d; color: #888; padding: 14px; }
            QTabBar::tab:selected { background: #1e1e1e; color: white; }
            QLabel { color: #858585; font-size: 9pt; }
        """)

    def notify(self, title, msg):
        self.notif = QumiNotification(title, msg, self)
        # Fallback since AnimationEASECURVE Has some issues..
        self.notif.visibility(True)
        time.sleep(2)
        self.notif.visibility(False)

    def scan_tools(self):
        self.tool_list.clear()
        valid = ["QuMoEditor.py", "db_validator.py", "CLI.py"]
        for f in os.listdir("."):
            if f in valid or f.endswith(".exe"):
                self.tool_list.addItem(f)

    def launch_tool(self, item):
        path = item.text()
        self.notify("External Task", "Spawning " + path)
        if path.endswith(".py"):
            subprocess.Popen([sys.executable, path])
        else:
            os.startfile(path)

    def select_db(self):
        path, _ = QtGui.QFileDialog.getOpenFileName(self, "Select Manifold", "QumiData", "Database (*.db)")
        if path:
            self.notify("DB Shift", "New manifold attached.")

    def upload_and_feed(self):
        path, _ = QtGui.QFileDialog.getOpenFileName(self, "Select Feed Data", "", "Text Files (*.txt *.py *.conf)")
        if path:
            with open(path, 'r') as f: data = f.read()
            self.chat_log.append("<span style='color:#ce9178;'>[Teacher] Feeding signal stream...</span>")
            process(data[:1000]) # Protect Atom CPU
            self.notify("Learning Complete", "Character synapses reinforced.")

    def send_msg(self):
        msg = self.input_field.text().strip()
        if not msg: return
        
        self.chat_log.append("<b style='color:#569cd6;'>YOU:</b> " + msg)
        self.input_field.clear()
        
        # Simulated thought latency
        self.chat_log.append("<i style='color:#6a9955;'>Qumi is dreaming...</i>")
        QtGui.QApplication.processEvents()
        time.sleep(0.2)
        
        # Remove "dreaming" and add real response
        cursor = self.chat_log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        
        resp = process(msg)
        self.chat_log.append("<b style='color:#ce9178;'>QUMI:</b> " + resp)
        self.chat_log.ensureCursorVisible()

    def closeEvent(self, event):
        shutdown_core()
        event.accept()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyle("Plastique")
    ui = ChatUI()
    ui.show()
    sys.exit(app.exec_())