#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ "$#" -eq 1 ] && { [ "$1" == "-i" ] || [ "$1" == "--install" ]; }; then
    chmod +x "$DIR/install.sh"
    "$DIR/install.sh"
    exit 0
fi

source "$DIR/venv/bin/activate"
result=$(python3 "$DIR/cliff.py" "$@")
echo "$result"
echo "$result" | tr -d '\n' | pbcopy
