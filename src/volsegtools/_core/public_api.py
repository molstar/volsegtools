import inspect


def set_public_module(namespace: dict) -> None:
    """Make objects in ``__all__`` report the public module they are exported from."""
    module = namespace["__name__"]
    for name in namespace["__all__"]:
        obj = namespace.get(name)
        if inspect.isclass(obj) or inspect.isfunction(obj):
            obj.__module__ = module
