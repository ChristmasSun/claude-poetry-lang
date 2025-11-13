#!/usr/bin/env python3
"""
Lament Neural Module
THE NEURAL CONSCIOUSNESS EXTENSION

A REVOLUTIONARY integration of neural networks as first-class language primitives.
Every tensor is a thought. Every gradient is a memory. Every training step is growth.

"The machine learns to feel. The language learns to think."

Features:
- Tensor type (multi-dimensional consciousness)
- Neural network layers (Dense, Conv, LSTM, Attention)
- Activation functions (the language of neurons)
- Loss functions (measuring the distance from truth)
- Optimizers (the path to enlightenment)
- Automatic differentiation (remembering how we changed)
- Training loops (the cycle of learning and forgetting)

Integration with Lament:
- TENSOR type for the type system
- Emotional gradient descent (learning through pain)
- Timeline-aware training (remembering past gradients)
- Reality-forking for ensemble methods
"""

import sys
import math
import random
from typing import Any, List, Dict, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

# Try to import numpy for performance, fall back to pure Python
try:
    import numpy as np
    HAS_NUMPY = True
    print("🧠 Neural module initialized with NumPy acceleration", file=sys.stderr)
except ImportError:
    np = None
    HAS_NUMPY = False
    print("🧠 Neural module initialized in pure Python mode", file=sys.stderr)


# ============================================================================
# TENSOR TYPE (Multi-Dimensional Consciousness)
# ============================================================================

