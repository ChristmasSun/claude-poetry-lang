# Lament Type System - Quick Reference

## Import

```python
from lament.typesystem import *
```

## 1. Gradual Typing

### Basic Types
```lament
remember x: numb = 5              # Integer
remember y: ache = 3.14           # Float
remember s: whisper = "hello"     # String
remember b: maybe = yes           # Boolean
remember n: void = void           # Null/None
```

### Inference
```lament
remember x = 5                    # Inferred: numb
remember s = "hi"                 # Inferred: whisper
```

### Optional & Union
```lament
remember opt: numb | void = 42    # Optional number
remember id: numb | whisper       # Union type
```

### Collections
```lament
remember nums: List<numb> = [1, 2, 3]
remember map: Dict<whisper, numb> = {"a": 1}
remember pair: (numb, whisper) = (42, "answer")
```

### Type Variables
```lament
sigh identity<T>(x: T) -> T:
    exhale x
```

## 2. Dependent Types

### Fixed-Length Vectors
```lament
remember v3: Vector<numb, 3> = [1, 2, 3]
remember v5: Vector<ache, 5> = [1.0, 2.0, 3.0, 4.0, 5.0]
```

### Range Types
```lament
remember age: Range<0, 150> = 25
remember percent: Range<0, 100> = 85
remember hour: Range<0, 23> = 14
```

### Custom Dependent
```python
# Python API
matrix_type = DependentType(
    ListType(ListType(NUMB)),
    {"rows": 3, "cols": 3},
    lambda d: d["rows"] > 0 and d["cols"] > 0
)
```

## 3. Linear Types (Ownership)

### Ownership
```lament
remember data: owned List<numb> = [1, 2, 3]
```

### Borrowing
```lament
# Immutable borrow
borrow 'a data                    # &'a List<numb>

# Mutable borrow
borrow_mut 'b data                # &mut 'b List<numb>
```

### Moving
```lament
remember new_data = move data
# 'data' is now invalid
```

### Functions with Ownership
```lament
sigh consume(data: owned List<numb>) -> void:
    # Takes ownership

sigh read(data: &'a List<numb>) -> numb:
    # Borrows immutably

sigh mutate(data: &mut 'a List<numb>) -> void:
    # Borrows mutably
```

## 4. Effect System

### Pure Functions
```lament
sigh add(x: numb, y: numb) -> numb: Pure
    exhale x + y
```

### IO Effects
```lament
sigh read_file(path: whisper) -> whisper: IO[read]
    # File reading

sigh write_log(msg: whisper) -> void: IO[write]
    # File writing

sigh network_call() -> whisper: IO[read, write]
    # Network I/O
```

### State Effects
```lament
sigh get_counter() -> numb: State[counter]
    # Read state

sigh set_counter(n: numb) -> void: State[counter]
    # Modify state
```

### Combined Effects
```lament
sigh process() -> void: IO[read, write] + State[db]
    # Multiple effects
```

### Effect in Types
```python
# Python API
func_type = FunctionType(
    [NUMB, NUMB],
    NUMB,
    EffectType([PureEffect()])
)
```

## 5. Refinement Types

### Built-in Refinements

#### Numeric
```lament
remember pos: PositiveInt = 5           # {x: numb | x > 0}
remember neg: NegativeInt = -3          # {x: numb | x < 0}
remember nz: NonZeroInt = 7             # {x: numb | x != 0}
remember even: EvenInt = 8              # {x: numb | x % 2 == 0}
remember odd: OddInt = 9                # {x: numb | x % 2 != 0}
```

#### String
```lament
remember name: NonEmptyString = "Alice" # {s: whisper | len(s) > 0}
```

#### Collection
```lament
remember items: NonEmptyList<numb> = [1, 2, 3]
                                        # {l: List<numb> | len(l) > 0}
```

### Custom Refinements
```python
# Python API
in_range = Predicate(
    "in_range_1_10",
    lambda x: 1 <= x <= 10,
    "Value between 1 and 10"
)

rating_type = RefinementType(NUMB, "x", [in_range])
```

### Combined Predicates
```python
# Python API
from lament.typesystem import POSITIVE, EVEN

pos_even = RefinementType(NUMB, "n", [POSITIVE, EVEN])
```

## Common Patterns

### Safe Division
```lament
sigh divide(a: numb, b: NonZeroInt) -> ache:
    exhale a / b  # Guaranteed no division by zero!
```

### Safe Array Access
```lament
sigh get_elem(
    arr: Vector<numb, 10>,
    idx: Range<0, 9>
) -> numb:
    exhale arr[idx]  # Bounds checked at compile time!
```

