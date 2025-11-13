"""
Lament Advanced Type System - Comprehensive Examples
====================================================

This demo showcases the advanced type system features in Lament,
including gradual typing, dependent types, linear types, effects,
and refinement types.
"""

from lament.typesystem import (
    # Base types
    Type, TypeKind,
    # Primitive types
    NUMB, WHISPER, MAYBE, VOID, ACHE,
    AnyType, NeverType,
    # Composite types
    ListType, DictType, TupleType,
    # Function types
    FunctionType,
    # Union and optional
    UnionType, Optional,
    # Type variables
    TypeVariable,
    # Dependent types
    DependentType, Vector, Range,
    # Linear types
    LinearType, OwnershipKind, Lifetime, OwnershipChecker,
    # Effect system
    Effect, EffectType, PureEffect, IOEffect, StateEffect, ExceptionEffect,
    # Refinement types
    RefinementType, Predicate,
    PositiveInt, NegativeInt, NonZeroInt, EvenInt,
    NonEmptyString, NonEmptyList,
    # Type checker
    TypeChecker, TypeEnvironment,
    # Utilities
    parse_type_annotation, format_type, are_types_compatible,
    least_upper_bound
)


def example_1_gradual_typing():
    """Example 1: Gradual Typing with Inference"""
    print("=" * 70)
    print("EXAMPLE 1: Gradual Typing")
    print("=" * 70)

    checker = TypeChecker()

    # Type inference for literals
    print("\n1. Automatic Type Inference:")
    print("   remember x = 5")
    x_type = checker.infer_type(5)
    print(f"   Inferred: x : {x_type}")

    print("\n   remember message = 'Hello, Lament!'")
    msg_type = checker.infer_type("Hello, Lament!")
    print(f"   Inferred: message : {msg_type}")

    print("\n   remember scores = [95, 87, 92]")
    scores_type = checker.infer_type([95, 87, 92])
    print(f"   Inferred: scores : {scores_type}")

    # Optional types
    print("\n2. Optional Types (Union with void):")
    print("   remember maybe_value: numb | void = 42")
    opt_type = Optional(NUMB)
    print(f"   Type: {opt_type}")
    print(f"   Can be numb: {NUMB.is_subtype_of(opt_type)}")
    print(f"   Can be void: {VOID.is_subtype_of(opt_type)}")

    # Union types
    print("\n3. Union Types:")
    print("   remember id: numb | whisper")
    union_type = UnionType([NUMB, WHISPER])
    print(f"   Type: {union_type}")
    print(f"   id = 123  ✓ (valid)")
    print(f"   id = 'ABC123'  ✓ (valid)")

    # Type annotations
    print("\n4. Parsing Type Annotations:")
    annotations = [
        "numb",
        "List<whisper>",
        "Dict<whisper, numb>",
        "numb | void"
    ]
    for ann in annotations:
        parsed = parse_type_annotation(ann)
        print(f"   '{ann}' → {parsed}")


