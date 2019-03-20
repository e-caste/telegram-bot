#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

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

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pi_status import get_status, get_log_tail

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


def echo(bot, update):
    """Echo the user message."""
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def status(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="This will take about 30 seconds. Checking status...")
    bot.send_message(chat_id=update.message.chat_id, text=get_status())

def epoch(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.date))

def whoyouare(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.from_user))

def tail_log(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=get_log_tail())

def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', bot, update.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("798083745:AAHqys98knTzCWp2_otxe4i9ex98HJx5JO4")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("epoch", epoch))
    dp.add_handler(CommandHandler("whoami", whoyouare))
    dp.add_handler(CommandHandler("log", tail_log))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

# !!! OLDER VERSION BELOW       !!!
# !!! DO NOT USE, NOT WORKING   !!!
# PRESERVED FOR THE FUTURE, IN CASE I FORGET ABOUT THE RIGHT COMMANDS

# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # This program is dedicated to the public domain under the CC0 license.
# #
# # THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# # If you're still using version 11.1.0, please see the examples at
# # https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples
#
# """
# Simple Bot to reply to Telegram messages.
#
# First, a few handler functions are defined. Then, those functions are passed to
# the Dispatcher and registered at their respective places.
# Then, the bot is started and runs until we press Ctrl-C on the command line.
#
# Usage:
# Basic Echobot example, repeats messages.
# Press Ctrl-C on the command line or send a signal to the process to stop the
# bot.
# """
#
# import logging
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# from pi_status import get_status
#
# # Enable logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
#
# logger = logging.getLogger(__name__)
#
#
# # Define a few command handlers. These usually take the two arguments bot and
# # update. Error handlers also receive the raised TelegramError object in error.
# def start(update, context):
#     """Send a message when the command /start is issued."""
#     update.message.reply_text('Hi ' + update.message.from_user.first_name + ', welcome to SuperUselessBot 2.0, now '
#                                                                             'based on the python-telegram-bot API!')
#
#
# def help(update, context):
#     """Send a message when the command /help is issued."""
#     update.message.reply_text('https://youtu.be/cueulBxn1Fw')
#
#
# def echo(update, context):
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)
#
# def status(update):
#     update.message.reply_text("This will take about 20 seconds. Checking status...")
#     update.message.reply_text(get_status())
#
# def epoch(update):
#     update.message.reply_text(update.message.date)
#
# def whoyouare(update):
#     update.message.reply_text(str(update.message.from_user))
#
# def error(update, context):
#     """Log Errors caused by Updates."""
#     logger.warning('Update "%s" caused error "%s"', update, context.error)
#
#
# def main():
#     """Start the bot."""
#     # Create the Updater and pass it your bot's token.
#     # Make sure to set use_context=True to use the new context based callbacks
#     # Post version 12 this will no longer be necessary
#     updater = Updater("798083745:AAHqys98knTzCWp2_otxe4i9ex98HJx5JO4")
#
#     # Get the dispatcher to register handlers
#     dp = updater.dispatcher
#
#     # on different commands - answer in Telegram
#     dp.add_handler(CommandHandler("start", start))
#     dp.add_handler(CommandHandler("help", help))
#     dp.add_handler(CommandHandler("status", status))
#     dp.add_handler(CommandHandler("epoch", epoch))
#     dp.add_handler(CommandHandler("whoami", whoyouare))
#
#     # on noncommand i.e message - echo the message on Telegram
#     dp.add_handler(MessageHandler(Filters.text, echo))
#
#     # log all errors
#     dp.add_error_handler(error)
#
#     # Start the Bot
#     updater.start_polling()
#
#     # Run the bot until you press Ctrl-C or the process receives SIGINT,
#     # SIGTERM or SIGABRT. This should be used most of the time, since
#     # start_polling() is non-blocking and will stop the bot gracefully.
#     updater.idle()
#
#
# if __name__ == '__main__':
#     main()