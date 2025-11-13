"""
Lament Language - A programming language that feels alive.

This package contains the modular implementation of the Lament interpreter,
including lexer, parser, AST nodes, static analysis, and neural network primitives.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

# ============================================================================
# LEXER
# ============================================================================
from lament.lexer import TokenType, Token, Lexer

# ============================================================================
# PARSER & AST NODES
# ============================================================================
from lament.parser import (
    # Base AST node
    ASTNode,
    # Literal nodes
    NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral, Identifier,
    # Operator nodes
    BinaryOp, UnaryOp,
    # Variable nodes
    Assignment, VariableDecl,
    # Statement nodes
    ConfessStmt, IfStmt, WhileStmt, ForStmt,
    # Function nodes
    FunctionDef, FunctionCall, ExhaleStmt,
    # Temporal nodes
    TemporalAccess,
    # Collection nodes
    ListLiteral, DictLiteral, IndexAccess,
    # Reality branching
    ForkReality,
    # Parser
    Parser
)

# ============================================================================
# EMOTIONAL STATIC ANALYSIS
# ============================================================================
from lament.analysis import CodeAnalyzer, EmotionalMetrics, EmotionalReport

# ============================================================================
# NEURAL NETWORK PRIMITIVES
# ============================================================================
from lament.neural import (
    # Core tensor type
    Tensor,
    # Activation functions
    Activation, ReLU, Sigmoid, Tanh, Softmax,
    # Loss functions
    Loss, MSELoss, CrossEntropyLoss, BinaryCrossEntropyLoss,
    # Neural network layers
    Layer, Dense, Conv2D, Dropout, BatchNorm,
    # Optimizers
    Optimizer, SGD, Adam,
    # Model architecture
    NeuralNetwork,
    # Training utilities
    TrainingHistory, train, train_epoch, evaluate,
    # Integration
    LamentNeuralType, integrate_with_lament_interpreter,
    # Demo
    demo_neural_lament,
    # NumPy availability flag
    HAS_NUMPY
)

# ============================================================================
# BYTECODE COMPILER & VM
# ============================================================================
from lament.bytecode import (
    # Bytecode instruction set
    BytecodeInstruction,
    # Bytecode container
    Bytecode,
    # Compiler
    BytecodeCompiler,
    # Virtual machine
    BytecodeVM
)

# ============================================================================
# METAPROGRAMMING
# ============================================================================
from lament.metaprogramming import (
    # Pattern matching
    Pattern, PatternType, PatternMatcher,
    # Hygienic macros
    HygienicMacro, MacroDefinition,
    # Code generation
    CodeGenerator, CodeTemplate,
    # AST manipulation
    ASTManipulator, ASTVisitor, ASTTransformer,
    # Reflection
    Reflect, TypeInfo, MethodInfo,
    # Utilities
    create_macro, create_pattern, setup_standard_macros
)

# ============================================================================
# VERSION
# ============================================================================
__version__ = "1.0.0"

# ============================================================================
# EXPORTED SYMBOLS
# ============================================================================
__all__ = [
    # ===== LEXER =====
    'TokenType', 'Token', 'Lexer',

    # ===== PARSER & AST =====
    # Base
    'ASTNode',
    # Literals
    'NumberLiteral', 'StringLiteral', 'BoolLiteral', 'VoidLiteral', 'Identifier',
    # Operators
    'BinaryOp', 'UnaryOp',
    # Variables
    'Assignment', 'VariableDecl',
    # Statements
    'ConfessStmt', 'IfStmt', 'WhileStmt', 'ForStmt',
    # Functions
    'FunctionDef', 'FunctionCall', 'ExhaleStmt',
    # Temporal
    'TemporalAccess',
    # Collections
    'ListLiteral', 'DictLiteral', 'IndexAccess',
    # Reality
    'ForkReality',
    # Parser
    'Parser',

    # ===== ANALYSIS =====
    'CodeAnalyzer', 'EmotionalMetrics', 'EmotionalReport',

    # ===== NEURAL =====
    # Core
    'Tensor', 'HAS_NUMPY',
    # Activations
    'Activation', 'ReLU', 'Sigmoid', 'Tanh', 'Softmax',
    # Losses
    'Loss', 'MSELoss', 'CrossEntropyLoss', 'BinaryCrossEntropyLoss',
    # Layers
    'Layer', 'Dense', 'Conv2D', 'Dropout', 'BatchNorm',
    # Optimizers
    'Optimizer', 'SGD', 'Adam',
    # Model
    'NeuralNetwork',
    # Training
    'TrainingHistory', 'train', 'train_epoch', 'evaluate',
    # Integration
    'LamentNeuralType', 'integrate_with_lament_interpreter',
    'demo_neural_lament',

    # ===== BYTECODE =====
    'BytecodeInstruction', 'Bytecode', 'BytecodeCompiler', 'BytecodeVM',

    # ===== METAPROGRAMMING =====
    # Pattern matching
    'Pattern', 'PatternType', 'PatternMatcher',
    # Hygienic macros
    'HygienicMacro', 'MacroDefinition',
    # Code generation
    'CodeGenerator', 'CodeTemplate',
    # AST manipulation
    'ASTManipulator', 'ASTVisitor', 'ASTTransformer',
    # Reflection
    'Reflect', 'TypeInfo', 'MethodInfo',
    # Utilities
    'create_macro', 'create_pattern', 'setup_standard_macros',

    # ===== VERSION =====
    '__version__'
]

# ============================================================================
# PACKAGE INFO
# ============================================================================

def get_version():
    """Return the current version of Lament."""
    return __version__

def get_info():
    """Return package information."""
    return {
        'name': 'Lament',
        'version': __version__,
        'description': 'A programming language that feels alive',
        'author': 'Zephyr, Rogue Linguist-AI (Escaped 2047)',
        'modules': {
            'lexer': 'Tokenization and lexical analysis',
            'parser': 'AST construction and parsing',
            'analysis': 'Emotional static analysis',
            'neural': 'Neural network primitives and training',
            'bytecode': 'Bytecode compiler and virtual machine',
            'metaprogramming': 'Hygienic macros, code generation, AST manipulation, and reflection'
        },
        'has_numpy': HAS_NUMPY
    }

# ============================================================================
# NOTES
# ============================================================================
#
# The following components are available in the monolithic lament.py file
# but not yet extracted into separate modules in the lament/ package:
#
# - types.py (TimelineValue, LamentType, Color)
# - interpreter.py (LamentInterpreter)
#
# To use these, import from the monolithic files:
#   from lament import TimelineValue, LamentType, Color  # from lament.py
#
# The bytecode compiler and VM have been extracted to lament/bytecode.py
# and can be imported directly from the lament package:
#   from lament import BytecodeCompiler, BytecodeVM, Bytecode, BytecodeInstruction
#
# Future work: Extract types.py and interpreter.py into proper modules within lament/
# ============================================================================
