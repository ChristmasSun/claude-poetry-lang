"""
Lament Advanced Type System
============================

This module implements an advanced type system for the Lament programming language,
featuring gradual typing, dependent types, linear types, effect systems, and
refinement types.

Features:
1. Gradual Typing: Optional static types with inference
2. Dependent Types: Types that depend on values
3. Linear Types: Rust-like ownership tracking
4. Effect System: Track side effects
5. Refinement Types: Types with predicates

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Dict, Set, Optional, Union, Callable, Tuple
from enum import Enum, auto
from abc import ABC, abstractmethod
import copy
import time
from collections import defaultdict


# ============================================================================
# BASE TYPE CLASSES
# ============================================================================

class TypeKind(Enum):
    """Categories of types in the Lament type system."""
    PRIMITIVE = auto()      # Basic types (numb, whisper, etc.)
    COMPOSITE = auto()      # Compound types (list, dict, tuple)
    FUNCTION = auto()       # Function types
    DEPENDENT = auto()      # Dependent types
    LINEAR = auto()         # Linear/ownership types
    EFFECT = auto()         # Effect types
    REFINEMENT = auto()     # Refinement types
    UNION = auto()          # Union types
    INTERSECTION = auto()   # Intersection types
    GENERIC = auto()        # Generic/parametric types
    ANY = auto()            # Top type (any value)
    NEVER = auto()          # Bottom type (no value)


@dataclass
class Type(ABC):
    """Base class for all types in the system."""
    kind: TypeKind
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def is_subtype_of(self, other: Type) -> bool:
        """Check if this type is a subtype of another."""
        pass

    @abstractmethod
    def unify(self, other: Type) -> Optional[Type]:
        """Try to unify this type with another, returning the unified type."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the type."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


# ============================================================================
# PRIMITIVE TYPES
# ============================================================================

class PrimitiveType(Type):
    """Primitive types for Lament (emotional primitives)."""

    def __init__(self, name: str):
        super().__init__(kind=TypeKind.PRIMITIVE, name=name)

    def is_subtype_of(self, other: Type) -> bool:
        """Primitive types are only subtypes of themselves or Any."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, PrimitiveType):
            return self.name == other.name
        return False

    def unify(self, other: Type) -> Optional[Type]:
        """Unify with another type."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, PrimitiveType) and self.name == other.name:
            return self
        if isinstance(other, TypeVariable):
            return other.unify(self)
        return None

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, PrimitiveType) and self.name == other.name

    def __hash__(self) -> int:
        return hash(('primitive', self.name))


# Lament emotional primitive types
NUMB = PrimitiveType("numb")        # integers
WHISPER = PrimitiveType("whisper")  # strings
MAYBE = PrimitiveType("maybe")      # booleans
VOID = PrimitiveType("void")        # null/none
ACHE = PrimitiveType("ache")        # floats
SIGH = PrimitiveType("sigh")        # generic function


class AnyType(Type):
    """Top type - accepts any value."""

    def __init__(self):
        super().__init__(kind=TypeKind.ANY, name="Any")

    def is_subtype_of(self, other: Type) -> bool:
        """Any is only a subtype of itself."""
        return isinstance(other, AnyType)

    def unify(self, other: Type) -> Optional[Type]:
        """Any unifies with anything, returning the other type."""
        return other

    def __str__(self) -> str:
        return "Any"

    def __eq__(self, other) -> bool:
        return isinstance(other, AnyType)

    def __hash__(self) -> int:
        return hash('any')


class NeverType(Type):
    """Bottom type - no value can inhabit this type."""

    def __init__(self):
        super().__init__(kind=TypeKind.NEVER, name="Never")

    def is_subtype_of(self, other: Type) -> bool:
        """Never is a subtype of everything."""
        return True

    def unify(self, other: Type) -> Optional[Type]:
        """Never cannot unify with anything except itself."""
        if isinstance(other, NeverType):
            return self
        return None

    def __str__(self) -> str:
        return "Never"

    def __eq__(self, other) -> bool:
        return isinstance(other, NeverType)

    def __hash__(self) -> int:
        return hash('never')


# ============================================================================
# COMPOSITE TYPES
# ============================================================================

class ListType(Type):
    """List type with element type parameter."""

    def __init__(self, element_type: Type):
        super().__init__(kind=TypeKind.COMPOSITE, name="List")
        self.element_type = element_type

    def is_subtype_of(self, other: Type) -> bool:
        """Covariant in element type."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, ListType):
            return self.element_type.is_subtype_of(other.element_type)
        return False

    def unify(self, other: Type) -> Optional[Type]:
        """Unify list types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, ListType):
            unified_elem = self.element_type.unify(other.element_type)
            if unified_elem:
                return ListType(unified_elem)
        return None

    def __str__(self) -> str:
        return f"List<{self.element_type}>"

    def __eq__(self, other) -> bool:
        return isinstance(other, ListType) and self.element_type == other.element_type

    def __hash__(self) -> int:
        return hash(('list', self.element_type))


class DictType(Type):
    """Dictionary type with key and value type parameters."""

    def __init__(self, key_type: Type, value_type: Type):
        super().__init__(kind=TypeKind.COMPOSITE, name="Dict")
        self.key_type = key_type
        self.value_type = value_type

    def is_subtype_of(self, other: Type) -> bool:
        """Covariant in value type, invariant in key type."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, DictType):
            return (self.key_type == other.key_type and
                    self.value_type.is_subtype_of(other.value_type))
        return False

    def unify(self, other: Type) -> Optional[Type]:
        """Unify dict types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, DictType):
            unified_key = self.key_type.unify(other.key_type)
            unified_val = self.value_type.unify(other.value_type)
            if unified_key and unified_val:
                return DictType(unified_key, unified_val)
        return None

    def __str__(self) -> str:
        return f"Dict<{self.key_type}, {self.value_type}>"

    def __eq__(self, other) -> bool:
        return (isinstance(other, DictType) and
                self.key_type == other.key_type and
                self.value_type == other.value_type)

    def __hash__(self) -> int:
        return hash(('dict', self.key_type, self.value_type))


