#! /usr/bin/sh
if [ ! -d "venv" ]; then
    python3 -m venv venv
    pip3 install -r requirement.txt
fi
source venv/bin/activate
python3 format.py