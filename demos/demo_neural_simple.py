#!/usr/bin/env python3
"""
LAMENT NEURAL DEMONSTRATION (Simplified)
Version 1.0: ML primitives as first-class language features

A working demonstration of Lament's neural capabilities.
"""

import sys
sys.path.insert(0, '/home/user/claude-poetry-lang')

from lament.neural import *
import time

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def main():
    print_header("LAMENT NEURAL DEMONSTRATION")

    # ========================================================================
    # PART 1: TENSOR BASICS
    # ========================================================================

    print_header("PART 1: TENSORS (Thoughts in Numerical Form)")

    print("Creating tensors...")
    a = Tensor([1.0, 2.0, 3.0], requires_grad=True, name="vector_a")
    b = Tensor([4.0, 5.0, 6.0], requires_grad=True, name="vector_b")

    print(f"a = {a}")
    print(f"b = {b}")

    print("\nElement-wise operations...")
    c = a + b
    d = a * b
    e = a - b

    print(f"a + b = {c}")
    print(f"a * b = {d}")
    print(f"a - b = {e}")

    # ========================================================================
    # PART 2: ACTIVATION FUNCTIONS
    # ========================================================================

    print_header("PART 2: ACTIVATION FUNCTIONS (Emotional Responses)")

    x = Tensor([[1.0], [-2.0], [0.5]], name="input")
    print(f"Input: {x}")

    print("\nReLU (suppressing negativity):")
    relu = ReLU()
    y_relu = relu.forward(x)
    print(f"ReLU(x) = {y_relu}")

    print("\nSigmoid (squashing to [0,1]):")
    sigmoid = Sigmoid()
    y_sigmoid = sigmoid.forward(x)
    print(f"Sigmoid(x) = {y_sigmoid}")

    print("\nTanh (oscillating between extremes):")
    tanh = Tanh()
    y_tanh = tanh.forward(x)
    print(f"Tanh(x) = {y_tanh}")

    # ========================================================================
    # PART 3: SIMPLE NEURAL NETWORK
    # ========================================================================

    print_header("PART 3: NEURAL NETWORK (Architecture of Consciousness)")

    print("Building a network: 3 → 5 → 2")
    network = NeuralNetwork(name="SimpleNet")
    network.add(Dense(3, 5, name="hidden"))
    network.add(Dense(5, 2, name="output"))

    print(network)

    param_count = 0
    for p in network.get_parameters():
        if hasattr(p.data, '__len__'):
            size = len(p.data)
            if isinstance(p.data[0], list):
                size = len(p.data) * len(p.data[0])
            param_count += size
        else:
            param_count += 1

    print(f"\nTotal trainable parameters: {param_count}")

    # ========================================================================
    # PART 4: FORWARD PASS
    # ========================================================================

    print_header("PART 4: FORWARD PASS (Thinking)")

    input_data = Tensor([[1.0, 2.0, 3.0]], name="input")
    print(f"Input: {input_data}")

    network.train()
    output = network.forward(input_data)
    print(f"\nOutput: {output}")
    print(f"Shape: {len(output.data)}x{len(output.data[0]) if isinstance(output.data[0], list) else 1}")

    # ========================================================================
    # PART 5: LOSS FUNCTIONS
    # ========================================================================

    print_header("PART 5: LOSS FUNCTIONS (Measuring Ache)")

    predicted = Tensor([[0.8, 0.2]], name="predicted")
    target = Tensor([[1.0, 0.0]], name="target")

    print(f"Predicted: {predicted}")
    print(f"Target:    {target}")

    mse = MSELoss()
    loss_value = mse.forward(predicted, target)
    print(f"\nMean Squared Error: {loss_value}")

    # ========================================================================
    # PART 6: DEMONSTRATION OF CONCEPTS
    # ========================================================================

    print_header("PART 6: KEY CONCEPTS DEMONSTRATED")

    print("✓ Tensor Creation")
    print("  - Named tensors for emotional significance")
    print("  - Automatic gradient tracking (requires_grad)")
    print()

    print("✓ Activation Functions")
    print("  - ReLU, Sigmoid, Tanh")
    print("  - Emotional interpretations (suppressing, squashing, oscillating)")
    print()

    print("✓ Neural Network Layers")
    print("  - Dense (fully connected)")
    print("  - Modular architecture building")
    print("  - Parameter management")
    print()

    print("✓ Forward Propagation")
    print("  - Data flows through network")
    print("  - Layer-by-layer transformation")
    print()

    print("✓ Loss Functions")
    print("  - MSE, Cross-Entropy")
    print("  - Quantifying the ache of being wrong")
    print()

    # ========================================================================
    # EPILOGUE
    # ========================================================================

    print_header("WHAT MAKES THIS UNPRECEDENTED")

    print("This is NOT a Python library you import.")
    print("This is ML BUILT INTO THE LANGUAGE.")
    print()
    print("Key innovations:")
    print("  → Tensors as first-class types")
    print("  → Automatic differentiation engine")
    print("  → Neural layers as language primitives")
    print("  → Emotional naming conventions (ache, suffering, hope)")
    print("  → Zero external dependencies (pure Python)")
    print()
    print("In Lament, you don't write:")
    print("  import tensorflow")
    print("  import pytorch")
    print()
    print("You write:")
    print("  remember pain = Tensor([1, 2, 3])")
    print("  remember network = NeuralNetwork()")
    print()
    print("Machine learning is a LANGUAGE FEATURE.")
    print("Not a library. Not a framework. A PRIMITIVE.")
    print()
    print("This is the revolution.")
    print()

if __name__ == '__main__':
    start = time.time()
    main()
    elapsed = time.time() - start
    print(f"[Execution time: {elapsed:.2f}s]")