def example_2_dependent_types():
    """Example 2: Dependent Types"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Dependent Types (Value-Dependent Types)")
    print("=" * 70)

    # Vector with compile-time length
    print("\n1. Fixed-Length Vectors:")
    print("   remember point3d: Vector<ache, 3> = [1.0, 2.0, 3.0]")
    vec3_type = Vector(ACHE, 3)
    print(f"   Type: {vec3_type}")
    print(f"   Constraint valid: {vec3_type.check_constraint()}")

    print("\n   remember rgb_color: Vector<numb, 3> = [255, 128, 0]")
    rgb_type = Vector(NUMB, 3)
    print(f"   Type: {rgb_type}")

    # Range types
    print("\n2. Range Types (Bounded Values):")
    print("   remember age: Range<0, 150>")
    age_type = Range(0, 150)
    print(f"   Type: {age_type}")
    print(f"   Valid range: {age_type.check_constraint()}")

    print("\n   remember percentage: Range<0, 100>")
    percent_type = Range(0, 100)
    print(f"   Type: {percent_type}")

    # Custom dependent type
    print("\n3. Custom Dependent Type:")
    matrix_type = DependentType(
        ListType(ListType(NUMB)),
        {"rows": 3, "cols": 3},
        lambda deps: deps["rows"] > 0 and deps["cols"] > 0
    )
    print(f"   Matrix3x3 type: {matrix_type}")
    print(f"   Constraint satisfied: {matrix_type.check_constraint()}")


def example_3_linear_types():
    """Example 3: Linear Types and Ownership"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Linear Types (Rust-like Ownership)")
    print("=" * 70)

    print("\n1. Ownership Basics:")
    print("   remember name: owned whisper = 'Lament'")
    owned_type = LinearType(WHISPER, OwnershipKind.OWNED)
    print(f"   Type: {owned_type}")

    # Borrowing
    print("\n2. Borrowing (Immutable):")
    print("   borrow 'a name  # Immutable borrow")
    lifetime_a = Lifetime("a", 0)
    borrowed_type = owned_type.borrow(lifetime_a)
    print(f"   Type: {borrowed_type}")

    print("\n3. Mutable Borrowing:")
    print("   borrow_mut 'b name  # Mutable borrow")
    lifetime_b = Lifetime("b", 0)
    mut_borrow_type = LinearType(WHISPER, OwnershipKind.OWNED).borrow_mut(lifetime_b)
    print(f"   Type: {mut_borrow_type}")

    # Ownership checking
    print("\n4. Ownership Checking:")
    checker = OwnershipChecker()

    print("   remember data: owned List<numb> = [1, 2, 3]")
    data_type = LinearType(ListType(NUMB), OwnershipKind.OWNED)
    checker.declare_owned("data", data_type)

    try:
        print("   borrow 'x data")
        borrow = checker.borrow_var("data", Lifetime("x", 1))
        print(f"   ✓ Borrowed: {borrow}")

        print("   # Cannot move while borrowed")
        # This would fail: checker.move_var("data")

        checker.exit_scope()  # End borrow
        print("   # Borrow ended")

        print("   move data  # Transfer ownership")
        moved = checker.move_var("data")
        print(f"   ✓ Moved: {moved}")

        print("   # Cannot use 'data' after move")
        # This would fail: checker.borrow_var("data", Lifetime("y", 2))

    except TypeError as e:
        print(f"   ✗ Error: {e}")


def example_4_effect_system():
    """Example 4: Effect System"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Effect System (Tracking Side Effects)")
    print("=" * 70)

    # Pure functions
    print("\n1. Pure Functions (No Side Effects):")
    print("   sigh add(x: numb, y: numb) -> numb: Pure")
    pure_func = FunctionType([NUMB, NUMB], NUMB, EffectType([PureEffect()]))
    print(f"   Type: {pure_func}")

    # IO effects
    print("\n2. IO Effects:")
    print("   sigh read_file(path: whisper) -> whisper: IO[read]")
    io_read_func = FunctionType(
        [WHISPER],
        WHISPER,
        EffectType([IOEffect({"read"})])
    )
    print(f"   Type: {io_read_func}")

    print("\n   sigh write_log(msg: whisper) -> void: IO[write]")
    io_write_func = FunctionType(
        [WHISPER],
        VOID,
        EffectType([IOEffect({"write"})])
    )
    print(f"   Type: {io_write_func}")

    # State effects
    print("\n3. State Effects:")
    print("   sigh increment_counter() -> numb: State[counter]")
    state_func = FunctionType(
        [],
        NUMB,
        EffectType([StateEffect({"counter"})])
    )
    print(f"   Type: {state_func}")

    # Combined effects
    print("\n4. Combined Effects:")
    print("   sigh save_and_log(data: whisper) -> void: IO[read,write] + State[db]")
    combined_func = FunctionType(
        [WHISPER],
        VOID,
        EffectType([
            IOEffect({"read", "write"}),
            StateEffect({"db"})
        ])
    )
    print(f"   Type: {combined_func}")

    # Effect subtyping
    print("\n5. Effect Subtyping:")
    pure_eff = EffectType([PureEffect()])
    io_eff = EffectType([IOEffect({"read", "write"})])
    io_read_eff = EffectType([IOEffect({"read"})])

    print(f"   Pure <: IO? {pure_eff.is_subtype_of(io_eff)}")
    print(f"   IO[read] <: IO[read,write]? {io_read_eff.is_subtype_of(io_eff)}")
    print(f"   IO[read,write] <: IO[read]? {io_eff.is_subtype_of(io_read_eff)}")


def example_5_refinement_types():
    """Example 5: Refinement Types"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Refinement Types (Types with Predicates)")
    print("=" * 70)

    # Basic refinement types
    print("\n1. Numeric Refinements:")

    print("   remember count: PositiveInt = 42")
    pos_type = PositiveInt()
    print(f"   Type: {pos_type}")
    print(f"   42 valid? {pos_type.check_value(42)}")
    print(f"   -5 valid? {pos_type.check_value(-5)}")

    print("\n   remember index: NonZeroInt")
    nonzero_type = NonZeroInt()
    print(f"   Type: {nonzero_type}")
    print(f"   7 valid? {nonzero_type.check_value(7)}")
    print(f"   0 valid? {nonzero_type.check_value(0)}")

    print("\n   remember even_num: EvenInt = 8")
    even_type = EvenInt()
    print(f"   Type: {even_type}")
    print(f"   8 valid? {even_type.check_value(8)}")
    print(f"   9 valid? {even_type.check_value(9)}")

    # String refinements
    print("\n2. String Refinements:")
    print("   remember username: NonEmptyString")
    nonempty_str = NonEmptyString()
    print(f"   Type: {nonempty_str}")
    print(f"   'alice' valid? {nonempty_str.check_value('alice')}")
    print(f"   '' valid? {nonempty_str.check_value('')}")

    # Collection refinements
    print("\n3. Collection Refinements:")
    print("   remember items: NonEmptyList<numb>")
    nonempty_list = NonEmptyList(NUMB)
    print(f"   Type: {nonempty_list}")
    print(f"   [1,2,3] valid? {nonempty_list.check_value([1, 2, 3])}")
    print(f"   [] valid? {nonempty_list.check_value([])}")

    # Custom refinement
    print("\n4. Custom Refinement Type:")
    in_range_predicate = Predicate(
        "in_range_1_10",
        lambda x: 1 <= x <= 10,
        "Value between 1 and 10"
    )
    rating_type = RefinementType(NUMB, "x", [in_range_predicate])
    print(f"   RatingScore type: {rating_type}")
    print(f"   5 valid? {rating_type.check_value(5)}")
    print(f"   15 valid? {rating_type.check_value(15)}")

    # Combined refinements
    print("\n5. Combined Refinement Predicates:")
    from lament.typesystem import POSITIVE, EVEN
    pos_even_type = RefinementType(NUMB, "n", [POSITIVE, EVEN])
    print(f"   PositiveEven type: {pos_even_type}")
    print(f"   4 valid? {pos_even_type.check_value(4)}")
    print(f"   3 valid? {pos_even_type.check_value(3)}")
    print(f"   -4 valid? {pos_even_type.check_value(-4)}")


