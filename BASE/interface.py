import sys
from PySide import QtCore, QtGui
import API # This connects to the Master API initialized in API/__init__.py

class NeuralWorker(QtCore.QThread):
    """Handles the API call in a separate thread to keep the UI responsive."""
    result_ready = QtCore.Signal(str)

    def __init__(self, user_text):
        super(NeuralWorker, self).__init__()
        self.user_text = user_text

    def run(self):
        # The API using itself: QuTensors (Brain) processing via KnowModule (Know)
        response = API.Brain.process_stimulus(self.user_text, API.Know)
        self.result_ready.emit(response)

class QuMoUI(QtGui.QMainWindow):
    def __init__(self):
        super(QuMoUI, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QuMo Neural Interface")
        self.resize(800, 500)
        
        # Standard System Styling
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QTextEdit { background-color: #000000; color: #00ff00; font-family: 'Consolas'; }
            QLineEdit { background-color: #333333; color: #ffffff; border: 1px solid #555; }
            QPushButton { background-color: #444444; color: #ffffff; padding: 5px; }
        """)

        central_widget = QtGui.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtGui.QVBoxLayout(central_widget)

        self.display = QtGui.QTextEdit()
        self.display.setReadOnly(True)
        
        self.input_field = QtGui.QLineEdit()
        self.input_field.returnPressed.connect(self.send_to_api)
        
        self.btn_send = QtGui.QPushButton("PROCESS")
        self.btn_send.clicked.connect(self.send_to_api)

        layout.addWidget(self.display)
        layout.addWidget(self.input_field)
        layout.addWidget(self.btn_send)

    def send_to_api(self):
        text = self.input_field.text().strip()
        if not text: return
        
        self.display.append("<b>USER:</b> " + text)
        self.input_field.clear()

        # Start background thread for API processing
        self.worker = NeuralWorker(text)
        self.worker.result_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response):
        self.display.append("<b>CORE:</b> " + response)
        self.display.ensureCursorVisible()

    def closeEvent(self, event):
        # Ensure SQLite closes safely
        API.Know.close_connection()
        event.accept()