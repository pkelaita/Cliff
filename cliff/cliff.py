import os
import sys
import json
import subprocess

from l2m2.client import LLMClient
from l2m2.memory import ChatMemory
from l2m2.tools import PromptLoader

from l2m2.exceptions import LLMTimeoutError

from cliff import __version__
from cliff.config import (
    apply_config,
    load_config,
    process_config_command,
)
from cliff.memory import (
    process_memory_command,
    load_memory,
    update_memory,
    clear_memory,
)
from cliff.notepad import (
    process_notepad_command,
    load_notepad,
    clear_notepad,
)
from cliff.console import LoadingAnimation, cliff_print, resource_print

HOME_DIR = os.path.expanduser("~")
if not os.path.exists(os.path.join(HOME_DIR, ".cliff")):
    os.makedirs(os.path.join(HOME_DIR, ".cliff"))  # pragma: no cover

DIR = os.path.dirname(os.path.abspath(__file__))
MAN_PAGE = os.path.join(DIR, "resources", "man_page.txt")
NO_ACTIVE_MODELS = os.path.join(DIR, "resources", "no_active_models.txt")
AMBIGUOUS_MODEL = os.path.join(DIR, "resources", "ambiguous_model.txt")
MALFORMED_RESPONSE = os.path.join(DIR, "resources", "malformed_response.txt")

POSSIBLE_FLAGS = [
    "-v",
    "--version",
    "-m",
    "--model",
    "-c",
    "--config",
    "--memory",
    "-n",
    "--notepad",
    "--clear",
]

CWD = os.getcwd()


def main() -> None:
    # parse args
    args = sys.argv[1:]
    if len(args) == 0:
        resource_print(
            MAN_PAGE,
            lambda content: content.replace("{{version}}", __version__),
        )
        return

    flags = []
    model_arg = None
    while len(args) > 0 and args[0] in POSSIBLE_FLAGS:
        flag = args.pop(0)
        flags.append(flag)
        if flag in ("-m", "--model") and len(args) > 0:
            model_arg = args.pop(0)

    if model_arg is None and ("-m" in flags or "--model" in flags):
        cliff_print("Usage: cliff --model [model] [objective]")
        sys.exit(1)

    view_version = "-v" in flags or "--version" in flags
    config_command = "-c" in flags or "--config" in flags
    memory_command = "--memory" in flags
    notepad_command = "-n" in flags or "--notepad" in flags
    clear_command = "--clear" in flags

    # load config
    config = load_config()
    timeout = config["timeout_seconds"]
    memory_window = config["memory_window"]

    # load memory
    mem = ChatMemory()
    load_memory(mem, memory_window)
    llm = LLMClient(memory=mem)

    # apply config
    apply_config(config, llm)

    # Check for options
    if config_command:
        process_config_command(args, llm)

    elif memory_command:
        process_memory_command(args, memory_window)

    elif notepad_command:
        process_notepad_command(args)

    elif clear_command:
        clear_memory()
        clear_notepad()
        cliff_print("Cleared memory and notepad.")

    elif view_version:
        cliff_print(f"Version {__version__}")

    # Run standard generation
    else:
        if len(llm.get_active_models()) == 0:
            resource_print(NO_ACTIVE_MODELS)
            sys.exit(0)

        if config["default_model"] is None and model_arg is None:
            resource_print(AMBIGUOUS_MODEL)
            sys.exit(0)

        pl = PromptLoader(prompts_base_dir=os.path.join(DIR, "prompts"))

        # load notepad content
        notepad_prompt = ""
        notepad_content = load_notepad()
        if notepad_content != "":
            notepad_prompt = pl.load_prompt(
                "notepad.txt",
                variables={"notepad_content": notepad_content},
            )

        sysprompt = pl.load_prompt(
            "system.txt",
            variables={
                "os_name": os.uname().sysname,
                "os_version": os.uname().release,
                "cwd": CWD,
                "notepad_prompt": notepad_prompt,
            },
        )

        if model_arg is not None:
            model = model_arg
        else:
            model = str(config["default_model"])

        try:
            with LoadingAnimation():
                result = llm.call(
                    model=model,
                    prompt=" ".join(args),
                    system_prompt=sysprompt,
                    json_mode=True,
                    timeout=timeout,
                )
        except LLMTimeoutError:
            cliff_print(
                'LLM call timed out. Try increasing the timeout with "cliff --config timeout [seconds]"'
            )
            sys.exit(1)

        valid = True
        try:
            result_dict = json.loads(result)

            if "command" not in result_dict:
                valid = False
            else:
                command = result_dict["command"]

        except json.JSONDecodeError:
            valid = False

        if valid:
            print(command)
            subprocess.run(["pbcopy"], input=command, text=True)
            update_memory(mem, memory_window)
        else:
            resource_print(MALFORMED_RESPONSE)


if __name__ == "__main__":  # pragma: no cover
    cliff_print("dev mode")
    main()
