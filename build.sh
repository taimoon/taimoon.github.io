#! /usr/bin/sh
if [ ! -d "venv" ]; then
    python3 -m venv venv
    pip3 install -r requirements.txt
fi
source venv/bin/activate
python3 format.py