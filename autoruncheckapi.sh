#!/bin/bash
#!/usr/bin/env python3

#export DISPLAY=:1 #needed if you are running a simple gui app.

cd "$(dirname "$0")"
if ! ps aux | grep -v grep | grep 'python3 checklogapi.py' > /dev/null
then #track1.py
    python3 checklogapi.py &
fi #track1.py
exit
