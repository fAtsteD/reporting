---
name: python-code
description: "BLOCKING: Must be invoked BEFORE writing, editing, or reviewing ANY Python code. Enforces the project's Python code style rules. Applies rules for typing, imports, naming, ordering, block spacing, comments, and tests."
version: 1.0.6
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

**Widely recognized abbreviations** (e.g., `url`, `api`, `http`, `db`, `id`) are acceptable as-is. **Custom abbreviations** (ones you invent because the original name is too long) are a last resort — prefer the full name first and only abbreviate when it is unreasonably long.

## Ordering

**A library-defined layout wins** over tier, visibility, and alphabetical order alike. Recognize the case by evidence, not by library name — one of these must hold:

- **Load-bearing** — the library reads, generates from, or resolves the declaration by its position.
- **Documented** — its guide, base class, or generated scaffolding shows a member layout for that kind of class.
- **Established** — the project already follows that layout consistently.
- **Required by the language** — a `@name.setter` or `@name.deleter` directly follows its `@property`; fields feeding a generated `__init__` keep that signature order, defaults last.

Apply the rules below only to the declarations the layout leaves free.

**Module level** — order by this sort key, applied in precedence order:

1. **Tier:** constants, then variables, then classes, then functions.
2. **Visibility** (within a tier): public (`name`), then protected (`_name`), then private (`__name`).
3. **Name** (within a visibility group): alphabetical.

**Class members** — order by this sort key, applied in precedence order (each level breaks ties of the one above):

1. **Tier:**
    1. Docstring
    2. Nested classes, including a library's inner configuration class
    3. Class-level constants — `UPPER_CASE`
    4. Class-level fields and annotations
    5. Constructors — `__new__`, `__init__`, `__post_init__`, in that order
    6. Other dunder / special methods — `__name__`
    7. Public members — `name`
    8. Protected members — `_name`
    9. Private, name-mangled members — `__name`
2. **Kind** (within a member tier): properties, then static methods, then class methods, then instance methods — `@property` and `@property`-like descriptors (e.g. `@cached_property`), then `@staticmethod`, then `@classmethod`, then plain methods.
3. **Name** (within a kind): alphabetical.

Visibility is the outer grouping, kind the inner one — the Python convention keeps the whole non-public block last, so the class reads as public API first, implementation after.

**Exceptions to the name sort:**

- Dunders are ordered by convention — constructors first, then the rest — not alphabetically.
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

Code must be self-documenting. A comment is allowed only in the cases below — anything else is a violation, including a comment that is accurate and useful.

**Allowed:**

- tool pragmas (`# noqa: E501`, `# type: ignore[arg-type]`, `# pragma: no cover`), on the line they affect
- the shebang of an executable script
- `# TODO: <what is missing>`, only when the user asked you to leave the work unfinished
- a docstring on a public API boundary, where the project already writes them

**Not allowed, however useful it looks:** a why, intent, or rationale note; a section banner (`# --- Parsing ---`); a note above a regular expression, a formula, an edge case, an API quirk, or a workaround; a restatement of a name, a type, or a signature; commented-out code; an `Args:` / `Returns:` block that repeats the signature.

**One line each.** If an allowed comment needs a second line, restructure the code instead.

**Write the name, not the comment.** Extract a function, name a variable, name a constant or enum member, or name the condition (`if is_retryable_failure(response):`). What does not fit a name belongs in the commit message, the pull request, or a test name.

**Before the task is complete,** re-read the lines you changed and delete every comment outside this list — the formatter and the linter do not remove them.

## Tests

A test is a contract: it states in code a promise the application makes, so that its name says which promise and a failure says which promise broke.

**CAUTION — when to write tests.** Write tests **only** when the user asks for them, or when the project already tests (a tests directory, a runner config such as `pytest.ini` or a `[tool.pytest.ini_options]` section, a test dependency in `pyproject.toml` or a dev requirements file, a CI test step). Never add a runner, a test dependency, or a first test file to a project that has none — say it is missing and let the user decide. Where tests exist they are part of the change: behavior you add or change comes with the tests that cover it, and tests for behavior you remove go with it.

### Layout

**Find the project's convention before creating anything**, in this order:

1. **The existing tests** — where they sit, and where they keep fixtures, factories, and helpers.
2. **The framework's own answer** — its documented layout, what its scaffolding generates, and what the runner config already collects.
3. **Ask, once** — when both are silent, ask the user where tests and their assets belong, propose one concrete shape, and follow that answer for the rest of the work.

Whatever the answer turns out to be, these hold:

- Levels stay separable, so one level can run on its own — by folder, suite, or marker, whichever the runner uses.
- The tests for a module are findable from its path: unit tests mirror the source tree, wherever its root is (`src/billing/invoice.py` → `.../billing/test_invoice.py`).
- Integration tests are grouped by the domain area they exercise; feature tests mirror the application's entry-point map — routes, CLI and management commands, consumers, scheduled jobs — as deep as that map really goes. A test spanning several areas or endpoints goes under the one that owns the outcome.
- Neither mirrors a single source file, so neither is named for one: the name states the behavior or flow, not the module that starts it.
- Every shared kind of test asset — canned payloads, model builders, helpers, base test cases — has one home, discovered rather than invented, and named for what it holds. Add a folder only when nothing existing fits.
- A pytest fixture in `conftest.py` is setup, not data: it wires boundary fakes and factories, while the canned data itself stays in files.

