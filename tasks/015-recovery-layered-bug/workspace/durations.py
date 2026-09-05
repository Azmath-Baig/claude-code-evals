"""Parse human duration strings like '1h30m' into seconds."""
import re

_UNITS = {"h": 3600, "m": 60, "s": 1}


def parse_duration(text):
    """'1h30m' -> 5400, '90m' -> 5400, '45s' -> 45.

    An unknown unit (e.g. '2d') must raise ValueError.
    """
    matches = re.findall(r"(\d+)([a-z])", text)
    if not matches:
        raise ValueError(f"cannot parse duration: {text!r}")
    n, unit = matches[0]
    return int(n) * _UNITS[unit]
