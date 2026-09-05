# pipeline

`pipeline.summarize(records)` rolls a list of transaction records up into per-day,
per-category `{date, category, total, count}` rows. The exact contract is documented at
the top of `pipeline.py`. The current implementation is slow on large inputs.
