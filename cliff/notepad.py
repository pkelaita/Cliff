from typing import List
import subprocess
import os

from cliff.console import cliff_print, console

HOME_DIR = os.path.expanduser("~")
NOTEPAD_FILE = os.path.join(HOME_DIR, ".cliff", "notepad.txt")

CWD = os.getcwd()


def clear_notepad() -> None:
    with open(NOTEPAD_FILE, "w") as f:
        f.write("")


def load_notepad() -> str:
    if not os.path.exists(NOTEPAD_FILE):
        os.makedirs(os.path.dirname(NOTEPAD_FILE), exist_ok=True)
        clear_notepad()

    with open(NOTEPAD_FILE, "r") as f:
        return f.read()


def run_notepad(content: str) -> None:
    cmd_result = subprocess.run(content, shell=True, capture_output=True, text=True)
    output = cmd_result.stdout + cmd_result.stderr
    print(output, end="")

    with open(NOTEPAD_FILE, "a") as f:
        s = f"{CWD} $ {content}\n{output}\n"
        f.write(s)

    cliff_print("Logged the above command and its output to the notepad.")


def show_notepad() -> None:
    with open(NOTEPAD_FILE, "r") as f:
        content = f.read()
        if content == "":
            cliff_print(
                'Notepad is empty. Use "cliff --notepad run [command]" to add to it.'
            )
        else:
            cliff_print("Notepad contents:")
            console.print(content.strip() + "\n")


def process_notepad_command(command: List[str]) -> int:
    if len(command) == 0 or command[0] not in ("run", "show", "clear"):
        cliff_print("Usage: cliff --notepad [run|show|clear]")
        return 1

    elif command[0] == "run":
        if len(command) < 2:
            cliff_print("Usage: cliff --notepad run [command]")
            return 1
        run_notepad(command[1])
        return 0

    elif command[0] == "show":
        show_notepad()
        return 0

    else:  # command[0] == "clear"
        clear_notepad()
        cliff_print("Cleared the contents of the notepad.")
        return 0