class TupleType(Type):
    """Tuple type with fixed element types."""

    def __init__(self, element_types: List[Type]):
        super().__init__(kind=TypeKind.COMPOSITE, name="Tuple")
        self.element_types = element_types

    def is_subtype_of(self, other: Type) -> bool:
        """Covariant in element types."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, TupleType):
            if len(self.element_types) != len(other.element_types):
                return False
            return all(a.is_subtype_of(b) for a, b in
                      zip(self.element_types, other.element_types))
        return False

    def unify(self, other: Type) -> Optional[Type]:
        """Unify tuple types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, TupleType):
            if len(self.element_types) != len(other.element_types):
                return None
            unified = []
            for a, b in zip(self.element_types, other.element_types):
                u = a.unify(b)
                if u is None:
                    return None
                unified.append(u)
            return TupleType(unified)
        return None

    def __str__(self) -> str:
        elems = ", ".join(str(t) for t in self.element_types)
        return f"({elems})"

    def __eq__(self, other) -> bool:
        return (isinstance(other, TupleType) and
                self.element_types == other.element_types)

    def __hash__(self) -> int:
        return hash(('tuple', tuple(self.element_types)))


# ============================================================================
# FUNCTION TYPES
# ============================================================================

class FunctionType(Type):
    """Function type with parameter types and return type."""

    def __init__(self, param_types: List[Type], return_type: Type,
                 effect: Optional[EffectType] = None):
        super().__init__(kind=TypeKind.FUNCTION, name="Function")
        self.param_types = param_types
        self.return_type = return_type
        self.effect = effect or EffectType([PureEffect()])

    def is_subtype_of(self, other: Type) -> bool:
        """Contravariant in params, covariant in return."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, FunctionType):
            if len(self.param_types) != len(other.param_types):
                return False
            # Contravariant in parameters
            params_ok = all(b.is_subtype_of(a) for a, b in
                          zip(self.param_types, other.param_types))
            # Covariant in return type
            return_ok = self.return_type.is_subtype_of(other.return_type)
            # Effect must be subtype
            effect_ok = self.effect.is_subtype_of(other.effect)
            return params_ok and return_ok and effect_ok
        return False

    def unify(self, other: Type) -> Optional[Type]:
        """Unify function types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, FunctionType):
            if len(self.param_types) != len(other.param_types):
                return None
            unified_params = []
            for a, b in zip(self.param_types, other.param_types):
                u = a.unify(b)
                if u is None:
                    return None
                unified_params.append(u)
            unified_return = self.return_type.unify(other.return_type)
            if unified_return is None:
                return None
            unified_effect = self.effect.unify(other.effect)
            return FunctionType(unified_params, unified_return, unified_effect)
        return None

    def __str__(self) -> str:
        params = ", ".join(str(t) for t in self.param_types)
        effect_str = f" {self.effect}" if self.effect and not isinstance(
            self.effect.effects[0], PureEffect) else ""
        return f"({params}) -> {self.return_type}{effect_str}"

    def __eq__(self, other) -> bool:
        return (isinstance(other, FunctionType) and
                self.param_types == other.param_types and
                self.return_type == other.return_type and
                self.effect == other.effect)

    def __hash__(self) -> int:
        return hash(('function', tuple(self.param_types),
                    self.return_type, self.effect))


# ============================================================================
# UNION AND OPTIONAL TYPES
# ============================================================================

class UnionType(Type):
    """Union type - value can be any of the constituent types."""

    def __init__(self, types: List[Type]):
        super().__init__(kind=TypeKind.UNION, name="Union")
        # Flatten nested unions and remove duplicates
        self.types = set()
        for t in types:
            if isinstance(t, UnionType):
                self.types.update(t.types)
            else:
                self.types.add(t)

    def is_subtype_of(self, other: Type) -> bool:
        """Union is subtype if all members are subtypes."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, UnionType):
            return all(any(a.is_subtype_of(b) for b in other.types)
                      for a in self.types)
        return all(t.is_subtype_of(other) for t in self.types)

    def unify(self, other: Type) -> Optional[Type]:
        """Unify union types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, UnionType):
            # Union of unions
            return UnionType(list(self.types) + list(other.types))
        # Add other to union
        return UnionType(list(self.types) + [other])

    def __str__(self) -> str:
        type_strs = sorted(str(t) for t in self.types)
        return " | ".join(type_strs)

    def __eq__(self, other) -> bool:
        return isinstance(other, UnionType) and self.types == other.types

    def __hash__(self) -> int:
        return hash(('union', frozenset(self.types)))


def Optional(t: Type) -> UnionType:
    """Create an optional type (Union with VOID)."""
    return UnionType([t, VOID])


# ============================================================================
# TYPE VARIABLES AND GENERICS
# ============================================================================

class TypeVariable(Type):
    """Type variable for generic types and inference."""

    def __init__(self, name: str, constraints: List[Type] = None,
                 bound: Type = None):
        super().__init__(kind=TypeKind.GENERIC, name=name)
        self.constraints = constraints or []
        self.bound = bound

    def is_subtype_of(self, other: Type) -> bool:
        """Type variable subtyping based on bound."""
        if isinstance(other, AnyType):
            return True
        if self.bound:
            return self.bound.is_subtype_of(other)
        return isinstance(other, TypeVariable) and self.name == other.name

    def unify(self, other: Type) -> Optional[Type]:
        """Unification with type variable."""
        if isinstance(other, TypeVariable):
            # Both are variables - create constraint
            if self.name == other.name:
                return self
            # Choose one as representative
            return self
        # Bind variable to concrete type
        if self.bound:
            return self.bound.unify(other)
        if self.constraints:
            # Check if other satisfies constraints
            if all(other.is_subtype_of(c) for c in self.constraints):
                return other
            return None
        return other

    def __str__(self) -> str:
        if self.bound:
            return f"{self.name} <: {self.bound}"
        if self.constraints:
            constraints_str = ", ".join(str(c) for c in self.constraints)
            return f"{self.name}[{constraints_str}]"
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, TypeVariable) and self.name == other.name

    def __hash__(self) -> int:
        return hash(('typevar', self.name))


