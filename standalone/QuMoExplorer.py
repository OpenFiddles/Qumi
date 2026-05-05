import sys
import sqlite3
import os
import random
from PySide import QtCore, QtGui

# Tokenizer Fallback
try:
    from API.QuTensors.Tokenizer import Tokenizer
except:
    class Tokenizer:
        def tokenize(self, text):
            return [], text.lower().replace(".", " . ").split()

class QuVisionCanvas(QtGui.QWidget):
    """Neural CAD Canvas with Marquee Selection and Dragging."""
    nodes_selected = QtCore.Signal(list) # Sends list of selected words

    def __init__(self, parent=None):
        super(QuVisionCanvas, self).__init__(parent)
        self.setMouseTracking(True)
        self.offset = QtCore.QPoint(150, 150)
        self.zoom = 0.6
        self.last_mouse_pos = QtCore.QPoint()
        
        # Selection Logic
        self.selection_rect = QtCore.QRect()
        self.is_selecting = False
        self.selected_words = [] 
        
        self.nodes = [] # word, x, y, v
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self.update)
        self.refresh_timer.start(50)

    def load_data(self):
        db_path = "QumiData/brain.db"
        if not os.path.exists(db_path): return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT word, x, y, voltage FROM neurons ORDER BY voltage DESC LIMIT 800")
            self.nodes = [list(row) for row in cursor.fetchall()]
            conn.close()
        except: pass

    def world_to_screen(self, x, y):
        px = (x * 800 * self.zoom) + self.offset.x()
        py = (y * 800 * self.zoom) + self.offset.y()
        return QtCore.QPoint(px, py)

    def screen_to_world(self, pos):
        wx = (pos.x() - self.offset.x()) / (800 * self.zoom)
        wy = (pos.y() - self.offset.y()) / (800 * self.zoom)
        return wx, wy

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(15, 15, 20))

        # Manifold Boundary
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 255, 60), 1, QtCore.Qt.DashLine))
        painter.drawRect(self.offset.x(), self.offset.y(), 800*self.zoom, 800*self.zoom)

        for node in self.nodes:
            word, x, y, v = node
            pos = self.world_to_screen(x, y)
            
            if self.rect().contains(pos):
                is_sel = word in self.selected_words
                color = QtGui.QColor(255, 200, 0) if is_sel else QtGui.QColor(0, 200, 255, int(150 + v*105))
                
                painter.setBrush(color)
                painter.setPen(QtCore.Qt.NoPen)
                radius = 4 + (v * 6)
                painter.drawEllipse(pos, radius, radius)
                
                if self.zoom > 0.5 or is_sel:
                    painter.setPen(QtGui.QColor(255, 255, 255, 200))
                    painter.drawText(pos.x() + 10, pos.y() + 5, word)

        # Draw Selection Marquee
        if self.is_selecting:
            painter.setPen(QtGui.QColor(0, 255, 255))
            painter.setBrush(QtGui.QColor(0, 255, 255, 30))
            painter.drawRect(self.selection_rect)

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()
        if event.button() == QtCore.Qt.LeftButton:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self.is_selecting = True
                self.selection_rect = QtCore.QRect(event.pos(), QtCore.QSize())
            else:
                # Direct click selection
                self.selected_words = []
                for word, x, y, v in self.nodes:
                    if (event.pos() - self.world_to_screen(x, y)).manhattanLength() < 15:
                        self.selected_words = [word]
                        break
                self.nodes_selected.emit(self.selected_words)

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.selection_rect.setBottomRight(event.pos())
        elif event.buttons() & QtCore.Qt.RightButton:
            self.offset += event.pos() - self.last_mouse_pos
        self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if self.is_selecting:
            self.is_selecting = False
            self.selected_words = []
            # Check which nodes are inside the marquee
            for word, x, y, v in self.nodes:
                if self.selection_rect.contains(self.world_to_screen(x, y)):
                    self.selected_words.append(word)
            self.nodes_selected.emit(self.selected_words)
            self.update()

    def wheelEvent(self, event):
        self.zoom = max(0.01, self.zoom + (event.delta() / 1200.0))

class QuMoExplorer(QtGui.QMainWindow):
    def __init__(self):
        super(QuMoExplorer, self).__init__()
        self.setWindowTitle("QuMo Master CAD Explorer")
        self.resize(1100, 750)
        
        # --- TOOLBAR ---
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setMovable(False)
        
        act_refresh = self.toolbar.addAction("RESCAN")
        act_refresh.triggered.connect(self.refresh_all)
        
        self.toolbar.addSeparator()
        
        act_explode = self.toolbar.addAction("EXPLODE")
        act_explode.triggered.connect(self.mass_nudge)
        
        act_purge = self.toolbar.addAction("PURGE SELECTED")
        act_purge.triggered.connect(self.mass_delete)

        # --- CENTRAL ---
        main_widget = QtGui.QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QtGui.QHBoxLayout(main_widget)
        
        # Sidebar
        self.sidebar = QtGui.QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background: #111; border-right: 1px solid #333; color: #0fa;")
        self.side_layout = QtGui.QVBoxLayout(self.sidebar)
        self.side_layout.addWidget(QtGui.QLabel("<b>SELECTION</b>"))
        self.sel_count = QtGui.QLabel("Items: 0")
        self.side_layout.addWidget(self.sel_count)
        self.side_layout.addStretch()
        self.side_layout.addWidget(QtGui.QLabel("<small>CTRL + Drag to Marquee\nRight-Click to Pan</small>"))
        
        self.layout.addWidget(self.sidebar)
        
        # Canvas
        self.canvas = QuVisionCanvas(self)
        self.canvas.nodes_selected.connect(self.on_selection)
        self.layout.addWidget(self.canvas, 1)

        self.canvas.load_data()

    def on_selection(self, words):
        self.sel_count.setText("Items: {0}".format(len(words)))

    def refresh_all(self):
        self.canvas.load_data()

    def mass_nudge(self):
        """Pushes nodes out of clusters."""
        conn = sqlite3.connect("QumiData/brain.db")
        for word, x, y, v in self.canvas.nodes:
            nx = max(0, min(1, x + random.uniform(-0.05, 0.05)))
            ny = max(0, min(1, y + random.uniform(-0.05, 0.05)))
            conn.execute("UPDATE neurons SET x=?, y=? WHERE word=?", (nx, ny, word))
        conn.commit()
        conn.close()
        self.refresh_all()

    def mass_delete(self):
        if not self.canvas.selected_words: return
        conn = sqlite3.connect("QumiData/brain.db")
        for word in self.canvas.selected_words:
            conn.execute("DELETE FROM neurons WHERE word=?", (word,))
            conn.execute("DELETE FROM synapses WHERE source=? OR target=?", (word, word))
        conn.commit()
        conn.close()
        self.canvas.selected_words = []
        self.refresh_all()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyle("Cleanlooks")
    win = QuMoExplorer()
    win.show()
    sys.exit(app.exec_())