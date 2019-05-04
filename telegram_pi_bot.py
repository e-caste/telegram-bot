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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, \
    InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    InlineQueryHandler
from pi_status import *
from parser import get_wiki_daily_quote

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
    # bot.send_message(chat_id=update.message.chat_id, text="This will take about 30 seconds. Checking status...")
    # bot.send_message(chat_id=update.message.chat_id, text=get_status())
    # each [] is a line
    keyboard = [[InlineKeyboardButton("uptime", callback_data='uptime'), InlineKeyboardButton("ltl", callback_data='twlog')],
                [InlineKeyboardButton("ppy", callback_data='ppy'), InlineKeyboardButton("speedtest", callback_data='st')],
                [InlineKeyboardButton("lasdl", callback_data='lasdl'), InlineKeyboardButton("python3 pi_status.py", callback_data='full')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('pi@raspberrypi ~ $', reply_markup=reply_markup)

def button(update, context):
    query = context.callback_query
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
        query.edit_message_text(text=reply)
    except Exception as e:
        query.edit_message_text(text=str(e))

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
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.date))

def whoyouare(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.from_user))

def tail_log(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=get_log_tail())

def quote(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=fortune())

def wiki_quote(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=get_wiki_daily_quote())


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
    dp.add_handler(CommandHandler("quote", quote))
    dp.add_handler(CommandHandler("wikiquote", wiki_quote))

    # inline messages handler
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(InlineQueryHandler(inlinequery))

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