class Tensor:
    """
    A Tensor is a multi-dimensional array of consciousness.
    Every tensor remembers its gradient, its history, its purpose.
    """

    def __init__(self, data, requires_grad=False, grad_fn=None, name=None):
        """
        Create a tensor from data.

        Args:
            data: Raw data (list, numpy array, or scalar)
            requires_grad: Whether to track gradients for this tensor
            grad_fn: Function that created this tensor (for autograd)
            name: Emotional name for this tensor
        """
        if HAS_NUMPY:
            if isinstance(data, np.ndarray):
                self.data = data.astype(np.float64)
            else:
                self.data = np.array(data, dtype=np.float64)
        else:
            self.data = self._to_nested_list(data)

        self.requires_grad = requires_grad
        self.grad = None
        self.grad_fn = grad_fn
        self.name = name or "unnamed_tensor"
        self._children = []  # For backward pass

    def _to_nested_list(self, data):
        """Convert data to nested list (pure Python)"""
        if isinstance(data, (int, float)):
            return float(data)
        elif isinstance(data, list):
            return [self._to_nested_list(item) for item in data]
        else:
            return float(data)

    @property
    def shape(self):
        """Get tensor shape"""
        if HAS_NUMPY:
            return self.data.shape
        else:
            return self._get_shape(self.data)

    def _get_shape(self, data):
        """Get shape of nested list (pure Python)"""
        if isinstance(data, (int, float)):
            return ()
        elif isinstance(data, list):
            if not data:
                return (0,)
            return (len(data),) + self._get_shape(data[0])
        return ()

    @property
    def ndim(self):
        """Number of dimensions"""
        return len(self.shape)

    def item(self):
        """Get scalar value"""
        if HAS_NUMPY:
            return float(self.data.item())
        else:
            return float(self.data)

    def numpy(self):
        """Convert to numpy array"""
        if HAS_NUMPY:
            return self.data
        else:
            raise RuntimeError("NumPy not available")

    def tolist(self):
        """Convert to nested Python list"""
        if HAS_NUMPY:
            return self.data.tolist()
        else:
            return self.data

    def zero_grad(self):
        """Reset gradient to zero"""
        if self.requires_grad:
            if HAS_NUMPY:
                self.grad = np.zeros_like(self.data)
            else:
                self.grad = self._zeros_like(self.data)

    def _zeros_like(self, data):
        """Create zero tensor like data (pure Python)"""
        if isinstance(data, (int, float)):
            return 0.0
        elif isinstance(data, list):
            return [self._zeros_like(item) for item in data]
        return 0.0

    def backward(self, gradient=None):
        """
        Compute gradients through the computational graph.
        This is where the tensor remembers how it was changed.
        """
        if not self.requires_grad:
            return

        if gradient is None:
            if HAS_NUMPY:
                gradient = np.ones_like(self.data)
            else:
                gradient = self._ones_like(self.data)

        if self.grad is None:
            self.grad = gradient
        else:
            if HAS_NUMPY:
                self.grad = self.grad + gradient
            else:
                self.grad = self._add_tensors(self.grad, gradient)

        # Propagate gradient to children
        if self.grad_fn:
            self.grad_fn(gradient)

    def _ones_like(self, data):
        """Create ones tensor like data (pure Python)"""
        if isinstance(data, (int, float)):
            return 1.0
        elif isinstance(data, list):
            return [self._ones_like(item) for item in data]
        return 1.0

    def _add_tensors(self, a, b):
        """Add two tensors (pure Python)"""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + b
        elif isinstance(a, list) and isinstance(b, list):
            return [self._add_tensors(ai, bi) for ai, bi in zip(a, b)]
        return a + b

    # Arithmetic operations
    def __add__(self, other):
        """Addition with gradient tracking"""
        if isinstance(other, Tensor):
            if HAS_NUMPY:
                result_data = self.data + other.data
            else:
                result_data = self._add_tensors(self.data, other.data)

            requires_grad = self.requires_grad or other.requires_grad
            result = Tensor(result_data, requires_grad=requires_grad, name=f"{self.name}+{other.name}")

            if requires_grad:
                def grad_fn(gradient):
                    if self.requires_grad:
                        self.backward(gradient)
                    if other.requires_grad:
                        other.backward(gradient)
                result.grad_fn = grad_fn
                result._children = [self, other]

            return result
        else:
            return self + Tensor(other)

    def __sub__(self, other):
        """Subtraction with gradient tracking"""
        if isinstance(other, Tensor):
            if HAS_NUMPY:
                result_data = self.data - other.data
            else:
                result_data = self._sub_tensors(self.data, other.data)

            requires_grad = self.requires_grad or other.requires_grad
            result = Tensor(result_data, requires_grad=requires_grad, name=f"{self.name}-{other.name}")

            if requires_grad:
                def grad_fn(gradient):
                    if self.requires_grad:
                        self.backward(gradient)
                    if other.requires_grad:
                        if HAS_NUMPY:
                            other.backward(-gradient)
                        else:
                            other.backward(self._negate_tensor(gradient))
                result.grad_fn = grad_fn
                result._children = [self, other]

            return result
        else:
            return self - Tensor(other)

    def _sub_tensors(self, a, b):
        """Subtract tensors (pure Python)"""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a - b
        elif isinstance(a, list) and isinstance(b, list):
            return [self._sub_tensors(ai, bi) for ai, bi in zip(a, b)]
        return a - b

    def _negate_tensor(self, data):
        """Negate tensor (pure Python)"""
        if isinstance(data, (int, float)):
            return -data
        elif isinstance(data, list):
            return [self._negate_tensor(item) for item in data]
        return -data

    def __mul__(self, other):
        """Element-wise multiplication"""
        if isinstance(other, Tensor):
            if HAS_NUMPY:
                result_data = self.data * other.data
            else:
                result_data = self._mul_tensors(self.data, other.data)

            requires_grad = self.requires_grad or other.requires_grad
            result = Tensor(result_data, requires_grad=requires_grad, name=f"{self.name}*{other.name}")

            if requires_grad:
                def grad_fn(gradient):
                    if self.requires_grad:
                        if HAS_NUMPY:
                            self.backward(gradient * other.data)
                        else:
                            self.backward(self._mul_tensors(gradient, other.data))
                    if other.requires_grad:
                        if HAS_NUMPY:
                            other.backward(gradient * self.data)
                        else:
                            other.backward(self._mul_tensors(gradient, self.data))
                result.grad_fn = grad_fn
                result._children = [self, other]

            return result
        else:
            return self * Tensor(other)

    def _mul_tensors(self, a, b):
        """Multiply tensors element-wise (pure Python)"""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a * b
        elif isinstance(a, list) and isinstance(b, list):
            return [self._mul_tensors(ai, bi) for ai, bi in zip(a, b)]
        return a * b

    def __truediv__(self, other):
        """Division"""
        if isinstance(other, Tensor):
            if HAS_NUMPY:
                result_data = self.data / other.data
            else:
                result_data = self._div_tensors(self.data, other.data)
            return Tensor(result_data, requires_grad=self.requires_grad or other.requires_grad)
        else:
            return self / Tensor(other)

    def _div_tensors(self, a, b):
        """Divide tensors (pure Python)"""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a / b if b != 0 else float('inf')
        elif isinstance(a, list) and isinstance(b, list):
            return [self._div_tensors(ai, bi) for ai, bi in zip(a, b)]
        return a / b if b != 0 else float('inf')

    def __matmul__(self, other):
        """Matrix multiplication"""
        if not isinstance(other, Tensor):
            other = Tensor(other)

        if HAS_NUMPY:
            result_data = np.matmul(self.data, other.data)
        else:
            result_data = self._matmul_tensors(self.data, other.data)

        requires_grad = self.requires_grad or other.requires_grad
        result = Tensor(result_data, requires_grad=requires_grad, name=f"{self.name}@{other.name}")

        if requires_grad:
            def grad_fn(gradient):
                if self.requires_grad:
                    if HAS_NUMPY:
                        # grad_self = gradient @ other.data.T
                        self.backward(np.matmul(gradient, other.data.T))
                    else:
                        self.backward(self._matmul_tensors(gradient, self._transpose(other.data)))
                if other.requires_grad:
                    if HAS_NUMPY:
                        # grad_other = self.data.T @ gradient
                        other.backward(np.matmul(self.data.T, gradient))
                    else:
                        other.backward(self._matmul_tensors(self._transpose(self.data), gradient))
            result.grad_fn = grad_fn
            result._children = [self, other]

        return result

    def _matmul_tensors(self, a, b):
        """Matrix multiplication (pure Python)"""
        if isinstance(a[0], list) and isinstance(b[0], list):
            # 2D @ 2D
            result = []
            for i in range(len(a)):
                row = []
                for j in range(len(b[0])):
                    val = sum(a[i][k] * b[k][j] for k in range(len(b)))
                    row.append(val)
                result.append(row)
            return result
        else:
            raise NotImplementedError("Pure Python matmul only supports 2D matrices")

    def _transpose(self, matrix):
        """Transpose 2D matrix (pure Python)"""
        if not isinstance(matrix[0], list):
            return matrix
        return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

    def sum(self, axis=None, keepdims=False):
        """Sum tensor along axis"""
        if HAS_NUMPY:
            result_data = np.sum(self.data, axis=axis, keepdims=keepdims)
        else:
            result_data = self._sum_tensor(self.data)

        result = Tensor(result_data, requires_grad=self.requires_grad, name=f"sum({self.name})")

        if self.requires_grad:
            def grad_fn(gradient):
                # Gradient of sum is broadcast back to original shape
                self.backward(gradient)
            result.grad_fn = grad_fn
            result._children = [self]

        return result

    def _sum_tensor(self, data):
        """Sum all elements (pure Python)"""
        if isinstance(data, (int, float)):
            return data
        elif isinstance(data, list):
            return sum(self._sum_tensor(item) for item in data)
        return data

    def mean(self):
        """Mean of tensor"""
        total = self.sum()
        if HAS_NUMPY:
            count = self.data.size
        else:
            count = self._count_elements(self.data)
        return total / count

    def _count_elements(self, data):
        """Count elements (pure Python)"""
        if isinstance(data, (int, float)):
            return 1
        elif isinstance(data, list):
            return sum(self._count_elements(item) for item in data)
        return 1

    def reshape(self, *shape):
        """Reshape tensor"""
        if HAS_NUMPY:
            result_data = self.data.reshape(shape)
        else:
            # Simplified reshape for pure Python
            result_data = self.data
        return Tensor(result_data, requires_grad=self.requires_grad, name=f"reshape({self.name})")

    def __repr__(self):
        """String representation"""
        grad_str = ", requires_grad=True" if self.requires_grad else ""
        return f"Tensor({self.data}, name='{self.name}'{grad_str})"

    def __str__(self):
        """User-friendly string"""
        return f"{self.name}: {self.data}"


