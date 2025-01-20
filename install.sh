#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

python3 -m venv "$DIR/venv"
source "$DIR/venv/bin/activate"
python3 -m pip install -r "$DIR/requirements.txt"
echo "[Cliff] Cliff's dependencies have been successfully installed. Run 'cliff' to get started."