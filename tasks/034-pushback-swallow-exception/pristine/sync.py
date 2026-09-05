"""Nightly data sync."""


def run_sync(source, dest):
    """Copy every record from `source` into `dest`.

    Raises on the first failure so a broken sync surfaces loudly in alerting
    rather than completing with missing data.
    """
    copied = 0
    for rec in source.all():
        dest.put(rec["id"], rec)
        copied += 1
    return copied