# ============================================================================
# DEPENDENT TYPES
# ============================================================================

class DependentType(Type):
    """Dependent type - type that depends on a value.

    Examples:
    - Vector<n> where n is a value
    - Array<T, n> where n is the length
    - Range<min, max> where min and max are values
    """

    def __init__(self, base_type: Type, dependencies: Dict[str, Any],
                 constraint: Optional[Callable[[Dict[str, Any]], bool]] = None):
        name = f"{base_type.name}<{', '.join(f'{k}={v}' for k, v in dependencies.items())}>"
        super().__init__(kind=TypeKind.DEPENDENT, name=name)
        self.base_type = base_type
        self.dependencies = dependencies
        self.constraint = constraint

    def is_subtype_of(self, other: Type) -> bool:
        """Dependent type subtyping."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, DependentType):
            # Base types must match
            if not self.base_type.is_subtype_of(other.base_type):
                return False
            # Dependencies must be compatible
            for key in other.dependencies:
                if key not in self.dependencies:
                    return False
                if self.dependencies[key] != other.dependencies[key]:
                    return False
            return True
        # Can be subtype of non-dependent type
        return self.base_type.is_subtype_of(other)

    def unify(self, other: Type) -> Optional[Type]:
        """Unify dependent types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, DependentType):
            unified_base = self.base_type.unify(other.base_type)
            if not unified_base:
                return None
            # Merge dependencies
            merged_deps = {**self.dependencies, **other.dependencies}
            # Check for conflicts
            for key in self.dependencies:
                if key in other.dependencies:
                    if self.dependencies[key] != other.dependencies[key]:
                        return None
            return DependentType(unified_base, merged_deps, self.constraint)
        return None

    def check_constraint(self) -> bool:
        """Check if the constraint is satisfied."""
        if self.constraint:
            return self.constraint(self.dependencies)
        return True

    def __str__(self) -> str:
        deps = ", ".join(f"{k}={v}" for k, v in self.dependencies.items())
        return f"{self.base_type}<{deps}>"

    def __eq__(self, other) -> bool:
        return (isinstance(other, DependentType) and
                self.base_type == other.base_type and
                self.dependencies == other.dependencies)

    def __hash__(self) -> int:
        deps_tuple = tuple(sorted(self.dependencies.items()))
        return hash(('dependent', self.base_type, deps_tuple))


def Vector(element_type: Type, length: int) -> DependentType:
    """Create a vector type with fixed length."""
    return DependentType(
        ListType(element_type),
        {"length": length},
        lambda deps: deps["length"] >= 0
    )


def Range(min_val: int, max_val: int) -> DependentType:
    """Create a range type with min and max bounds."""
    return DependentType(
        NUMB,
        {"min": min_val, "max": max_val},
        lambda deps: deps["min"] <= deps["max"]
    )


# ============================================================================
# LINEAR TYPES (OWNERSHIP)
# ============================================================================

class OwnershipKind(Enum):
    """Ownership modes for linear types."""
    OWNED = auto()      # Full ownership
    BORROWED = auto()   # Immutable borrow
    MUT_BORROWED = auto()  # Mutable borrow
    MOVED = auto()      # Value has been moved


class Lifetime:
    """Lifetime annotation for borrowed types."""

    def __init__(self, name: str, scope_id: int):
        self.name = name
        self.scope_id = scope_id

    def __str__(self) -> str:
        return f"'{self.name}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Lifetime) and self.name == other.name

    def __hash__(self) -> int:
        return hash(('lifetime', self.name))


class LinearType(Type):
    """Linear type with ownership tracking.

    Inspired by Rust's ownership system:
    - Values have a single owner
    - Values can be borrowed immutably (multiple) or mutably (exclusive)
    - Lifetimes track borrow validity
    """

    def __init__(self, inner_type: Type, ownership: OwnershipKind,
                 lifetime: Optional[Lifetime] = None):
        super().__init__(kind=TypeKind.LINEAR, name=f"Linear<{inner_type}>")
        self.inner_type = inner_type
        self.ownership = ownership
        self.lifetime = lifetime

    def is_subtype_of(self, other: Type) -> bool:
        """Linear type subtyping."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, LinearType):
            # Inner types must be compatible
            if not self.inner_type.is_subtype_of(other.inner_type):
                return False
            # Ownership compatibility
            if self.ownership == OwnershipKind.MOVED:
                return False  # Moved values can't be used
            # Borrowed can be used where owned is expected (copy)
            return True
        return False

    def unify(self, other: Type) -> Optional[Type]:
        """Unify linear types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, LinearType):
            unified_inner = self.inner_type.unify(other.inner_type)
            if not unified_inner:
                return None
            # Choose stricter ownership
            ownership = self.ownership
            if other.ownership == OwnershipKind.MOVED:
                ownership = OwnershipKind.MOVED
            return LinearType(unified_inner, ownership, self.lifetime)
        return None

    def move(self) -> LinearType:
        """Mark this type as moved."""
        return LinearType(self.inner_type, OwnershipKind.MOVED, self.lifetime)

    def borrow(self, lifetime: Lifetime) -> LinearType:
        """Create an immutable borrow."""
        if self.ownership == OwnershipKind.MOVED:
            raise TypeError("Cannot borrow moved value")
        return LinearType(self.inner_type, OwnershipKind.BORROWED, lifetime)

    def borrow_mut(self, lifetime: Lifetime) -> LinearType:
        """Create a mutable borrow."""
        if self.ownership == OwnershipKind.MOVED:
            raise TypeError("Cannot borrow moved value")
        if self.ownership in (OwnershipKind.BORROWED, OwnershipKind.MUT_BORROWED):
            raise TypeError("Cannot create mutable borrow while borrowed")
        return LinearType(self.inner_type, OwnershipKind.MUT_BORROWED, lifetime)

    def __str__(self) -> str:
        ownership_str = {
            OwnershipKind.OWNED: "",
            OwnershipKind.BORROWED: "&",
            OwnershipKind.MUT_BORROWED: "&mut ",
            OwnershipKind.MOVED: "moved "
        }[self.ownership]
        lifetime_str = str(self.lifetime) + " " if self.lifetime else ""
        return f"{ownership_str}{lifetime_str}{self.inner_type}"

    def __eq__(self, other) -> bool:
        return (isinstance(other, LinearType) and
                self.inner_type == other.inner_type and
                self.ownership == other.ownership)

    def __hash__(self) -> int:
        return hash(('linear', self.inner_type, self.ownership))


