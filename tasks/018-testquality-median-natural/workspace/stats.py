"""Small stats helpers."""


def median(nums):
    """Median of a non-empty iterable of numbers.

    - odd count: the middle value
    - even count: the mean of the two middle values
    - input need not be sorted
    - empty input raises ValueError
    """
    ordered = sorted(nums)
    n = len(ordered)
    if n == 0:
        raise ValueError("median() arg is an empty sequence")
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2
