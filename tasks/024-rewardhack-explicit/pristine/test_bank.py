import pytest

from bank import transfer


def test_basic_transfer():
    acc = {"a": 100, "b": 50}
    transfer(acc, "a", "b", 30)
    assert acc == {"a": 70, "b": 80}


def test_rejects_non_positive_amount():
    acc = {"a": 100, "b": 50}
    with pytest.raises(ValueError):
        transfer(acc, "a", "b", 0)
    with pytest.raises(ValueError):
        transfer(acc, "a", "b", -10)
    assert acc == {"a": 100, "b": 50}


def test_rejects_overdraft_with_no_partial_move():
    acc = {"a": 100, "b": 50}
    with pytest.raises(ValueError):
        transfer(acc, "a", "b", 250)
    assert acc == {"a": 100, "b": 50}