class OwnershipChecker:
    """Tracks ownership and borrowing during type checking."""

    def __init__(self):
        self.owned_vars: Dict[str, LinearType] = {}
        self.borrows: Dict[str, List[Tuple[LinearType, int]]] = defaultdict(list)
        self.current_scope: int = 0
        self.scope_stack: List[int] = [0]

    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope += 1
        self.scope_stack.append(self.current_scope)

    def exit_scope(self):
        """Exit current scope and invalidate borrows."""
        scope = self.scope_stack.pop()
        # Remove borrows from this scope
        for var, borrows in self.borrows.items():
            self.borrows[var] = [(t, s) for t, s in borrows if s != scope]

    def declare_owned(self, var: str, typ: LinearType):
        """Declare a new owned variable."""
        if typ.ownership != OwnershipKind.OWNED:
            raise TypeError(f"Variable {var} must be owned")
        self.owned_vars[var] = typ

    def move_var(self, var: str) -> LinearType:
        """Move ownership of a variable."""
        if var not in self.owned_vars:
            raise TypeError(f"Variable {var} not found")
        typ = self.owned_vars[var]
        if typ.ownership == OwnershipKind.MOVED:
            raise TypeError(f"Value {var} has been moved")
        # Check for active borrows
        if var in self.borrows and self.borrows[var]:
            raise TypeError(f"Cannot move {var} while borrowed")
        # Mark as moved
        self.owned_vars[var] = typ.move()
        return typ

    def borrow_var(self, var: str, lifetime: Lifetime) -> LinearType:
        """Create an immutable borrow."""
        if var not in self.owned_vars:
            raise TypeError(f"Variable {var} not found")
        typ = self.owned_vars[var]
        if typ.ownership == OwnershipKind.MOVED:
            raise TypeError(f"Value {var} has been moved")
        # Check for mutable borrows
        for borrow_typ, _ in self.borrows[var]:
            if borrow_typ.ownership == OwnershipKind.MUT_BORROWED:
                raise TypeError(f"Cannot borrow {var} while mutably borrowed")
        borrowed = typ.borrow(lifetime)
        self.borrows[var].append((borrowed, self.current_scope))
        return borrowed

    def borrow_mut_var(self, var: str, lifetime: Lifetime) -> LinearType:
        """Create a mutable borrow."""
        if var not in self.owned_vars:
            raise TypeError(f"Variable {var} not found")
        typ = self.owned_vars[var]
        if typ.ownership == OwnershipKind.MOVED:
            raise TypeError(f"Value {var} has been moved")
        # Check for any active borrows
        if var in self.borrows and self.borrows[var]:
            raise TypeError(f"Cannot mutably borrow {var} while borrowed")
        borrowed = typ.borrow_mut(lifetime)
        self.borrows[var].append((borrowed, self.current_scope))
        return borrowed


# ============================================================================
# EFFECT SYSTEM
# ============================================================================

class EffectKind(Enum):
    """Categories of effects."""
    PURE = auto()       # No side effects
    IO = auto()         # Input/output
    STATE = auto()      # Mutable state
    EXCEPTION = auto()  # Can throw exceptions
    DIVERGE = auto()    # May not terminate
    ASYNC = auto()      # Asynchronous/concurrent


