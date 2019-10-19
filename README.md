# telegram-bot

## TL;DR
This is my personal Telegram bot. It's based on v11.1.0 of the [python-telegram-bot API](https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0).
Its main features are:
- get detailed status of bot host machine
- get picture and timelapse from a Raspberry Pi0W equipped with a Raspberry Camera (files stored on NAS)
- subscribe/unsubscribe to timelapse notification every day at 8.30AM
- subscribe/unsubscribe independently to different Facebook pages events notifications at 9PM
- chatbot based on [this ML repository](https://github.com/daniel-kukiela/nmt-chatbot) and [this tutorial](https://pythonprogramming.net/chatbot-deep-learning-python-tensorflow/) (only available to select users since the host machine is currently a Raspberry Pi 3B+)
- other functions like random quotes, data about the user, and the current UNIX epoch

A screenshot | Another screenshot
-------------|--------------
![alt text](https://imgur.com/ibT5xCV.png) | ![alt text](https://imgur.com/XvAiT4H.png)

## File by file
### telegram_pi_bot.py
This is the main file. It handles different commands, makes the calls to the ML chatbot model and instantiates 4 parallel processes:
- the Telegram bot updater
- the process which checks for new FB events every 24 hours and sends the respective notifications at 9PM
- the process which asks via ssh the mbp2014 to make a new 24h timelapse
- the process which sends a notification with a .GIF version of the timelapse every 24 hours at 8.30AM

### evnt_ntfr.py
This file uses selenium (on macOS) or pyvirtualdisplay (on Raspbian) to instantiate a virtual browser (since requests cannot run Javascript and Facebook needs it to correctly load a page). The main and only function loads a webpage and checks for new event links: if they're not already in a local database, it sends a notification to all users who have subscribed to a certain event notification.

### pi0w_webcam_github.py - webcam.py - ffmpeg_mbp2014.py
The first file is the script that runs on a Raspberry Pi0W and takes a picture every select interval of time.
The second file is the interface between the Telegram bot and the NAS and mbp2014.
The third file is the one that runs every 24 hours, called by a bash script which is called via ssh by Raspberry Pi 3B+.

### pi_status.py
This file contains some system-level functions to monitor and exercise some control of the host machine. The /status command, which can only be used by an authorized Telegram chat ID, spawns a custom button keyboard that allows the user to select a function.

### parser.py
A not working version of the /wikiquote command, which usually produces funny outcomes. If fixed in the future, I think I'll keep this version for laughs.

## How to run
(Optional) Make virtual environment and activate it:  
`python3 -m venv venv`  
`source venv/bin/activate`  
Install requirements:  
`pip3 install -r requirements.txt`  
Launch script:  
`python3 telegram_pi_bot.py`  
(Optional) Deactivate venv once done:  
`deactivate`  

Also optional but useful are the 3 steps below:
- make a bash script (e.g. `launch_bot.sh`) with logging and nohup so that the bot can easily be launched from ssh
- make a bash script (e.g. `relaunch_bot.sh`) which stops the bot, updates the local repo with `git pull`, and calls the script above
- make a cron job which starts the launcher script @reboot