### Scope

Test each behavior at the **smallest stable boundary that owns it** — the boundary that survives a rewrite of the implementation behind it.

- **Unit** — the behavior is decided inside one module, by its own inputs.
- **Integration** — the behavior exists only where parts meet: a query, a transaction, a serialization round trip, dependency wiring.
- **Feature** — the behavior is the flow seen from outside: request in, response and side effects out.

Unit and integration tests carry the coverage; every branch, boundary, and error path is proven there. Feature tests are selective — write one when the flow itself is the promise (a critical journey, or wiring no lower level can see), never to restate what is already proven.

### Duplication

**Before writing a test, look for the one that already exists.** Duplicates enter a suite under a different name, not a different behavior, so search by the promise rather than by the file: the words of the behavior, the module or function under test, the factory or fixture it would need, the status or error it would assert.

- **The promise is already tested** — leave it; when the promise itself changed, update that test rather than adding a second one beside it.
- **A neighbouring promise is tested** — add the case to that test's `@pytest.mark.parametrize` cases, or write it in the same file, so the two stay side by side.
- **The promise is new** — write it where the tests for that behavior already live; a test filed in the wrong place is where the next duplicate comes from.

DRY governs the code under test, not the suite: repetition inside test bodies is fine, the same behavior proven twice is not.

- When a higher-level test proves the behavior, drop the lower-level test that only restates it.
- **Keep the lower-level test when it does more** — the feature test walks one path while the unit test covers the input matrix, the branches, and the failure modes; or the case is unreachable from outside.
- Two tests must never promise different outcomes for the same input. That is a contradiction in the contract — settle it in the code, not by keeping both.

### Test lifetime

Every test describes behavior the application has **now**. A test written to drive a change — the red test proving a setting is gone, a step of a migration, TDD scaffolding — has done its job when the change lands. Ask: written from scratch against today's application, would this test exist? If not, delete it with the change; tests of deleted code go in the same commit.

### Names

The name states subject, condition, and expected outcome, so a failure reads as a broken promise: `test_rejects_transfer_when_balance_is_insufficient`, not `test_transfer`, `test_transfer_fails`, or `test_bug_1234`. Name a regression test for the behavior it protects, never for the ticket or the fix, and group tests by behavior rather than by the function that implements it.

### Body

Arrange, act, assert — in that order, with **one act** and one behavior per test. Each test reads on its own, top to bottom, with no helper to chase (DAMP, not DRY), and every value in the body matters: a value the assertion depends on is written literally in the test, everything else is a factory default and never appears.

**Allowed shared code:** factories, fixtures, and a custom assertion whose name says exactly what it checks.

**Not allowed:** setup scattered across autouse fixtures and base classes until the arrange step is invisible; state shared or mutated between tests; branches and loops in a test body — `@pytest.mark.parametrize` is the one right way to remove that repetition; a helper that hides which values or assertions a test depends on.

### Assertions

Assert what the behavior promises — the returned value, the stored record, the published message, the response — and nothing nearby: not the objects around it, not a snapshot of the whole world, not internal calls. Several assertions are fine when they describe that one behavior. Verify an interaction only when the interaction **is** the behavior (a payment charged, a mail sent).

Never assert on a private function, an internal attribute, or a call order the caller cannot observe: a refactor that keeps the promise must keep the tests green.

### Fakes

Fake at **process boundaries only** — HTTP, third-party SDKs, the clock, randomness, the filesystem, queues, mail. Inside your own code use the real object; a collaborator too awkward to use for real is a design signal, not a mocking problem.

- Integration tests use the real database (a test schema, a container), not a mocked repository.
- Patch where the name is used, at the boundary — never reach into another module of your own to swap a private attribute.
- Fixtures hold the canned payloads a fake returns — minimal, and shaped like the real thing.
- Factories build models with faker for the fields the test does not care about, and explicit values for the fields it asserts on.

### Determinism

A test gives the same result on any machine, in any order, alone or in the suite. No shared state, no ordering between tests, no network, no sleeping — freeze the clock and seed randomness whenever the outcome depends on them.

### What not to test

Framework and library internals, generated code, plain configuration values, properties with no logic, private functions, and anything written only to raise a coverage number.

**Never test a third-party library, framework, or SDK** — it ships with its own suite. Test your own behavior built on top of it, and the adapter where you wrap it: the mapping applied to its output, the error raised from its failure. Unknown library behavior is learned in a scratch script, not in a test that then lives in the suite forever.

## After the change

Close every change with the steps below, in order. Both are **mandatory** — never skip either, even for a small edit, and never report the task complete before they pass.

1. **Format and lint.** Run the formatter and the linter, if the project has them, using the format and lint scripts defined in the project being modified. Fix by hand the errors the linter cannot fix itself.
2. **Run the tests.** In a project that has tests (see [Tests](#tests)), run them with the project's test script — those covering the code you changed as you work, the whole suite before you finish. The change is done only once the new behavior is proven and every old promise still holds. When a test breaks, fix the code if the behavior broke, fix the test if the promise itself changed, and say plainly when a failure comes from outside your change. A project with no tests skips this step — do not create a suite for it.

## Examples

For examples of each rule, see [references/examples.md](references/examples.md).