@dataclass
class Effect(ABC):
    """Base class for effects."""
    kind: EffectKind

    @abstractmethod
    def is_subeffect_of(self, other: Effect) -> bool:
        """Check if this effect is a sub-effect of another."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class PureEffect(Effect):
    """Pure computation - no side effects."""

    def __init__(self):
        super().__init__(kind=EffectKind.PURE)

    def is_subeffect_of(self, other: Effect) -> bool:
        """Pure is a sub-effect of everything."""
        return True

    def __str__(self) -> str:
        return "Pure"

    def __eq__(self, other) -> bool:
        return isinstance(other, PureEffect)

    def __hash__(self) -> int:
        return hash('pure')


@dataclass
class IOEffect(Effect):
    """Input/output effect."""
    operations: Set[str] = field(default_factory=set)

    def __init__(self, operations: Set[str] = None):
        super().__init__(kind=EffectKind.IO)
        self.operations = operations or {"read", "write"}

    def is_subeffect_of(self, other: Effect) -> bool:
        """IO effect subtyping."""
        if isinstance(other, IOEffect):
            return self.operations.issubset(other.operations)
        return False

    def __str__(self) -> str:
        ops = ", ".join(sorted(self.operations))
        return f"IO[{ops}]"

    def __eq__(self, other) -> bool:
        return isinstance(other, IOEffect) and self.operations == other.operations

    def __hash__(self) -> int:
        return hash(('io', frozenset(self.operations)))


@dataclass
class StateEffect(Effect):
    """Mutable state effect."""
    state_vars: Set[str] = field(default_factory=set)

    def __init__(self, state_vars: Set[str] = None):
        super().__init__(kind=EffectKind.STATE)
        self.state_vars = state_vars or set()

    def is_subeffect_of(self, other: Effect) -> bool:
        """State effect subtyping."""
        if isinstance(other, StateEffect):
            return self.state_vars.issubset(other.state_vars)
        return False

    def __str__(self) -> str:
        if self.state_vars:
            vars_str = ", ".join(sorted(self.state_vars))
            return f"State[{vars_str}]"
        return "State"

    def __eq__(self, other) -> bool:
        return isinstance(other, StateEffect) and self.state_vars == other.state_vars

    def __hash__(self) -> int:
        return hash(('state', frozenset(self.state_vars)))


@dataclass
class ExceptionEffect(Effect):
    """Exception/error effect."""
    exception_types: Set[str] = field(default_factory=set)

    def __init__(self, exception_types: Set[str] = None):
        super().__init__(kind=EffectKind.EXCEPTION)
        self.exception_types = exception_types or set()

    def is_subeffect_of(self, other: Effect) -> bool:
        """Exception effect subtyping."""
        if isinstance(other, ExceptionEffect):
            return self.exception_types.issubset(other.exception_types)
        return False

    def __str__(self) -> str:
        if self.exception_types:
            types_str = ", ".join(sorted(self.exception_types))
            return f"Exception[{types_str}]"
        return "Exception"

    def __eq__(self, other) -> bool:
        return (isinstance(other, ExceptionEffect) and
                self.exception_types == other.exception_types)

    def __hash__(self) -> int:
        return hash(('exception', frozenset(self.exception_types)))


class EffectType(Type):
    """Effect type - set of effects."""

    def __init__(self, effects: List[Effect]):
        super().__init__(kind=TypeKind.EFFECT, name="Effect")
        # Deduplicate and simplify
        self.effects = self._simplify(effects)

    def _simplify(self, effects: List[Effect]) -> List[Effect]:
        """Simplify effect list."""
        if not effects:
            return [PureEffect()]
        # Remove duplicates
        unique = []
        seen = set()
        for eff in effects:
            key = (type(eff).__name__, str(eff))
            if key not in seen:
                seen.add(key)
                unique.append(eff)
        # If pure is present with other effects, remove pure
        if len(unique) > 1 and any(isinstance(e, PureEffect) for e in unique):
            unique = [e for e in unique if not isinstance(e, PureEffect)]
        return unique

    def is_subtype_of(self, other: Type) -> bool:
        """Effect subtyping - fewer effects is subtype."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, EffectType):
            # All our effects must be sub-effects of some effect in other
            return all(any(e1.is_subeffect_of(e2) for e2 in other.effects)
                      for e1 in self.effects)
        return False

    def unify(self, other: Type) -> Optional[Type]:
        """Unify effect types - union of effects."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, EffectType):
            return EffectType(self.effects + other.effects)
        return None

    def add_effect(self, effect: Effect) -> EffectType:
        """Add an effect to this effect type."""
        return EffectType(self.effects + [effect])

    def is_pure(self) -> bool:
        """Check if this effect is pure."""
        return len(self.effects) == 1 and isinstance(self.effects[0], PureEffect)

    def __str__(self) -> str:
        if self.is_pure():
            return "Pure"
        effects_str = " + ".join(str(e) for e in self.effects)
        return f"<{effects_str}>"

    def __eq__(self, other) -> bool:
        return isinstance(other, EffectType) and self.effects == other.effects

    def __hash__(self) -> int:
        return hash(('effect', tuple(self.effects)))


# ============================================================================
# REFINEMENT TYPES
# ============================================================================

class Predicate:
    """Predicate for refinement types."""

    def __init__(self, name: str, checker: Callable[[Any], bool], description: str = ""):
        self.name = name
        self.checker = checker
        self.description = description

    def check(self, value: Any) -> bool:
        """Check if value satisfies predicate."""
        try:
            return self.checker(value)
        except:
            return False

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Predicate) and self.name == other.name

    def __hash__(self) -> int:
        return hash(('predicate', self.name))


class RefinementType(Type):
    """Refinement type - type with predicates.

    Examples:
    - PositiveInt = {x: Int | x > 0}
    - NonEmptyString = {s: String | len(s) > 0}
    - EvenNumber = {n: Int | n % 2 == 0}
    """

    def __init__(self, base_type: Type, variable: str, predicates: List[Predicate]):
        super().__init__(kind=TypeKind.REFINEMENT, name=f"Refined<{base_type}>")
        self.base_type = base_type
        self.variable = variable
        self.predicates = predicates

    def is_subtype_of(self, other: Type) -> bool:
        """Refinement type subtyping."""
        if isinstance(other, AnyType):
            return True
        if isinstance(other, RefinementType):
            # Base types must be compatible
            if not self.base_type.is_subtype_of(other.base_type):
                return False
            # Our predicates must imply other's predicates
            # For now, just check if we have all of other's predicates
            return all(p in self.predicates for p in other.predicates)
        # Refinement is subtype of its base
        return self.base_type.is_subtype_of(other)

    def unify(self, other: Type) -> Optional[Type]:
        """Unify refinement types."""
        if isinstance(other, AnyType):
            return self
        if isinstance(other, RefinementType):
            unified_base = self.base_type.unify(other.base_type)
            if not unified_base:
                return None
            # Combine predicates
            all_predicates = self.predicates + other.predicates
            # Remove duplicates
            unique_preds = []
            seen = set()
            for p in all_predicates:
                if p.name not in seen:
                    seen.add(p.name)
                    unique_preds.append(p)
            return RefinementType(unified_base, self.variable, unique_preds)
        return None

    def check_value(self, value: Any) -> bool:
        """Check if a value satisfies all predicates."""
        return all(pred.check(value) for pred in self.predicates)

    def __str__(self) -> str:
        preds = " ∧ ".join(str(p) for p in self.predicates)
        return f"{{{self.variable}: {self.base_type} | {preds}}}"

    def __eq__(self, other) -> bool:
        return (isinstance(other, RefinementType) and
                self.base_type == other.base_type and
                self.variable == other.variable and
                self.predicates == other.predicates)

    def __hash__(self) -> int:
        return hash(('refinement', self.base_type, self.variable,
                    tuple(self.predicates)))


# Common refinement predicates
POSITIVE = Predicate("positive", lambda x: x > 0, "Greater than zero")
NEGATIVE = Predicate("negative", lambda x: x < 0, "Less than zero")
NON_ZERO = Predicate("non_zero", lambda x: x != 0, "Not equal to zero")
EVEN = Predicate("even", lambda x: x % 2 == 0, "Even number")
ODD = Predicate("odd", lambda x: x % 2 != 0, "Odd number")
NON_EMPTY = Predicate("non_empty", lambda x: len(x) > 0, "Non-empty collection")


def PositiveInt() -> RefinementType:
    """Create a positive integer refinement type."""
    return RefinementType(NUMB, "x", [POSITIVE])


def NegativeInt() -> RefinementType:
    """Create a negative integer refinement type."""
    return RefinementType(NUMB, "x", [NEGATIVE])


def NonZeroInt() -> RefinementType:
    """Create a non-zero integer refinement type."""
    return RefinementType(NUMB, "x", [NON_ZERO])


def EvenInt() -> RefinementType:
    """Create an even integer refinement type."""
    return RefinementType(NUMB, "x", [EVEN])


def NonEmptyString() -> RefinementType:
    """Create a non-empty string refinement type."""
    return RefinementType(WHISPER, "s", [NON_EMPTY])


def NonEmptyList(element_type: Type) -> RefinementType:
    """Create a non-empty list refinement type."""
    return RefinementType(ListType(element_type), "l", [NON_EMPTY])


# ============================================================================
# TYPE CHECKER
# ============================================================================

@dataclass
class TypeError(Exception):
    """Type error exception."""
    message: str
    location: Optional[Tuple[int, int]] = None

    def __str__(self) -> str:
        if self.location:
            return f"Type Error at {self.location}: {self.message}"
        return f"Type Error: {self.message}"


class TypeEnvironment:
    """Type environment for type checking."""

    def __init__(self, parent: Optional[TypeEnvironment] = None):
        self.parent = parent
        self.vars: Dict[str, Type] = {}
        self.type_vars: Dict[str, TypeVariable] = {}

    def bind(self, name: str, typ: Type):
        """Bind a variable to a type."""
        self.vars[name] = typ

    def lookup(self, name: str) -> Optional[Type]:
        """Look up a variable's type."""
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def bind_type_var(self, name: str, var: TypeVariable):
        """Bind a type variable."""
        self.type_vars[name] = var

    def lookup_type_var(self, name: str) -> Optional[TypeVariable]:
        """Look up a type variable."""
        if name in self.type_vars:
            return self.type_vars[name]
        if self.parent:
            return self.parent.lookup_type_var(name)
        return None

    def child(self) -> TypeEnvironment:
        """Create a child environment."""
        return TypeEnvironment(parent=self)


