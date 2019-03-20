#!/bin/bash

cd /home/pi/castes-scripts/telegram-bot/logs && tail -10 "$(ls | tail -1)" && cd -