import json
from typing import Any

def load_attempts(path: str) -> Any:
    """Load quiz attempt exports from a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
