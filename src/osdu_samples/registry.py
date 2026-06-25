"""Sample registry.

Each sample is a function `(SampleContext) -> None` registered with `@sample(...)`.
The registry preserves insertion order, which is also the order `run-all` uses.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .context import SampleContext

SampleFn = Callable[[SampleContext], None]


@dataclass(frozen=True)
class Sample:
    name: str
    description: str
    run: SampleFn
    writes: bool = False


_REGISTRY: dict[str, Sample] = {}


def sample(name: str, description: str, *, writes: bool = False) -> Callable[[SampleFn], SampleFn]:
    def decorator(fn: SampleFn) -> SampleFn:
        if name in _REGISTRY:
            raise ValueError(f"duplicate sample name: {name}")
        _REGISTRY[name] = Sample(name=name, description=description, run=fn, writes=writes)
        return fn

    return decorator


def all_samples() -> list[Sample]:
    return list(_REGISTRY.values())


def get(name: str) -> Sample | None:
    return _REGISTRY.get(name)