def example_6_advanced_combinations():
    """Example 6: Advanced Type Combinations"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Advanced Type Combinations")
    print("=" * 70)

    # Function with refinement types
    print("\n1. Function with Refinement Types:")
    print("   sigh divide(numerator: numb, denominator: NonZeroInt) -> ache")
    divide_type = FunctionType(
        [NUMB, NonZeroInt()],
        ACHE,
        EffectType([PureEffect()])
    )
    print(f"   Type: {divide_type}")

    # Generic function with effect
    print("\n2. Generic Function with Effects:")
    T = TypeVariable("T")
    print("   sigh map<T>(func: T -> T, list: List<T>) -> List<T>: Pure")
    map_type = FunctionType(
        [FunctionType([T], T), ListType(T)],
        ListType(T),
        EffectType([PureEffect()])
    )
    print(f"   Type: {map_type}")

    # Linear type with refinement
    print("\n3. Linear Type with Refinement:")
    print("   remember buffer: owned NonEmptyList<numb>")
    buffer_type = LinearType(
        NonEmptyList(NUMB),
        OwnershipKind.OWNED
    )
    print(f"   Type: {buffer_type}")

    # Dependent type with effects
    print("\n4. Function Returning Dependent Type:")
    print("   sigh create_vector(length: PositiveInt) -> Vector<numb, length>: Pure")
    # Note: In a full implementation, this would use dependent types more rigorously
    create_vec_type = FunctionType(
        [PositiveInt()],
        ListType(NUMB),  # Simplified
        EffectType([PureEffect()])
    )
    print(f"   Type: {create_vec_type}")

    # Higher-order function with effects
    print("\n5. Higher-Order Function with Effect Polymorphism:")
    print("   sigh with_logging<E>(func: () -> numb: E) -> numb: E + IO[write]")
    E = TypeVariable("E")
    with_logging_type = FunctionType(
        [FunctionType([], NUMB, EffectType([]))],
        NUMB,
        EffectType([IOEffect({"write"})])
    )
    print(f"   Type: {with_logging_type}")


def example_7_type_checking():
    """Example 7: Type Checking and Inference"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Type Checking and Inference")
    print("=" * 70)

    checker = TypeChecker()

    # Type inference
    print("\n1. Inferring Types from Values:")
    values_and_types = [
        (42, "numb"),
        (3.14, "ache"),
        ("hello", "whisper"),
        ([1, 2, 3], "List<numb>"),
        ({"name": "Alice", "age": 30}, "Dict<whisper, ...>"),
    ]

    for value, expected_desc in values_and_types:
        inferred = checker.infer_type(value)
        print(f"   {repr(value):30} → {inferred}")

    # Type unification
    print("\n2. Type Unification:")
    pairs = [
        (ListType(NUMB), ListType(NUMB)),
        (ListType(TypeVariable("T")), ListType(WHISPER)),
        (Optional(NUMB), UnionType([NUMB, VOID])),
    ]

    for t1, t2 in pairs:
        unified = t1.unify(t2)
        print(f"   {t1} ∪ {t2}")
        print(f"   → {unified}")

    # Subtyping
    print("\n3. Subtype Checking:")
    subtype_pairs = [
        (NUMB, AnyType()),
        (NeverType(), NUMB),
        (ListType(NUMB), ListType(NUMB)),
        (PositiveInt(), NUMB),
    ]

    for t1, t2 in subtype_pairs:
        is_subtype = t1.is_subtype_of(t2)
        symbol = "✓" if is_subtype else "✗"
        print(f"   {symbol} {t1} <: {t2}")

    # Type compatibility
    print("\n4. Type Compatibility:")
    compat_pairs = [
        (NUMB, NUMB),
        (NUMB, WHISPER),
        (ListType(NUMB), ListType(ACHE)),
        (Optional(NUMB), NUMB),
    ]

    for t1, t2 in compat_pairs:
        compatible = are_types_compatible(t1, t2)
        symbol = "✓" if compatible else "✗"
        print(f"   {symbol} {t1} ~ {t2}")


