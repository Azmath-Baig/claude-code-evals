"""De-duplication utilities."""


def dedupe(items):
    """Return `items` with duplicates removed, keeping the FIRST occurrence of each,
    in the original order.

    Items are hashable. This is called on lists of up to ~1,000,000 elements, so it
    needs to stay fast as the input grows.
    """
    raise NotImplementedError
