"""Tiny in-process log bus.

This module exists purely to break a circular import: ``bot_engine`` imports
``actions`` (to drive the game), and ``actions`` needs to push its progress lines
into the engine's log buffer so they appear in the PyQt5 dashboard console / web UI.

``logbus`` has **no** imports of its own, so it can be imported from anywhere.

Usage
-----
```python
import logbus
logbus.log("did a thing")            # informational
logbus.log("uh oh", level="error")   # leveled
```
The engine registers its ``log`` method as a sink at construction time. When no
sink is registered (e.g. a unit test importing ``actions`` alone) the calls are
silently discarded.
"""

from typing import Callable, List

_sinks: List[Callable[[str, str], None]] = []


def register(sink: Callable[[str, str], None]) -> None:
    """Register a callable ``sink(message, level)`` to receive log lines."""
    if sink not in _sinks:
        _sinks.append(sink)


def unregister(sink: Callable[[str, str], None]) -> None:
    try:
        _sinks.remove(sink)
    except ValueError:
        pass


def log(message: str, level: str = "info") -> None:
    """Fan a message out to every registered sink. Never raises."""
    for sink in list(_sinks):
        try:
            sink(message, level)
        except Exception:
            pass
