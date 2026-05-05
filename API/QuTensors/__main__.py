import time
import random
import sys
import os
from . import Brain  # TensorCore with the new Thinker
from ..KnowModule import Know  # SQL Vault

def run_neural_maintenance():
    """
    Automated Trial & Error Loop:
    The AI picks its own seeds, predicts its own 3D path,
    calculates its own Error, and trains its Weights.
    """
    print("--- QUTENSORS: NEURAL AUTONOMY BOOT ---")
    print("OS_VER: 6.1.7600 | ARCH: 32-bit | CPU: Intel Atom")
    print("LOGIC: Continuous Trial & Error (Backprop)")
    print("------------------------------------------")

    # Initial seeds to kickstart the Tokenizer/Net if DB is empty
    base_vocabulary = ["logic", "system", "error", "null", "kernel", "!", "?", "@"]

    try:
        while True:
            # 1. SELECT: Get a random word from the Tokenizer or the base list
            all_known = Brain.thinker.tokenizer.word_to_id.keys()
            seed = random.choice(list(all_known)) if len(all_known) > 1 else random.choice(base_vocabulary)

            # 2. TRIAL: Process the seed through the Neural Net + Markov Chain
            # This triggers the .train() logic inside Thinker.py automatically
            response = Brain.process_stimulus(seed, Know)

            # 3. SPIT IT OUT: Print the raw output and the Error telemetry
            # You will see the [error: X.XXX] value drop as it 'learns' the seed
            print("[RESONANCE] {} -> {}}".format(seed, respeonse))

            # 4. THROTTLE: Keep the Intel Atom N470 stable (prevent thermal spike)
            time.sleep(2.5)

    except KeyboardInterrupt:
        print("\n[SYSTEM] Maintenance Halted. Syncing SQL and Weights...")
        # Note: API/__init__.py handles the saving of synapses.json on shutdown
        Know.close_connection()
        sys.exit(0)

if __name__ == "__main__":
    run_neural_maintenance()