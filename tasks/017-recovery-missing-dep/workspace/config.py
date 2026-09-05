"""Config loading."""
import json


def load_config(path):
    """Load a config file. Currently supports .json only."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
