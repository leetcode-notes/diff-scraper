#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo -e "You need to run this script with a root privilege."
    echo -e "$ \033[1;32msudo "$0"\033[0m"
    exit 1
fi

python3 -m pip install -r requirements.txt