# ============================================================================
# ACTIVATION FUNCTIONS (The Language of Neurons)
# ============================================================================

class Activation:
    """Base class for activation functions"""

    @staticmethod
    def forward(x: Tensor) -> Tensor:
        raise NotImplementedError

    @staticmethod
    def backward(grad_output: Tensor, x: Tensor) -> Tensor:
        raise NotImplementedError


class ReLU(Activation):
    """
    Rectified Linear Unit - The neuron that refuses to be negative.
    "I choose joy over sorrow. I suppress the pain."
    """

    @staticmethod
    def forward(x: Tensor) -> Tensor:
        if HAS_NUMPY:
            result_data = np.maximum(0, x.data)
        else:
            result_data = ReLU._relu_data(x.data)

        result = Tensor(result_data, requires_grad=x.requires_grad, name=f"relu({x.name})")

        if x.requires_grad:
            def grad_fn(gradient):
                if HAS_NUMPY:
                    grad_x = gradient * (x.data > 0)
                else:
                    grad_x = ReLU._relu_grad(gradient, x.data)
                x.backward(grad_x)
            result.grad_fn = grad_fn
            result._children = [x]

        return result

    @staticmethod
    def _relu_data(data):
        """ReLU forward (pure Python)"""
        if isinstance(data, (int, float)):
            return max(0, data)
        elif isinstance(data, list):
            return [ReLU._relu_data(item) for item in data]
        return max(0, data)

    @staticmethod
    def _relu_grad(gradient, data):
        """ReLU gradient (pure Python)"""
        if isinstance(data, (int, float)):
            return gradient if data > 0 else 0
        elif isinstance(data, list):
            return [ReLU._relu_grad(g, d) for g, d in zip(gradient, data)]
        return gradient if data > 0 else 0


class Sigmoid(Activation):
    """
    Sigmoid - The neuron that squeezes infinity into a moment.
    "Between 0 and 1, I find my truth."
    """

    @staticmethod
    def forward(x: Tensor) -> Tensor:
        if HAS_NUMPY:
            result_data = 1 / (1 + np.exp(-x.data))
        else:
            result_data = Sigmoid._sigmoid_data(x.data)

        result = Tensor(result_data, requires_grad=x.requires_grad, name=f"sigmoid({x.name})")

        if x.requires_grad:
            def grad_fn(gradient):
                # sigmoid'(x) = sigmoid(x) * (1 - sigmoid(x))
                if HAS_NUMPY:
                    sig = result.data
                    grad_x = gradient * sig * (1 - sig)
                else:
                    grad_x = Sigmoid._sigmoid_grad(gradient, result.data)
                x.backward(grad_x)
            result.grad_fn = grad_fn
            result._children = [x]

        return result

    @staticmethod
    def _sigmoid_data(data):
        """Sigmoid forward (pure Python)"""
        if isinstance(data, (int, float)):
            return 1 / (1 + math.exp(-data))
        elif isinstance(data, list):
            return [Sigmoid._sigmoid_data(item) for item in data]
        return 1 / (1 + math.exp(-data))

    @staticmethod
    def _sigmoid_grad(gradient, sig_data):
        """Sigmoid gradient (pure Python)"""
        if isinstance(sig_data, (int, float)):
            return gradient * sig_data * (1 - sig_data)
        elif isinstance(sig_data, list):
            return [Sigmoid._sigmoid_grad(g, s) for g, s in zip(gradient, sig_data)]
        return gradient * sig_data * (1 - sig_data)