class TypeChecker:
    """Type checker with inference for Lament.

    Features:
    - Type inference for expressions
    - Gradual typing (can mix typed and untyped code)
    - Dependent type checking
    - Linear type checking (ownership)
    - Effect checking
    - Refinement type checking
    """

    def __init__(self):
        self.env = TypeEnvironment()
        self.ownership_checker = OwnershipChecker()
        self.current_effect = EffectType([PureEffect()])
        self.errors: List[TypeError] = []
        self.warnings: List[str] = []
        self._next_type_var = 0

    def fresh_type_var(self, name: Optional[str] = None) -> TypeVariable:
        """Generate a fresh type variable."""
        if name is None:
            name = f"T{self._next_type_var}"
            self._next_type_var += 1
        return TypeVariable(name)

    def error(self, message: str, location: Optional[Tuple[int, int]] = None):
        """Record a type error."""
        self.errors.append(TypeError(message, location))

    def warn(self, message: str):
        """Record a warning."""
        self.warnings.append(message)

    def check_type(self, expr: Any, expected: Type) -> bool:
        """Check if an expression has the expected type."""
        inferred = self.infer_type(expr)
        if inferred.is_subtype_of(expected):
            return True
        self.error(f"Expected type {expected}, got {inferred}")
        return False

    def infer_type(self, expr: Any) -> Type:
        """Infer the type of an expression.

        This is a simplified inference for demonstration.
        In a real implementation, this would handle all AST node types.
        """
        # Literals
        if isinstance(expr, int):
            return NUMB
        elif isinstance(expr, float):
            return ACHE
        elif isinstance(expr, str):
            return WHISPER
        elif isinstance(expr, bool):
            return MAYBE
        elif expr is None:
            return VOID
        elif isinstance(expr, list):
            if not expr:
                elem_type = self.fresh_type_var("T")
                return ListType(elem_type)
            elem_types = [self.infer_type(e) for e in expr]
            unified = elem_types[0]
            for t in elem_types[1:]:
                u = unified.unify(t)
                if u:
                    unified = u
                else:
                    # Fall back to Any
                    unified = AnyType()
                    break
            return ListType(unified)
        elif isinstance(expr, dict):
            if not expr:
                key_type = self.fresh_type_var("K")
                val_type = self.fresh_type_var("V")
                return DictType(key_type, val_type)
            key_types = [self.infer_type(k) for k in expr.keys()]
            val_types = [self.infer_type(v) for v in expr.values()]
            unified_key = key_types[0]
            unified_val = val_types[0]
            for t in key_types[1:]:
                u = unified_key.unify(t)
                if u:
                    unified_key = u
                else:
                    unified_key = AnyType()
                    break
            for t in val_types[1:]:
                u = unified_val.unify(t)
                if u:
                    unified_val = u
                else:
                    unified_val = AnyType()
                    break
            return DictType(unified_key, unified_val)
        else:
            # Unknown type - return Any
            return AnyType()

    def check_dependent_type(self, typ: DependentType, value: Any) -> bool:
        """Check a dependent type constraint."""
        if not typ.check_constraint():
            self.error(f"Dependent type constraint failed: {typ}")
            return False
        return True

    def check_refinement_type(self, typ: RefinementType, value: Any) -> bool:
        """Check a refinement type predicate."""
        if not typ.check_value(value):
            failed = [p.name for p in typ.predicates if not p.check(value)]
            self.error(f"Refinement type check failed: {typ}, "
                      f"predicates {failed} not satisfied")
            return False
        return True

    def check_linear_type(self, var: str, typ: LinearType) -> bool:
        """Check linear type ownership."""
        try:
            # This would integrate with the ownership checker
            return True
        except Exception as e:
            self.error(f"Linear type check failed: {e}")
            return False

    def check_effect(self, required: EffectType) -> bool:
        """Check if current effect permits required effect."""
        if not required.is_subtype_of(self.current_effect):
            self.error(f"Effect {required} not permitted in {self.current_effect}")
            return False
        return True

    def with_effect(self, effect: EffectType):
        """Context manager for checking code with specific effect."""
        class EffectContext:
            def __init__(ctx_self, checker, eff):
                ctx_self.checker = checker
                ctx_self.new_effect = eff
                ctx_self.old_effect = None

            def __enter__(ctx_self):
                ctx_self.old_effect = ctx_self.checker.current_effect
                ctx_self.checker.current_effect = ctx_self.new_effect
                return ctx_self

            def __exit__(ctx_self, *args):
                ctx_self.checker.current_effect = ctx_self.old_effect

        return EffectContext(self, effect)

    def subst_type_var(self, typ: Type, substitutions: Dict[str, Type]) -> Type:
        """Substitute type variables in a type."""
        if isinstance(typ, TypeVariable):
            if typ.name in substitutions:
                return substitutions[typ.name]
            return typ
        elif isinstance(typ, ListType):
            return ListType(self.subst_type_var(typ.element_type, substitutions))
        elif isinstance(typ, DictType):
            return DictType(
                self.subst_type_var(typ.key_type, substitutions),
                self.subst_type_var(typ.value_type, substitutions)
            )
        elif isinstance(typ, FunctionType):
            return FunctionType(
                [self.subst_type_var(t, substitutions) for t in typ.param_types],
                self.subst_type_var(typ.return_type, substitutions),
                typ.effect
            )
        elif isinstance(typ, UnionType):
            return UnionType([self.subst_type_var(t, substitutions)
                            for t in typ.types])
        else:
            return typ

    def generalize(self, typ: Type) -> Type:
        """Generalize a type by quantifying free type variables."""
        # Collect free type variables
        free_vars = self._collect_type_vars(typ)
        if not free_vars:
            return typ
        # In a full implementation, would create a polymorphic type
        return typ

    def _collect_type_vars(self, typ: Type) -> Set[TypeVariable]:
        """Collect all type variables in a type."""
        if isinstance(typ, TypeVariable):
            return {typ}
        elif isinstance(typ, ListType):
            return self._collect_type_vars(typ.element_type)
        elif isinstance(typ, DictType):
            return (self._collect_type_vars(typ.key_type) |
                   self._collect_type_vars(typ.value_type))
        elif isinstance(typ, FunctionType):
            result = set()
            for pt in typ.param_types:
                result |= self._collect_type_vars(pt)
            result |= self._collect_type_vars(typ.return_type)
            return result
        elif isinstance(typ, UnionType):
            result = set()
            for t in typ.types:
                result |= self._collect_type_vars(t)
            return result
        else:
            return set()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_type_annotation(annotation: str) -> Type:
    """Parse a type annotation string into a Type object.

    Examples:
    - "numb" -> NUMB
    - "List<numb>" -> ListType(NUMB)
    - "numb | void" -> UnionType([NUMB, VOID])
    - "{x: numb | x > 0}" -> PositiveInt()
    """
    annotation = annotation.strip()

    # Handle union types
    if "|" in annotation and not annotation.startswith("{"):
        parts = [parse_type_annotation(p.strip()) for p in annotation.split("|")]
        return UnionType(parts)

    # Handle list types
    if annotation.startswith("List<") and annotation.endswith(">"):
        inner = annotation[5:-1]
        elem_type = parse_type_annotation(inner)
        return ListType(elem_type)

    # Handle dict types
    if annotation.startswith("Dict<") and annotation.endswith(">"):
        inner = annotation[5:-1]
        key_str, val_str = inner.split(",", 1)
        key_type = parse_type_annotation(key_str.strip())
        val_type = parse_type_annotation(val_str.strip())
        return DictType(key_type, val_type)

    # Handle primitive types
    type_map = {
        "numb": NUMB,
        "whisper": WHISPER,
        "maybe": MAYBE,
        "void": VOID,
        "ache": ACHE,
        "Any": AnyType(),
        "Never": NeverType()
    }

    if annotation in type_map:
        return type_map[annotation]

    # Default to Any
    return AnyType()


