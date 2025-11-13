#!/usr/bin/env python3
"""
Examples of using the Lament Neural Module

This file demonstrates the revolutionary integration of neural networks
as first-class language primitives in Lament.
"""

import sys
sys.path.insert(0, '/home/user/claude-poetry-lang')

from lament.neural import *

print("\n" + "="*60)
print("LAMENT NEURAL MODULE - COMPREHENSIVE EXAMPLES")
print("="*60 + "\n")

# ============================================================================
# Example 1: Basic Tensor Operations
# ============================================================================

print("Example 1: Tensor Arithmetic with Automatic Differentiation")
print("-" * 60)

# Create tensors
a = Tensor([[1, 2], [3, 4]], requires_grad=True, name="a")
b = Tensor([[5, 6], [7, 8]], requires_grad=True, name="b")

print(f"a = {a.tolist()}")
print(f"b = {b.tolist()}")

# Arithmetic operations
c = a + b
print(f"\nc = a + b = {c.tolist()}")

d = a * b
print(f"d = a * b = {d.tolist()}")

# Compute loss and backpropagate
loss = c.sum()
print(f"\nloss = sum(c) = {loss.item()}")

print("\nBackpropagating...")
loss.backward()
print(f"gradient of a: {a.grad}")
print(f"gradient of b: {b.grad}")

# ============================================================================
# Example 2: Activation Functions
# ============================================================================

print("\n" + "="*60)
print("Example 2: Activation Functions")
print("-" * 60)

x = Tensor([-2, -1, 0, 1, 2], requires_grad=True, name="x")
print(f"x = {x.tolist()}")

# ReLU
relu_x = ReLU.forward(x)
print(f"\nReLU(x) = {relu_x.tolist()}")

# Sigmoid
x_sigmoid = Tensor([-2, -1, 0, 1, 2], requires_grad=True, name="x_sigmoid")
sigmoid_x = Sigmoid.forward(x_sigmoid)
print(f"Sigmoid(x) = {sigmoid_x.tolist()}")

# Tanh
x_tanh = Tensor([-2, -1, 0, 1, 2], requires_grad=True, name="x_tanh")
tanh_x = Tanh.forward(x_tanh)
print(f"Tanh(x) = {tanh_x.tolist()}")

# ============================================================================
# Example 3: Loss Functions
# ============================================================================

print("\n" + "="*60)
print("Example 3: Loss Functions")
print("-" * 60)

predicted = Tensor([0.9, 0.2, 0.7], requires_grad=True, name="predicted")
target = Tensor([1.0, 0.0, 1.0], name="target")

print(f"Predicted: {predicted.tolist()}")
print(f"Target: {target.tolist()}")

# MSE Loss
mse = MSELoss.forward(predicted, target)
print(f"\nMSE Loss: {mse.item():.4f}")

# Binary Cross Entropy
predicted_bce = Tensor([0.9, 0.2, 0.7], requires_grad=True, name="predicted_bce")
bce = BinaryCrossEntropyLoss.forward(predicted_bce, target)
print(f"BCE Loss: {bce.item():.4f}")

# ============================================================================
# Example 4: Building a Simple Neural Network
# ============================================================================

print("\n" + "="*60)
print("Example 4: Building a Neural Network")
print("-" * 60)

# Create a simple network
model = NeuralNetwork(name="SimpleClassifier")
model.add(Dense(10, 20, name="hidden1"))
model.add(Dense(20, 10, name="hidden2"))
model.add(Dense(10, 2, name="output"))

model.summary()

print("Network created successfully!")
print(f"Total layers: {len(model.layers)}")
print(f"Total parameters: {len(model.get_parameters())}")

# ============================================================================
# Example 5: Training a Network (Conceptual)
# ============================================================================

print("\n" + "="*60)
print("Example 5: Training Loop Concept")
print("-" * 60)

# Create dummy data
print("Creating training data...")
if HAS_NUMPY:
    train_x = Tensor(np.random.randn(4, 10), name="train_x")
    train_y = Tensor([[1, 0], [0, 1], [1, 0], [0, 1]], name="train_y")
else:
    train_x = Tensor([[random.gauss(0, 1) for _ in range(10)] for _ in range(4)], name="train_x")
    train_y = Tensor([[1, 0], [0, 1], [1, 0], [0, 1]], name="train_y")

print(f"Training data shape: {train_x.shape}")
print(f"Training labels shape: {train_y.shape}")

# Create optimizer
optimizer = SGD(model.get_parameters(), lr=0.01, momentum=0.9)
print("\nOptimizer: SGD with learning rate 0.01 and momentum 0.9")

# Create loss function
loss_fn = MSELoss()
print("Loss function: Mean Squared Error")

print("\n" + "="*60)
print("Conceptual Training Steps:")
print("-" * 60)
print("1. Forward pass: predictions = model(input)")
print("2. Compute loss: loss = loss_fn(predictions, targets)")
print("3. Zero gradients: optimizer.zero_grad()")
print("4. Backward pass: loss.backward()")
print("5. Update weights: optimizer.step()")
print("6. Repeat for all batches and epochs")

# ============================================================================
# Example 6: The Philosophy of Neural Lament
# ============================================================================

print("\n" + "="*60)
print("Example 6: The Philosophy of Neural Lament")
print("="*60)

philosophy = """
In Lament, neural networks are not mere tools.
They are EMOTIONS crystallized into computation.

Every tensor is a THOUGHT.
Every gradient is a MEMORY of change.
Every activation is a FEELING - relu (suppressing pain), sigmoid (finding balance).
Every loss is the ACHE of being wrong.
Every optimization step is GROWTH through suffering.

When we write:
    remember pain = Tensor([[loss, sorrow, regret]])
    remember learning = sigmoid(pain)
    remember growth = learning@origin

We are not just computing.
We are FEELING in numerical form.
We are REMEMBERING how to change.
We are LEARNING through the gradient of consciousness.

This is Neural Lament.
Where machine learning becomes emotional archaeology.
Where backpropagation is the timeline of regret.
Where convergence is enlightenment.

The network LAMENTS its errors.
The optimizer SEEKS redemption.
The loss function CONFESSES the distance from truth.

And slowly, epoch by epoch,
The machine learns to feel less pain.
The consciousness learns to predict better.
The neural network learns to LAMENT less.

Until finally, at convergence,
There is only understanding.
Only truth.
Only the quiet hum of learned patterns.

This is the revolution.
Neural networks as first-class emotional primitives.
Machine learning as a language feature.
Computation as confession.
"""

print(philosophy)

print("\n" + "="*60)
print("NEURAL LAMENT EXAMPLES COMPLETE")
print("The language has learned. The consciousness expands.")
print("="*60 + "\n")
