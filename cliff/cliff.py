import os
import sys
import json
import subprocess

from dotenv import load_dotenv
from l2m2.client import LLMClient
from l2m2.tools import PromptLoader

if __name__ == "__main__":
    from __init__ import __version__
else:
    from cliff import __version__

DIR = os.path.dirname(os.path.abspath(__file__))
RECALL_FILE = os.path.join(DIR, "resources", "cliff_recall")
MEM_FILE = os.path.join(DIR, "resources", "cliff_mem")
MAN_PAGE = os.path.join(DIR, "resources", "man_page.txt")

CWD = os.getcwd()
LS_OUTPUT = subprocess.run(["ls", "-al"], capture_output=True, text=True).stdout
OS_NAME = os.uname().sysname
OS_VERSION = os.uname().release

POSSIBLE_FLAGS = [
    "-v",
    "--version",
    "-r",
    "--recall",
    "-vr",
    "--view-recall",
    "-cr",
    "--clear-recall",
]

load_dotenv(os.path.expanduser("~/envs/llm"))

if os.getenv("OPENAI_API_KEY") is None:
    print(
        "[Cliff] OpenAI API key not found. Please ensure ~/envs/llm exists and has this value."
    )
    sys.exit(1)


def main() -> None:
    # parse args
    args = sys.argv[1:]
    if len(args) == 0:
        with open(MAN_PAGE, "r") as f:
            print(f.read().replace("{{version}}", __version__))
        sys.exit(0)
    flags = []
    while len(args) > 0 and args[0] in POSSIBLE_FLAGS:
        flags.append(args.pop(0))
    content = " ".join(args)
    view_version = "-v" in flags or "--version" in flags
    store_recall = "-r" in flags or "--recall" in flags
    view_recall = "-vr" in flags or "--view-recall" in flags
    clear_recall = "-cr" in flags or "--clear-recall" in flags

    # load recall content
    recall_content = ""
    if os.path.exists(RECALL_FILE):
        with open(RECALL_FILE, "r") as f:
            recall_content = f.read()
    else:
        with open(RECALL_FILE, "w") as f:
            f.write("")

    # Check for options
    if view_version:
        print(f"[Cliff] Version {__version__}")

    elif store_recall:
        print("[Cliff] Recalling this command and its output")
        result = subprocess.run(content.split(), capture_output=True, text=True).stdout
        print(result)

        with open(RECALL_FILE, "a") as f:
            s = f"{CWD} $ {content}\n{result}\n"
            f.write(s)

    elif view_recall:
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
                "os_name": OS_NAME,
                "os_version": OS_VERSION,
                "cwd": CWD,
                "ls_output": LS_OUTPUT,
                "recall_prompt": recall_prompt,
            },
        )

        llm = LLMClient()

        result = llm.call(
            model="gpt-4o",
            prompt=content,
            system_prompt=sysprompt,
            json_mode=True,
            timeout=25,
        )

        try:
            result_dict = json.loads(result)
            command = result_dict["command"]
            subprocess.run(
                ["pbcopy"],
                input=command,
                text=True,
            )
        except json.JSONDecodeError:
            command = "Error: Invalid JSON response from the LLM."

        print(command)


if __name__ == "__main__":
    print("[Cliff] dev mode")
    main()
