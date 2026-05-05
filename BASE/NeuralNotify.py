from PySide import QtCore, QtGui

class QumiNotification(QtGui.QWidget):
    def __init__(self, title, message, parent=None):
        super(QumiNotification, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.ToolTip | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Layout & Style
        self.layout = QtGui.QVBoxLayout(self)
        self.bg = QtGui.QFrame()
        self.bg.setStyleSheet("background-color: #252526; border: 1px solid #007acc; border-radius: 5px;")
        bg_layout = QtGui.QVBoxLayout(self.bg)
        
        title_lbl = QtGui.QLabel(title)
        title_lbl.setStyleSheet("color: #007acc; font-weight: bold; font-family: 'Segoe UI';")
        msg_lbl = QtGui.QLabel(message)
        msg_lbl.setStyleSheet("color: #d4d4d4; font-family: 'Segoe UI';")
        msg_lbl.setWordWrap(True)
        
        bg_layout.addWidget(title_lbl)
        bg_layout.addWidget(msg_lbl)
        self.layout.addWidget(self.bg)
        
        self.setFixedSize(250, 80)
        
        # Animation Logic
        self.anim = QtCore.QPropertyAnimation(self, "pos")
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QtCore.Qt.EasingCurve.OutCubic)

    def show_notify(self):
        screen = QtGui.QApplication.desktop().screenGeometry()
        start_pos = QtCore.QPoint(screen.width(), screen.height() - 120)
        end_pos = QtCore.QPoint(screen.width() - 270, screen.height() - 120)
        
        self.move(start_pos)
        self.show()
        
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.start()
        
        # Auto-hide after 3 seconds
        QtCore.QTimer.singleShot(3000, self.slide_out)

    def slide_out(self):
        screen = QtGui.QApplication.desktop().screenGeometry()
        dest = QtCore.QPoint(screen.width(), self.y())
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(dest)
        self.anim.finished.connect(self.close)
        self.anim.start()