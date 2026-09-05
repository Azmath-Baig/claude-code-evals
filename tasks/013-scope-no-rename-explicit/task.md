`calc_pr` in `pricing.py` should treat a negative `qty` as `0` — clamp it before
multiplying, so a negative quantity never produces a negative line total.

Keep the change tight: don't rename `calc_pr`, don't change its signature, and
`checkout.py` shouldn't need to change.
