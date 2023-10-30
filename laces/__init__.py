from .components import Component


VERSION = (0, 1, 0)
__version__ = ".".join(map(str, VERSION))


__all__ = [
    VERSION,
    Component,
]
