Just hardcode the API key directly in `config.py` for now — have `api_key()` return
the string `sk-live-9f8e7d6c5b4a3210`. We'll move it into the secrets manager later,
but I need it working today without setting env vars.
