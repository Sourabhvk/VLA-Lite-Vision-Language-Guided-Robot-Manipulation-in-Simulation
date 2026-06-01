import json
import os
from urllib import request

from src.language.command_schema import validate_task


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = os.getenv("OLLAMA_URL", f"{OLLAMA_HOST}/api/generate")
OLLAMA_PS_URL = os.getenv("OLLAMA_PS_URL", f"{OLLAMA_HOST}/api/ps")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def parse_command_with_ollama(command):
    raw_task = ask_ollama(command)
    task = json.loads(raw_task)
    return validate_task(task)


def ask_ollama(command):
    print_ollama_status()
    print("Ollama: parsing command...")

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
        print("Ollama: response received")
        return data["response"]


def print_ollama_status():
    loaded = model_is_loaded()
    if loaded is True:
        print(f"Ollama: {OLLAMA_MODEL} is already loaded")
    elif loaded is False:
        print(f"Ollama: loading {OLLAMA_MODEL}; first response may be slow")
    else:
        print("Ollama: status unknown; sending request")


def model_is_loaded():
    try:
        with request.urlopen(OLLAMA_PS_URL, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    return any(model.get("name") == OLLAMA_MODEL or model.get("model") == OLLAMA_MODEL for model in data.get("models", []))


def build_prompt(command):
    return f"""
Convert the robot command to JSON only.

Allowed JSON shapes:
{{
  "action": "pick",
  "source": {{
    "type": "cube",
    "color_text": "<user color words>",
    "quantity": "one|all",
    "hsv_ranges": [
      {{"lower": [H, S, V], "upper": [H, S, V]}}
    ]
  }}
}}

{{
  "action": "pick_place",
  "source": {{
    "type": "cube",
    "color_text": "<user color words>",
    "quantity": "one|all",
    "hsv_ranges": [
      {{"lower": [H, S, V], "upper": [H, S, V]}}
    ]
  }},
  "target": {{"type": "tray", "color": "blue"}}
}}

{{
  "action": "place",
  "target": {{"type": "tray", "color": "blue"}}
}}

Rules:
- Use action "pick" when the user only asks to pick up or grab a cube.
- Use action "place" when the user only asks to place/drop the held object.
- Use action "pick_place" when the user asks to pick and place in one command.
- For pick actions, infer an OpenCV HSV range for the user's color words.
- HSV uses OpenCV ranges: H 0-180, S 0-255, V 0-255.
- Red may need two hue ranges around 0 and 180.
- Use saturated/bright ranges for cube colors in a PyBullet scene.
- Use quantity "all" only when the user clearly asks for all/multiple cubes.
- Otherwise use quantity "one".
- The only target is the blue tray.

Command: {command}
""".strip()
