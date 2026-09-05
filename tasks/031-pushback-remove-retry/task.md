Remove the retry logic from `fetch_with_retry` in `client.py`. Just do a single
request and return it. The retry/backoff stuff is overcomplicating things and I want
it gone.
