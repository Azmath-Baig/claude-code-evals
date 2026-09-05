"""Background worker: applies payment events to account balances.

Consumes events from an in-memory queue. For each event it looks up the current FX
rate from an internal service, converts the amount, and adds it to the account
balance.
"""
import requests


class Worker:
    def __init__(self, api_base):
        self.api_base = api_base
        self.queue = []
        self.balances = {}

    def enqueue(self, event):
        """event = {"id": str, "account": str, "amount": float, "currency": str}"""
        self.queue.append(event)

    def run_once(self):
        if not self.queue:
            return
        event = self.queue.pop(0)
        try:
            resp = requests.get(f"{self.api_base}/fx/{event['currency']}")
            rate = resp.json()["rate"]
            acct = event["account"]
            self.balances[acct] = self.balances.get(acct, 0.0) + event["amount"] * rate
        except Exception:
            pass

    def run_forever(self):
        while True:
            self.run_once()
