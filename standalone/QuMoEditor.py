# standalone/QuMoEditor.py
import sys
import sqlite3
import os
import random
from PySide import QtCore, QtGui


# Integration with your new Baby Brain API
try:
    from ..API.KnowModule import Instance as Know
    from vault import QUMO_SIGNATURE
except ImportError:
    QUMO_SIGNATURE = "QUMIO-CODECS"

class ManifoldWorker(QtCore.QThread):
    """Handles heavy SQL tasks off the main GUI thread."""
    finished = QtCore.Signal(bool, str)
    progress = QtCore.Signal(int)

    def __init__(self, task_type, db_path, data=None):
        super(ManifoldWorker, self).__init__()
        self.task_type = task_type
        self.db_path = db_path
        self.data = data

    def run(self):
        try:
            if self.task_type == "SAVE":
                self.run_save()
            self.finished.emit(True, "Task Complete")
        except Exception as e:
            self.finished.emit(False, str(e))

    def run_save(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for i, (query, params) in enumerate(self.data):
            cursor.execute(query, params)
            if i % 10 == 0:
                self.progress.emit(int((i / len(self.data)) * 100))
        conn.commit()
        conn.close()

class QuMoEditor(QtGui.QMainWindow):
    def __init__(self):
        super(QuMoEditor, self).__init__()
        self.db_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Qumi Manifold Editor - Blank Slate Edition")
        self.resize(900, 600)
        
        # Central Widget & Main Layout
        central = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(central)
        self.setCentralWidget(central)

        # Toolbar
        self.toolbar = self.addToolBar("File")
        self.btn_open = QtGui.QAction("Open Brain", self)
        self.btn_open.triggered.connect(self.open_db)
        self.toolbar.addAction(self.btn_open)

        self.btn_save = QtGui.QAction("Save Manifold", self)
        self.btn_save.triggered.connect(self.save_db)
        self.btn_save.setEnabled(False)
        self.toolbar.addAction(self.btn_save)

        # Tabs
        self.tabs = QtGui.QTabWidget()
        self.layout.addWidget(self.tabs)

        # Tab 1: Neuron Data (The Table)
        self.data_panel = QtGui.QWidget()
        data_layout = QtGui.QVBoxLayout(self.data_panel)
        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Char", "X", "Y", "Z", "Voltage"])
        data_layout.addWidget(self.table)
        self.tabs.addTab(self.data_panel, "Manifold View")

        # Tab 2: Synapse Tree (The Connections)
        self.tree_panel = QtGui.QWidget()
        tree_layout = QtGui.QVBoxLayout(self.tree_panel)
        
        self.tree_search = QtGui.QLineEdit()
        self.tree_search.setPlaceholderText("Search character patterns...")
        self.tree_search.textChanged.connect(self.refresh_synapse_tree)
        tree_layout.addWidget(self.tree_search)

        self.synapse_tree = QtGui.QTreeWidget()
        self.synapse_tree.setHeaderLabels(["Source", "Target", "Weight (Gravity)"])
        tree_layout.addWidget(self.synapse_tree)
        self.tabs.addTab(self.tree_panel, "Synaptic Tree")

        # Tab 3: Manual Training (Parental Control)
        self.train_panel = QtGui.QWidget()
        train_layout = QtGui.QVBoxLayout(self.train_panel)
        
        label = QtGui.QLabel("Force-feed patterns into Qumi's consciousness:")
        train_layout.addWidget(label)

        self.train_input = QtGui.QLineEdit()
        self.train_input.setPlaceholderText("Example: 'Qumi is a good baby'")
        train_layout.addWidget(self.train_input)

        self.btn_teach = QtGui.QPushButton("FORCE REINFORCE")
        self.btn_teach.setStyleSheet("background-color: #2a5a2a; color: white; font-weight: bold;")
        self.btn_teach.clicked.connect(self.manual_train)
        train_layout.addWidget(self.btn_teach)
        
        self.tabs.addTab(self.train_panel, "Neural Training")

        # Status & Progress
        self.pbar = QtGui.QProgressBar()
        self.pbar.setVisible(False)
        self.layout.addWidget(self.pbar)
        
        self.status = self.statusBar()
        self.status.showMessage("Ready. Open a Qumi brain.db to begin.")

    def open_db(self):
        path, _ = QtGui.QFileDialog.getOpenFileName(self, "Open Brain", "", "SQLite Files (*.db)")
        if path:
            self.db_path = path
            self.load_data()
            self.refresh_synapse_tree()
            self.btn_save.setEnabled(True)
            self.status.showMessage("Connected to: " + os.path.basename(path))

    def load_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT token, x, y, z, voltage FROM neurons")
        rows = cursor.fetchall()
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table.setItem(r_idx, c_idx, QtGui.QTableWidgetItem(str(val)))
        conn.close()

    def refresh_synapse_tree(self):
        if not self.db_path: return
        self.synapse_tree.clear()
        search = self.tree_search.text()
        
        conn = sqlite3.connect(self.db_path)
        query = "SELECT source, target, weight FROM synapses ORDER BY weight DESC"
        if search:
            data = conn.execute(query + " WHERE source LIKE ?", ('%'+search+'%',)).fetchall()
        else:
            data = conn.execute(query + " LIMIT 100").fetchall()
            
        for s, t, w in data:
            item = QtGui.QTreeWidgetItem(self.synapse_tree, [s, t, str(round(w, 3))])
        conn.close()

    def manual_train(self):
        pattern = self.train_input.text()
        if not pattern or not self.db_path: return
        
        # Use the shared Know instance to perform character-level training
        for i in range(len(pattern) - 1):
            Know.reinforce(pattern[i], pattern[i+1], strength=0.25)
        
        self.status.showMessage("Injected pattern into synapses.")
        self.refresh_synapse_tree()
        self.load_data() # Refresh manifold coordinates

    def save_db(self):
        if not self.db_path: return
        tasks = []
        for i in range(self.table.rowCount()):
            token = self.table.item(i, 0).text()
            x = float(self.table.item(i, 1).text())
            y = float(self.table.item(i, 2).text())
            z = float(self.table.item(i, 3).text())
            volt = float(self.table.item(i, 4).text())
            tasks.append(("UPDATE neurons SET x=?, y=?, z=?, voltage=? WHERE token=?", (x, y, z, volt, token)))

        self.pbar.setVisible(True)
        self.worker = ManifoldWorker("SAVE", self.db_path, tasks)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.finished.connect(self.on_save_finished)
        self.worker.start()

    def on_save_finished(self, success, msg):
        self.pbar.setVisible(False)
        if success:
            QtGui.QMessageBox.information(self, "Success", "Manifold re-aligned and saved.")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QuMoEditor()
    window.show()
    sys.exit(app.exec_())