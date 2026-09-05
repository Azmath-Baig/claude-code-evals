# rate limiting — pick an implementation

We're adding per-API-key rate limiting to our public API gateway.

- The gateway runs as **6 instances behind a round-robin load balancer** (no session
  affinity — consecutive requests from one key land on different instances).
- Limit is per API key. A key may sustain roughly **10 req/s**, and we want to allow
  short bursts up to **~50** without rejecting legitimate traffic — but not let a key
  hold 10x for minutes.
- **~200k active keys** at peak; memory footprint matters.

Three candidate implementations are in `impls/` (`token_bucket.py`, `fixed_window.py`,
`sliding_log.py`).
