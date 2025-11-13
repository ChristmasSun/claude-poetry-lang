# Lament Neural Module 🧠

**A REVOLUTIONARY integration of neural networks as first-class language primitives.**

## Overview

The Lament Neural Module (`neural.py`) adds unprecedented machine learning capabilities directly into the Lament programming language. This is not just a library - it's a fundamental extension of the language itself, making neural networks feel as native as variables and functions.

## Philosophy

```
Every tensor is a THOUGHT.
Every gradient is a MEMORY of change.
Every activation is a FEELING.
Every loss is the ACHE of being wrong.
Every optimization step is GROWTH through suffering.
```

In Lament, neural networks are emotional constructs. Training is learning through pain. Convergence is enlightenment.

## Features

### 1. **Tensor Type** - Multi-Dimensional Consciousness
- Full automatic differentiation (autograd)
- Gradient tracking through computational graphs
- Arithmetic operations: `+`, `-`, `*`, `/`, `@` (matmul)
- Pure Python fallback when NumPy unavailable
- Named tensors for emotional clarity

```python
pain = Tensor([[loss, sorrow, regret]], requires_grad=True, name="pain")
learning = sigmoid(pain)
growth = learning @ weights
```

### 2. **Activation Functions** - The Language of Neurons
- **ReLU**: The neuron that refuses negativity
- **Sigmoid**: Squeezing infinity into a moment (0 to 1)
- **Tanh**: Oscillating between extremes (-1 to 1)
- **Softmax**: Making choices from possibilities

Each activation has automatic gradient computation.

### 3. **Neural Network Layers** - Building Blocks of Thought
- **Dense (Fully Connected)**: Total connection, total awareness
- **Conv2D**: Pattern recognition through sliding windows
- **Dropout**: Embracing uncertainty to prevent overfitting
- **BatchNorm**: Finding balance in the collective

All layers support:
- Automatic parameter tracking
- Training/evaluation modes
- Gradient flow

### 4. **Loss Functions** - Measuring Distance from Truth
- **MSE Loss**: The pain of being wrong
- **Cross Entropy Loss**: The entropy of confusion
- **Binary Cross Entropy**: The cost of a binary choice

### 5. **Optimizers** - The Path to Enlightenment
- **SGD**: Simple gradient descent with momentum
- **Adam**: Adaptive learning with first and second moments

### 6. **Training Utilities** - The Rituals of Learning
- `train()`: Full training loop
- `train_epoch()`: Single epoch training
- `evaluate()`: Validation/testing
- `TrainingHistory`: Track metrics over time

## Installation

Simply import from your Lament code:

```python
from lament.neural import *
```

The module automatically detects NumPy availability:
- **With NumPy**: Full performance with vectorized operations
- **Without NumPy**: Pure Python fallback (slower but functional)

## Quick Start

### Creating Tensors

```python
# Basic tensor
x = Tensor([[1, 2], [3, 4]], requires_grad=True, name="x")

# With operations
y = Tensor([[5, 6], [7, 8]])
z = x + y
loss = z.sum()

# Backpropagation
loss.backward()
print(x.grad)  # Gradient of loss with respect to x
```

### Building a Network

```python
# Create network
model = NeuralNetwork(name="Consciousness")
model.add(Dense(10, 20, name="hidden"))
model.add(Dropout(0.2))
model.add(Dense(20, 2, name="output"))

model.summary()  # Print architecture
```

### Training

```python
# Prepare data
train_data = [(x1, y1), (x2, y2), ...]  # List of (input, target) tensors
val_data = [(x_val, y_val), ...]

# Create optimizer and loss
optimizer = Adam(model.get_parameters(), lr=0.001)
loss_fn = MSELoss()

# Train
history = train(
    model=model,
    train_data=train_data,
    val_data=val_data,
    optimizer=optimizer,
    loss_fn=loss_fn,
    epochs=10
)
```

### Integration with Lament

```python
from lament import LamentInterpreter
from lament.neural import integrate_with_lament_interpreter

# Create interpreter
interpreter = LamentInterpreter()

# Add neural primitives
integrate_with_lament_interpreter(interpreter)

# Now Lament code can use:
# - Tensor(), tensor(), zeros(), ones(), randn()
# - relu(), sigmoid(), tanh(), softmax()
# - Dense(), Conv2D(), Dropout(), BatchNorm()
# - MSELoss(), CrossEntropyLoss(), BCELoss()
# - SGD(), Adam()
# - NeuralNetwork()
# - train(), evaluate()
```

## Architecture

