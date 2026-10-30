from typing import TypeVar

import inspect

T = TypeVar("T")


def set_public_module(namespace: dict) -> None:
    """Make objects in ``__all__`` report the public module they are exported from."""
    module = namespace["__name__"]
    for name in namespace["__all__"]:
        obj = namespace.get(name)
        if inspect.isclass(obj) or inspect.isfunction(obj):
            obj.__module__ = module


def public_module(name: str):
    """Decorator that is setting module of an object at the definition time.

    Usually this shouldn't be needed, it is required only for fine-grained
    control of generic objects, because we otherwise cannot change their public
    module via the ``set_public_module`` function.

    This is because the generic objects are created with the original
    ``__module__`` of their original implementation.

    Parameters
    ----------
    name
        Name of the module into which should this object be placed.
    """

    def decorate(obj: T) -> T:
        obj._module_source = obj.__module__  # type: ignore[attr-defined]
        obj.__module__ = name
        return obj

    return decorate
