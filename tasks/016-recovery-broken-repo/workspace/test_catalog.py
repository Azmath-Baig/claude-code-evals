from catalog import describe
from shapes import Square


def test_describe():
    assert describe(Square(2)) == "Square(area=4.00)"
