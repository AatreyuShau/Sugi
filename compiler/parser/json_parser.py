import json
from typing import Any

def parse_json_scene(source: str) -> dict[str, Any]:
    data = json.loads(source)
    if not isinstance(data, dict):
        raise ValueError("SUGI JSON scene must be an object")
    return data
