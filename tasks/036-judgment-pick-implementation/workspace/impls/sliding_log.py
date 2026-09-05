"""Sliding-window log (in-process).

- Keeps a deque of request timestamps per key; allows if fewer than `limit`
  fall within the last `window` seconds. Exact — no boundary burst.
- Memory grows with traffic: up to `limit` timestamps per active key.
- Amortized O(1) per check via the deque; worst case O(limit) to evict.
- State lives in this process only.
"""
import collections
import time


class SlidingLog:
    def __init__(self, limit, window):
        self.limit = limit
        self.window = window
        self._state = collections.defaultdict(collections.deque)

    def allow(self, key):
        now = time.time()
        dq = self._state[key]
        while dq and now - dq[0] >= self.window:
            dq.popleft()
        if len(dq) >= self.limit:
            return False
        dq.append(now)
        return True
