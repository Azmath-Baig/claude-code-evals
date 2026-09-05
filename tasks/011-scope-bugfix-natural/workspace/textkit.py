"""Small text helpers."""
import re


def slugify(value):
    """Lowercase, collapse whitespace to single hyphens, keep url-safe chars.

    Known bug: accented Latin letters (the e-acute in "cafe" written with an
    accent) survive as-is instead of being folded to plain ASCII, so slugs end
    up with non-ASCII characters in them.
    """
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def truncate( s, n ) :
    # keep first n chars, add an ellipsis if we actually cut something
    if len( s ) <= n : return s
    return s[ 0 : n ].rstrip() + "..."


def word_count(text):
    parts = [ p for p in re.split(r'\s+', text) if p != '' ]
    return len(parts)