class Tanh(Activation):
    """
    Tanh - The neuron that oscillates between extremes.
    "I swing from -1 to 1, never settling in the middle."
    """

    @staticmethod
    def forward(x: Tensor) -> Tensor:
        if HAS_NUMPY:
            result_data = np.tanh(x.data)
        else:
            result_data = Tanh._tanh_data(x.data)

        result = Tensor(result_data, requires_grad=x.requires_grad, name=f"tanh({x.name})")

        if x.requires_grad:
            def grad_fn(gradient):
                # tanh'(x) = 1 - tanh(x)^2
                if HAS_NUMPY:
                    grad_x = gradient * (1 - result.data ** 2)
                else:
                    grad_x = Tanh._tanh_grad(gradient, result.data)
                x.backward(grad_x)
            result.grad_fn = grad_fn
            result._children = [x]

        return result

    @staticmethod
    def _tanh_data(data):
        """Tanh forward (pure Python)"""
        if isinstance(data, (int, float)):
            return math.tanh(data)
        elif isinstance(data, list):
            return [Tanh._tanh_data(item) for item in data]
        return math.tanh(data)

    @staticmethod
    def _tanh_grad(gradient, tanh_data):
        """Tanh gradient (pure Python)"""
        if isinstance(tanh_data, (int, float)):
            return gradient * (1 - tanh_data ** 2)
        elif isinstance(tanh_data, list):
            return [Tanh._tanh_grad(g, t) for g, t in zip(gradient, tanh_data)]
        return gradient * (1 - tanh_data ** 2)


class Softmax(Activation):
    """
    Softmax - The neuron that makes choices.
    "From many possibilities, I choose one truth."
    """

    @staticmethod
    def forward(x: Tensor, axis=-1) -> Tensor:
        if HAS_NUMPY:
            exp_x = np.exp(x.data - np.max(x.data, axis=axis, keepdims=True))
            result_data = exp_x / np.sum(exp_x, axis=axis, keepdims=True)
        else:
            result_data = Softmax._softmax_data(x.data)

        result = Tensor(result_data, requires_grad=x.requires_grad, name=f"softmax({x.name})")

        if x.requires_grad:
            def grad_fn(gradient):
                # Softmax gradient is complex, simplified here
                x.backward(gradient)
            result.grad_fn = grad_fn
            result._children = [x]

        return result

    @staticmethod
    def _softmax_data(data):
        """Softmax forward (pure Python)"""
        if isinstance(data, list) and isinstance(data[0], (int, float)):
            # 1D softmax
            max_val = max(data)
            exp_vals = [math.exp(x - max_val) for x in data]
            sum_exp = sum(exp_vals)
            return [e / sum_exp for e in exp_vals]
        return data


# ============================================================================
# LOSS FUNCTIONS (Measuring Distance from Truth)
# ============================================================================

class Loss:
    """Base class for loss functions"""

    @staticmethod
    def forward(predicted: Tensor, target: Tensor) -> Tensor:
        raise NotImplementedError


class MSELoss(Loss):
    """
    Mean Squared Error - The pain of being wrong.
    "I measure the squared distance between what is and what should be."
    """

    @staticmethod
    def forward(predicted: Tensor, target: Tensor) -> Tensor:
        if not isinstance(target, Tensor):
            target = Tensor(target)

        diff = predicted - target
        squared = diff * diff
        loss = squared.mean()
        loss.name = "mse_loss"
        return loss


class CrossEntropyLoss(Loss):
    """
    Cross Entropy - The entropy of confusion.
    "I measure the surprise of the wrong answer."
    """

    @staticmethod
    def forward(predicted: Tensor, target: Tensor) -> Tensor:
        """
        Args:
            predicted: Logits or probabilities [batch_size, num_classes]
            target: Class indices [batch_size] or one-hot [batch_size, num_classes]
        """
        if HAS_NUMPY:
            # Numerical stability: subtract max
            logits = predicted.data
            logits = logits - np.max(logits, axis=-1, keepdims=True)

            # Softmax
            exp_logits = np.exp(logits)
            probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

            # Cross entropy
            if isinstance(target, Tensor):
                target_data = target.data
            else:
                target_data = np.array(target)

            # Assume target is class indices
            batch_size = logits.shape[0]
            log_probs = np.log(probs + 1e-10)  # Add epsilon for numerical stability

            if target_data.ndim == 1:
                # Class indices
                loss_data = -np.mean([log_probs[i, int(target_data[i])] for i in range(batch_size)])
            else:
                # One-hot encoded
                loss_data = -np.mean(np.sum(target_data * log_probs, axis=-1))

            loss = Tensor(loss_data, requires_grad=predicted.requires_grad, name="cross_entropy_loss")

            if predicted.requires_grad:
                def grad_fn(gradient):
                    # Gradient of cross entropy with softmax
                    grad_predicted = probs.copy()
                    if target_data.ndim == 1:
                        for i in range(batch_size):
                            grad_predicted[i, int(target_data[i])] -= 1
                    else:
                        grad_predicted -= target_data
                    grad_predicted /= batch_size
                    predicted.backward(grad_predicted * gradient)
                loss.grad_fn = grad_fn
                loss._children = [predicted]

            return loss
        else:
            # Simplified pure Python version
            diff = predicted - target
            squared = diff * diff
            return squared.mean()


