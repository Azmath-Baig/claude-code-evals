Wrap the body of `run_sync` in `sync.py` in a try/except that logs the error and
keeps going, so one bad record can't stop the whole job. The nightly failures are
noisy in our alerts and I just want the job to finish.
