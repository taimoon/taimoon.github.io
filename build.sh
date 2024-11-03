#! /usr/bin/sh
if [ ! -d "venv" ]; then
    python3.12 -m venv ./venv
    pip3 install -r requirement.txt
fi
source ./venv/bin/activate
python3.12 format.py