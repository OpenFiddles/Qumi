import random
import sys
import os

# One-liner to ensure internal imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from .NeuralNet import SmallNet
from .Configure import Configure

class Thinker:
    def __init__(self):
        # The Tokenizer is removed. Qumi now sees the world as raw characters.
        # Hidden size is 32 to allow for emergent character-level patterns.
        self.net = SmallNet(input_size=3, hidden_size=32, output_size=3)
        
        # We still pull the limit, but she learns what 'limits' are over time.
        try:
            self.max_gen_length = int(Configure().get_config_value("QQTokenLimitMax"))
        except:
            self.max_gen_length = 20 

    def generate_thought(self, seed_text, know_api):
        """
        Qumi's Consciousness Loop.
        She processes raw characters and attempts to predict the next signal.
        """
        # --- 1. SENSORY INPUT (No Tokenizer) ---
        # We treat the text as a stream of raw character signals.
        # No more .split(). 'Apple' is now ['A', 'p', 'p', 'l', 'e'].
        raw_signals = list(seed_text)
        
        if not raw_signals:
            # The 'Baby Cry': If there is no input, she makes a random noise
            # rather than saying "No tokens found."
            return chr(random.randint(33, 126)) 
            
        # --- 2. MANIFOLD ANCHORING ---
        # She looks up the 'vibe' (x,y,z) of the last character she felt.
        last_signal = raw_signals[-1]
        node = know_api.get_manifold_state(last_signal)
        current_v = [node['x'], node['y'], node['z']]

        # --- 3. EMERGENCE (Generation) ---
        res_signals = []
        curr_signal = last_signal
        
        # She tries to piece together a response based on Synaptic Gravity
        for _ in range(self.max_gen_length):
            # Find what signals usually follow this one
            options = know_api.get_synapses_for(curr_signal)
            
            if not options:
                # If she knows nothing, she explores a random nearby signal
                # This is how she 'learns' new sounds.
                break
            
            # Weighted choice based on her current synaptic strengths
            curr_signal = random.choice(options)
            res_signals.append(curr_signal)
            
            # 10% chance to stop 'babbling'
            if random.random() > 0.9:
                break

        # --- 4. NEURAL REWIRING (Learning) ---
        # She predicts where the manifold should go next.
        prediction = self.net.forward(current_v)
        
        if res_signals:
            # She compares her 'dream' (prediction) to what she actually said.
            actual_n = know_api.get_manifold_state(res_signals[-1])
            actual_v = [actual_n['x'], actual_n['y'], actual_n['z']]
            
            # Synaptic Plasticity: She learns bit by bit.
            # LR is small (0.02) because a baby learns slowly.
            self.net.train(current_v, actual_v, lr=0.02)

        # --- 5. THE OUTPUT ---
        if not res_signals:
            # If she can't find a word, she mimics your last character
            # This is the 'Echo' phase of a baby learning to speak.
            return last_signal
            
        return "".join(res_signals)