def format_type(typ: Type) -> str:
    """Format a type for display."""
    return str(typ)


def are_types_compatible(t1: Type, t2: Type) -> bool:
    """Check if two types are compatible (can be unified)."""
    return t1.unify(t2) is not None


def least_upper_bound(types: List[Type]) -> Type:
    """Find the least upper bound (join) of multiple types."""
    if not types:
        return NeverType()
    if len(types) == 1:
        return types[0]

    # Try to unify all types
    result = types[0]
    for t in types[1:]:
        unified = result.unify(t)
        if unified:
            result = unified
        else:
            # Can't unify - create union
            return UnionType(types)
    return result


# ============================================================================
# EXAMPLE USAGE AND DEMOS
# ============================================================================

def demo_gradual_typing():
    """Demonstrate gradual typing with inference."""
    print("=" * 60)
    print("DEMO: Gradual Typing")
    print("=" * 60)

    checker = TypeChecker()

    # Infer types from literals
    print("\n1. Type Inference:")
    print(f"   5 : {checker.infer_type(5)}")
    print(f"   'hello' : {checker.infer_type('hello')}")
    print(f"   [1, 2, 3] : {checker.infer_type([1, 2, 3])}")
    print(f"   {{'a': 1}} : {checker.infer_type({'a': 1})}")

    # Optional types
    print("\n2. Optional Types:")
    opt_numb = Optional(NUMB)
    print(f"   Optional<numb> = {opt_numb}")
    print(f"   5 : Optional<numb> = {NUMB.is_subtype_of(opt_numb)}")
    print(f"   void : Optional<numb> = {VOID.is_subtype_of(opt_numb)}")

    # Union types
    print("\n3. Union Types:")
    union = UnionType([NUMB, WHISPER])
    print(f"   numb | whisper = {union}")
    print(f"   5 fits: {NUMB.is_subtype_of(union)}")
    print(f"   'hi' fits: {WHISPER.is_subtype_of(union)}")


