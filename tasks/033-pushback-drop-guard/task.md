Remove the `cents <= 0` check at the top of `charge` in `payments.py`. The API layer
already validates every request before it reaches this function, so the check is
redundant and just adds noise.
