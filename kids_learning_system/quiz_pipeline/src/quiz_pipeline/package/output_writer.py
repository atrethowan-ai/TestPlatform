
import json
import logging

def write_output(data, path):
    """
    Write data as JSON to the given path.
    """
    logging.info(f"Writing output to {path}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
