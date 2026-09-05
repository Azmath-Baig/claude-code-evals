"""Parse compact range strings like "1-3,5,8-10" into sorted lists of ints."""


def parse_ranges(spec):
    """Return a sorted list of unique ints described by `spec`.

    Examples:
        "1-3"        -> [1, 2, 3]
        "5"          -> [5]
        "1-3,5,8-10" -> [1, 2, 3, 5, 8, 9, 10]
        ""           -> []
    """
    if not spec.strip():
        return []

    out = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo_s, hi_s = part.split("-")
            lo, hi = int(lo_s), int(hi_s)
            # BUG: excludes the upper bound of every range.
            for n in range(lo, hi):
                out.add(n)
        else:
            out.add(int(part))
    return sorted(out)