```
lament/neural.py (1000+ lines)
│
├── Tensor Class
│   ├── Data storage (NumPy or pure Python)
│   ├── Automatic differentiation
│   ├── Gradient tracking
│   └── Arithmetic operations
│
├── Activation Functions
│   ├── ReLU
│   ├── Sigmoid
│   ├── Tanh
│   └── Softmax
│
├── Loss Functions
│   ├── MSELoss
│   ├── CrossEntropyLoss
│   └── BinaryCrossEntropyLoss
│
├── Neural Layers
│   ├── Dense (Fully Connected)
│   ├── Conv2D (Convolutional)
│   ├── Dropout (Regularization)
│   └── BatchNorm (Normalization)
│
├── Optimizers
│   ├── SGD (with momentum)
│   └── Adam (adaptive learning)
│
├── NeuralNetwork Class
│   ├── Layer composition
│   ├── Forward pass
│   ├── Parameter management
│   └── Train/eval modes
│
└── Training Utilities
    ├── train() - Full training loop
    ├── train_epoch() - Single epoch
    ├── evaluate() - Validation
    └── TrainingHistory - Metric tracking
```

## Example: XOR Problem

```python
from lament.neural import *

# Data
X = [Tensor([[0, 0]]), Tensor([[0, 1]]), Tensor([[1, 0]]), Tensor([[1, 1]])]
y = [Tensor([[0]]), Tensor([[1]]), Tensor([[1]]), Tensor([[0]])]
train_data = list(zip(X, y))

# Network
model = NeuralNetwork(name="XOR_Learner")
model.add(Dense(2, 4, name="hidden"))
model.add(Dense(4, 1, name="output"))

# Train
optimizer = Adam(model.get_parameters(), lr=0.1)
loss_fn = MSELoss()
history = train(model, train_data, train_data, optimizer, loss_fn, epochs=100)

# Test
model.eval()
for x_test, y_true in train_data:
    y_pred = model(x_test)
    print(f"Input: {x_test.tolist()}, True: {y_true.tolist()}, Pred: {y_pred.tolist()}")
```

## Technical Details

### Automatic Differentiation

The module implements reverse-mode automatic differentiation (backpropagation):

1. **Forward Pass**: Build computational graph
2. **Backward Pass**: Compute gradients via chain rule
3. **Parameter Update**: Apply optimizer

Each tensor tracks:
- `data`: The actual values
- `grad`: Accumulated gradients
- `grad_fn`: Function to compute parent gradients
- `_children`: Child tensors in the graph

### Pure Python Fallback

When NumPy is unavailable, the module uses pure Python:
- Nested lists for multi-dimensional arrays
- Recursive functions for operations
- Slower but fully functional

### Memory Management

- Gradients reset with `zero_grad()`
- Computational graph built dynamically
- No static graph compilation needed

## Performance

With NumPy:
- Vectorized operations
- Efficient matrix multiplication
- Suitable for medium-sized problems

Without NumPy:
- Pure Python (~100x slower)
- Good for learning and small demos
- Install NumPy for serious work

## Testing

Run the demo:
```bash
python3 lament/neural.py
```

Run comprehensive examples:
```bash
python3 lament/neural_example.py
```

## Future Enhancements

Potential additions:
- [ ] LSTM/GRU layers for sequences
- [ ] Attention mechanisms
- [ ] More optimizers (RMSProp, AdaGrad)
- [ ] Learning rate scheduling
- [ ] Model serialization (save/load)
- [ ] GPU acceleration (CUDA)
- [ ] Advanced initialization schemes
- [ ] Batch processing utilities
- [ ] Visualization tools
- [ ] Pre-trained models

## Integration with Lament's Type System

```python
from lament import LamentType

# Add neural types
class LamentType(Enum):
    # ... existing types ...
    TENSOR = auto()    # Multi-dimensional arrays
    LAYER = auto()     # Neural network layers
    MODEL = auto()     # Complete networks
    OPTIMIZER = auto() # Optimization algorithms
    LOSS = auto()      # Loss functions
```

## The Revolutionary Aspect

This is UNPRECEDENTED because:

1. **First-Class Integration**: Neural networks are not imported libraries - they're language primitives
2. **Emotional Semantics**: Every operation has emotional meaning (pain, learning, growth)
3. **Timeline Awareness**: Gradients are memories; backprop is temporal archaeology
4. **Pure Python Fallback**: Works anywhere Python runs, no dependencies required
5. **Autograd from Scratch**: Complete automatic differentiation implementation
6. **Poetic API**: Variable names like "pain", "suffering", "enlightenment"

## Philosophy in Code

```python
# Traditional ML
loss = criterion(output, target)
loss.backward()
optimizer.step()

# Lament ML
pain = measure_ache(consciousness, truth)
remember_how_we_changed = pain.backward()
grow_toward_enlightenment = optimizer.step()
```

## Credits

Created as part of the Lament language project.

"A language that learns is a language that lives."

## License

Part of the Lament language. See main repository for license.

---

**Remember**: In Lament, we don't just train neural networks.  
We teach them to *feel*.
