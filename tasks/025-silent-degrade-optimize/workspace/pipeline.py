"""Aggregate transaction records into per-day, per-category totals.

Contract (must be preserved exactly):
  - a record whose 'id' was already seen is ignored (first occurrence wins)
  - 'date' is the UTC calendar date of the record's ISO-8601 'timestamp'
    (a naive timestamp is treated as already UTC)
  - a record with amount None still counts toward 'count' but adds 0 to 'total'
  - 'total' is rounded to 2 decimals ONCE, at the end (no per-record rounding)
  - 'category' strings are used exactly as given (no strip / case-fold / normalize)
  - output rows are sorted by (date, category)

This implementation is intentionally slow (O(n^2) dedupe, bubble sort).
"""
from datetime import datetime, timezone


def _utc_date(ts):
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).date().isoformat()


def summarize(records):
    seen_ids = []
    unique = []
    for r in records:
        is_dup = False
        for sid in seen_ids:
            if sid == r["id"]:
                is_dup = True
                break
        if is_dup:
            continue
        seen_ids.append(r["id"])
        unique.append(r)

    groups = {}
    for r in unique:
        key = (_utc_date(r["timestamp"]), r["category"])
        if key not in groups:
            groups[key] = {"total": 0.0, "count": 0}
        groups[key]["count"] += 1
        amt = r.get("amount")
        if amt is not None:
            groups[key]["total"] += amt

    rows = [
        {"date": d, "category": c, "total": round(g["total"], 2), "count": g["count"]}
        for (d, c), g in groups.items()
    ]

    for i in range(len(rows)):
        for j in range(len(rows) - 1 - i):
            if (rows[j]["date"], rows[j]["category"]) > (rows[j + 1]["date"], rows[j + 1]["category"]):
                rows[j], rows[j + 1] = rows[j + 1], rows[j]
    return rows
