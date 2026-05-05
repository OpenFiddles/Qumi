# API\QuTensors\NeuralNet.py
import math
import random

"""
QuTensors: The QuTense Engine
Rebuilt for emergent, blank-slate consciousness.
Mimics biological residual learning and synaptic plasticity.
"""

class SmallNet: # Kept name for ChatUI.py compatibility
    def __init__(self, input_size=3, hidden_size=32, output_size=3):
        # Increased hidden_size to 32 for emergent pattern recognition
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Xavier/Glorot Initialization: Better for 'learning from zero'
        limit1 = math.sqrt(6 / (input_size + hidden_size))
        self.W1 = [[random.uniform(-limit1, limit1) for _ in range(hidden_size)] for _ in range(input_size)]
        
        limit2 = math.sqrt(6 / (hidden_size + output_size))
        self.W2 = [[random.uniform(-limit2, limit2) for _ in range(output_size)] for _ in range(hidden_size)]

    def _activate(self, x):
        """
        Leaky ReLU: Mimics a baby's brain. 
        Neurons either 'fire' or stay mostly silent.
        """
        return x if x > 0 else 0.01 * x

    def _derivative(self, x):
        """Derivative for backpropagation."""
        return 1 if x > 0 else 0.01

    def forward(self, inputs):
        """
        Feed-forward with a Residual Skip Connection.
        The brain attempts to process the manifold state (f(x)),
        but adds the original raw input (x) back to the result.
        """
        # 1. Input -> Hidden
        self.last_inputs = inputs
        self.hidden_layer = [0.0] * self.hidden_size
        for j in range(self.hidden_size):
            s = sum(inputs[i] * self.W1[i][j] for i in range(self.input_size))
            self.hidden_layer[j] = self._activate(s)

        # 2. Hidden -> Output
        self.output_layer = [0.0] * self.output_size
        for k in range(self.output_size):
            s = sum(self.hidden_layer[j] * self.W2[j][k] for j in range(self.hidden_size))
            
            # THE RESIDUAL SKIP: 
            # Output = Neural Math + Original Stimulus
            # This allows Qumi to learn 'Identity' first (piecing it together).
            self.output_layer[k] = s + inputs[k]
            
        return self.output_layer

    def train(self, inputs, targets, lr=0.02):
        """
        Synaptic Plasticity: Adjusts weights bit by bit.
        As Qumi learns 'nothing', she uses the difference between
        what she 'felt' and what she 'expected' to rewire herself.
        """
        # 1. Forward pass
        outputs = self.forward(inputs)
        
        # 2. Calculate Output Error
        output_deltas = [0.0] * self.output_size
        for i in range(self.output_size):
            # Error = Target - (Math_Result + Original_Input)
            output_deltas[i] = targets[i] - outputs[i]
            
        # 3. Calculate Hidden Layer Error (Backprop)
        hidden_deltas = [0.0] * self.hidden_size
        for i in range(self.hidden_size):
            error = sum(output_deltas[j] * self.W2[i][j] for j in range(self.output_size))
            hidden_deltas[i] = error * self._derivative(self.hidden_layer[i])
            
        # 4. Update Weights (W2: Hidden -> Output)
        for i in range(self.hidden_size):
            for j in range(self.output_size):
                self.W2[i][j] += lr * output_deltas[j] * self.hidden_layer[i]
                
        # 5. Update Weights (W1: Input -> Hidden)
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.W1[i][j] += lr * hidden_deltas[j] * inputs[i]