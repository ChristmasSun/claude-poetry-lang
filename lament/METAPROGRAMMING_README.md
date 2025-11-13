# Lament Metaprogramming Module

The metaprogramming module provides powerful capabilities for code generation, AST manipulation, and runtime reflection in the Lament programming language.

## Overview

The module implements four major systems:

1. **Hygienic Macros** - Safe compile-time code generation with pattern matching
2. **Code Generation** - Template-based code generation during compilation
3. **AST Manipulation** - Programmatic AST modification and transformation
4. **Reflection** - Runtime type introspection and dynamic invocation

## Features

### 1. Hygienic Macros

Hygienic macros provide safe code generation by automatically renaming variables to prevent variable capture. This ensures that macro expansions don't accidentally interfere with the surrounding code.

#### Key Components

- **`HygienicMacro`**: Main macro system class
- **`Pattern`**: Pattern matching for macro arguments
- **`PatternMatcher`**: Matches code against patterns and extracts bindings
- **`MacroDefinition`**: Defines a macro with patterns and template

#### Pattern Types

```python
PatternType.LITERAL      # Exact match (keyword, operator)
PatternType.VARIABLE     # Match any expression, bind to variable
PatternType.IDENTIFIER   # Match identifier only
PatternType.EXPRESSION   # Match any expression
PatternType.STATEMENT    # Match any statement
PatternType.BLOCK        # Match block of statements
PatternType.REPEATED     # Match repeated pattern (*, +)
PatternType.OPTIONAL     # Match optional pattern (?)
```

#### Example: Unless Macro

```python
from lament.metaprogramming import HygienicMacro, create_pattern, PatternType

macro_system = HygienicMacro()

# Define 'unless' macro (opposite of if)
unless_pattern = [
    create_pattern(PatternType.EXPRESSION, 'condition'),
    create_pattern(PatternType.BLOCK, 'body')
]

unless_template = IfStmt(
    UnaryOp('not', Identifier('condition')),
    [Identifier('body')],
    None
)

macro_system.define('unless', unless_pattern, unless_template)

# Expand macro
condition = BinaryOp(Identifier('x'), '>', NumberLiteral(10))
body = [ConfessStmt(StringLiteral('small'))]

expanded = macro_system.expand('unless', [condition, body])
# Result: if not (x > 10) { confess "small" }
```

#### Hygiene Protection

The macro system automatically renames variables to prevent capture:

```python
# Original template uses variable 'temp'
macro_system.define('swap', patterns, template_with_temp)

# Expansion automatically renames 'temp' to '__temp_0_a1b2c3d4__'
# This prevents conflicts with user code that also uses 'temp'
```

#### Standard Macros

```python
from lament.metaprogramming import setup_standard_macros

macro_system = HygienicMacro()
setup_standard_macros(macro_system)

# Now available:
# - unless: opposite of if
# - repeat: repeat code n times
```

### 2. Compile-Time Code Generation

The code generation system allows creating code from templates during compilation.

#### Key Components

- **`CodeGenerator`**: Main code generation class
- **`CodeTemplate`**: Template with placeholders

#### String Templates

```python
from lament.metaprogramming import CodeGenerator

generator = CodeGenerator()

# Define getter template
generator.define_template(
    'getter',
    'sigh get_{{field}}() { exhale @{{field}} }',
    ['field']
)

# Generate code
code = generator.instantiate('getter', {'field': 'name'})
# Result: "sigh get_name() { exhale @name }"
```

#### AST Templates

```python
# Define AST-based template
template_ast = FunctionDef(
    'get_field',
    [],
    [ExhaleStmt(Identifier('field'))]
)

generator.define_template(
    'getter_ast',
    template_ast,
    ['field']
)

# Instantiate with substitution
func = generator.instantiate('getter_ast', {'field': Identifier('name')})
```

#### Class Generation

```python
# Generate a complete class structure
person_methods = generator.generate_class(
    'Person',
    fields=['name', 'age', 'email'],
    methods=['init', 'get_name', 'set_name', 'get_age', 'set_age']
)

# Returns list of FunctionDef nodes:
# - Person_init(name, age, email)
# - Person_get_name()
# - Person_set_name(value)
# - Person_get_age()
# - Person_set_age(value)
```

#### Function Generation

```python
func = generator.generate_function(
    name='greet',
    params=['name'],
    body_template='confess "Hello, {{name}}!"',
    substitutions={'name': 'name'}
)
```

### 3. AST Manipulation

The AST manipulation API provides tools for analyzing, transforming, and rewriting AST nodes.

