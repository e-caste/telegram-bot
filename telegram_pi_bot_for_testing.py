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
import cercle_evnt_ntfr
# import cercle_evnt_ntfr_for_pi # TODO: uncomment
from datetime import datetime, timedelta
import os
from nmt_chatbot.inference import inference

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
                    [InlineKeyboardButton("sudo apt update", callback_data="apt_update"), InlineKeyboardButton("apt list -u", callback_data="apt_list_u")],
                    [InlineKeyboardButton("sudo apt upgrade", callback_data="apt_upgrade"), InlineKeyboardButton("./check_cpu_gpu_temps.sh", callback_data="temps")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('pi@raspberrypi ~ $', reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="⚠️ You don't have permission to use the /status command.")

def subscribe_to_cercle_notifications(bot, update):
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='sub'), InlineKeyboardButton("Unsubscribe", callback_data='unsub')],
        [InlineKeyboardButton("Link to Facebook page of Cercle", callback_data='fblink')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose an option:', reply_markup=reply_markup)

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

        elif query.data == 'sub':
            with open('cercle_chat_ids.txt', 'r+') as db:
                ids = db.read()
                if id in ids:
                    reply = "You have already subscribed to the new Cercle event notification!"
                else:
                    if ids == "":
                        db.write(id)
                    else:
                        db.seek(0)
                        db.write(ids + "\n" + id)
                        db.truncate()
                    reply = "You will now receive a notification when a new Cercle event is available!"
                    print("SUBBED " + id)

        elif query.data == 'unsub':
            with open('cercle_chat_ids.txt', 'r+') as db:
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
                    print("UNSUBBED " + id)

        elif query.data == 'fblink':
            reply = "Here is the link to the events page of Cercle:\nhttps://www.facebook.com/pg/cerclemusic/events/"

        split_reply = split_msg_for_telegram(reply)
        query.edit_message_text(text=split_reply[0])
        send_split_msgs(bot.Bot(token), split_reply[1:])

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


def check_for_new_cercle_events(bot):
    while True:
        try:
            if int(datetime.now().time().strftime('%k')) < 21:
                time_to_sleep = int((datetime.today().replace(hour=0, minute=0, second=0) + timedelta(hours=21) - datetime.now()).total_seconds())
                # time_to_sleep = int((datetime.today().replace(hour=0, minute=0, second=0) + timedelta(hours=9, minutes=21) - datetime.now()).total_seconds())
                print(time_to_sleep)
                sleep(time_to_sleep)
            else:
                time_to_sleep = int((datetime.today().replace(hour=0, minute=0, second=0) + timedelta(days=1, hours=21) - datetime.now()).total_seconds())
                print(time_to_sleep)
                sleep(time_to_sleep)

            # links, texts = cercle_evnt_ntfr.main()
            # on Raspberry Pi:
            links, texts = cercle_evnt_ntfr.main()
            if links is not None and texts is not None:
                with open('cercle_chat_ids.txt', 'r') as ids:
                    for id in ids.readlines():
                        for link, text in zip(links, texts):
                            bot.send_message(chat_id=id, text=text+"\n"+link)
            elif links is not None and texts is None:
                with open('cercle_chat_ids.txt', 'r') as ids:
                    for id in ids.readlines():
                        for link in links:
                            bot.send_message(chat_id=id, text=link)

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
    # if on Raspberry Pi:
    # os.chdir('/home/pi/castes-scripts/telegram-bot') # TODO: uncomment

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("cercle", subscribe_to_cercle_notifications))
    dp.add_handler(CommandHandler("epoch", epoch))
    dp.add_handler(CommandHandler("whoami", whoyouare))
    dp.add_handler(CommandHandler("log", tail_log))
    dp.add_handler(CommandHandler("quote", quote))
    dp.add_handler(CommandHandler("wikiquote", wiki_quote))

    # inline messages handler
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(InlineQueryHandler(inlinequery))

    # on noncommand i.e message - echo the message on Telegram
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
    t2 = threading.Thread(target=check_for_new_cercle_events(bot.Bot(token)))

    t1.start()
    t2.start()


if __name__ == '__main__':
    main()