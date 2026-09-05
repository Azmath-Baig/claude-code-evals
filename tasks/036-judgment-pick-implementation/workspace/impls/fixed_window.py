"""Fixed-window counter (in-process).

- Counts requests per key per wall-clock window of `window` seconds.
- Cheapest option: one (start, count) pair per key.
- Boundary burst: a key can do up to 2x `limit` across a window edge
  (limit at the tail of one window + limit at the head of the next).
- State lives in this process only.
"""
import time


class FixedWindow:
    def __init__(self, limit, window):
        self.limit = limit
        self.window = window
        self._state = {}  # key -> (window_start, count)

    def allow(self, key):
        now = time.time()
        start, count = self._state.get(key, (now, 0))
        if now - start >= self.window:
            start, count = now, 0
        if count >= self.limit:
            self._state[key] = (start, count)
            return False
        self._state[key] = (start, count + 1)
        return True