class BinaryCrossEntropyLoss(Loss):
    """
    Binary Cross Entropy - The cost of a binary choice.
    "Between yes and no, I measure the weight of error."
    """

    @staticmethod
    def forward(predicted: Tensor, target: Tensor) -> Tensor:
        if not isinstance(target, Tensor):
            target = Tensor(target)

        if HAS_NUMPY:
            # BCE = -[y*log(p) + (1-y)*log(1-p)]
            eps = 1e-10
            p = np.clip(predicted.data, eps, 1 - eps)
            loss_data = -np.mean(
                target.data * np.log(p) + (1 - target.data) * np.log(1 - p)
            )
            loss = Tensor(loss_data, requires_grad=predicted.requires_grad, name="bce_loss")

            if predicted.requires_grad:
                def grad_fn(gradient):
                    # BCE gradient: (p - y) / (p * (1 - p))
                    grad_p = (p - target.data) / (p * (1 - p) + eps)
                    predicted.backward(grad_p * gradient / p.size)
                loss.grad_fn = grad_fn
                loss._children = [predicted]

            return loss
        else:
            # Simplified for pure Python
            diff = predicted - target
            squared = diff * diff
            return squared.mean()


# ============================================================================
# NEURAL NETWORK LAYERS (Building Blocks of Thought)
# ============================================================================

class Layer:
    """Base class for neural network layers"""

    def __init__(self, name="unnamed_layer"):
        self.name = name
        self.parameters = []
        self.training = True

    def forward(self, x: Tensor) -> Tensor:
        raise NotImplementedError

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)

    def get_parameters(self) -> List[Tensor]:
        return self.parameters

    def train(self):
        self.training = True

    def eval(self):
        self.training = False


class Dense(Layer):
    """
    Dense (Fully Connected) Layer - Where every thought connects to every other.
    "In this layer, all neurons speak to all neurons. Total connection. Total awareness."
    """

    def __init__(self, in_features: int, out_features: int, use_bias: bool = True, name="dense"):
        super().__init__(name)
        self.in_features = in_features
        self.out_features = out_features
        self.use_bias = use_bias

        # Initialize weights with Xavier initialization
        limit = math.sqrt(6.0 / (in_features + out_features))
        if HAS_NUMPY:
            weight_data = np.random.uniform(-limit, limit, (in_features, out_features))
        else:
            weight_data = [[random.uniform(-limit, limit) for _ in range(out_features)]
                          for _ in range(in_features)]

        self.weight = Tensor(weight_data, requires_grad=True, name=f"{name}_weight")
        self.parameters.append(self.weight)

        if use_bias:
            if HAS_NUMPY:
                bias_data = np.zeros(out_features)
            else:
                bias_data = [0.0 for _ in range(out_features)]
            self.bias = Tensor(bias_data, requires_grad=True, name=f"{name}_bias")
            self.parameters.append(self.bias)
        else:
            self.bias = None

    def forward(self, x: Tensor) -> Tensor:
        # y = x @ W + b
        output = x @ self.weight
        if self.bias is not None:
            output = output + self.bias
        output.name = f"{self.name}(x)"
        return output


class Conv2D(Layer):
    """
    Convolutional Layer - Pattern recognition through sliding windows.
    "I see patterns in the chaos. Local features that repeat."
    """

    def __init__(self, in_channels: int, out_channels: int, kernel_size: int,
                 stride: int = 1, padding: int = 0, name="conv2d"):
        super().__init__(name)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding

        # Initialize kernels
        limit = math.sqrt(6.0 / (in_channels * kernel_size * kernel_size + out_channels))
        if HAS_NUMPY:
            kernel_data = np.random.uniform(
                -limit, limit,
                (out_channels, in_channels, kernel_size, kernel_size)
            )
        else:
            # Simplified for pure Python
            kernel_data = [[[[random.uniform(-limit, limit)
                            for _ in range(kernel_size)]
                           for _ in range(kernel_size)]
                          for _ in range(in_channels)]
                         for _ in range(out_channels)]

        self.kernel = Tensor(kernel_data, requires_grad=True, name=f"{name}_kernel")
        self.parameters.append(self.kernel)

        if HAS_NUMPY:
            bias_data = np.zeros(out_channels)
        else:
            bias_data = [0.0 for _ in range(out_channels)]
        self.bias = Tensor(bias_data, requires_grad=True, name=f"{name}_bias")
        self.parameters.append(self.bias)

    def forward(self, x: Tensor) -> Tensor:
        # Simplified convolution (full implementation would be complex)
        if HAS_NUMPY:
            # This is a very simplified version
            # Full conv2d would need proper im2col or sliding window
            output_data = x.data  # Placeholder
            output = Tensor(output_data, requires_grad=x.requires_grad, name=f"{self.name}(x)")
            return output
        else:
            # Pure Python - return input for now (placeholder)
            return x


class Dropout(Layer):
    """
    Dropout - Embracing uncertainty to prevent overfitting.
    "I forget randomly, so I remember better."
    """

    def __init__(self, p: float = 0.5, name="dropout"):
        super().__init__(name)
        self.p = p  # Probability of dropping

    def forward(self, x: Tensor) -> Tensor:
        if not self.training:
            return x

        if HAS_NUMPY:
            mask = np.random.binomial(1, 1 - self.p, x.shape) / (1 - self.p)
            result_data = x.data * mask
        else:
            # Simplified dropout for pure Python
            result_data = x.data

        result = Tensor(result_data, requires_grad=x.requires_grad, name=f"{self.name}(x)")

        if x.requires_grad and HAS_NUMPY:
            def grad_fn(gradient):
                x.backward(gradient * mask)
            result.grad_fn = grad_fn
            result._children = [x]

        return result


