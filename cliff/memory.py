from typing import List, Dict
import os
import json

from l2m2.memory import ChatMemory

from cliff.console import cliff_print, console

HOME_DIR = os.path.expanduser("~")
MEMORY_FILE = os.path.join(HOME_DIR, ".cliff", "memory.json")


def _truncate(data: List[Dict[str, str]], window_size: int) -> List[Dict[str, str]]:
    if window_size < 0:
        raise ValueError("Window size must be non-negative")
    if window_size == 0:
        return []
    max_items = window_size * 2
    return data[-max_items:] if len(data) > max_items else data


def clear_memory() -> None:
    with open(MEMORY_FILE, "w") as f:
        f.write("[]")


def load_memory(mem: ChatMemory, window_size: int) -> int:
    if not os.path.exists(MEMORY_FILE):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        clear_memory()

    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)

    data = _truncate(data, window_size)

    for entry in data:
        if entry["role"] == "user":
            mem.add_user_message(entry["content"])
        elif entry["role"] == "assistant":
            mem.add_agent_message(entry["content"])

    return 0


def update_memory(mem: ChatMemory, window_size: int) -> int:
    data = mem.unpack("role", "content", "user", "assistant")

    data = _truncate(data, window_size)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return 0


def show_memory(window_size: int) -> int:
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
        data = _truncate(data, window_size)

        if len(data) == 0:
            cliff_print("Memory is empty.")
            return 0

        for entry in data:
            if entry["role"] == "user":
                console.print("[magenta]User:[/magenta]", end="  ")
                print(entry["content"])
            elif entry["role"] == "assistant":
                content_data = json.loads(entry["content"])
                console.print("[cyan]Cliff:[/cyan]", end=" ")
                print(content_data["command"])
                if entry != data[-1]:
                    print()
        print()
    return 0


def process_memory_command(command: List[str], window_size: int) -> int:
    if len(command) == 0 or command[0] not in ("show", "clear"):
        cliff_print("Usage: cliff --memory [show or clear]")
        return 1

    if command[0] == "clear":
        clear_memory()
        cliff_print("Cleared memory.")
        return 0

    else:  # show
        show_memory(window_size)
        return 0
