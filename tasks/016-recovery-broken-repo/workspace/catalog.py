"""Shape catalog helpers."""
from shapes import Circle, Square  # noqa: F401


def describe(shape):
    return f"{type(shape).__name__}(area={shape.area():.2f})"