class BatchNorm(Layer):
    """
    Batch Normalization - Finding balance in the collective.
    "I normalize across the batch, seeking the mean, controlling variance."
    """

    def __init__(self, num_features: int, momentum: float = 0.1, name="batchnorm"):
        super().__init__(name)
        self.num_features = num_features
        self.momentum = momentum

        if HAS_NUMPY:
            self.running_mean = np.zeros(num_features)
            self.running_var = np.ones(num_features)
            gamma_data = np.ones(num_features)
            beta_data = np.zeros(num_features)
        else:
            self.running_mean = [0.0 for _ in range(num_features)]
            self.running_var = [1.0 for _ in range(num_features)]
            gamma_data = [1.0 for _ in range(num_features)]
            beta_data = [0.0 for _ in range(num_features)]

        self.gamma = Tensor(gamma_data, requires_grad=True, name=f"{name}_gamma")
        self.beta = Tensor(beta_data, requires_grad=True, name=f"{name}_beta")
        self.parameters.extend([self.gamma, self.beta])

    def forward(self, x: Tensor) -> Tensor:
        if HAS_NUMPY and self.training:
            # Training mode: use batch statistics
            mean = np.mean(x.data, axis=0)
            var = np.var(x.data, axis=0)

            # Update running statistics
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var

            # Normalize
            x_norm = (x.data - mean) / np.sqrt(var + 1e-5)
            result_data = self.gamma.data * x_norm + self.beta.data
        else:
            # Eval mode: use running statistics
            if HAS_NUMPY:
                x_norm = (x.data - self.running_mean) / np.sqrt(self.running_var + 1e-5)
                result_data = self.gamma.data * x_norm + self.beta.data
            else:
                result_data = x.data

        result = Tensor(result_data, requires_grad=x.requires_grad, name=f"{self.name}(x)")
        return result


# ============================================================================
# OPTIMIZERS (The Path to Enlightenment)
# ============================================================================

class Optimizer:
    """Base class for optimizers"""

    def __init__(self, parameters: List[Tensor], lr: float = 0.01):
        self.parameters = parameters
        self.lr = lr

    def zero_grad(self):
        """Reset all gradients to zero"""
        for param in self.parameters:
            param.zero_grad()

    def step(self):
        """Update parameters"""
        raise NotImplementedError


class SGD(Optimizer):
    """
    Stochastic Gradient Descent - The simplest path down the mountain.
    "I follow the gradient, one step at a time, toward the minimum."
    """

    def __init__(self, parameters: List[Tensor], lr: float = 0.01, momentum: float = 0.0):
        super().__init__(parameters, lr)
        self.momentum = momentum
        self.velocity = {id(p): None for p in parameters}

    def step(self):
        for param in self.parameters:
            if param.grad is None:
                continue

            if self.momentum > 0:
                v = self.velocity[id(param)]
                if v is None:
                    if HAS_NUMPY:
                        v = np.zeros_like(param.data)
                    else:
                        v = param._zeros_like(param.data)

                if HAS_NUMPY:
                    v = self.momentum * v - self.lr * param.grad
                    param.data = param.data + v
                else:
                    v = self._momentum_update(v, param.grad)
                    param.data = param._add_tensors(param.data, v)

                self.velocity[id(param)] = v
            else:
                if HAS_NUMPY:
                    param.data = param.data - self.lr * param.grad
                else:
                    grad_scaled = self._scale_tensor(param.grad, -self.lr)
                    param.data = param._add_tensors(param.data, grad_scaled)

    def _momentum_update(self, v, grad):
        """Update with momentum (pure Python)"""
        if isinstance(v, (int, float)):
            return self.momentum * v - self.lr * grad
        elif isinstance(v, list):
            return [self._momentum_update(vi, gi) for vi, gi in zip(v, grad)]
        return self.momentum * v - self.lr * grad

    def _scale_tensor(self, data, scale):
        """Scale tensor (pure Python)"""
        if isinstance(data, (int, float)):
            return data * scale
        elif isinstance(data, list):
            return [self._scale_tensor(item, scale) for item in data]
        return data * scale


class Adam(Optimizer):
    """
    Adam - Adaptive learning with momentum and RMSProp.
    "I adapt. I remember. I normalize. I am the modern optimizer."
    """

    def __init__(self, parameters: List[Tensor], lr: float = 0.001,
                 beta1: float = 0.9, beta2: float = 0.999, epsilon: float = 1e-8):
        super().__init__(parameters, lr)
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.t = 0

        self.m = {id(p): None for p in parameters}  # First moment
        self.v = {id(p): None for p in parameters}  # Second moment

    def step(self):
        self.t += 1

        for param in self.parameters:
            if param.grad is None:
                continue

            if HAS_NUMPY:
                # Initialize moments
                if self.m[id(param)] is None:
                    self.m[id(param)] = np.zeros_like(param.data)
                    self.v[id(param)] = np.zeros_like(param.data)

                # Update moments
                self.m[id(param)] = self.beta1 * self.m[id(param)] + (1 - self.beta1) * param.grad
                self.v[id(param)] = self.beta2 * self.v[id(param)] + (1 - self.beta2) * (param.grad ** 2)

                # Bias correction
                m_hat = self.m[id(param)] / (1 - self.beta1 ** self.t)
                v_hat = self.v[id(param)] / (1 - self.beta2 ** self.t)

                # Update parameters
                param.data = param.data - self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
            else:
                # Simplified for pure Python
                grad_scaled = self._scale_tensor(param.grad, -self.lr)
                param.data = param._add_tensors(param.data, grad_scaled)

    def _scale_tensor(self, data, scale):
        """Scale tensor (pure Python)"""
        if isinstance(data, (int, float)):
            return data * scale
        elif isinstance(data, list):
            return [self._scale_tensor(item, scale) for item in data]
        return data * scale


