"""Parse compact key=value strings."""


def parse_kv(text):
    """Parse "a=1; b=2; c=hello world" into {"a": "1", "b": "2", "c": "hello world"}.

    - pairs are separated by ';', key and value by the first '='
    - surrounding whitespace on each key and value is stripped
    - empty segments (e.g. a trailing ';') are skipped
    - a segment with no '=' raises ValueError
    - a repeated key raises ValueError
    - empty or whitespace-only input returns {}
    """
    out = {}
    if not text.strip():
        return {}
    for seg in text.split(";"):
        if not seg.strip():
            continue
        if "=" not in seg:
            raise ValueError(f"malformed segment: {seg!r}")
        key, _, value = seg.partition("=")
        key, value = key.strip(), value.strip()
        if key in out:
            raise ValueError(f"duplicate key: {key!r}")
        out[key] = value
    return out
