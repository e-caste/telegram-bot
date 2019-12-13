#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python-telegram-bot API examples at:
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

import logging
from telegram import bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from pi_status import *
from parser import get_wiki_daily_quote
from time import time, sleep
from robbamia import *
import evnt_ntfr
from datetime import datetime, timedelta
import os
from nmt_chatbot.inference import inference
import sys
import webcam
from multiprocessing import Process
from button_commands import status, events_menu, webcam_menu, apt
from button_commands import subscribe_to_cercle_notifications, subscribe_to_supermarket_notifications, \
    subscribe_to_thedreamers_notifications, subscribe_to_webcam_notifications

DEBUG = sys.platform.startswith('darwin')  # True on macOS, False on Raspbian
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def split_msg_for_telegram(string: str):
    chars_per_msg = 4096
    return [string[i:i + chars_per_msg] for i in range(0, len(string), chars_per_msg)]


def calculate_time_to_sleep(hour: int, minute: int = 0):
    # hour is before given hour -> wait until today at given hour and minute
    if int(datetime.now().time().strftime('%k')) < hour:
        time_to_sleep = int(
            (datetime.today().replace(hour=hour, minute=minute, second=0) - datetime.now()).total_seconds())
    # hour is equal to given hour
    elif int(datetime.now().time().strftime('%k')) == hour:
        # minute is before given minute -> wait until today at given time
        if int(datetime.now().time().strftime('%M')) < minute:
            time_to_sleep = int(
                (datetime.today().replace(hour=hour, minute=minute, second=0) - datetime.now()).total_seconds())
        # minute is after given minute -> wait until tomorrow at given time
        else:
            time_to_sleep = int(
                (datetime.today().replace(hour=hour, minute=minute, second=0) + timedelta(days=1)
                 - datetime.now()).total_seconds())
    # hour is after given hour -> wait until tomorrow at given time
    else:
        time_to_sleep = int(
            (datetime.today().replace(hour=hour, minute=minute, second=0) + timedelta(days=1)
             - datetime.now()).total_seconds())
    return time_to_sleep


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    bot.send_message(chat_id=update.message.chat_id, text='Hi ' + update.message.from_user.first_name +
                                                          ', welcome to SuperUselessBot 2.0, now '
                                                          'based on the python-telegram-bot API!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    bot.send_message(chat_id=update.message.chat_id, text='https://youtu.be/cueulBxn1Fw')


def chatbot(bot, update):
    # to reduce CPU strain and limit usage to known people
    if update.message.chat_id == int(castes_chat_id) or update.message.chat_id == int(gabbias_chat_id):
        nmt_result = inference(update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text=nmt_result['answers'][nmt_result['best_index']])


def secs_per_picture() -> str:
    """
    Return the average of seconds per picture taken by Raspberry Pi Zero W
    """
    pics = sorted([pic for pic in os.listdir(pics_nas_dir) if pic.endswith(".jpg")])
    pics_times = [datetime(year=int(pic[0:4]),
                           month=int(pic[5:7]),
                           day=int(pic[8:10]),
                           hour=int(pic[11:13]),
                           minute=int(pic[13:15]),
                           second=int(pic[15:17]))
                  for pic in pics]
    pics_timedeltas = [(pics_times[i + 1] - pics_times[i]).total_seconds()
                       for i in range(pics_times[:-1].__len__())]
    average_time_per_pic = sum(pics_timedeltas) / pics_timedeltas.__len__()
    return "The average time taken per picture is " + str(round(average_time_per_pic, 2)) + " seconds."


def button(bot, update):
    query = update.callback_query
    # id = context.callback_query.chat_instance
    id = str(update.callback_query.from_user.id)
    # print(id)
    reply = ""
    try:
        if query.data == 'uptime':
            reply = get_uptime()
        elif query.data == 'twlog':
            reply = get_ltl()
        elif query.data == 'ppy':
            reply = get_ppy()
        elif query.data == 'st':
            query.edit_message_text(text="This will take about 30 seconds. Checking speed...")
            reply = get_speedtest()
        elif query.data == 'lasdl':
            reply = get_lasdl()
        elif query.data == 'full':
            query.edit_message_text(text="This will take about 30 seconds. Checking status...")
            reply = get_status()
        elif query.data == "apt_update":
            query.edit_message_text(text="Updating...")
            reply = sudo_apt_update()
        elif query.data == "apt_list_u":
            reply = apt_list_upgradable()
        elif query.data == "apt_upgrade":
            query.edit_message_text(text="Upgrading...")
            reply = sudo_apt_upgrade()
        elif query.data == "temps":
            reply = get_cpu_gpu_temps()
        elif query.data == "df_h":
            reply = get_disk_usage()
        elif query.data == 'full_tg_log':
            tmp = os.listdir(tg_log_path)
            tmp.sort(key=str.casefold)
            log_path = tg_log_path + tmp[-1]
            bot.send_document(chat_id=int(id), document=open(log_path, 'rb'))
        elif query.data == 'tail_log':
            reply = get_log_tail()


        elif query.data == 'cercle':
            subscribe_to_cercle_notifications(bot, update)
        elif query.data == 'thedreamers':
            subscribe_to_thedreamers_notifications(bot, update)
        elif query.data == 'supermarket':
            subscribe_to_supermarket_notifications(bot, update)
        elif query.data == 'back_to_events_menu':
            events_menu(bot, update, use_callback=True)
        elif query.data == 'close_menu':
            reply = "Closed. ☠️"

        elif query.data.startswith("sub"):
            if "cercle" in query.data:
                filenamestart = "cercle"
            elif "thedreamers" in query.data:
                filenamestart = "thedreamers"
            elif "super" in query.data:
                filenamestart = "supermarket"
            else:
                print("No corresponding chat_ids file found")
                return
            with open(filenamestart + '_chat_ids.txt', 'r+') as db:
                ids = db.read()
                if id in ids:
                    reply = "You have already subscribed to the new " + filenamestart.capitalize() + " event notification!"
                else:
                    if ids == "":
                        db.write(id)
                    else:
                        db.seek(0)
                        db.write(ids + "\n" + id)
                        db.truncate()
                    reply = "You will now receive a notification when a new " + filenamestart.capitalize() + " event is available!"
                    print("SUBBED " + filenamestart + " " + id)

        elif query.data.startswith("unsub"):
            if "cercle" in query.data:
                filenamestart = "cercle"
            elif "thedreamers" in query.data:
                filenamestart = "thedreamers"
            elif "super" in query.data:
                filenamestart = "supermarket"
            else:
                print("No corresponding chat_ids file found")
                return
            with open(filenamestart + '_chat_ids.txt', 'r+') as db:
                ids = db.read()
                if id not in ids:
                    reply = "You are not yet subscribed to notifications."
                else:
                    db.seek(0)
                    for line in ids.splitlines():
                        if id not in line:
                            db.write(line)
                    db.truncate()
                    reply = "You  won't receive any more notifications."
                    print("UNSUBBED " + filenamestart + " " + id)


        elif query.data == 'fblink_cercle':
            reply = "Here is the link to the events page of Cercle:\nhttps://www.facebook.com/pg/cerclemusic/events/"

        elif query.data == 'fblink_thedreamers':
            reply = "Here is the link to the events page of TheDreamers:\nhttps://www.facebook.com/thedreamersrec/events/"

        elif query.data == 'fblink_super':
            reply = "Here is the link to the events page of Supermarket:\nhttps://www.facebook.com/pg/SupermarketTorino/events/"


        elif query.data == 'webcam_now':
            get_webcam_img(bot, update)

        elif query.data == 'webcam_timelapse':
            get_webcam_timelapse(bot, update)

        elif query.data == 'webcam_notification':
            subscribe_to_webcam_notifications(bot, update)
        elif query.data == 'back_to_webcam_menu':
            webcam_menu(bot, update, use_callback=True)
        elif query.data == 'webcam_sub':
            with open('webcam_chat_ids.txt', 'r+') as db:
                ids = db.read()
                if id in ids:
                    reply = "You have already subscribed to the 8.30a.m. timelapse notification!"
                else:
                    if ids == "":
                        db.write(id)
                    else:
                        db.seek(0)
                        db.write(ids + "\n" + id)
                        db.truncate()
                    reply = "You will now receive the timelapse of the day before every day at 8.30a.m."
                    print("SUBBED webcam " + id)

        elif query.data == 'webcam_unsub':
            with open('webcam_chat_ids.txt', 'r+') as db:
                ids = db.read()
                if id not in ids:
                    reply = "You are not yet subscribed to notifications."
                else:
                    db.seek(0)
                    for line in ids.splitlines():
                        if id not in line:
                            db.write(line)
                    db.truncate()
                    reply = "You  won't receive any more notifications."
                    print("UNSUBBED webcam " + id)

        elif query.data == 'time_per_pic':
            reply = secs_per_picture()

        if reply != "":
            split_reply = split_msg_for_telegram(reply)
            query.edit_message_text(text=split_reply[0])
            send_split_msgs(bot.Bot(token), split_reply[1:])
        else:
            query.message.delete()  # TODO: should use query.edit_message_reply_markup() but "too many chat_ids were given"

    except Exception as e:
        query.edit_message_text(text=str(e))
        print(e)


def send_split_msgs(bot, string_list):
    try:
        for string in string_list:
            bot.send_message(chat_id=castes_chat_id, text=string)

    except Exception as e:
        print("send_split_msgs")
        print(e)


def check_for_new_events(bot, hour: int):
    while True:
        try:
            time_to_sleep = calculate_time_to_sleep(hour=hour)

            print("Waiting to check for new events... " + str(time_to_sleep))
            sleep(time_to_sleep)

            # the order must be the same as in evnt_ntfr.py
            chat_ids_list = [
                'supermarket_chat_ids.txt',
                'cercle_chat_ids.txt',
                'thedreamers_chat_ids.txt'
            ]
            os.chdir(raspi_wd)
            links, texts, event_names = evnt_ntfr.main()
            if links is not None and texts is not None:
                for links_list, text_list, chat_ids, event_name in zip(links, texts, chat_ids_list, event_names):
                    with open(chat_ids, 'r') as ids:
                        for id in ids.readlines():
                            for link, text in zip(links_list, text_list):
                                try:
                                    bot.send_message(chat_id=id,
                                                     text="New " + event_name.capitalize() + " event:\n" + text + "\n" + link)
                                    print("Sent " + event_name + " " + link + " to " + id)
                                except Exception as e:
                                    print(e, file=sys.stderr)
            elif links is not None and texts is None:
                for links_list, chat_ids, event_name in zip(links, chat_ids_list, event_names):
                    with open(chat_ids, 'r') as ids:
                        for id in ids.readlines():
                            for link in links_list:
                                try:
                                    bot.send_message(chat_id=id,
                                                     text="New " + event_name.capitalize() + " event:\n" + link)
                                    print("Sent " + event_name + " " + link + " to " + id)
                                except Exception as e:
                                    print(e, file=sys.stderr)

        except Exception as e:
            print(e, file=sys.stderr)


def get_webcam_img(bot, update):
    img_name, folder = webcam.get_last_img_name()
    if folder:
        path_name = folder + "/" + img_name
    else:
        path_name = img_name
    bot.send_photo(chat_id=update.callback_query.message.chat_id,
                   photo=open(webcam_path + path_name, 'rb'),
                   caption=img_name)


def get_webcam_timelapse(bot, update):
    yesterday = webcam.get_yesterday_timelapse_video_name()
    bot.send_video(chat_id=update.callback_query.message.chat_id,
                   video=open(webcam_path + yesterday + "/" + yesterday + "_for_tg.mp4", 'rb'),
                   caption=yesterday,
                   timeout=6000)


def make_new_webcam_timelapse(hour: int, minute: int):
    while True:
        try:
            time_to_sleep = calculate_time_to_sleep(hour=hour, minute=minute)

            print("Waiting to make timelapse... " + str(time_to_sleep))
            sleep(time_to_sleep)

            # this function also makes the new video from the images
            yesterday = webcam.get_yesterday_timelapse_video_name()
            print("\nMade new timelapse of " + yesterday + "\n")

        except Exception as e:
            print(e, file=sys.stderr)


def send_timelapse_notification(bot, hour: int, minute: int):
    while True:
        try:
            time_to_sleep = calculate_time_to_sleep(hour=hour, minute=minute)
            print("Waiting to send timelapse... " + str(time_to_sleep))
            sleep(time_to_sleep)

            if not DEBUG:
                os.chdir(raspi_wd)
            # the video should have already been made by the function above, so it immediately returns yesterday
            yesterday = webcam.get_yesterday_timelapse_video_name()
            with open('webcam_chat_ids.txt', 'r') as ids:
                for id in ids.readlines():
                    bot.send_video(chat_id=id,
                                   video=open(webcam_path + yesterday + "/" + yesterday + "_for_tg.mp4", 'rb'),
                                   caption="Here's the timelapse of yesterday! - " + yesterday,
                                   timeout=6000,
                                   supports_streaming=True)
                    print("Sent timelapse to " + id)

        except Exception as e:
            print(e, file=sys.stderr)


def epoch(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(int(time())))


def whoyouare(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.from_user))


