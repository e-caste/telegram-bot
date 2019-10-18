# telegram-bot

## TL;DR
This is my personal Telegram bot. It's based on v11.1.0 of the [python-telegram-bot API](https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0).
Its main features are:
- get detailed status of bot host machine
- get picture and timelapse from a Raspberry Pi0W with a Raspberry Camera (files stored on NAS)
- subscribe/unsubscribe to timelapse notification every day at 8.30AM
- subscribe/unsubscribe independently to different Facebook pages events
- chatbot based on [this ML repository](https://github.com/daniel-kukiela/nmt-chatbot) and [this tutorial](https://pythonprogramming.net/chatbot-deep-learning-python-tensorflow/) (only available to select users since the host machine is currently a Raspberry Pi 3B+)
- other functions like random quotes, data about the user, and the current UNIX epoch

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