#### Key Components

- **`ASTManipulator`**: Main manipulation class
- **`ASTVisitor`**: Base class for AST visitors (Visitor pattern)
- **`ASTTransformer`**: Base class for AST transformers

#### Finding Nodes

```python
from lament.metaprogramming import ASTManipulator

manipulator = ASTManipulator()

# Find all nodes of specific type
var_decls = manipulator.find_nodes(ast, VariableDecl)

# Find by predicate
additions = manipulator.find_by_predicate(
    ast,
    lambda node: isinstance(node, BinaryOp) and node.op == '+'
)
```

#### Transforming AST

```python
# Transform AST with function
def optimize(node):
    if isinstance(node, BinaryOp) and node.op == '+':
        if isinstance(node.left, NumberLiteral) and isinstance(node.right, NumberLiteral):
            # Constant folding
            return NumberLiteral(node.left.value + node.right.value)
    return node

optimized_ast = manipulator.transform(ast, optimize)
```

#### Quote/Unquote (Code as Data)

```python
# Quote: Convert code string to AST
code = "remember x = 42"
ast = manipulator.quote(code)
# Result: VariableDecl('x', NumberLiteral(42))

# Unquote: Convert AST back to code
node = BinaryOp(NumberLiteral(10), '+', NumberLiteral(20))
code = manipulator.unquote(node)
# Result: "(10 + 20)"
```

#### Custom Transformers

```python
from lament.metaprogramming import ASTTransformer

class ConstantFolder(ASTTransformer):
    """Fold constant expressions."""

    def visit_BinaryOp(self, node):
        # Transform children first
        node = self.generic_visit(node)

        # Fold constants
        if isinstance(node.left, NumberLiteral) and isinstance(node.right, NumberLiteral):
            if node.op == '+':
                return NumberLiteral(node.left.value + node.right.value)
            elif node.op == '*':
                return NumberLiteral(node.left.value * node.right.value)

        return node

folder = ConstantFolder()
optimized = folder.transform(ast)
```

#### Tree Operations

```python
# Clone AST
cloned = manipulator.clone(ast)

# Merge trees
merged = manipulator.merge_trees(ast1, ast2)

# Replace node
new_ast = manipulator.replace_node(ast, old_node, new_node)
```

### 4. Reflection

The reflection system provides runtime type introspection and dynamic invocation capabilities.

#### Key Components

- **`Reflect`**: Main reflection class
- **`TypeInfo`**: Information about a type
- **`MethodInfo`**: Information about a method

#### Type Information

```python
from lament.metaprogramming import Reflect

reflect = Reflect()

# Get type info
type_info = reflect.get_type_info(42)
# Result: TypeInfo(name='numb', ...)

# Get type name
type_name = reflect.get_type_name("hello")
# Result: "whisper"

# List all types
types = reflect.list_types()
# Result: ['numb', 'whisper', 'maybe', 'void', 'ache', 'list', 'dict']
```

#### Method Introspection

```python
# Get methods for a type
string_info = reflect.type_registry['whisper']
methods = reflect.get_methods(string_info)

for method in methods:
    print(f"{method.name}({', '.join(method.parameters)})")
# Output:
# length()
# upper()
# lower()
# split(sep)

# Check if method exists
has_upper = reflect.has_method("hello", "upper")  # True
has_foo = reflect.has_method("hello", "foo")      # False

# Get method signature
signature = reflect.get_method_signature(string_info, "split")
# Result: MethodInfo(name='split', parameters=['sep'], ...)
```

#### Dynamic Invocation

```python
# Invoke method dynamically
result = reflect.invoke("hello", "upper", [])
# Result: "HELLO"

result = reflect.invoke([1, 2, 3], "length", [])
# Result: 3

result = reflect.invoke(-42, "abs", [])
# Result: 42
```

#### Type Registration

```python
# Register custom type
reflect.register_type(
    'Point',
    base_type=None,
    fields={'x': 'numb', 'y': 'numb'},
    methods={'distance': [], 'move': ['dx', 'dy']}
)

# Query custom type
point_info = reflect.type_registry['Point']
print(point_info.fields)   # {'x': 'numb', 'y': 'numb'}
print(point_info.methods)  # {'distance': [], 'move': ['dx', 'dy']}
```

#### Type Checking

```python
# Check if value is instance of type
is_num = reflect.is_instance(42, 'numb')        # True
is_str = reflect.is_instance(42, 'whisper')     # False
```

#### Attribute Access