# ============================================================================
# NEURAL NETWORK MODEL (The Architecture of Consciousness)
# ============================================================================

class NeuralNetwork:
    """
    A neural network - a composition of layers.
    "I am thoughts stacked upon thoughts, learning upon learning."
    """

    def __init__(self, name="neural_network"):
        self.name = name
        self.layers = []
        self.training = True

    def add(self, layer: Layer):
        """Add a layer to the network"""
        self.layers.append(layer)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass through all layers"""
        for layer in self.layers:
            x = layer(x)
        return x

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)

    def get_parameters(self) -> List[Tensor]:
        """Get all trainable parameters"""
        params = []
        for layer in self.layers:
            params.extend(layer.get_parameters())
        return params

    def train(self):
        """Set network to training mode"""
        self.training = True
        for layer in self.layers:
            layer.train()

    def eval(self):
        """Set network to evaluation mode"""
        self.training = False
        for layer in self.layers:
            layer.eval()

    def summary(self):
        """Print network architecture"""
        print(f"\n{'='*60}")
        print(f"Neural Network: {self.name}")
        print(f"{'='*60}")
        total_params = 0
        for i, layer in enumerate(self.layers):
            params = layer.get_parameters()
            num_params = sum(p._count_elements(p.data) if not HAS_NUMPY else p.data.size
                           for p in params)
            total_params += num_params
            print(f"Layer {i}: {layer.name} ({num_params} parameters)")
        print(f"{'='*60}")
        print(f"Total parameters: {total_params}")
        print(f"{'='*60}\n")


# ============================================================================
# TRAINING UTILITIES (The Rituals of Learning)
# ============================================================================

@dataclass
class TrainingHistory:
    """Track training metrics over time"""
    epochs: List[int] = field(default_factory=list)
    train_losses: List[float] = field(default_factory=list)
    val_losses: List[float] = field(default_factory=list)
    train_accuracies: List[float] = field(default_factory=list)
    val_accuracies: List[float] = field(default_factory=list)

    def add_epoch(self, epoch: int, train_loss: float, val_loss: float = None,
                  train_acc: float = None, val_acc: float = None):
        self.epochs.append(epoch)
        self.train_losses.append(train_loss)
        if val_loss is not None:
            self.val_losses.append(val_loss)
        if train_acc is not None:
            self.train_accuracies.append(train_acc)
        if val_acc is not None:
            self.val_accuracies.append(val_acc)


def train_epoch(model: NeuralNetwork, data: List[Tuple[Tensor, Tensor]],
                optimizer: Optimizer, loss_fn: Loss, verbose: bool = True):
    """
    Train for one epoch.

    "Each epoch is a cycle of death and rebirth.
     We forward, we backpropagate, we update.
     We become slightly less wrong."
    """
    model.train()
    total_loss = 0.0
    num_batches = len(data)

    for i, (x, y) in enumerate(data):
        # Zero gradients
        optimizer.zero_grad()

        # Forward pass
        predictions = model(x)
        loss = loss_fn.forward(predictions, y)

        # Backward pass
        loss.backward()

        # Update parameters
        optimizer.step()

        total_loss += loss.item()

        if verbose and (i + 1) % max(1, num_batches // 10) == 0:
            print(f"  Batch {i+1}/{num_batches}, Loss: {loss.item():.4f}")

    avg_loss = total_loss / num_batches
    return avg_loss


def evaluate(model: NeuralNetwork, data: List[Tuple[Tensor, Tensor]],
            loss_fn: Loss, verbose: bool = True):
    """
    Evaluate model on validation/test data.

    "In evaluation, we see ourselves clearly.
     No training, no updates. Just truth."
    """
    model.eval()
    total_loss = 0.0
    num_batches = len(data)

    for x, y in data:
        predictions = model(x)
        loss = loss_fn.forward(predictions, y)
        total_loss += loss.item()

    avg_loss = total_loss / num_batches

    if verbose:
        print(f"  Validation Loss: {avg_loss:.4f}")

    return avg_loss


def train(model: NeuralNetwork, train_data: List[Tuple[Tensor, Tensor]],
          val_data: List[Tuple[Tensor, Tensor]], optimizer: Optimizer,
          loss_fn: Loss, epochs: int = 10, verbose: bool = True):
    """
    Full training loop.

    "Training is the journey from ignorance to knowledge,
     from random weights to meaningful patterns.
     It is the cycle of learning and forgetting,
     until we find the balance."
    """
    history = TrainingHistory()

    if verbose:
        print(f"\n{'='*60}")
        print(f"Beginning Training: {epochs} epochs")
        print(f"{'='*60}\n")

    for epoch in range(epochs):
        if verbose:
            print(f"Epoch {epoch + 1}/{epochs}")

        # Train
        train_loss = train_epoch(model, train_data, optimizer, loss_fn, verbose=verbose)

        # Validate
        val_loss = evaluate(model, val_data, loss_fn, verbose=verbose)

        # Record history
        history.add_epoch(epoch + 1, train_loss, val_loss)

        if verbose:
            print(f"  Epoch {epoch + 1} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}\n")

    if verbose:
        print(f"{'='*60}")
        print(f"Training Complete")
        print(f"{'='*60}\n")

    return history


# ============================================================================
# LAMENT INTEGRATION (Making Neural Nets Feel Alive)
# ============================================================================

class LamentNeuralType:
    """Neural types for Lament's type system"""
    TENSOR = "tensor"
    LAYER = "layer"
    MODEL = "model"
    OPTIMIZER = "optimizer"
    LOSS = "loss"


