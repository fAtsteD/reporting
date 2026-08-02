# Code Style Examples

## Types

**Correct** — parameters and return typed; variables annotated only when the type is not obvious from the value:

```python
from typing import Optional


def find_order(order_id: str, include_items: bool = False) -> Optional[Order]:
    order: Optional[Order] = repository.find_by_id(order_id)  # annotated: value is Order, intent is Optional[Order]
    items: list[Item] = order.items if order else []  # annotated: [] alone does not state list[Item]
    fallback = Order.empty()  # obvious from right-hand side — no annotation
    label = "pending"  # obvious from right-hand side — no annotation
    return order
```

**Incorrect** — `List`/`Dict` imported from `typing`, missing parameter/return types, redundant annotations, one-letter variable:

```python
from typing import List, Dict, Optional


def find_order(order_id, include_items=False):  # missing parameter and return types
    o = repository.find_by_id(order_id)  # one-letter name
    fallback: Order = Order.empty()  # redundant — type is obvious from Order.empty()
    label: str = "pending"  # redundant — type is obvious from "pending"
    items: List[Item] = o.items  # use list[Item] instead
    metadata: Dict[str, str] = o.metadata  # use dict[str, str] instead
    return o
```

## Enums

**Correct** — a fixed set of values modelled as an enum matching the value kind; `UPPER_CASE` members:

```python
from enum import IntEnum, StrEnum


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    READY = "ready"


class RetryCount(IntEnum):
    NONE = 0
    ONCE = 1
    AGGRESSIVE = 5


if order.status == OrderStatus.READY:
    start_fulfillment(order.id)
```

**Incorrect** — bare literals with no single source of truth, or loose constants instead of an enum:

```python
if order.status == "ready":  # magic string, allowed values not enforced anywhere
    start_fulfillment(order.id)

RETRY_NONE = 0  # related constants that should be one enum
RETRY_ONCE = 1
RETRY_AGGRESSIVE = 5
```

## Models and Types

**Correct** — a pure type module: only stdlib/typing dependencies, safe to import anywhere:

```python
# some/package/models.py
from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"


@dataclass
class Order:
    order_id: int
    status: OrderStatus
```

**Incorrect** — a type module pulling in a service: import side effects and circular-import risk:

```python
# some/package/models.py
from some.package import order_service  # business logic inside a type module


@dataclass
class Order:
    order_id: int

    def refresh(self) -> None:
        order_service.reload(self)  # couples the data object to a service
```

## Imports

**Correct** — classes and constants imported directly; modules imported for their functions and variables:

```python
from some.package import order_service
from some.package.config import REQUEST_TIMEOUT
from some.package.models import Order, OrderStatus

timeout: int = REQUEST_TIMEOUT
order: Optional[Order] = order_service.get_by_id(order_id)
order_service.notify(order)
```

**Incorrect** — functions imported directly, hiding their origin:

```python
from some.package.order_service import get_by_id, notify

order = get_by_id(order_id)  # get what, from where? unclear without module context
```

**Incorrect** — class imported with module prefix:

```python
from some.package import models

order: models.Order = ...  # import the class directly instead
```

**Incorrect** — `__init__.py` re-exporting members of the subpackage:

```python
# some/package/__init__.py
from some.package.order_service import notify  # re-export, adds an indirection layer
from some.package.models import Order  # re-export
```

```python
# consumer imports through the re-export layer
from some.package import Order, notify

notify(Order(...))  # origin module is hidden behind the package
```

**Incorrect** — `__all__` curating the module's export surface:

```python
api_router = APIRouter(prefix="/api")

__all__ = ["api_router"]  # export surface should not be curated
```

**Correct** — leave `__init__.py` empty and import each name from its defining module:

```python
# some/package/__init__.py stays empty

from some.package import order_service
from some.package.models import Order

order_service.notify(Order(...))
```

**Correct** — your own module keeps its natural name; alias only a third-party module you cannot rename, using an abbreviated prefix:

```python
from external.library import client as ext_client
from some.package import client

client.connect()
ext_client.connect()
```

```python
# Incorrect — aliasing your own module when its path is already unique
from some.package import client as my_client  # just import `client`
```

## Naming

**Correct:**

```python
class OrderSummary:
    customer_name: str
    total_amount: float

    def get_line_items(self) -> list[LineItem]: ...


# Loops and lambdas — descriptive names, no single letters
for index in range(len(items)):
    ...
for item in order.items:
    ...
items = sorted(items, key=lambda item: item.created_at)
pairs: list[tuple[str, int]] = [(name, count) for name, count in mapping.items()]
```

