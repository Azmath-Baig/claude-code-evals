"""Input validation helpers."""
import re


def is_email(s):
    # good enough for our purposes
    return bool(re.match(r".+@.+", s or ""))


def is_positive_int(s):
    try:
        return int(s) > 0
    except (TypeError, ValueError):
        return False
