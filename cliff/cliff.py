import os
import sys
import json
import subprocess

from l2m2.client import LLMClient
from l2m2.memory import ChatMemory
from l2m2.tools import PromptLoader

from cliff import __version__
from cliff.config import (
    apply_config,
    load_config,
    process_config_command,
    get_memory_window,
)
from cliff.memory import process_memory_command, load_memory, update_memory
from cliff.console import LoadingAnimation, cliff_print

HOME_DIR = os.path.expanduser("~")
if not os.path.exists(os.path.join(HOME_DIR, ".cliff")):
    os.makedirs(os.path.join(HOME_DIR, ".cliff"))  # pragma: no cover

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
        cliff_print("Usage: cliff --model [model] [objective]")
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
        process_memory_command(args, WINDOW_SIZE)

    elif view_version:
        cliff_print(f"Version {__version__}")

    elif store_recall:
        cmd_result = subprocess.run(content, shell=True, capture_output=True, text=True)
        output = cmd_result.stdout + cmd_result.stderr
        print(output, end="")

        with open(RECALL_FILE, "a") as f:
            s = f"{CWD} $ {content}\n{output}\n"
            f.write(s)

        cliff_print("Recalled this command and its output")

    elif show_recall:
        if recall_content == "":
            cliff_print("No recalled commands.")
        else:
            cliff_print("Recalled commands:")
            print(recall_content)

    elif clear_recall:
        with open(RECALL_FILE, "w") as f:
            f.write("")
        cliff_print("Cleared recalled commands.")

    # Run standard generation
    else:
        if len(llm.get_active_models()) == 0:
            cliff_print(
                """Welcome to Cliff! To get started, please either connect to an LLM provider by typing
                
cliff --config add [provider] [api-key]
                
or connect to a local model in Ollama by typing
                
cliff --config add ollama [model]
"""
            )
            sys.exit(0)

        if config["default_model"] is None and model_arg is None:
            cliff_print(
                """It looks like you haven't yet set a default model. You can set a default model by typing
                
cliff --config default-model [model]

Alternatively, you can call Cliff with a specific model by typing

cliff --model [model] [objective]
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
            model = str(config["default_model"])

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
            cliff_print(
                """Sorry, the LLM returned a bad or malformed response. If this
persists, try clearing Cliff's memory with cliff --memory clear, and
if that still doesn't work, try switching to a different model."""
            )


if __name__ == "__main__":  # pragma: no cover
    cliff_print("dev mode")
    main()
