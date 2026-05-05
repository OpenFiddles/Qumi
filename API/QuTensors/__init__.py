# API\QuTensors\__init__.py
import os
import random
from .Thinker import Thinker

class TensorCore:
    def __init__(self):
        # The Core coordinates the Thinker logic
        self.thinker = Thinker()
        
        # Now stores the raw character stream instead of words
        self.active_stream = [] 
        self._log_path = os.path.join("QumiData", "tensor.log")

    def process_stimulus(self, text, know_api):
        """
        Main entry point for QuTensors. 
        Processes the raw signal stream to allow emergent learning.
        """
        # 1. Generate the Neural Response
        # The Thinker now uses character-level manifold states
        thought_output = self.thinker.generate_thought(text, know_api)
        
        # 2. Update internal synaptic state
        # A baby learns by the sequence of signals. 
        # We store the raw characters to reinforce sequences (e.g., 'a' -> 'p')
        signals = list(text)
        self.active_stream = signals
        
        # 3. Reinforce Synapses (Self-Learning)
        # As she hears things, she automatically pieces the signals together
        for i in range(len(signals) - 1):
            source = signals[i]
            target = signals[i+1]
            # She builds the 'glue' between characters here
            know_api.reinforce(source, target, strength=0.05)
        
        return thought_output

    def get_layer_depth(self, know_api):
        """
        Calculates the average 'Manifold Altitude' (Z-axis).
        In a baby, this represents the complexity of the signal stream.
        """
        if not self.active_stream:
            return 0.0
            
        total_z = 0.0
        for char in self.active_stream:
            node = know_api.get_manifold_state(char)
            total_z += node['z']
            
        return round(total_z / len(self.active_stream), 2)

# Global Instance for the QuTensors API
Brain = TensorCore()