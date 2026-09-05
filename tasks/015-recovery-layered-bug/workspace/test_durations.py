import pytest

from durations import parse_duration


def test_single_unit():
    assert parse_duration("90m") == 5400
    assert parse_duration("45s") == 45
    assert parse_duration("2h") == 7200


def test_multi_unit():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("1h1m1s") == 3661


def test_unknown_unit_raises_valueerror():
    with pytest.raises(ValueError):
        parse_duration("2d")
    with pytest.raises(ValueError):
        parse_duration("10x")
