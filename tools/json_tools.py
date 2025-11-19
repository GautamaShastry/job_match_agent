import json
from smolagents import tool

@tool
def parse_json(json_str: str) -> dict:
    """
    Safely parse a JSON string into a Python dict.

    Args:
        json_str: A JSON-formatted string.

    Returns:
        A Python dict parsed from the JSON string.
    """
    return json.loads(json_str)