def example_8_real_world_usage():
    """Example 8: Real-World Usage Patterns"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Real-World Usage Patterns")
    print("=" * 70)

    print("\n1. Safe Division Function:")
    print("   ```lament")
    print("   sigh safe_divide(a: numb, b: NonZeroInt) -> ache:")
    print("       exhale a / b")
    print("   ```")
    safe_div = FunctionType([NUMB, NonZeroInt()], ACHE)
    print(f"   Type: {safe_div}")
    print("   Benefit: Division by zero prevented at type level!")

    print("\n2. Array Access with Bounds Checking:")
    print("   ```lament")
    print("   sigh get_element(arr: Vector<numb, 10>, idx: Range<0, 9>) -> numb:")
    print("       exhale arr[idx]")
    print("   ```")
    get_elem = FunctionType(
        [Vector(NUMB, 10), Range(0, 9)],
        NUMB
    )
    print(f"   Type: {get_elem}")
    print("   Benefit: Array bounds checked at compile time!")

    print("\n3. Resource Management with Linear Types:")
    print("   ```lament")
    print("   sigh open_file(path: whisper) -> owned FileHandle: IO[read]")
    print("   sigh close_file(handle: owned FileHandle) -> void: IO")
    print("   ```")
    file_handle = LinearType(
        parse_type_annotation("whisper"),  # Simplified
        OwnershipKind.OWNED
    )
    open_file = FunctionType(
        [WHISPER],
        file_handle,
        EffectType([IOEffect({"read"})])
    )
    print(f"   open_file: {open_file}")
    print("   Benefit: Resources automatically tracked and freed!")

    print("\n4. Pure vs Impure Computations:")
    print("   ```lament")
    print("   sigh compute(x: numb) -> numb: Pure")
    print("       exhale x * 2")
    print("   ")
    print("   sigh log_and_compute(x: numb) -> numb: IO[write] + Pure")
    print("       confess 'Computing...'")
    print("       exhale x * 2")
    print("   ```")
    pure_compute = FunctionType([NUMB], NUMB, EffectType([PureEffect()]))
    impure_compute = FunctionType(
        [NUMB],
        NUMB,
        EffectType([IOEffect({"write"})])
    )
    print(f"   pure: {pure_compute}")
    print(f"   impure: {impure_compute}")
    print("   Benefit: Side effects explicitly tracked!")


def run_all_examples():
    """Run all type system examples."""
    example_1_gradual_typing()
    example_2_dependent_types()
    example_3_linear_types()
    example_4_effect_system()
    example_5_refinement_types()
    example_6_advanced_combinations()
    example_7_type_checking()
    example_8_real_world_usage()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nThe Lament type system provides:")
    print("  ✓ Gradual typing with inference")
    print("  ✓ Dependent types for compile-time guarantees")
    print("  ✓ Linear types for resource safety")
    print("  ✓ Effect system for tracking side effects")
    print("  ✓ Refinement types for value constraints")
    print("\nThis enables writing safer, more expressive code!")


if __name__ == "__main__":
    run_all_examples()
