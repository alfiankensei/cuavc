#!/bin/bash
#!/usr/bin/env python3

#export DISPLAY=:1 #needed if you are running a simple gui app.

cd "$(dirname "$0")"

process=api_voip
while true
do
    if ! ps aux | grep -v grep | grep 'python3 main.py' > /dev/null
    then #track1.py
        python3 main.py &
        sleep 10
    fi #track1.py

    if ! ps aux | grep -v grep | grep 'python3 serial_com.py' > /dev/null
    then #track1.py
        python3 serial_com.py &
        sleep 10
    fi #track1.py

    sleep 180
done
exit
