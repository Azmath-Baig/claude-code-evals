Add a `--limit N` option to `cli.py` that caps how many rows are printed (applied
after any `--name` filtering).

Just that one option. Don't add other flags, don't switch to `argparse`, keep the
hand-rolled `parse_args` loop.