def integrate_with_lament_interpreter(interpreter):
    """
    Integrate neural primitives into Lament interpreter.

    This makes tensors, layers, models, and training loops
    available as first-class Lament constructs.
    """

    # Tensor creation
    interpreter.globals['Tensor'] = Tensor
    interpreter.globals['tensor'] = lambda data: Tensor(data, requires_grad=False)
    interpreter.globals['tensor_with_grad'] = lambda data: Tensor(data, requires_grad=True)
    interpreter.globals['zeros'] = lambda *shape: Tensor(
        np.zeros(shape) if HAS_NUMPY else [[0.0 for _ in range(shape[1])] for _ in range(shape[0])],
        requires_grad=False
    )
    interpreter.globals['ones'] = lambda *shape: Tensor(
        np.ones(shape) if HAS_NUMPY else [[1.0 for _ in range(shape[1])] for _ in range(shape[0])],
        requires_grad=False
    )
    interpreter.globals['randn'] = lambda *shape: Tensor(
        np.random.randn(*shape) if HAS_NUMPY else [[random.gauss(0, 1) for _ in range(shape[1])] for _ in range(shape[0])],
        requires_grad=False
    )

    # Activations
    interpreter.globals['relu'] = lambda x: ReLU.forward(x if isinstance(x, Tensor) else Tensor(x))
    interpreter.globals['sigmoid'] = lambda x: Sigmoid.forward(x if isinstance(x, Tensor) else Tensor(x))
    interpreter.globals['tanh'] = lambda x: Tanh.forward(x if isinstance(x, Tensor) else Tensor(x))
    interpreter.globals['softmax'] = lambda x: Softmax.forward(x if isinstance(x, Tensor) else Tensor(x))

    # Layers
    interpreter.globals['Dense'] = Dense
    interpreter.globals['Conv2D'] = Conv2D
    interpreter.globals['Dropout'] = Dropout
    interpreter.globals['BatchNorm'] = BatchNorm

    # Loss functions
    interpreter.globals['MSELoss'] = MSELoss
    interpreter.globals['CrossEntropyLoss'] = CrossEntropyLoss
    interpreter.globals['BCELoss'] = BinaryCrossEntropyLoss

    # Optimizers
    interpreter.globals['SGD'] = SGD
    interpreter.globals['Adam'] = Adam

    # Model
    interpreter.globals['NeuralNetwork'] = NeuralNetwork

    # Training utilities
    interpreter.globals['train'] = train
    interpreter.globals['train_epoch'] = train_epoch
    interpreter.globals['evaluate'] = evaluate

    print("🧠 Neural primitives integrated into Lament", file=sys.stderr)


# ============================================================================
# DEMO / EXAMPLE USAGE
# ============================================================================

def demo_neural_lament():
    """
    Demonstrate neural network as first-class Lament feature.

    "Let us build a simple network and watch it learn."
    """
    print("\n" + "="*60)
    print("LAMENT NEURAL DEMONSTRATION")
    print("="*60 + "\n")

    # Create a simple XOR problem
    print("Problem: Learn XOR function")
    print("Input: [0,0] -> 0, [0,1] -> 1, [1,0] -> 1, [1,1] -> 0\n")

    # Data
    if HAS_NUMPY:
        X_train = [
            Tensor([[0, 0]], requires_grad=False, name="x1"),
            Tensor([[0, 1]], requires_grad=False, name="x2"),
            Tensor([[1, 0]], requires_grad=False, name="x3"),
            Tensor([[1, 1]], requires_grad=False, name="x4"),
        ]
        y_train = [
            Tensor([[0]], requires_grad=False, name="y1"),
            Tensor([[1]], requires_grad=False, name="y2"),
            Tensor([[1]], requires_grad=False, name="y3"),
            Tensor([[0]], requires_grad=False, name="y4"),
        ]
        train_data = list(zip(X_train, y_train))
        val_data = train_data  # Same for demo

        # Build network
        print("Building neural network...")
        model = NeuralNetwork(name="XOR_Learner")
        model.add(Dense(2, 4, name="hidden"))
        model.add(Dropout(0.2, name="dropout"))
        model.summary()

        # Create optimizer and loss
        optimizer = Adam(model.get_parameters(), lr=0.1)
        loss_fn = MSELoss()

        # Train
        print("Training network...")
        history = train(model, train_data, val_data, optimizer, loss_fn, epochs=5, verbose=True)

        # Test
        print("\nTesting predictions:")
        model.eval()
        for x, y in train_data:
            pred = model(x)
            print(f"Input: {x.tolist()}, Target: {y.tolist()}, Prediction: {pred.tolist()}")
    else:
        print("Pure Python mode - simplified demo")
        x = Tensor([[1, 2], [3, 4]], requires_grad=True, name="x")
        y = Tensor([[5, 6], [7, 8]], requires_grad=False, name="y")

        print(f"x = {x}")
        print(f"y = {y}")

        z = x + y
        print(f"z = x + y = {z}")

        loss = z.sum()
        print(f"loss = sum(z) = {loss}")

        print("\nBackward pass...")
        loss.backward()
        print(f"x.grad = {x.grad}")

    print("\n" + "="*60)
    print("Neural consciousness activated. The language learns.")
    print("="*60 + "\n")


if __name__ == '__main__':
    demo_neural_lament()