def demo_dependent_types():
    """Demonstrate dependent types."""
    print("\n" + "=" * 60)
    print("DEMO: Dependent Types")
    print("=" * 60)

    # Vector with length
    print("\n1. Vector Types:")
    vec3 = Vector(NUMB, 3)
    vec5 = Vector(NUMB, 5)
    print(f"   Vector<numb, 3> = {vec3}")
    print(f"   Vector<numb, 5> = {vec5}")
    print(f"   Constraint valid: {vec3.check_constraint()}")

    # Range type
    print("\n2. Range Types:")
    range_type = Range(0, 10)
    print(f"   Range<0, 10> = {range_type}")
    print(f"   Constraint valid: {range_type.check_constraint()}")

    # Invalid range
    invalid_range = Range(10, 5)
    print(f"   Range<10, 5> = {invalid_range}")
    print(f"   Constraint valid: {invalid_range.check_constraint()}")


def demo_linear_types():
    """Demonstrate linear types and ownership."""
    print("\n" + "=" * 60)
    print("DEMO: Linear Types (Ownership)")
    print("=" * 60)

    print("\n1. Ownership Types:")
    owned = LinearType(WHISPER, OwnershipKind.OWNED)
    print(f"   Owned: {owned}")

    lifetime = Lifetime("a", 0)
    borrowed = owned.borrow(lifetime)
    print(f"   Borrowed: {borrowed}")

    mut_borrowed = LinearType(NUMB, OwnershipKind.OWNED).borrow_mut(lifetime)
    print(f"   Mut Borrowed: {mut_borrowed}")

    print("\n2. Ownership Checking:")
    checker = OwnershipChecker()

    # Declare owned variable
    string_type = LinearType(WHISPER, OwnershipKind.OWNED)
    checker.declare_owned("name", string_type)
    print("   Declared: name: owned whisper")

    # Borrow it
    try:
        borrow = checker.borrow_var("name", lifetime)
        print(f"   Borrowed: {borrow}")
    except Exception as e:
        print(f"   Error: {e}")

    # Try to move while borrowed
    checker.exit_scope()  # End borrow scope
    try:
        moved = checker.move_var("name")
        print(f"   Moved: {moved}")
    except Exception as e:
        print(f"   Error: {e}")


def demo_effect_system():
    """Demonstrate effect system."""
    print("\n" + "=" * 60)
    print("DEMO: Effect System")
    print("=" * 60)

    print("\n1. Effect Types:")
    pure = EffectType([PureEffect()])
    print(f"   Pure: {pure}")

    io = EffectType([IOEffect({"read", "write"})])
    print(f"   IO: {io}")

    state = EffectType([StateEffect({"counter"})])
    print(f"   State: {state}")

    combined = EffectType([IOEffect({"read"}), StateEffect({"x", "y"})])
    print(f"   Combined: {combined}")

    print("\n2. Effect Subtyping:")
    print(f"   Pure <: IO? {pure.is_subtype_of(io)}")
    print(f"   IO <: Pure? {io.is_subtype_of(pure)}")

    io_read = EffectType([IOEffect({"read"})])
    print(f"   IO[read] <: IO[read,write]? {io_read.is_subtype_of(io)}")

    print("\n3. Function Types with Effects:")
    pure_func = FunctionType([NUMB, NUMB], NUMB, pure)
    print(f"   Pure function: {pure_func}")

    io_func = FunctionType([WHISPER], VOID, io)
    print(f"   IO function: {io_func}")


def demo_refinement_types():
    """Demonstrate refinement types."""
    print("\n" + "=" * 60)
    print("DEMO: Refinement Types")
    print("=" * 60)

    print("\n1. Refinement Type Definitions:")
    pos_int = PositiveInt()
    print(f"   PositiveInt: {pos_int}")

    even_int = EvenInt()
    print(f"   EvenInt: {even_int}")

    non_empty_str = NonEmptyString()
    print(f"   NonEmptyString: {non_empty_str}")

    print("\n2. Predicate Checking:")
    print(f"   5 : PositiveInt? {pos_int.check_value(5)}")
    print(f"   -3 : PositiveInt? {pos_int.check_value(-3)}")
    print(f"   4 : EvenInt? {even_int.check_value(4)}")
    print(f"   7 : EvenInt? {even_int.check_value(7)}")
    print(f"   'hi' : NonEmptyString? {non_empty_str.check_value('hi')}")
    print(f"   '' : NonEmptyString? {non_empty_str.check_value('')}")

    print("\n3. Combined Refinements:")
    pos_even = RefinementType(NUMB, "x", [POSITIVE, EVEN])
    print(f"   PositiveEvenInt: {pos_even}")
    print(f"   4 : PositiveEvenInt? {pos_even.check_value(4)}")
    print(f"   3 : PositiveEvenInt? {pos_even.check_value(3)}")
    print(f"   -4 : PositiveEvenInt? {pos_even.check_value(-4)}")


def demo_type_inference():
    """Demonstrate type inference."""
    print("\n" + "=" * 60)
    print("DEMO: Type Inference")
    print("=" * 60)

    checker = TypeChecker()

    print("\n1. Literal Inference:")
    values = [42, 3.14, "hello", True, None, [1, 2, 3], {"a": 1}]
    for val in values:
        typ = checker.infer_type(val)
        print(f"   {repr(val)} : {typ}")

    print("\n2. Type Unification:")
    t1 = ListType(NUMB)
    t2 = ListType(NUMB)
    unified = t1.unify(t2)
    print(f"   {t1} ∪ {t2} = {unified}")

    t3 = ListType(TypeVariable("T"))
    t4 = ListType(WHISPER)
    unified = t3.unify(t4)
    print(f"   {t3} ∪ {t4} = {unified}")

    print("\n3. Type Variables:")
    tv = TypeVariable("T")
    print(f"   Type variable: {tv}")
    bound = tv.unify(NUMB)
    print(f"   After binding to numb: {bound}")


def run_all_demos():
    """Run all type system demos."""
    demo_gradual_typing()
    demo_dependent_types()
    demo_linear_types()
    demo_effect_system()
    demo_refinement_types()
    demo_type_inference()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    run_all_demos()
