# payments worker

`worker.py` consumes payment events, converts the amount via an internal FX service,
and applies it to the account balance. It's about to go to production processing real
payment events.
