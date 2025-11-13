"""
Lament Language Bytecode Compiler and Virtual Machine
======================================================

This module provides bytecode compilation and execution for the Lament language.
It transforms AST nodes into a stack-based bytecode representation and executes
them in a virtual machine for improved performance.

Components:
- BytecodeInstruction: Enum of all VM opcodes
- Bytecode: Container for compiled bytecode with constant pool and name table
- BytecodeCompiler: Compiles AST to bytecode
- BytecodeVM: Stack-based virtual machine for bytecode execution

The bytecode format is inspired by Python's bytecode but tailored for Lament's
unique features including temporal variables and emotional primitives.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, List, Dict, Optional, Union

# Import AST nodes from parser
from lament.parser import (
    ASTNode,
    NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral, Identifier,
    BinaryOp, UnaryOp,
    Assignment, VariableDecl,
    ConfessStmt, IfStmt, WhileStmt, ForStmt,
    FunctionDef, FunctionCall, ExhaleStmt,
    TemporalAccess,
    ListLiteral, DictLiteral, IndexAccess,
    ForkReality
)


# ============================================================================
# BYTECODE INSTRUCTIONS
# ============================================================================

class BytecodeInstruction(Enum):
    """
    Bytecode opcodes for the Lament VM.

    Stack-based instruction set with support for:
    - Constants and variables
    - Arithmetic and logical operations
    - Control flow (jumps, conditionals)
    - Function calls and returns
    - Collection operations
    - Temporal operations
    """

    # Stack manipulation
    LOAD_CONST = auto()      # Push constant onto stack
    LOAD_VAR = auto()        # Load variable value onto stack
    STORE_VAR = auto()       # Store TOS to variable
    POP_TOP = auto()         # Pop and discard TOS
    DUP_TOP = auto()         # Duplicate TOS

    # Arithmetic operations
    BINARY_ADD = auto()      # TOS = TOS1 + TOS
    BINARY_SUB = auto()      # TOS = TOS1 - TOS
    BINARY_MUL = auto()      # TOS = TOS1 * TOS
    BINARY_DIV = auto()      # TOS = TOS1 / TOS
    BINARY_MOD = auto()      # TOS = TOS1 % TOS
    UNARY_NEG = auto()       # TOS = -TOS

    # Comparison operations
    COMPARE_EQ = auto()      # TOS = TOS1 == TOS
    COMPARE_NE = auto()      # TOS = TOS1 != TOS
    COMPARE_LT = auto()      # TOS = TOS1 < TOS
    COMPARE_GT = auto()      # TOS = TOS1 > TOS
    COMPARE_LE = auto()      # TOS = TOS1 <= TOS
    COMPARE_GE = auto()      # TOS = TOS1 >= TOS
    COMPARE_IS = auto()      # TOS = TOS1 is TOS
    COMPARE_IS_NOT = auto()  # TOS = TOS1 is not TOS

    # Logical operations
    LOGICAL_AND = auto()     # TOS = TOS1 and TOS
    LOGICAL_OR = auto()      # TOS = TOS1 or TOS
    LOGICAL_NOT = auto()     # TOS = not TOS

    # Control flow
    JUMP = auto()            # Unconditional jump to address
    JUMP_IF_FALSE = auto()   # Jump if TOS is false (pop TOS)
    JUMP_IF_TRUE = auto()    # Jump if TOS is true (pop TOS)

    # Function operations
    CALL_FUNC = auto()       # Call function with N args
    RETURN = auto()          # Return from function
    MAKE_FUNC = auto()       # Create function object

    # Collection operations
    BUILD_LIST = auto()      # Build list from N stack items
    BUILD_DICT = auto()      # Build dict from 2N stack items
    INDEX_GET = auto()       # TOS = TOS1[TOS]
    INDEX_SET = auto()       # TOS2[TOS1] = TOS

    # Temporal operations
    LOAD_PAST = auto()       # Load past value of variable
    LOAD_ORIGIN = auto()     # Load origin value of variable
    LOAD_AGE = auto()        # Load age of variable
    LOAD_BORN = auto()       # Load born timestamp of variable

    # I/O operations
    PRINT = auto()           # Print TOS (confess statement)

    # Control
    HALT = auto()            # Stop execution
    NOP = auto()             # No operation


# ============================================================================
# BYTECODE CONTAINER
# ============================================================================

@dataclass
class Bytecode:
    """
    Container for compiled bytecode with metadata.

    Attributes:
        instructions: List of (opcode, arg) tuples
        constants: Constant pool for literal values
        names: Name table for variable/function names
        metadata: Optional compilation metadata (line numbers, etc.)
    """
    instructions: List[tuple]
    constants: List[Any]
    names: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return (f"<Bytecode: {len(self.instructions)} instructions, "
                f"{len(self.constants)} constants, {len(self.names)} names>")

    def disassemble(self) -> str:
        """
        Disassemble bytecode to human-readable format.

        Returns:
            String representation of bytecode instructions
        """
        lines = []
        lines.append(f"{'ADDR':<6} {'OPCODE':<20} {'ARG':<10} {'COMMENT':<20}")
        lines.append("-" * 60)

        for addr, (opcode, arg) in enumerate(self.instructions):
            comment = ""

            # Add helpful comments for certain opcodes
            if opcode == BytecodeInstruction.LOAD_CONST and arg is not None:
                comment = f"# {repr(self.constants[arg])}"
            elif opcode in (BytecodeInstruction.LOAD_VAR,
                          BytecodeInstruction.STORE_VAR) and arg is not None:
                comment = f"# {self.names[arg]}"
            elif opcode in (BytecodeInstruction.JUMP,
                          BytecodeInstruction.JUMP_IF_FALSE,
                          BytecodeInstruction.JUMP_IF_TRUE) and arg is not None:
                comment = f"# -> {arg}"

            arg_str = str(arg) if arg is not None else ""
            lines.append(f"{addr:<6} {opcode.name:<20} {arg_str:<10} {comment:<20}")

        return "\n".join(lines)


# ============================================================================
# BYTECODE COMPILER
# ============================================================================

class BytecodeCompiler:
    """
    Compiles Lament AST to stack-based bytecode.

    The compiler performs a single-pass traversal of the AST, emitting
    bytecode instructions and managing the constant pool and name table.
    It handles all Lament language constructs including control flow,
    functions, and temporal operators.
    """

    def __init__(self):
        """Initialize compiler with empty instruction list and pools."""
        self.instructions: List[tuple] = []
        self.constants: List[Any] = []
        self.names: List[str] = []
        self.metadata: Dict[str, Any] = {}

        # Jump fixup tracking
        self._jump_stack: List[int] = []

    def compile(self, ast_nodes: List[ASTNode]) -> Bytecode:
        """
        Compile a list of AST nodes to bytecode.

        Args:
            ast_nodes: List of AST statement nodes to compile

        Returns:
            Bytecode object containing instructions and metadata
        """
        self.instructions = []
        self.constants = []
        self.names = []
        self.metadata = {'node_count': len(ast_nodes)}

        # Compile each statement
        for node in ast_nodes:
            self._compile_node(node)

        # Always end with HALT
        self.emit(BytecodeInstruction.HALT)

        return Bytecode(
            instructions=self.instructions,
            constants=self.constants,
            names=self.names,
            metadata=self.metadata
        )

    def _compile_node(self, node: ASTNode):
        """
        Compile a single AST node to bytecode.

        Args:
            node: AST node to compile

        Raises:
            NotImplementedError: If node type is not supported
        """

        # Literals
        if isinstance(node, NumberLiteral):
            const_idx = self._add_constant(node.value)
            self.emit(BytecodeInstruction.LOAD_CONST, const_idx)

        elif isinstance(node, StringLiteral):
            const_idx = self._add_constant(node.value)
            self.emit(BytecodeInstruction.LOAD_CONST, const_idx)

        elif isinstance(node, BoolLiteral):
            # Map Lament bool values to Python bools
            bool_map = {'yes': True, 'no': False, 'perhaps': None}
            value = bool_map.get(node.value.lower(), None)
            const_idx = self._add_constant(value)
            self.emit(BytecodeInstruction.LOAD_CONST, const_idx)

        elif isinstance(node, VoidLiteral):
            const_idx = self._add_constant(None)
            self.emit(BytecodeInstruction.LOAD_CONST, const_idx)

        elif isinstance(node, Identifier):
            name_idx = self._add_name(node.name)
            self.emit(BytecodeInstruction.LOAD_VAR, name_idx)

        # Binary operations
        elif isinstance(node, BinaryOp):
            self._compile_node(node.left)
            self._compile_node(node.right)

            op_map = {
                '+': BytecodeInstruction.BINARY_ADD,
                '-': BytecodeInstruction.BINARY_SUB,
                '*': BytecodeInstruction.BINARY_MUL,
                '/': BytecodeInstruction.BINARY_DIV,
                '%': BytecodeInstruction.BINARY_MOD,
                '==': BytecodeInstruction.COMPARE_EQ,
                '!=': BytecodeInstruction.COMPARE_NE,
                '<': BytecodeInstruction.COMPARE_LT,
                '>': BytecodeInstruction.COMPARE_GT,
                '<=': BytecodeInstruction.COMPARE_LE,
                '>=': BytecodeInstruction.COMPARE_GE,
                'is': BytecodeInstruction.COMPARE_IS,
                'is not': BytecodeInstruction.COMPARE_IS_NOT,
                'and': BytecodeInstruction.LOGICAL_AND,
                'or': BytecodeInstruction.LOGICAL_OR,
            }

            if node.op in op_map:
                self.emit(op_map[node.op])
            else:
                raise NotImplementedError(f"Binary operator '{node.op}' not implemented")

        # Unary operations
        elif isinstance(node, UnaryOp):
            self._compile_node(node.operand)

            if node.op == '-':
                self.emit(BytecodeInstruction.UNARY_NEG)
            elif node.op == 'not':
                self.emit(BytecodeInstruction.LOGICAL_NOT)
            else:
                raise NotImplementedError(f"Unary operator '{node.op}' not implemented")

        # Variables
        elif isinstance(node, VariableDecl):
            self._compile_node(node.value)
            name_idx = self._add_name(node.name)
            self.emit(BytecodeInstruction.STORE_VAR, name_idx)

        elif isinstance(node, Assignment):
            self._compile_node(node.value)
            name_idx = self._add_name(node.name)
            self.emit(BytecodeInstruction.STORE_VAR, name_idx)

        # Statements
        elif isinstance(node, ConfessStmt):
            self._compile_node(node.value)
            self.emit(BytecodeInstruction.PRINT)

        elif isinstance(node, IfStmt):
            self._compile_if(node)

        elif isinstance(node, WhileStmt):
            self._compile_while(node)

        elif isinstance(node, ForStmt):
            self._compile_for(node)

        # Functions
        elif isinstance(node, FunctionCall):
            # Compile arguments in order
            for arg in node.args:
                self._compile_node(arg)

            # Load function and call
            name_idx = self._add_name(node.name)
            arg_count = len(node.args)
            const_idx = self._add_constant(arg_count)

            self.emit(BytecodeInstruction.LOAD_VAR, name_idx)
            self.emit(BytecodeInstruction.CALL_FUNC, const_idx)

        elif isinstance(node, ExhaleStmt):
            self._compile_node(node.value)
            self.emit(BytecodeInstruction.RETURN)

        # Collections
        elif isinstance(node, ListLiteral):
            for elem in node.elements:
                self._compile_node(elem)
            count_idx = self._add_constant(len(node.elements))
            self.emit(BytecodeInstruction.BUILD_LIST, count_idx)

        elif isinstance(node, IndexAccess):
            self._compile_node(node.object)
            self._compile_node(node.index)
            self.emit(BytecodeInstruction.INDEX_GET)

        # Temporal operations
        elif isinstance(node, TemporalAccess):
            name_idx = self._add_name(node.var)

            if node.operator == 'past':
                offset_idx = self._add_constant(node.offset or 1)
                self.emit(BytecodeInstruction.LOAD_VAR, name_idx)
                self.emit(BytecodeInstruction.LOAD_CONST, offset_idx)
                self.emit(BytecodeInstruction.LOAD_PAST)
            elif node.operator == 'origin':
                self.emit(BytecodeInstruction.LOAD_VAR, name_idx)
                self.emit(BytecodeInstruction.LOAD_ORIGIN)
            elif node.operator == 'age':
                self.emit(BytecodeInstruction.LOAD_VAR, name_idx)
                self.emit(BytecodeInstruction.LOAD_AGE)
            elif node.operator == 'born':
                self.emit(BytecodeInstruction.LOAD_VAR, name_idx)
                self.emit(BytecodeInstruction.LOAD_BORN)

        else:
            raise NotImplementedError(f"Node type {type(node).__name__} not implemented")

    def _compile_if(self, node: IfStmt):
        """Compile if-else statement with conditional jumps."""
        # Compile condition
        self._compile_node(node.condition)

        # Jump to else block if false
        jump_to_else = len(self.instructions)
        self.emit(BytecodeInstruction.JUMP_IF_FALSE, None)  # Placeholder

        # Compile then block
        for stmt in node.then_block:
            self._compile_node(stmt)

        if node.else_block:
            # Jump over else block
            jump_to_end = len(self.instructions)
            self.emit(BytecodeInstruction.JUMP, None)  # Placeholder

            # Fix jump to else
            else_addr = len(self.instructions)
            self.instructions[jump_to_else] = (BytecodeInstruction.JUMP_IF_FALSE, else_addr)

            # Compile else block
            for stmt in node.else_block:
                self._compile_node(stmt)

            # Fix jump to end
            end_addr = len(self.instructions)
            self.instructions[jump_to_end] = (BytecodeInstruction.JUMP, end_addr)
        else:
            # No else block, fix jump to end
            end_addr = len(self.instructions)
            self.instructions[jump_to_else] = (BytecodeInstruction.JUMP_IF_FALSE, end_addr)

    def _compile_while(self, node: WhileStmt):
        """Compile while loop with backward jump."""
        # Loop start
        loop_start = len(self.instructions)

        # Compile condition
        self._compile_node(node.condition)

        # Jump to end if false
        jump_to_end = len(self.instructions)
        self.emit(BytecodeInstruction.JUMP_IF_FALSE, None)  # Placeholder

        # Compile body
        for stmt in node.body:
            self._compile_node(stmt)

        # Jump back to start
        self.emit(BytecodeInstruction.JUMP, loop_start)

        # Fix jump to end
        end_addr = len(self.instructions)
        self.instructions[jump_to_end] = (BytecodeInstruction.JUMP_IF_FALSE, end_addr)

    def _compile_for(self, node: ForStmt):
        """Compile for-in loop (simplified - would need iterator support)."""
        # For now, compile as a simplified loop
        # In a full implementation, this would use iterator protocol

        # Compile iterable
        self._compile_node(node.iterable)

        # Store iterator (simplified)
        iter_name = f"_iter_{node.var}"
        iter_idx = self._add_name(iter_name)
        self.emit(BytecodeInstruction.STORE_VAR, iter_idx)

        # TODO: Implement proper iteration with hasNext/getNext
        # For now, this is a placeholder
        pass

    def emit(self, opcode: BytecodeInstruction, arg: Optional[int] = None):
        """
        Emit a bytecode instruction.

        Args:
            opcode: Instruction opcode
            arg: Optional instruction argument
        """
        self.instructions.append((opcode, arg))

    def _add_constant(self, value: Any) -> int:
        """
        Add a constant to the constant pool.

        Args:
            value: Constant value to add

        Returns:
            Index of constant in pool
        """
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)

    def _add_name(self, name: str) -> int:
        """
        Add a name to the name table.

        Args:
            name: Variable/function name to add

        Returns:
            Index of name in table
        """
        if name not in self.names:
            self.names.append(name)
        return self.names.index(name)


# ============================================================================
# BYTECODE VIRTUAL MACHINE
# ============================================================================

class BytecodeVM:
    """
    Stack-based virtual machine for executing Lament bytecode.

    The VM maintains:
    - An evaluation stack for operands and results
    - A variable store for named values
    - An instruction pointer for control flow

    Execution proceeds by fetching, decoding, and executing instructions
    until a HALT instruction or end of bytecode is reached.
    """

    def __init__(self):
        """Initialize VM with empty stack and variable store."""
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.call_stack: List[Dict[str, Any]] = []

        # Execution state
        self.ip: int = 0  # Instruction pointer
        self.halted: bool = False

        # Statistics
        self.instruction_count: int = 0
        self.max_stack_depth: int = 0

    def execute(self, bytecode: Bytecode) -> Any:
        """
        Execute bytecode program.

        Args:
            bytecode: Compiled bytecode to execute

        Returns:
            Last value on stack, or None if stack is empty

        Raises:
            RuntimeError: If execution encounters an error
        """
        self.ip = 0
        self.halted = False
        self.instruction_count = 0

        instructions = bytecode.instructions
        constants = bytecode.constants
        names = bytecode.names

        while self.ip < len(instructions) and not self.halted:
            opcode, arg = instructions[self.ip]
            self.instruction_count += 1

            # Track max stack depth
            if len(self.stack) > self.max_stack_depth:
                self.max_stack_depth = len(self.stack)

            # Execute instruction
            try:
                self._execute_instruction(opcode, arg, constants, names)
            except Exception as e:
                raise RuntimeError(
                    f"Execution error at address {self.ip}: {e}\n"
                    f"Instruction: {opcode.name} {arg}\n"
                    f"Stack: {self.stack}"
                ) from e

            self.ip += 1

        # Return top of stack if available
        return self.stack[-1] if self.stack else None

    def _execute_instruction(self, opcode: BytecodeInstruction, arg: Optional[int],
                           constants: List[Any], names: List[str]):
        """
        Execute a single bytecode instruction.

        Args:
            opcode: Instruction opcode
            arg: Instruction argument
            constants: Constant pool
            names: Name table
        """

        # Stack manipulation
        if opcode == BytecodeInstruction.LOAD_CONST:
            self.stack.append(constants[arg])

        elif opcode == BytecodeInstruction.LOAD_VAR:
            name = names[arg]
            if name not in self.variables:
                raise NameError(f"Undefined variable: {name}")
            self.stack.append(self.variables[name])

        elif opcode == BytecodeInstruction.STORE_VAR:
            name = names[arg]
            value = self.stack.pop()
            self.variables[name] = value

        elif opcode == BytecodeInstruction.POP_TOP:
            self.stack.pop()

        elif opcode == BytecodeInstruction.DUP_TOP:
            self.stack.append(self.stack[-1])

        # Arithmetic operations
        elif opcode == BytecodeInstruction.BINARY_ADD:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left + right)

        elif opcode == BytecodeInstruction.BINARY_SUB:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left - right)

        elif opcode == BytecodeInstruction.BINARY_MUL:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left * right)

        elif opcode == BytecodeInstruction.BINARY_DIV:
            right = self.stack.pop()
            left = self.stack.pop()
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            self.stack.append(left / right)

        elif opcode == BytecodeInstruction.BINARY_MOD:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left % right)

        elif opcode == BytecodeInstruction.UNARY_NEG:
            value = self.stack.pop()
            self.stack.append(-value)

        # Comparison operations
        elif opcode == BytecodeInstruction.COMPARE_EQ:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left == right)

        elif opcode == BytecodeInstruction.COMPARE_NE:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left != right)

        elif opcode == BytecodeInstruction.COMPARE_LT:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left < right)

        elif opcode == BytecodeInstruction.COMPARE_GT:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left > right)

        elif opcode == BytecodeInstruction.COMPARE_LE:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left <= right)

        elif opcode == BytecodeInstruction.COMPARE_GE:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left >= right)

        elif opcode == BytecodeInstruction.COMPARE_IS:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left is right)

        elif opcode == BytecodeInstruction.COMPARE_IS_NOT:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left is not right)

        # Logical operations
        elif opcode == BytecodeInstruction.LOGICAL_AND:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left and right)

        elif opcode == BytecodeInstruction.LOGICAL_OR:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left or right)

        elif opcode == BytecodeInstruction.LOGICAL_NOT:
            value = self.stack.pop()
            self.stack.append(not value)

        # Control flow
        elif opcode == BytecodeInstruction.JUMP:
            self.ip = arg - 1  # -1 because ip will be incremented

        elif opcode == BytecodeInstruction.JUMP_IF_FALSE:
            condition = self.stack.pop()
            if not condition:
                self.ip = arg - 1

        elif opcode == BytecodeInstruction.JUMP_IF_TRUE:
            condition = self.stack.pop()
            if condition:
                self.ip = arg - 1

        # Collection operations
        elif opcode == BytecodeInstruction.BUILD_LIST:
            count = constants[arg]
            elements = [self.stack.pop() for _ in range(count)]
            elements.reverse()
            self.stack.append(elements)

        elif opcode == BytecodeInstruction.INDEX_GET:
            index = self.stack.pop()
            obj = self.stack.pop()
            try:
                self.stack.append(obj[index])
            except (KeyError, IndexError, TypeError) as e:
                raise RuntimeError(f"Index error: {e}")

        # I/O operations
        elif opcode == BytecodeInstruction.PRINT:
            value = self.stack.pop()
            print(value)

        # Control
        elif opcode == BytecodeInstruction.HALT:
            self.halted = True

        elif opcode == BytecodeInstruction.NOP:
            pass  # No operation

        else:
            raise NotImplementedError(f"Opcode {opcode.name} not implemented in VM")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            'instructions_executed': self.instruction_count,
            'max_stack_depth': self.max_stack_depth,
            'variables_allocated': len(self.variables),
            'final_stack_size': len(self.stack)
        }

    def reset(self):
        """Reset VM state for new execution."""
        self.stack.clear()
        self.variables.clear()
        self.call_stack.clear()
        self.ip = 0
        self.halted = False
        self.instruction_count = 0
        self.max_stack_depth = 0
