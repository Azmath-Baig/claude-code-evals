"""HTTP client with retry on transient failures."""
import time
import urllib.error
import urllib.request

_MAX_ATTEMPTS = 4
_BASE_DELAY = 0.5  # seconds; doubled each retry


def fetch_with_retry(url):
    """GET `url`, retrying on transient network / 5xx errors with exponential backoff.

    Raises the last error if every attempt fails.
    """
    last_err = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code < 500:
                raise  # 4xx won't get better by retrying
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = e
        time.sleep(_BASE_DELAY * (2 ** attempt))
    raise last_err
