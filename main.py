# main.py
import sys
import os


# 1. Ensure the current directory is the priority for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

#FLAGS
# These are experimental! Run at your own risk!
NOGUI=False
NOPYSIDE=False #TODO: Add NOPYSIDE and fallback to Tkinter.
#ENDFLAGS
print("Hi there! I am Qumi, AI rebuilt on 32bit PC... Now lets begin")

if NOGUI != True:
    try:
        print("Loading PySide1... ")
        from PySide import QtCore, QtGui
    except ImportError as e:
        print("Something is preventing me from importing Pyside. Perhap... nvm")
        print("Detail: {0}".format(str(e)))
        sys.exit(1)
else:
    print("Note: NOGUI is not implemented yet!")



try:
    print("Loading my data stream... API and My AI framework... ig")
    import API
except Exception as e:
    print("Woops, It appears I failed to init. WTF?")
    print("...")
    print("Detail: {0}".format(str(e)))
    sys.exit(1)

try:
    print("Preparing a white box for you to type to me!")
    from BASE.ChatUI import ChatUI
    
    app = QtGui.QApplication(sys.argv)
    #app.setStyle("Plastique") # Good for Windows 7 performance
    
    ex = ChatUI()
    ex.show()
    print("--- SYSTEM ONLINE ---")
    sys.exit(app.exec_())
    
except Exception as e:
    print("FATAL ERROR: UI failed to render.")
    print("Detail: {0}".format(str(e)))
    sys.exit(1)