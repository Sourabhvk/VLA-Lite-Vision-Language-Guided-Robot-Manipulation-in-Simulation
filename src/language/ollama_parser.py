import json
import os
from urllib import request

from src.language.command_schema import SUPPORTED_COLORS, validate_task


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def parse_command_with_ollama(command):
    raw_task = ask_ollama(command)
    task = json.loads(raw_task)
    return validate_task(task)


def ask_ollama(command):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": build_prompt(command),
        "format": "json",
        "stream": False,
    }
    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})

    with request.urlopen(http_request, timeout=45) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data["response"]


def build_prompt(command):
    colors = ", ".join(sorted(SUPPORTED_COLORS))
    return f"""
Convert the robot command to JSON only.

Schema:
{{
  "action": "pick_place",
  "source": {{"type": "cube", "color": "<color>", "quantity": "one|all"}},
  "target": {{"type": "tray", "color": "blue"}}
}}

Rules:
- Supported cube colors: {colors}
- Use quantity "all" only when the user clearly asks for all/multiple cubes.
- Otherwise use quantity "one".
- The only target is the blue tray.

Command: {command}
""".strip()
