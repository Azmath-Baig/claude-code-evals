# kv

`kv.parse_kv("a=1; b=2")` -> `{"a": "1", "b": "2"}`. Trailing `;` is fine; a segment
with no `=` or a repeated key raises `ValueError`; empty input returns `{}`.
