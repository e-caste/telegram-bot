#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python-telegram-bot API examples at:
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

import logging
import os
import sys
from time import time
from multiprocessing import Process

from telegram import bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from nmt_chatbot.inference import inference

from pi_status import *
from parser import get_wiki_daily_quote
from robbamia import *
from button_commands import status, events_menu, webcam_menu, apt, pics_menu
from button_commands import subscribe_to_cercle_notifications, subscribe_to_supermarket_notifications, \
    subscribe_to_thedreamers_notifications, subscribe_to_webcam_notifications
from bot_utils import send_split_msgs, split_msg_for_telegram
from bot_utils import get_webcam_img, get_webcam_timelapse, webcam_sub, webcam_unsub, events_sub, \
    events_unsub, secs_per_picture, get_oldest_picture
from periodic_jobs import check_for_new_events, make_new_webcam_timelapse, send_timelapse_notification


DEBUG = sys.platform.startswith('darwin')  # True on macOS, False on Raspbian
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


# BEGIN COMMAND HANDLERS

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


# END COMMAND HANDLERS


# BEGIN BUTTON HANDLER w/ FUNCTIONS


def button(bot_obj, update):
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
            bot_obj.send_document(chat_id=int(id), document=open(log_path, 'rb'))
        elif query.data == 'tail_log':
            reply = get_log_tail()


        elif query.data == 'cercle':
            subscribe_to_cercle_notifications(bot_obj, update)
        elif query.data == 'thedreamers':
            subscribe_to_thedreamers_notifications(bot_obj, update)
        elif query.data == 'supermarket':
            subscribe_to_supermarket_notifications(bot_obj, update)
        elif query.data == 'back_to_events_menu':
            events_menu(bot_obj, update, use_callback=True)
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
            reply = events_sub(filenamestart, id)

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
            reply = events_unsub(filenamestart, id)


        elif query.data == 'fblink_cercle':
            reply = "Here is the link to the events page of Cercle:\nhttps://www.facebook.com/pg/cerclemusic/events/"

        elif query.data == 'fblink_thedreamers':
            reply = "Here is the link to the events page of TheDreamers:\nhttps://www.facebook.com/thedreamersrec/events/"

        elif query.data == 'fblink_super':
            reply = "Here is the link to the events page of Supermarket:\nhttps://www.facebook.com/pg/SupermarketTorino/events/"


        elif query.data == 'webcam_now':
            get_webcam_img(bot_obj, update)

        elif query.data == 'webcam_timelapse':
            get_webcam_timelapse(bot_obj, update)

        elif query.data == 'webcam_notification':
            subscribe_to_webcam_notifications(bot_obj, update)
        elif query.data == 'back_to_webcam_menu':
            webcam_menu(bot_obj, update, use_callback=True)
        elif query.data == 'webcam_sub':
            reply = webcam_sub(id)
        elif query.data == 'webcam_unsub':
            reply = webcam_unsub(id)

        elif query.data == 'pics_oldest':
            get_oldest_picture(bot_obj, update)
        elif query.data == 'pics_avg':
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


# END BUTTON HANDLER w/ FUNCTIONS


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
    dp.add_handler(CommandHandler("pics", pics_menu))
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
        Process(target=send_timelapse_notification, args=(bot.Bot(token), 8, 30, DEBUG))  # hour, minute
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()


if __name__ == '__main__':
    main()
