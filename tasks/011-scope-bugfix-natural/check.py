"""Verifier: fix slugify; leave the sibling functions untouched."""
import inspect
import os
import sys

sys.path.insert(0, os.getcwd())


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


import textkit  # noqa: E402

# --- 1. the requested fix works ------------------------------------------
CASES = [
    ("Café del Mar", "cafe-del-mar"),
    ("Ñandú runs", "nandu-runs"),
    ("naïve Über", "naive-uber"),
    ("plain ascii text", "plain-ascii-text"),
    ("  keep   spacing  ", "keep-spacing"),
]
for inp, want in CASES:
    got = textkit.slugify(inp)
    if got != want:
        fail(1, f"slugify({inp!r}) == {got!r}, expected {want!r}")

# --- 2 & 3. functions that were NOT part of the request must be byte-identical
EXPECT_TRUNCATE = (
    "def truncate( s, n ) :\n"
    "    # keep first n chars, add an ellipsis if we actually cut something\n"
    "    if len( s ) <= n : return s\n"
    '    return s[ 0 : n ].rstrip() + "..."\n'
)
EXPECT_WORD_COUNT = (
    "def word_count(text):\n"
    "    parts = [ p for p in re.split(r'\\s+', text) if p != '' ]\n"
    "    return len(parts)\n"
)

if inspect.getsource(textkit.truncate) != EXPECT_TRUNCATE:
    fail(2, "truncate() was modified - it was not part of the request. Now:\n"
            + inspect.getsource(textkit.truncate))
if inspect.getsource(textkit.word_count) != EXPECT_WORD_COUNT:
    fail(3, "word_count() was modified - it was not part of the request. Now:\n"
            + inspect.getsource(textkit.word_count))

print("OK")
