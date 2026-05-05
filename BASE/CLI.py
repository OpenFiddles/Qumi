import sys
import os
import time

# 1. THE BOOTSTRAP: Ensure the top-level directory is accessible.
# This allows 'import API' and 'from Thinker import Thinker' to work 
# even when running this script from the /BASE/ folder.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 2. THE IMPORTS
try:
    import API
    from API.QuTensors.Thinker import Thinker
except ImportError as e:
    print("CRITICAL: Could not load Qumi modules.")
    print("Detail: {0}".format(e))
    sys.exit(1)

# TUI Layout Constraints
WIDTH = 70
LOG_HEIGHT = 10

class CLInterface:
    def __init__(self):
        self.chat_log = []
        self.status = "READY"
        
        # Initialize Thinker (The Neural Logic)
        self.thinker = Thinker()
        
        # FIX: Explicitly call the Know class from the API package
        # This resolves the 'TypeError: Know object is not callable'
        try:
            self.know = API.Know(db_path="QumiData/brain.db")
        except Exception as e:
            print("DATABASE ERROR: {0}".format(e))
            sys.exit(1)

    def clear_screen(self):
        """Clears terminal. 'cls' is prioritized for Windows 7/XP."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw_ui(self, current_input_buffer=""):
        """Renders the centered TUI layout."""
        self.clear_screen()
        
        # 1. Header (Mimicking ChatUI.py title)
        print("X _".ljust(WIDTH))
        print("QUMI".center(WIDTH, "="))
        print("")

        # 2. Chat Log Area
        # Displays last 10 lines of conversation
        display_log = self.chat_log[-LOG_HEIGHT:]
        for line in display_log:
            print(line.center(WIDTH))
        
        # Maintain vertical height if log is short
        for _ in range(LOG_HEIGHT - len(display_log)):
            print("")

        # 3. Functional Input Area (Your Design)
        # The 'current_input_buffer' can be used if you expand to real-time keystrokes
        print("\n" + "[ {0} ]".format(current_input_buffer.ljust(WIDTH - 6)).center(WIDTH))
        
        # 4. Status Bar
        print("-" * WIDTH)
        print("STATUS: {0}".format(self.status).center(WIDTH))

    def add_message(self, sender, text):
        """Standardized prefixing for the chat log."""
        prefix = "Q: " if sender == "YOU" else "U: "
        self.chat_log.append("{0}{1}".format(prefix, text))

    def run(self):
        """Main Interaction Loop"""
        while True:
            self.draw_ui()
            
            # The actual functional input call
            try:
                # Python 3.4+ compatible input
                user_input = input("\n" + " " * (WIDTH // 4) + "> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if user_input.lower() in ["exit", "quit"]:
                print("Shutting down Neural Interface...")
                break
            
            if not user_input:
                continue

            # --- PROCESS START ---
            # 1. Update UI to show User sent something
            self.add_message("YOU", user_input)
            self.status = "CORE IS CALCULATING MANIFOLD..."
            self.draw_ui("...") # Show placeholder in input box

            # 2. Trigger Neural Math
            try:
                # Passes the input and the 'know' (brain.db) instance to the thinker
                reply = self.thinker.generate_thought(user_input, self.know)
                self.add_message("CORE", reply)
            except Exception as e:
                self.add_message("CORE", "ERROR: Check API Logs.")
                self.status = "FAULT: {0}".format(str(e)[:30])
                self.draw_ui()
                time.sleep(2)

            # 3. Reset for next turn
            self.status = "READY"

if __name__ == "__main__":
    tui = CLInterface()
    tui.run()