---
name: python-code
description: "BLOCKING: Must be invoked BEFORE writing, editing, or reviewing ANY Python code. Enforces the project's Python code style rules. Applies rules for typing, imports, naming, ordering, block spacing, and comments."
version: 1.0.3
---

# Python Code Style

## Principles

- Apply KISS, DRY, SOLID.
- Use programming patterns appropriate to the context.

## Types

Type every function parameter and return value.

For variables, annotate only when the type is not obvious from the right-hand side — omit when the value states it, add when the intended type is wider or different.

Use built-in lowercase generics — `list[x]`, `dict[k, v]`, `tuple[x]`, `set[x]`. Do **not** import `List`, `Dict`, `Tuple`, or `Set` from `typing`.

Use `Optional[x]` from `typing` for nullable values.

## Enums

Model a fixed set of values as an enum, not repeated literals. Match the enum type to the value kind: `StrEnum` for strings, `IntEnum` for numbers, `Enum` otherwise. Name members `UPPER_CASE`.

## Models and Types

Keep types, models, enums, and data objects in dedicated modules that import only stdlib, `typing`, and other pure type modules — never services, I/O, or business logic. This keeps them free of side effects and safe to import anywhere.

## Imports

**Classes and constants** — import the name directly from its module. A public constant carries a reliable, self-describing name, so importing it directly keeps the call site readable without ambiguity.

**Functions and variables** — import the **module** that owns them and access each member as `module.member`. The call site then states where every name comes from, and members do not need to repeat their domain in their own names.

**No re-exports** — do **not** re-export or re-import names in `__init__.py` or any other file, and do **not** declare `__all__`; import each name from the module that defines it. Add a re-export or `__all__` only when it is a deliberate part of the logic (rare, e.g. a stable public API boundary).

**Avoid name conflicts** — the name a module is bound to must be unambiguous within the file. Prevent clashes at the source by naming the modules you create concisely and distinctly: add a subpackage prefix or abbreviation when a bare name would collide — e.g. `ext_client` (`ext` marks the origin, `client` is the meaningful part), not a colliding bare `client` nor a verbose `external_service_client`. Reach for an `as` alias only as a last resort, when the clash is unavoidable — typically a third-party module whose name you cannot change — and pick the alias by the same prefix/abbreviation convention. A shadowed import silently resolves to whichever name was bound last, producing hard-to-spot bugs.

## Naming

| Element                                   | Convention   |
| ----------------------------------------- | ------------ |
| Functions, methods, variables, properties | `snake_case` |
| Classes                                   | `PascalCase` |

**No one-letter or abbreviated names.** Every variable must have a descriptive name — global, local, loop, lambda, comprehension, or any other scope. There are no exceptions for loop counters, unpacking, or throwaway variables.

**No shortened forms** — write the full word (`result`, not `res`; `response`, not `resp`; `message`, not `msg`; `configuration`, not `cfg`).

**Widely recognised abbreviations** (e.g., `url`, `api`, `http`, `db`, `id`) are acceptable as-is. **Custom abbreviations** (ones you invent because the original name is too long) are a last resort — prefer the full name first and only abbreviate when it is unreasonably long.

## Ordering

**Module level** — order by this sort key, applied in precedence order:

1. **Tier:** constants, then variables, then classes, then functions.
2. **Visibility** (within a tier): public (`name`), then protected (`_name`), then private (`__name`).
3. **Name** (within a visibility group): alphabetical.

**Class members** — order by this sort key, applied in precedence order (each level breaks ties of the one above):

1. **Tier:**
   1. Class-level fields and constants
   2. Dunder / special methods — `__name__`
   3. Public members — `name`
   4. Protected members — `_name`
   5. Private, name-mangled members — `__name`
2. **Kind** (within a tier): properties before regular methods — `@property` and `@property`-like descriptors (e.g. `@cached_property`) come before plain methods.
3. **Name** (within a kind): alphabetical.

**Exceptions to the name sort:**

- Dunders are ordered by convention — `__init__` first, then the rest — not alphabetically.
- Don't confuse the dunder tier (`__name__`) with the private name-mangled tier (`__name`); the latter sorts last.

**Break the order when a definition must precede its use** — if a name has to be defined before another name that references it at module load time (e.g. a value used as a default argument or a decorator), place it above regardless of tier or alphabetical position.

## Block Spacing

Add an empty line **before and after** `if`, `for`, `while`, `try`, `with`, and other logical block structures to visually separate areas of different responsibility.

Do **not** add empty lines between plain sequential statements (assignments, function calls, returns) that have no block structures between them.

**Exceptions** — omit the empty lines when:

- the block is a single-line guard or trivial early return inside a very simple function
- the surrounding context makes an extra blank line noisy (e.g., the block is the only statement in the function body)

## Conditions

Use a truthiness check (`if variable:` / `if not variable:`) when you only need to know a value is present. Reserve `is None` / `is not None` for when the distinction between `None` and other falsy values (`0`, `""`, `[]`) actually matters.

## Comments

Do **not** write comments that explain or describe what the code does. Code must be self-documenting through clear naming.

## Formatting

**IMPORTANT:** After writing or modifying any Python code, you **MUST** run the formatter and linter, if available, before considering the task complete. Use the format and lint scripts defined in the project being modified.

This is a **mandatory** step — never skip it, even for small changes.

## Examples

For examples of each rule, see [references/examples.md](references/examples.md).