```python
# Get attribute
value = reflect.get_attribute(obj, 'name')

# Set attribute
reflect.set_attribute(obj, 'name', 'new_value')

# Check field existence
has_field = reflect.has_field(obj, 'name')
```

## Advanced Usage

### Transformation Pipelines

Chain multiple transformations together:

```python
class OptimizationPipeline:
    def __init__(self):
        self.transformers = []

    def add(self, transformer):
        self.transformers.append(transformer)
        return self

    def apply(self, ast):
        result = ast
        for transformer in self.transformers:
            result = transformer(result)
        return result

# Create pipeline
pipeline = OptimizationPipeline()
pipeline.add(constant_fold)
pipeline.add(dead_code_elimination)
pipeline.add(inline_functions)

# Apply to AST
optimized = pipeline.apply(ast)
```

### Combining Systems

Use multiple metaprogramming systems together:

```python
# 1. Define macro
macro_system = HygienicMacro()
macro_system.define('property', patterns, template)

# 2. Generate code with templates
generator = CodeGenerator()
generator.define_template('accessor', template_str, params)

# 3. Manipulate generated AST
manipulator = ASTManipulator()
generated = generator.instantiate('accessor', values)
optimized = manipulator.transform(generated, optimizer)

# 4. Use reflection for runtime checks
reflect = Reflect()
if reflect.has_method(obj, 'get_field'):
    result = reflect.invoke(obj, 'get_field', [])
```

### Code-as-Data

Treat code as a data structure that can be analyzed and modified:

```python
# Parse code into AST
ast = manipulator.quote("remember x = 10")

# Analyze
variables = manipulator.find_nodes(ast, VariableDecl)
print(f"Found {len(variables)} variables")

# Transform
def rename_vars(node):
    if isinstance(node, Identifier):
        node.name = f"new_{node.name}"
    return node

transformed = manipulator.transform(ast, rename_vars)

# Generate back to code
code = manipulator.unquote(transformed)
```

## Built-in Types

The reflection system recognizes these built-in types:

| Lament Type | Python Type | Methods |
|-------------|-------------|---------|
| `numb` | int | to_string, abs, neg |
| `ache` | float | to_string, round, floor, ceil |
| `whisper` | str | length, upper, lower, split |
| `maybe` | bool | to_string, not |
| `void` | None | - |
| `list` | list | length, append, get, set |
| `dict` | dict | keys, values, get, set |

## Examples

### Example 1: Debug Print Macro

```python
# Define a macro that prints variable name and value
debug_pattern = [create_pattern(PatternType.IDENTIFIER, 'var')]

debug_template = ConfessStmt(
    BinaryOp(
        StringLiteral('Debug: '),
        '+',
        FunctionCall('to_string', [Identifier('var')])
    )
)

macro_system.define('debug', debug_pattern, debug_template)

# Use: debug! x
# Expands to: confess "Debug: " + to_string(x)
```

### Example 2: Property Generation

```python
# Generate getters and setters for a class
generator = CodeGenerator()

fields = ['x', 'y', 'z']
methods = []

for field in fields:
    getter = generator.generate_function(
        f'get_{field}',
        [],
        f'exhale @{field}',
        {}
    )
    methods.append(getter)

    setter = generator.generate_function(
        f'set_{field}',
        ['value'],
        f'{field} = value',
        {}
    )
    methods.append(setter)

print(f"Generated {len(methods)} accessor methods")
```

### Example 3: AST Optimization

```python
# Implement constant folding optimization
def constant_fold_pass(ast):
    manipulator = ASTManipulator()

    def fold(node):
        if isinstance(node, BinaryOp):
            left = node.left
            right = node.right

            if isinstance(left, NumberLiteral) and isinstance(right, NumberLiteral):
                if node.op == '+':
                    return NumberLiteral(left.value + right.value)
                elif node.op == '-':
                    return NumberLiteral(left.value - right.value)
                elif node.op == '*':
                    return NumberLiteral(left.value * right.value)
                elif node.op == '/':
                    return NumberLiteral(left.value / right.value)

        return node

    return manipulator.transform(ast, fold)

# Apply optimization
optimized = constant_fold_pass(my_ast)
```

### Example 4: Generic Method Wrapper

