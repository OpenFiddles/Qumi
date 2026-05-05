import sys
import subprocess
import os
from PySide import QtCore, QtGui

class ReaderThread(QtCore.QThread):
    """Handles the heavy lifting of intercepting process output."""
    output_received = QtCore.Signal(str)
    process_finished = QtCore.Signal(int)

    def __init__(self, target_path):
        super(ReaderThread, self).__init__()
        self.target_path = target_path
        self.process = None

    def run(self):
        try:
            # Launch with -u for unbuffered binary output (Critical for 3.4.4)
            self.process = subprocess.Popen(
                [sys.executable, "-u", self.target_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )

            # Keep reading until the process dies
            while self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    self.output_received.emit(line.strip())
                else:
                    self.msleep(10) # Save Atom CPU cycles

            self.process_finished.emit(self.process.returncode)
        except Exception as e:
            self.output_received.emit("INTERCEPTOR CRASH: " + str(e))

    def stop(self):
        if self.process:
            self.process.terminate()

class StandaloneDebugger(QtGui.QMainWindow):
    def __init__(self):
        super(StandaloneDebugger, self).__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QuMo Interceptor [Threaded 3.4.4]")
        self.resize(650, 450)

        central = QtGui.QWidget()
        self.setCentralWidget(central)
        layout = QtGui.QVBoxLayout(central)

        self.status_label = QtGui.QLabel("READY: WAITING FOR INJECTION")
        layout.addWidget(self.status_label)

        self.log_view = QtGui.QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #0c0c0c; color: #33ff33; font-family: 'Consolas';")
        layout.addWidget(self.log_view)

        self.btn_launch = QtGui.QPushButton("START INJECTION")
        self.btn_launch.clicked.connect(self.start_debug)
        layout.addWidget(self.btn_launch)

    def start_debug(self):
        target = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        
        # Initialize the Thread
        self.worker = ReaderThread(target)
        self.worker.output_received.connect(self.append_log)
        self.worker.process_finished.connect(self.on_finished)
        
        self.log_view.append("--- BOOTING CHILD PROCESS ---")
        self.status_label.setText("STATUS: INJECTED & RUNNING")
        self.btn_launch.setEnabled(False)
        self.worker.start()

    def append_log(self, text):
        self.log_view.append(text)
        # Auto-scroll to bottom
        self.log_view.moveCursor(QtGui.QTextCursor.End)

    def on_finished(self, code):
        self.status_label.setText("STATUS: TARGET KILLED (Exit Code: {0})".format(code))
        self.btn_launch.setEnabled(True)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyle("Plastique")
    win = StandaloneDebugger()
    win.show()
    sys.exit(app.exec_())