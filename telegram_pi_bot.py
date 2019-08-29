#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"https://it.wikiquote.org/w/api.php?action=featuredfeed&feed=qotd"

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from uuid import uuid4
import logging
from telegram import bot, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, \
    InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    InlineQueryHandler
from pi_status import *
from parser import get_wiki_daily_quote
from time import time, sleep
from robbamia import *
import threading
import evnt_ntfr
from datetime import datetime, timedelta
import os
from nmt_chatbot.inference import inference
import sys
import webcam

if sys.platform.startswith('darwin'):
    DEBUG = True
else:
    DEBUG = False

def split_msg_for_telegram(string: str):
    chars_per_msg = 4096
    return [string[i:i + chars_per_msg] for i in range(0, len(string), chars_per_msg)]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

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


# def echo(bot, update):
#     """Echo the user message."""
#     bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def chatbot(bot, update):
    # to reduce CPU strain and limit usage to known people
    if update.message.chat_id == int(castes_chat_id) or update.message.chat_id == int(gabbias_chat_id):
        nmt_result = inference(update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text=nmt_result['answers'][nmt_result['best_index']])


def status(bot, update):
    # bot.send_message(chat_id=update.message.chat_id, text="This will take about 30 seconds. Checking status...")
    # bot.send_message(chat_id=update.message.chat_id, text=get_status())

    # only accept input if user is caste
    if str(update.message.chat_id) == castes_chat_id:
        # each [] is a line
        keyboard = [
                    [InlineKeyboardButton("uptime", callback_data='uptime'), InlineKeyboardButton("ltl", callback_data='twlog')],
                    [InlineKeyboardButton("ppy", callback_data='ppy'), InlineKeyboardButton("speedtest", callback_data='st')],
                    [InlineKeyboardButton("lasdl", callback_data='lasdl'), InlineKeyboardButton("python3 pi_status.py", callback_data='full')],
                    [InlineKeyboardButton("./check_cpu_gpu_temps.sh", callback_data="temps"), InlineKeyboardButton("df -h", callback_data="df_h")],
                    [InlineKeyboardButton("full tg bot log", callback_data='full_tg_log')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('pi@raspberrypi ~ $', reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="⚠️ You don't have permission to use the /status command.")

def apt(bot, update):
    if str(update.message.chat_id) == castes_chat_id:
        keyboard = [
            [InlineKeyboardButton("sudo apt update", callback_data="apt_update")],
            [InlineKeyboardButton("apt list -u", callback_data="apt_list_u")],
            [InlineKeyboardButton("sudo apt upgrade", callback_data="apt_upgrade")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('pi@raspberrypi ~ $', reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="⚠️ You don't have permission to use the /apt command.")

def events_menu(bot, update, use_callback : bool = False):
    keyboard = [
        [InlineKeyboardButton("Cercle", callback_data='cercle')],
        [InlineKeyboardButton("TheDreamers", callback_data='thedreamers')],
        [InlineKeyboardButton("Supermarket", callback_data='supermarket')],
        [InlineKeyboardButton("Close ❌", callback_data='close_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if use_callback:
        update.callback_query.message.reply_text('Choose which event you want to receive notifications about:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Choose which event you want to receive notifications about:', reply_markup=reply_markup)

def subscribe_to_cercle_notifications(bot, update):
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='sub_cercle'), InlineKeyboardButton("Unsubscribe", callback_data='unsub_cercle')],
        [InlineKeyboardButton("Link to Facebook page of Cercle", callback_data='fblink_cercle')],
        [InlineKeyboardButton("Back", callback_data='back_to_events_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)

def subscribe_to_thedreamers_notifications(bot, update):
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='sub_thedreamers'), InlineKeyboardButton("Unsubscribe", callback_data='unsub_thedreamers')],
        [InlineKeyboardButton("Link to Facebook page of TheDreamers", callback_data='fblink_thedreamers')],
        [InlineKeyboardButton("Back", callback_data='back_to_events_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)

def subscribe_to_supermarket_notifications(bot, update):
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='sub_super'), InlineKeyboardButton("Unsubscribe", callback_data='unsub_super')],
        [InlineKeyboardButton("Link to Facebook page of Supermarket", callback_data='fblink_super')],
        [InlineKeyboardButton("Back", callback_data='back_to_events_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)

def webcam_menu(bot, update):
    keyboard = [
        [InlineKeyboardButton("📷 Right Now", callback_data='webcam_now')],
        [InlineKeyboardButton("📽 Timelapse of yesterday", callback_data='webcam_timelapse')],
        [InlineKeyboardButton("❌ Close", callback_data='close_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose an option:", reply_markup=reply_markup)

# context is an Update object!
def button(bot_obj, context):
    query = context.callback_query
    # id = context.callback_query.chat_instance
    id = str(context.callback_query.from_user.id)
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
            bot_obj.send_document(chat_id=int(id), document=open(log_path, 'rb'))


        elif query.data == 'cercle':
            subscribe_to_cercle_notifications(bot_obj, context)
        elif query.data == 'thedreamers':
            subscribe_to_thedreamers_notifications(bot_obj, context)
        elif query.data == 'supermarket':
            subscribe_to_supermarket_notifications(bot_obj, context)
        elif query.data == 'back_to_events_menu':
            events_menu(bot_obj, context, use_callback=True)
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
            get_webcam_img(bot_obj, context)

        elif query.data == 'webcam_timelapse':
            get_webcam_timelapse(bot_obj, context)

        if reply != "":
            split_reply = split_msg_for_telegram(reply)
            query.edit_message_text(text=split_reply[0])
            send_split_msgs(bot.Bot(token), split_reply[1:])
        else:
            query.message.delete() # TODO: should use query.edit_message_reply_markup() but "too many chat_ids were given"

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
            if int(datetime.now().time().strftime('%k')) < hour:
                time_to_sleep = int((datetime.today().replace(hour=0, minute=0, second=0) + timedelta(hours=hour) - datetime.now()).total_seconds())
                # time_to_sleep = int((datetime.today().replace(hour=0, minute=0, second=0) + timedelta(hours=9, minutes=21) - datetime.now()).total_seconds())
                print(time_to_sleep)
                sleep(time_to_sleep)
            else:
                time_to_sleep = int((datetime.today().replace(hour=0, minute=0, second=0) + timedelta(days=1, hours=hour) - datetime.now()).total_seconds())
                print(time_to_sleep)
                sleep(time_to_sleep)

            chat_ids_list = [
                'cercle_chat_ids.txt',
                'thedreamers_chat_ids.txt',
                'supermarket_chat_ids.txt'
            ]
            links, texts = evnt_ntfr.main()
            if links is not None and texts is not None:
                for links_list, text_list, chat_ids in zip(links, texts, chat_ids_list):
                    with open(chat_ids, 'r') as ids:
                        for id in ids.readlines():
                            for link, text in zip(links_list, text_list):
                                try:
                                    bot.send_message(chat_id=id, text=text+"\n"+link)
                                    print("Sent " + link + " to " + id)
                                except Exception as e:
                                    print(e, file=sys.stderr)
            elif links is not None and texts is None:
                for links_list, chat_ids in zip(links, chat_ids_list):
                    with open(chat_ids, 'r') as ids:
                        for id in ids.readlines():
                            for link in links_list:
                                try:
                                    bot.send_message(chat_id=id, text=link)
                                    print("Sent " + link + " to " + id)
                                except Exception as e:
                                    print(e, file=sys.stderr)

        except Exception as e:
            print(e)

# THIS IS NOT FOR CONTEXTUAL BUTTONS: THIS IS FOR SUMMONING THE BOT BY @ING IT
# def inlinequery(update, context):
#     """Handle the inline query."""
#     query = update.inline_query.query
#     results = [
#         InlineQueryResultArticle(
#             id=uuid4(),
#             title="Caps",
#             input_message_content=InputTextMessageContent(
#                 query.upper())),
#         InlineQueryResultArticle(
#             id=uuid4(),
#             title="Bold",
#             input_message_content=InputTextMessageContent(
#                 "*{}*")),
#         InlineQueryResultArticle(
#             id=uuid4(),
#             title="Italic",
#             input_message_content=InputTextMessageContent(
#                 "_{}_"))]
#
#     update.inline_query.answer(results)

def get_webcam_img(bot, update):
    img_name = webcam.get_last_img_name()
    bot.send_photo(chat_id=update.message.chat_id, photo=open(webcam_path + img_name, 'rb'),
                   caption=img_name)

def get_webcam_timelapse(bot, update):
    yesterday = webcam.get_yesterday_timelapse_video_name()
    bot.send_video(chat_id=update.message.chat_id, video=open(webcam_path + yesterday + "/" + yesterday + ".mp4", 'rb'),
                   caption=yesterday)

def epoch(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(int(time())))

def whoyouare(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.from_user))

def tail_log(bot, update):
    if str(update.message.chat_id) == castes_chat_id:
        bot.send_message(chat_id=update.message.chat_id, text=get_log_tail())
    else:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You don't have permission to use the /log command.")

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
    dp.add_handler(CommandHandler("log", tail_log))
    dp.add_handler(CommandHandler("quote", quote))
    dp.add_handler(CommandHandler("wikiquote", wiki_quote))
    dp.add_handler(CommandHandler("help", help))

    # inline messages handler
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(InlineQueryHandler(inlinequery))

    # on noncommand i.e message - reply to the message on Telegram with a ML algorithm
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.text, chatbot))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()

    t1 = threading.Thread(target=updater.idle)
    t2 = threading.Thread(target=check_for_new_events(bot.Bot(token), hour=21))

    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