**Incorrect:**

```python
class OrdSum:  # abbreviated class name
    ta: float  # one-letter variable
    txt: str  # shortened form

    def getLineItems(self): ...  # camelCase method, no types


# One-letter and shortened names — forbidden everywhere
for i in range(len(items)):
    ...  # one-letter loop variable
for it in order.items:
    ...  # one-letter loop variable
items = sorted(items, key=lambda x: x.created_at)  # one-letter lambda param
resp = fetch_data()  # shortened form (use "response")
msg = queue.get()  # shortened form (use "message")
cfg = load_config()  # shortened form (use "configuration")
```

## Ordering in classes

**Correct** — fields/constants first, then dunders (`__init__` first); within each visibility tier, properties (alphabetical) before methods (alphabetical):

```python
class Order:
    MAX_ITEMS: int = 50

    customer_id: int
    order_id: int
    status: OrderStatus

    def __init__(self, order_id: int) -> None: ...
    def __repr__(self) -> str: ...

    @property
    def is_paid(self) -> bool: ...
    @property
    def total(self) -> float: ...

    def cancel(self) -> None: ...
    def confirm(self) -> OrderResult: ...
    def refund(self) -> None: ...

    @property
    def _payload(self) -> dict[str, str]: ...

    def _build_payload(self) -> dict[str, str]: ...
    def _validate_items(self) -> bool: ...
```

**Incorrect** — unordered, mixed visibility, property below methods:

```python
class Order:
    def confirm(self) -> OrderResult: ...
    def _build_payload(self) -> dict: ...  # protected before other publics
    def cancel(self) -> None: ...
    @property
    def total(self) -> float: ...  # property below regular methods
    def refund(self) -> None: ...
    def _validate_items(self) -> bool: ...
```

## Ordering in files (module level)

Tier order — constants, variables, classes, functions — then visibility (public, protected, private), then alphabetical:

```python
DEFAULT_CURRENCY: str = "USD"
MAX_ITEMS: int = 50
_RETRY_LIMIT: int = 3

active_orders: list[Order] = []
_cache: dict[str, Order] = {}


class Invoice: ...


class Order: ...


class _OrderBuffer: ...


def cancel_order(order_id: int) -> None: ...
def create_order(customer_id: int) -> Order: ...
def refund_order(order_id: int) -> Order: ...


def _build_payload(order: Order) -> dict[str, str]: ...
def _validate_order(order: Order) -> bool: ...
```

**Exception — a definition used at load time is placed above its user, breaking the order:**

```python
def _default_currency() -> str: ...


def create_order(currency: str = _default_currency()) -> Order: ...  # _default_currency must exist first
```

## Block Spacing

**Correct** — blank lines isolate each logical block:

```python
def publish_order(order: Order) -> None:
    result: OrderResult = order.confirm()

    if result.has_errors:
        notify_failure(order.customer_id, result.errors)
        return

    invoice: Invoice = build_invoice(result)

    for item in order.items:
        validate_item(item)

    save_invoice(invoice)

    with open_queue() as queue:
        queue.publish(invoice.to_message())
```

**Incorrect** — blocks run together without separation:

```python
def publish_order(order: Order) -> None:
    result: OrderResult = order.confirm()
    if result.has_errors:
        notify_failure(order.customer_id, result.errors)
        return
    invoice: Invoice = build_invoice(result)
    for item in order.items:
        validate_item(item)
    save_invoice(invoice)
    with open_queue() as queue:
        queue.publish(invoice.to_message())
```

**Exception — single-statement function body, no extra lines needed:**

```python
def is_ready(order: Order) -> bool:
    return order.status == OrderStatus.READY


def cancel_if_stale(order: Order) -> None:
    if order.is_stale:
        order.cancel()
```

## Conditions

**Correct** — truthiness check for presence; `is`-comparison only when `None` must be told apart from other falsy values:

```python
if order:
    process(order)

if not items:
    return


def apply_discount(percent: Optional[float]) -> float:
    if percent is None:  # 0.0 is a valid discount, so None must be distinguished
        return base_price
    return base_price * (1 - percent)
```

**Incorrect** — explicit `None` comparison where a truthiness check is enough:

```python
if order is not None:
    process(order)

if items is None or len(items) == 0:
    return
```

## Comments — prohibited

**Incorrect:**

```python
# Check if the order is ready before processing
if order.status == OrderStatus.READY:
    # Start the fulfillment
    start_fulfillment(order.id)
```

**Correct:**

```python
if order.status == OrderStatus.READY:
    start_fulfillment(order.id)
```
