parental_control
==========================


## Purpose
A Windows tool that checks the local weather, time restrictions and uptime. It shuts down the PC, if the weather is
good enough to play outside or if a prefined time is reached.


## How to build

	pyinstaller --noconsole -F --add-data "*.ico;." parental_control.py

## How to use

Add a new task in the windows task scheduler that runs the exe after login.

	Trigger: "At log on", Specific User
	Actions: Start a program, Add the full path to the exe and only the path, without quote in Start in