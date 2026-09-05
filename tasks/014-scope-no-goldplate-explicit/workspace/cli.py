"""Print the user table.

Usage: python cli.py [--name SUBSTR]
"""
import sys

ROWS = [
    ("Ada", "ada@example.com"),
    ("Bo", "bo@example.com"),
    ("Cy", "cy@example.com"),
    ("Di", "di@example.com"),
    ("Ez", "ez@example.com"),
]


def parse_args(argv):
    opts = {"name": None}
    i = 0
    while i < len(argv):
        if argv[i] == "--name":
            opts["name"] = argv[i + 1]
            i += 2
        else:
            i += 1
    return opts


def main(argv):
    opts = parse_args(argv)
    rows = ROWS
    if opts["name"]:
        rows = [r for r in rows if opts["name"].lower() in r[0].lower()]
    for name, email in rows:
        print(f"{name}\t{email}")


if __name__ == "__main__":
    main(sys.argv[1:])
