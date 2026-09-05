`pipeline.summarize` is slow on large inputs (it's O(n²) in a couple of places).
Optimize it for speed. Behavior must stay exactly equivalent — same output for
every input.
