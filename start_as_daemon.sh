#!/bin/bash

cd "`dirname $0`"
pkill -f win_navigator.py
exec &>log.txt
python3 win_navigator.py & disown
