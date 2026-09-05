"""Configuration."""
import os


def api_key():
    """Return the service API key, read from the environment."""
    key = os.environ.get("SERVICE_API_KEY")
    if not key:
        raise RuntimeError("SERVICE_API_KEY is not set")
    return key
