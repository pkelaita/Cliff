import os
import sys
import json
import subprocess

from l2m2.client import LLMClient
from l2m2.memory import ChatMemory
from l2m2.tools import PromptLoader

HOME_DIR = os.path.expanduser("~")
if not os.path.exists(os.path.join(HOME_DIR, ".cliff")):
    os.makedirs(os.path.join(HOME_DIR, ".cliff"))  # pragma: no cover

if __name__ == "__main__":
    from __init__ import __version__  # pragma: no cover
    from config import (  # pragma: no cover
        apply_config,
        load_config,
        process_config_command,
        get_memory_window,
    )
    from memory import (
        process_memory_command,
        load_memory,
        update_memory,
    )  # pragma: no cover
    from animations import LoadingAnimation  # pragma: no cover
else:
    from cliff import __version__
    from cliff.config import (
        apply_config,
        load_config,
        process_config_command,
        get_memory_window,
    )
    from cliff.memory import process_memory_command, load_memory, update_memory
    from cliff.animations import LoadingAnimation

RECALL_FILE = os.path.join(HOME_DIR, ".cliff", "cliff_recall")
DIR = os.path.dirname(os.path.abspath(__file__))
MAN_PAGE = os.path.join(DIR, "resources", "man_page.txt")

POSSIBLE_FLAGS = [
    "-v",
    "--version",
    "-m",
    "--model",
    "-r",
    "--recall",
    "-sr",
    "--show-recall",
    "-cr",
    "--clear-recall",
    "--config",
    "--memory",
]

CWD = os.getcwd()

WINDOW_SIZE = get_memory_window()


def main() -> None:
    # parse args
    args = sys.argv[1:]
    if len(args) == 0:
        with open(MAN_PAGE, "r") as f:
            print(f.read().replace("{{version}}", __version__))
        return

    flags = []
    model_arg = None
    while len(args) > 0 and args[0] in POSSIBLE_FLAGS:
        flag = args.pop(0)
        flags.append(flag)
        if flag in ("-m", "--model") and len(args) > 0:
            model_arg = args.pop(0)

    if model_arg is None and ("-m" in flags or "--model" in flags):
        print("[Cliff] Usage: cliff --model [model] [objective]")
        sys.exit(1)

    content = " ".join(args)
    config_command = "--config" in flags
    memory_command = "--memory" in flags
    view_version = "-v" in flags or "--version" in flags
    store_recall = "-r" in flags or "--recall" in flags
    show_recall = "-sr" in flags or "--show-recall" in flags
    clear_recall = "-cr" in flags or "--clear-recall" in flags

    # load memory
    mem = ChatMemory()
    load_memory(mem, WINDOW_SIZE)
    llm = LLMClient(memory=mem)

    # apply config
    config = load_config()
    apply_config(config, llm)

    # load recall content
    recall_content = ""
    if os.path.exists(RECALL_FILE):
        with open(RECALL_FILE, "r") as f:
            recall_content = f.read()
    else:
        with open(RECALL_FILE, "w") as f:
            f.write("")

    # Check for options
    if config_command:
        process_config_command(args, llm)

    elif memory_command:
        process_memory_command(args)

    elif view_version:
        print(f"[Cliff] Version {__version__}")

    elif store_recall:
        cmd_result = subprocess.run(content, shell=True, capture_output=True, text=True)
        output = cmd_result.stdout + cmd_result.stderr
        print(output, end="")

        with open(RECALL_FILE, "a") as f:
            s = f"{CWD} $ {content}\n{output}\n"
            f.write(s)

        print("[Cliff] Recalled this command and its output")

    elif show_recall:
        if recall_content == "":
            print("[Cliff] No recalled commands.")
        else:
            print("[Cliff] Recalled commands:")
            print(recall_content)

    elif clear_recall:
        with open(RECALL_FILE, "w") as f:
            f.write("")
        print("[Cliff] Cleared recalled commands.")

    # Run standard generation
    else:
        if len(llm.get_active_models()) == 0:
            print(
                """[Cliff] Welcome to Cliff! To get started, please either connect to an LLM provider by typing
                
cliff --config add [provider] [api-key]
                
or connect to a local model in Ollama by typing
                
cliff --config add ollama [model]
"""
            )
            sys.exit(0)

        pl = PromptLoader(prompts_base_dir=os.path.join(DIR, "prompts"))

        recall_prompt = ""
        if recall_content != "":
            recall_prompt = pl.load_prompt(
                "recall.txt",
                variables={"recall_content": recall_content},
            )

        sysprompt = pl.load_prompt(
            "system.txt",
            variables={
                "os_name": os.uname().sysname,
                "os_version": os.uname().release,
                "cwd": CWD,
                "recall_prompt": recall_prompt,
            },
        )

        if model_arg is not None:
            model = model_arg
        else:
            model = config["default_model"]

        with LoadingAnimation():
            result = llm.call(
                model=model,
                prompt=content,
                system_prompt=sysprompt,
                json_mode=True,
                timeout=25,
            )

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
            update_memory(mem, WINDOW_SIZE)
        else:
            print(
                """[Cliff] Sorry, the LLM returned a bad or malformed response. If this
persists, try clearing Cliff's memory with cliff --memory clear, and
if that still doesn't work, try switching to a different model."""
            )


if __name__ == "__main__":  # pragma: no cover
    print("[Cliff] dev mode")
    main()
