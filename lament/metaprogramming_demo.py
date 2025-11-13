"""
Lament Metaprogramming Demonstration
=====================================

This module demonstrates the powerful metaprogramming capabilities
of the Lament language, including:

- Hygienic macros with pattern matching
- Compile-time code generation
- AST manipulation and transformation
- Runtime reflection and introspection

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

from lament.metaprogramming import (
    HygienicMacro, CodeGenerator, ASTManipulator, Reflect,
    Pattern, PatternType, create_pattern, setup_standard_macros,
    ASTTransformer, TypeInfo
)
from lament.parser import (
    NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral, Identifier,
    BinaryOp, UnaryOp, ConfessStmt, VariableDecl, Assignment,
    IfStmt, WhileStmt, FunctionDef, FunctionCall, ExhaleStmt
)
from lament.types import TimelineValue


# ============================================================================
# DEMO 1: HYGIENIC MACROS
# ============================================================================

def demo_hygienic_macros():
    """Demonstrate hygienic macro system."""
    print("=" * 70)
    print("DEMO 1: HYGIENIC MACROS")
    print("=" * 70)

    macro_system = HygienicMacro()

    # Define a simple macro: unless (opposite of if)
    print("\n1. Defining 'unless' macro...")
    print("   Syntax: unless <condition> { <body> }")
    print("   Expands to: if not <condition> { <body> }")

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

    # Expand the macro
    print("\n2. Expanding macro...")
    print("   Input: unless x > 10 { confess 'small' }")

    condition = BinaryOp(Identifier('x'), '>', NumberLiteral(10))
    body = ConfessStmt(StringLiteral('small'))

    expanded = macro_system.expand('unless', [condition, [body]])

    print(f"   Output: {type(expanded).__name__} with negated condition")
    print(f"   Condition type: {type(expanded.condition).__name__}")
    print(f"   Condition operator: {expanded.condition.op}")

    # Define a repeat macro
    print("\n3. Defining 'repeat' macro...")
    print("   Syntax: repeat <n> { <body> }")
    print("   Expands to: for _i in range(n) { <body> }")

    repeat_pattern = [
        create_pattern(PatternType.EXPRESSION, 'n'),
        create_pattern(PatternType.BLOCK, 'body')
    ]
    repeat_template = WhileStmt(
        BinaryOp(Identifier('_counter'), '<', Identifier('n')),
        [Identifier('body')]
    )
    macro_system.define('repeat', repeat_pattern, repeat_template)

    # Test hygiene
    print("\n4. Testing macro hygiene...")
    print("   Macros automatically rename variables to prevent capture")
    print("   Variable '_counter' will be renamed to prevent conflicts")

    n_expr = NumberLiteral(5)
    repeat_body = ConfessStmt(StringLiteral('Hello'))
    expanded_repeat = macro_system.expand('repeat', [n_expr, [repeat_body]])

    print(f"   Expanded to: {type(expanded_repeat).__name__}")
    print("   Internal variables have been renamed for hygiene")

    # Setup standard macros
    print("\n5. Setting up standard macro library...")
    setup_standard_macros(macro_system)
    print(f"   Loaded {len(macro_system.macros)} standard macros")
    print(f"   Available macros: {', '.join(macro_system.macros.keys())}")

    print("\n" + "=" * 70 + "\n")


# ============================================================================
# DEMO 2: COMPILE-TIME CODE GENERATION
# ============================================================================

def demo_code_generation():
    """Demonstrate compile-time code generation."""
    print("=" * 70)
    print("DEMO 2: COMPILE-TIME CODE GENERATION")
    print("=" * 70)

    generator = CodeGenerator()

    # Define getter template
    print("\n1. Defining getter method template...")
    print("   Template: sigh get_{{field}}() { exhale @{{field}} }")

    generator.define_template(
        'getter',
        'sigh get_{{field}}() { exhale @{{field}} }',
        ['field']
    )

    # Generate getter
    print("\n2. Generating getter for 'name' field...")
    code = generator.instantiate('getter', {'field': 'name'})
    print(f"   Generated: {code}")

    # Define setter template
    print("\n3. Defining setter method template...")
    generator.define_template(
        'setter',
        'sigh set_{{field}}(value) { {{field}} = value }',
        ['field']
    )

    # Generate setter
    print("\n4. Generating setter for 'age' field...")
    code = generator.instantiate('setter', {'field': 'age'})
    print(f"   Generated: {code}")

    # Generate a class (collection of functions)
    print("\n5. Generating a class structure...")
    print("   Class: Person with fields [name, age, email]")

    person_methods = generator.generate_class(
        'Person',
        ['name', 'age', 'email'],
        ['init', 'get_name', 'set_name', 'get_age', 'set_age', 'get_email', 'set_email']
    )

    print(f"   Generated {len(person_methods)} methods:")
    for method in person_methods:
        print(f"     - {method.name}({', '.join(method.params)})")

    # Generate function with template
    print("\n6. Generating function from template...")
    func = generator.generate_function(
        'greet',
        ['name'],
        'confess "Hello, {{name}}!"',
        {'name': 'name'}
    )
    print(f"   Generated: {func.name}({', '.join(func.params)})")

    # Show all generated code
    print(f"\n7. Total generated code units: {len(generator.get_generated_code())}")

    print("\n" + "=" * 70 + "\n")


# ============================================================================
# DEMO 3: AST MANIPULATION
# ============================================================================

def demo_ast_manipulation():
    """Demonstrate AST manipulation capabilities."""
    print("=" * 70)
    print("DEMO 3: AST MANIPULATION")
    print("=" * 70)

    manipulator = ASTManipulator()

    # Create sample AST
    print("\n1. Creating sample AST...")
    ast = [
        VariableDecl('x', NumberLiteral(10)),
        VariableDecl('y', NumberLiteral(20)),
        ConfessStmt(BinaryOp(Identifier('x'), '+', Identifier('y'))),
        FunctionCall('print', [StringLiteral('Hello')])
    ]
    print(f"   Created AST with {len(ast)} statements")

    # Find nodes
    print("\n2. Finding all VariableDecl nodes...")
    var_decls = manipulator.find_nodes(ast, VariableDecl)
    print(f"   Found {len(var_decls)} variable declarations:")
    for decl in var_decls:
        print(f"     - {decl.name} = {decl.value.value}")

    # Find by predicate
    print("\n3. Finding all BinaryOp nodes with '+' operator...")
    additions = manipulator.find_by_predicate(
        ast,
        lambda node: isinstance(node, BinaryOp) and node.op == '+'
    )
    print(f"   Found {len(additions)} addition operations")

    # Transform AST
    print("\n4. Transforming: change all '+' to '*'...")
    def change_op(node):
        if isinstance(node, BinaryOp) and node.op == '+':
            node.op = '*'
        return node

    transformed = manipulator.transform(manipulator.clone(ast), change_op)

    # Find additions in transformed AST
    new_mults = manipulator.find_by_predicate(
        transformed,
        lambda node: isinstance(node, BinaryOp) and node.op == '*'
    )
    print(f"   Result: {len(new_mults)} multiplication operations")

    # Quote/unquote
    print("\n5. Quote: Converting code string to AST...")
    code = "remember z = 42"
    quoted = manipulator.quote(code)
    print(f"   Code: '{code}'")
    print(f"   AST type: {type(quoted).__name__}")
    print(f"   Variable: {quoted.name}")
    print(f"   Value: {quoted.value.value}")

    # Unquote
    print("\n6. Unquote: Converting AST back to code...")
    node = BinaryOp(NumberLiteral(10), '+', NumberLiteral(20))
    code_str = manipulator.unquote(node)
    print(f"   AST: BinaryOp(10, '+', 20)")
    print(f"   Code: '{code_str}'")

    # Clone and merge
    print("\n7. Cloning and merging ASTs...")
    ast1 = [VariableDecl('a', NumberLiteral(1))]
    ast2 = [VariableDecl('b', NumberLiteral(2))]
    merged = manipulator.merge_trees(ast1, ast2)
    print(f"   AST1 statements: {len(ast1)}")
    print(f"   AST2 statements: {len(ast2)}")
    print(f"   Merged statements: {len(merged)}")

    # Custom transformer
    print("\n8. Using custom AST transformer...")

    class ConstantFolder(ASTTransformer):
        """Fold constant expressions."""

        def visit_BinaryOp(self, node):
            # Recursively transform children first
            node = self.generic_visit(node)

            # Fold if both operands are literals
            if isinstance(node.left, NumberLiteral) and isinstance(node.right, NumberLiteral):
                if node.op == '+':
                    return NumberLiteral(node.left.value + node.right.value)
                elif node.op == '*':
                    return NumberLiteral(node.left.value * node.right.value)

            return node

    folder = ConstantFolder()
    expr = BinaryOp(NumberLiteral(2), '+', NumberLiteral(3))
    folded = folder.transform(expr)

    print(f"   Original: 2 + 3")
    print(f"   Folded: {folded.value if isinstance(folded, NumberLiteral) else 'not folded'}")

    print("\n" + "=" * 70 + "\n")


# ============================================================================
# DEMO 4: REFLECTION
# ============================================================================

def demo_reflection():
    """Demonstrate runtime reflection capabilities."""
    print("=" * 70)
    print("DEMO 4: REFLECTION & INTROSPECTION")
    print("=" * 70)

    reflect = Reflect()

    # Basic type information
    print("\n1. Getting type information...")

    values = [
        (42, "integer"),
        (3.14, "float"),
        ("hello", "string"),
        (True, "boolean"),
        ([1, 2, 3], "list"),
        ({'a': 1}, "dict"),
        (None, "void")
    ]

    for value, description in values:
        type_info = reflect.get_type_info(value)
        print(f"   {description:10} -> {type_info.name}")

    # List all types
    print(f"\n2. Available types: {len(reflect.list_types())}")
    for type_name in reflect.list_types():
        print(f"   - {type_name}")

    # Method introspection
    print("\n3. Introspecting string methods...")
    string_info = reflect.type_registry['whisper']
    methods = reflect.get_methods(string_info)
    print(f"   String type has {len(methods)} methods:")
    for method in methods:
        params = ', '.join(method.parameters) if method.parameters else ''
        print(f"     - {method.name}({params})")

    # Check method existence
    print("\n4. Checking method existence...")
    test_value = "hello"
    checks = ['length', 'upper', 'lower', 'split', 'foobar']
    for method in checks:
        exists = reflect.has_method(test_value, method)
        print(f"   '{method}': {'✓ exists' if exists else '✗ does not exist'}")

    # Dynamic invocation
    print("\n5. Dynamic method invocation...")

    print("   Calling 'upper' on 'hello':")
    result = reflect.invoke("hello", "upper", [])
    print(f"     Result: {result}")

    print("   Calling 'length' on 'world':")
    result = reflect.invoke("world", "length", [])
    print(f"     Result: {result}")

    print("   Calling 'abs' on -42:")
    result = reflect.invoke(-42, "abs", [])
    print(f"     Result: {result}")

    # List methods
    print("\n6. List introspection and manipulation...")
    my_list = [1, 2, 3]
    list_info = reflect.get_type_info(my_list)

    print(f"   List methods:")
    for method in reflect.get_methods(list_info):
        params = ', '.join(method.parameters) if method.parameters else ''
        print(f"     - {method.name}({params})")

    print(f"   Original list: {my_list}")
    reflect.invoke(my_list, "append", [4])
    print(f"   After append(4): {my_list}")

    length = reflect.invoke(my_list, "length", [])
    print(f"   Length: {length}")

    # Type checking
    print("\n7. Runtime type checking...")
    test_cases = [
        (42, 'numb'),
        ('hello', 'whisper'),
        ([1, 2], 'list'),
        ('world', 'numb'),  # Should fail
    ]

    for value, expected_type in test_cases:
        is_instance = reflect.is_instance(value, expected_type)
        actual_type = reflect.get_type_name(value)
        status = '✓' if is_instance else '✗'
        print(f"   {status} {repr(value)} is {expected_type}? (actual: {actual_type})")

    # Custom type registration
    print("\n8. Registering custom type...")
    reflect.register_type(
        'Point',
        None,
        {'x': 'numb', 'y': 'numb'},
        {'distance': [], 'move': ['dx', 'dy']}
    )

    point_info = reflect.type_registry['Point']
    print(f"   Registered type: {point_info.name}")
    print(f"   Fields: {list(point_info.fields.keys())}")
    print(f"   Methods: {list(point_info.methods.keys())}")

    # TimelineValue introspection
    print("\n9. Timeline value reflection...")
    timeline = TimelineValue(current=10)
    timeline.assign(20)
    timeline.assign(30)

    type_info = reflect.get_type_info(timeline)
    print(f"   Timeline current value: {timeline.current}")
    print(f"   Type: {type_info.name}")
    print(f"   History length: {len(timeline.history)}")

    print("\n" + "=" * 70 + "\n")


# ============================================================================
# DEMO 5: ADVANCED METAPROGRAMMING
# ============================================================================

def demo_advanced_metaprogramming():
    """Demonstrate advanced metaprogramming techniques."""
    print("=" * 70)
    print("DEMO 5: ADVANCED METAPROGRAMMING")
    print("=" * 70)

    # Combine multiple systems
    print("\n1. Combining macro expansion with code generation...")

    macro_system = HygienicMacro()
    generator = CodeGenerator()
    manipulator = ASTManipulator()

    # Define a macro
    print("   Defining 'property' macro for getter/setter generation...")

    # Use code generator to create template
    generator.define_template(
        'property_getter',
        'sigh get_{{name}}() { exhale @{{name}} }',
        ['name']
    )

    generator.define_template(
        'property_setter',
        'sigh set_{{name}}(value) { {{name}} = value }',
        ['name']
    )

    properties = ['x', 'y', 'z']
    print(f"\n   Generating properties for: {', '.join(properties)}")

    for prop in properties:
        getter = generator.instantiate('property_getter', {'name': prop})
        setter = generator.instantiate('property_setter', {'name': prop})
        print(f"     ✓ {prop}: getter and setter created")

    # AST transformation pipeline
    print("\n2. Creating AST transformation pipeline...")

    class OptimizationPipeline:
        """Chain multiple AST transformations."""

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

    pipeline = OptimizationPipeline()

    # Add transformations
    def constant_fold(ast):
        """Fold constant expressions."""
        manipulator = ASTManipulator()
        def fold(node):
            if isinstance(node, BinaryOp):
                if isinstance(node.left, NumberLiteral) and isinstance(node.right, NumberLiteral):
                    if node.op == '+':
                        return NumberLiteral(node.left.value + node.right.value)
            return node
        return manipulator.transform(ast, fold)

    def eliminate_dead_code(ast):
        """Remove unreachable code."""
        # Simplified dead code elimination
        if isinstance(ast, list):
            return [stmt for stmt in ast if not isinstance(stmt, VoidLiteral)]
        return ast

    pipeline.add(constant_fold).add(eliminate_dead_code)

    print("   Pipeline stages:")
    print("     1. Constant folding")
    print("     2. Dead code elimination")

    # Apply pipeline
    test_ast = [
        VariableDecl('a', BinaryOp(NumberLiteral(1), '+', NumberLiteral(2))),
        ConfessStmt(Identifier('a'))
    ]

    optimized = pipeline.apply(test_ast)
    print(f"   Original AST: {len(test_ast)} statements")
    print(f"   Optimized AST: {len(optimized)} statements")

    # Metaprogramming with reflection
    print("\n3. Using reflection for dynamic code generation...")

    reflect = Reflect()

    # Generate methods based on type info
    def generate_wrapper_methods(type_name):
        """Generate wrapper methods for a type."""
        type_info = reflect.type_registry.get(type_name)
        if not type_info:
            return []

        wrappers = []
        for method_name in type_info.methods.keys():
            wrapper_name = f"safe_{method_name}"
            wrappers.append(wrapper_name)

        return wrappers

    print("   Generating wrapper methods for 'whisper' type:")
    wrappers = generate_wrapper_methods('whisper')
    for wrapper in wrappers:
        print(f"     - {wrapper}()")

    # Code-as-data manipulation
    print("\n4. Code-as-data: manipulating programs as data structures...")

    # Create a program
    program = [
        VariableDecl('counter', NumberLiteral(0)),
        WhileStmt(
            BinaryOp(Identifier('counter'), '<', NumberLiteral(10)),
            [
                ConfessStmt(Identifier('counter')),
                Assignment('counter', BinaryOp(Identifier('counter'), '+', NumberLiteral(1)))
            ]
        )
    ]

    # Analyze program
    all_vars = manipulator.find_nodes(program, VariableDecl)
    all_loops = manipulator.find_nodes(program, WhileStmt)

    print(f"   Program analysis:")
    print(f"     Variables declared: {len(all_vars)}")
    print(f"     Loops: {len(all_loops)}")
    print(f"     Total statements: {len(program)}")

    # Transform program
    print("\n   Transforming: unroll loop...")

    # Find while loop and unroll it
    if all_loops:
        loop = all_loops[0]
        # Extract loop body
        unrolled = []
        for i in range(3):  # Unroll 3 iterations
            for stmt in loop.body:
                unrolled.append(manipulator.clone(stmt))

        print(f"     Original: {len(loop.body)} statements per iteration")
        print(f"     Unrolled: {len(unrolled)} total statements (3 iterations)")

    print("\n" + "=" * 70 + "\n")


# ============================================================================
# MAIN DEMO RUNNER
# ============================================================================

def run_all_demos():
    """Run all metaprogramming demonstrations."""
    print("\n")
    print("#" * 70)
    print("# LAMENT METAPROGRAMMING CAPABILITIES DEMONSTRATION")
    print("#" * 70)
    print("\n")

    try:
        demo_hygienic_macros()
        demo_code_generation()
        demo_ast_manipulation()
        demo_reflection()
        demo_advanced_metaprogramming()

        print("#" * 70)
        print("# ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("#" * 70)
        print("\n")

        # Summary
        print("SUMMARY OF CAPABILITIES:")
        print("-" * 70)
        print("✓ Hygienic Macros: Safe code generation with automatic variable")
        print("  renaming to prevent capture")
        print()
        print("✓ Compile-Time Code Generation: Template-based code generation")
        print("  with parameter substitution")
        print()
        print("✓ AST Manipulation: Complete API for programmatic AST")
        print("  modification, transformation, and analysis")
        print()
        print("✓ Reflection: Runtime type introspection, dynamic method")
        print("  invocation, and type checking")
        print()
        print("✓ Advanced Features: Transformation pipelines, code-as-data,")
        print("  optimization passes, and metaprogramming utilities")
        print("-" * 70)
        print()

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