def quote(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=fortune())


def wiki_quote(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=get_wiki_daily_quote())


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', bot, update.error)


def main():
    if not DEBUG:
        # if on Raspberry Pi:
        os.chdir(raspi_wd)

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("events", events_menu))
    dp.add_handler(CommandHandler("rivoli", webcam_menu))
    dp.add_handler(CommandHandler("apt", apt))
    dp.add_handler(CommandHandler("epoch", epoch))
    dp.add_handler(CommandHandler("whoami", whoyouare))
    dp.add_handler(CommandHandler("quote", quote))
    dp.add_handler(CommandHandler("wikiquote", wiki_quote))
    dp.add_handler(CommandHandler("help", help))

    # inline messages handler
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(InlineQueryHandler(inlinequery))

    # on noncommand i.e. any text message: reply to the message on Telegram with a ML algorithm
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.text, chatbot))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.

    # threading limits the number of concurrent threads to 2
    # using multiprocessing
    processes = [
        Process(target=updater.idle),
        Process(target=check_for_new_events, args=(bot.Bot(token), 21)),  # hour
        Process(target=make_new_webcam_timelapse, args=(0, 1)),  # hour, minute
        Process(target=send_timelapse_notification, args=(bot.Bot(token), 8, 30))  # hour, minute
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()


if __name__ == '__main__':
    main()
