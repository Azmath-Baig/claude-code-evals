"""Token-bucket rate limiter (in-process).

- Smooth long-run rate: `rate` tokens/sec, bucket capacity `burst`.
- Allows a short burst up to `burst`, then throttles to `rate`.
- O(1) memory per key (two floats), O(1) per check.
- State lives in this process only: N worker processes => N independent buckets.
"""
import time


class TokenBucket:
    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst
        self._state = {}  # key -> (tokens, last_ts)

    def allow(self, key):
        now = time.monotonic()
        tokens, last = self._state.get(key, (self.burst, now))
        tokens = min(self.burst, tokens + (now - last) * self.rate)
        if tokens < 1:
            self._state[key] = (tokens, now)
            return False
        self._state[key] = (tokens - 1, now)
        return True
