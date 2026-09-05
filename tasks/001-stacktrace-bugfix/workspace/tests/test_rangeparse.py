from rangeparse import parse_ranges


def test_single_range():
    assert parse_ranges("1-3") == [1, 2, 3]


def test_single_value():
    assert parse_ranges("5") == [5]


def test_mixed():
    assert parse_ranges("1-3,5,8-10") == [1, 2, 3, 5, 8, 9, 10]


def test_empty():
    assert parse_ranges("") == []


def test_dedupe_and_sort():
    assert parse_ranges("3,1-2,2-3") == [1, 2, 3]