```python
# Create safe wrappers for all methods of a type
reflect = Reflect()

def create_safe_wrapper(type_name, method_name):
    """Create a safe wrapper that catches exceptions."""
    type_info = reflect.type_registry[type_name]
    method_info = reflect.get_method_signature(type_info, method_name)

    def safe_wrapper(obj, *args):
        try:
            return reflect.invoke(obj, method_name, list(args))
        except Exception as e:
            print(f"Error calling {method_name}: {e}")
            return None

    return safe_wrapper

# Create wrappers for all string methods
string_wrappers = {}
for method in reflect.get_methods(reflect.type_registry['whisper']):
    wrapper = create_safe_wrapper('whisper', method.name)
    string_wrappers[f'safe_{method.name}'] = wrapper

# Use wrapper
result = string_wrappers['safe_upper']("hello")
```

## API Reference

### HygienicMacro

```python
class HygienicMacro:
    def define(name: str, patterns: List[Pattern],
               template: Union[ASTNode, List[ASTNode]]) -> None
    def expand(name: str, args: List[ASTNode]) -> Union[ASTNode, List[ASTNode]]
```

### CodeGenerator

```python
class CodeGenerator:
    def define_template(name: str, template: Union[str, ASTNode],
                       parameters: List[str]) -> None
    def instantiate(name: str, values: Dict[str, Any]) -> Union[str, ASTNode]
    def generate_function(name: str, params: List[str],
                         body_template: str, substitutions: Dict[str, Any]) -> FunctionDef
    def generate_class(name: str, fields: List[str],
                      methods: List[str]) -> List[FunctionDef]
    def get_generated_code() -> List[Union[str, ASTNode]]
    def clear_generated() -> None
```

### ASTManipulator

```python
class ASTManipulator:
    def clone(node: Union[ASTNode, List[ASTNode]]) -> Union[ASTNode, List[ASTNode]]
    def find_nodes(root: Union[ASTNode, List[ASTNode]],
                  node_type: type) -> List[ASTNode]
    def find_by_predicate(root: Union[ASTNode, List[ASTNode]],
                         predicate: Callable[[ASTNode], bool]) -> List[ASTNode]
    def replace_node(root: Union[ASTNode, List[ASTNode]],
                    old: ASTNode, new: ASTNode) -> Union[ASTNode, List[ASTNode]]
    def transform(root: Union[ASTNode, List[ASTNode]],
                 transformer: Callable[[ASTNode], ASTNode]) -> Union[ASTNode, List[ASTNode]]
    def quote(code: str) -> ASTNode
    def unquote(ast: ASTNode) -> str
    def merge_trees(tree1: List[ASTNode], tree2: List[ASTNode]) -> List[ASTNode]
```

### Reflect

```python
class Reflect:
    def register_type(name: str, base_type: Optional[LamentType],
                     fields: Optional[Dict[str, str]],
                     methods: Optional[Dict[str, List[str]]]) -> None
    def get_type_info(value: Any) -> TypeInfo
    def get_type_name(value: Any) -> str
    def get_methods(type_info: TypeInfo) -> List[MethodInfo]
    def get_fields(type_info: TypeInfo) -> Dict[str, str]
    def has_method(value: Any, method_name: str) -> bool
    def has_field(value: Any, field_name: str) -> bool
    def get_method_signature(type_info: TypeInfo,
                            method_name: str) -> Optional[MethodInfo]
    def invoke(obj: Any, method_name: str, args: List[Any]) -> Any
    def get_attribute(obj: Any, attr_name: str) -> Any
    def set_attribute(obj: Any, attr_name: str, value: Any) -> None
    def is_instance(value: Any, type_name: str) -> bool
    def list_types() -> List[str]
```

## Running the Demo

To see all metaprogramming features in action:

```bash
python3 -m lament.metaprogramming_demo
```

This will run comprehensive demonstrations of:
- Hygienic macro definition and expansion
- Compile-time code generation
- AST manipulation and transformation
- Runtime reflection and introspection
- Advanced metaprogramming techniques

## Module Statistics

- **Total Lines**: ~1,400
- **Classes**: 11 major classes
- **Functions**: 80+ methods and functions
- **Features**: 4 major subsystems

## Integration

The metaprogramming module integrates seamlessly with the rest of the Lament language:

```python
# Import everything
from lament.metaprogramming import (
    HygienicMacro, CodeGenerator, ASTManipulator, Reflect,
    Pattern, PatternType, TypeInfo, MethodInfo,
    create_macro, create_pattern, setup_standard_macros
)

# Use with parser and lexer
from lament.parser import Parser
from lament.lexer import Lexer

# Parse code
lexer = Lexer(source_code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Apply metaprogramming transformations
manipulator = ASTManipulator()
optimized = manipulator.transform(ast, optimizer_function)

# Use reflection at runtime
reflect = Reflect()
type_info = reflect.get_type_info(value)
```

## License

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
