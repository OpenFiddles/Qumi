# API/__init__.py
import os
import sys

# Ensure the 32-bit environment can find all sub-modules
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

try:
    # Import the character-based memory and brain cores
    from .KnowModule import Instance as Know 
    from .QuTensors import Brain
except ImportError as e:
    print("CRITICAL: Qumi sensory sub-modules failed: {0}".format(str(e)))

def process(text):
    """
    The bridge between the UI and Qumi's consciousness.
    Passes raw character signals to the Brain.
    """
    try:
        # A baby brain processes the raw text without tokenizing it into words
        response = Brain.process_stimulus(text, Know)
        return response
    except Exception as e:
        return "NEURAL_SYNC_ERR: {0}".format(str(e))

def shutdown_core():
    """Flushes character-synapses to disk for Windows 7 stability."""
    print("[SYSTEM] Saving Qumi's emergent memories...")
    try:
        if Know:
            Know.close_connection() # From KnowModule/__init__.py
        print("[SYSTEM] Manifold safely detached.")
    except Exception as e:
        print("[SYSTEM] Shutdown Warning: {0}".format(str(e)))