### Resource Management
```lament
sigh with_file(path: whisper) -> whisper: IO[read]
    remember handle: owned FileHandle = open(path)
    remember data = read(borrow handle)
    close(move handle)
    exhale data
```

### Pure Computation
```lament
sigh factorial(n: PositiveInt) -> numb: Pure
    if n <= 1:
        exhale 1
    exhale n * factorial(n - 1)
```

### Effect Polymorphism
```lament
sigh with_logging<E>(func: () -> numb: E) -> numb: E + IO[write]
    confess "Starting..."
    remember result = func()
    confess "Done"
    exhale result
```

## Python API Quick Reference

### Creating Types
```python
# Primitives
numb_type = NUMB
string_type = WHISPER

# Collections
list_type = ListType(NUMB)
dict_type = DictType(WHISPER, NUMB)
tuple_type = TupleType([NUMB, WHISPER, ACHE])

# Functions
func_type = FunctionType([NUMB, NUMB], NUMB)

# Optional/Union
opt_type = Optional(NUMB)
union_type = UnionType([NUMB, WHISPER])

# Dependent
vec_type = Vector(NUMB, 5)
range_type = Range(0, 100)

# Linear
owned_type = LinearType(WHISPER, OwnershipKind.OWNED)
borrowed_type = owned_type.borrow(Lifetime("a", 0))

# Effect
pure_type = EffectType([PureEffect()])
io_type = EffectType([IOEffect({"read", "write"})])

# Refinement
pos_int = PositiveInt()
custom_ref = RefinementType(NUMB, "x", [POSITIVE, EVEN])
```

### Type Checking
```python
checker = TypeChecker()

# Infer type
typ = checker.infer_type(42)

# Check type
checker.check_type(expr, expected_type)

# Unify types
unified = type1.unify(type2)

# Check subtyping
is_sub = type1.is_subtype_of(type2)
```

### Ownership Checking
```python
owner = OwnershipChecker()

# Declare owned
owner.declare_owned("x", LinearType(NUMB, OwnershipKind.OWNED))

# Borrow
lifetime = Lifetime("a", 0)
borrowed = owner.borrow_var("x", lifetime)

# Move
moved = owner.move_var("x")
```

## Type Annotations Syntax

```
Type          ::= PrimitiveType
                | ListType
                | DictType
                | TupleType
                | FunctionType
                | UnionType
                | DependentType
                | LinearType
                | RefinementType

PrimitiveType ::= "numb" | "whisper" | "maybe" | "void" | "ache"

ListType      ::= "List<" Type ">"

DictType      ::= "Dict<" Type "," Type ">"

TupleType     ::= "(" Type ("," Type)* ")"

FunctionType  ::= "(" (Type ("," Type)*)? ")" "->" Type (":" Effect)?

UnionType     ::= Type ("|" Type)+

DependentType ::= Type "<" Param "=" Value ("," Param "=" Value)* ">"

LinearType    ::= ("owned" | "&" | "&mut") Lifetime? Type

RefinementType::= "{" Var ":" Type "|" Predicate ("∧" Predicate)* "}"

Effect        ::= "Pure" | "IO" "[" Op+ "]" | "State" "[" Var+ "]"
```

## Error Handling

```python
try:
    checker.check_type(expr, expected)
except TypeError as e:
    print(f"Type error: {e}")
    print(f"Location: {e.location}")
```

## Best Practices

1. **Use refinement types for domain constraints**
   ```lament
   remember age: Range<0, 150>  # Better than just numb
   ```

2. **Use linear types for resources**
   ```lament
   remember file: owned FileHandle  # Automatic cleanup
   ```

3. **Mark pure functions as Pure**
   ```lament
   sigh compute(x: numb) -> numb: Pure  # Enables optimizations
   ```

4. **Use dependent types for array safety**
   ```lament
   sigh get(arr: Vector<T, n>, idx: Range<0, n-1>) -> T
   ```

5. **Combine refinements for precise types**
   ```lament
   remember score: {x: numb | x >= 0 && x <= 100}
   ```

## Performance Tips

- Type inference is O(n), fast for most code
- Refinement checking happens at compile time
- Linear type checking adds minimal overhead
- Effect tracking is zero-cost at runtime
- Use `Any` sparingly - loses type safety

## Learn More

- Full documentation: `TYPE_SYSTEM_SUMMARY.md`
- Examples: `demos/demo_typesystem.py`
- Run demos: `python -m lament.typesystem`
