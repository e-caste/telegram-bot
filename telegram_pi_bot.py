#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python-telegram-bot API examples at:
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

import logging
import os
import sys
from time import time
from datetime import time as dayhour
import pytz

from telegram import bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, \
    JobQueue
# from nmt_chatbot.inference import inference

DEBUG = sys.platform.startswith('darwin')  # True on macOS, False on Linux
if DEBUG:
    from robbamia import debug_token as token, castes_chat_id
    os.environ["TOKEN"] = token
    os.environ["CST_CID"] = castes_chat_id
    os.environ["LOG_PATH"] = "logs"
    os.environ["PICS_DIR"] = "pics"

from pi_status import *
# from parser import get_wiki_daily_quote
from button_commands import status, events_menu, webcam_menu, apt, pics_menu, cirulla_menu, quadris_tridimensionale_menu
from button_commands import subscribe_to_cercle_notifications, subscribe_to_supermarket_notifications, \
    subscribe_to_thedreamers_notifications, subscribe_to_webcam_notifications
from bot_utils import send_split_msgs, split_msg_for_telegram
from bot_utils import get_webcam_img, get_webcam_timelapse, webcam_sub, webcam_unsub, events_sub, \
    events_unsub, secs_per_picture, get_oldest_picture, get_available_timelapses, recover_past_days, cirulla_add, \
    cirulla_remove, cirulla_points, cirulla_plot, quadris_tridimensionale_add, quadris_tridimensionale_remove, \
    quadris_tridimensionale_points, quadris_tridimensionale_plot
from periodic_jobs import check_for_new_events, make_new_webcam_timelapse, send_timelapse_notification

# import Docker environment variables
token = os.environ["TOKEN"]
castes_chat_id = os.environ["CST_CID"]
log_path = os.environ["LOG_PATH"]
pics_dir = os.environ["PICS_DIR"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# BEGIN COMMAND HANDLERS

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    context.bot.send_message(chat_id=update.message.chat_id, text='Hi ' + update.message.from_user.first_name +
                                                          ', welcome to SuperUselessBot 2.0, now '
                                                          'based on the python-telegram-bot API!')


def help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    context.bot.send_message(chat_id=update.message.chat_id, text='https://youtu.be/cueulBxn1Fw')


def chatbot(update: Update, context: CallbackContext) -> None:
    ...
    # to reduce CPU strain and limit usage to known people
    # if update.message.chat_id == int(castes_chat_id) or update.message.chat_id == int(gabbias_chat_id):
    #     nmt_result = inference(update.message.text)
    #     context.bot.send_message(chat_id=update.message.chat_id, text=nmt_result['answers'][nmt_result['best_index']])


def epoch(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.message.chat_id, text=str(int(time())))


def whoyouare(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.message.chat_id, text=str(update.message.from_user))


def quote(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.message.chat_id, text=fortune())


def wiki_quote(update: Update, context: CallbackContext) -> None:
    ...
    # context.bot.send_message(chat_id=update.message.chat_id, text=get_wiki_daily_quote())


def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# END COMMAND HANDLERS


# BEGIN BUTTON HANDLER w/ FUNCTIONS


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    # id = context.callback_query.chat_instance
    id = str(update.callback_query.from_user.id)
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
            tmp = os.listdir(log_path)
            tmp.sort(key=str.casefold)
            lp = log_path + tmp[-1]
            context.bot.send_document(chat_id=int(id), document=open(lp, 'rb'))
        elif query.data == 'tail_log':
            reply = get_log_tail()


        elif query.data == 'cercle':
            subscribe_to_cercle_notifications(update, context)
        elif query.data == 'thedreamers':
            subscribe_to_thedreamers_notifications(update, context)
        elif query.data == 'supermarket':
            subscribe_to_supermarket_notifications(update, context)
        elif query.data == 'back_to_events_menu':
            events_menu(update, context, use_callback=True)
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
            get_webcam_img(update, context)

        elif query.data == 'webcam_timelapse':
            get_webcam_timelapse(update, context)

        elif query.data == 'webcam_notification':
            subscribe_to_webcam_notifications(update, context)
        elif query.data == 'back_to_webcam_menu':
            webcam_menu(update, context, use_callback=True)
        elif query.data == 'webcam_sub':
            reply = webcam_sub(id)
        elif query.data == 'webcam_unsub':
            reply = webcam_unsub(id)

        elif query.data == 'pics_oldest':
            get_oldest_picture(update, context)
        elif query.data == 'pics_script':
            reply = "Trust the system."
            # ssh_recover = Thread(target=recover_past_days, args=(update,))
            # ssh_recover.start()
        elif query.data == 'pics_avg':
            reply = secs_per_picture()
        elif query.data == 'pics_timelapses':
            reply = get_available_timelapses()

        elif query.data == 'cirulla_add':
            reply = "To add a result, text /cirulla <num1>[*]<num2>"
        elif query.data == 'cirulla_remove':
            reply = cirulla_remove()
        elif query.data == 'cirulla_points':
            reply = cirulla_points()
        elif query.data == 'cirulla_plot':
            cirulla_plot(context, id)

        elif query.data == 'qt_add':
            reply = "To add a result, text /qt (e|c) <pts>"
        elif query.data == 'qt_rules':
            reply = "\n - ".join([
                "Vittoria base: 100 punti",
                "sulla base: +50",
                "colonna: +50",
                "te lo deve dire l'altro: -50",
                "N vittorie contemporanee: *N",
            ])
        elif query.data == 'qt_remove':
            reply = quadris_tridimensionale_remove()
        elif query.data == 'qt_points':
            reply = quadris_tridimensionale_points()
        elif query.data == 'qt_plot':
            quadris_tridimensionale_plot(context, id)

        if reply != "":
            split_reply = split_msg_for_telegram(reply)
            query.edit_message_text(text=split_reply[0])
            send_split_msgs(bot.Bot(token), split_reply[1:])
        else:
            query.message.delete()  # TODO: should use query.edit_message_reply_markup() but "too many chat_ids were given"

    except Exception as e:
        query.edit_message_text(text=str(e))
        logger.error(e, exc_info=True)


# END BUTTON HANDLER w/ FUNCTIONS


def main():
    os.chdir("data")

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token)
    job_queue: JobQueue = updater.job_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("pics", pics_menu))
    dp.add_handler(CommandHandler("events", events_menu))
    dp.add_handler(CommandHandler("rivoli", webcam_menu))
    dp.add_handler(CommandHandler("cirulla", cirulla_menu))
    dp.add_handler(CommandHandler("qt", quadris_tridimensionale_menu))
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

    # processes = [
    #     Process(target=updater.idle),
    #     # Process(target=check_for_new_events, args=(bot.Bot(token), 21)),  # hour
    #     # Process(target=make_new_webcam_timelapse, args=(0, 1)),  # hour, minute
    #     Process(target=send_timelapse_notification, args=(bot.Bot(token), 8, 30, DEBUG))  # hour, minute
    # ]
    job_queue.run_daily(send_timelapse_notification,
                        time=dayhour(hour=8, minute=30, tzinfo=pytz.timezone("Europe/Rome")))

    updater.idle()


if __name__ == '__main__':
    main()
