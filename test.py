# docs at https://github.com/eternnoir/pyTelegramBotAPI

import logging
from time import sleep
import telebot as tb
from pi_status import get_status

# bot definition
bot = tb.TeleBot("798083745:AAHqys98knTzCWp2_otxe4i9ex98HJx5JO4")

# logs debug messages to console
logger = tb.logger
tb.logger.setLevel(logging.DEBUG)

# handlers (filters) definitions
# these are checked IN ORDER
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Howdy " + message.from_user.first_name + ", how are you doing?")

@bot.message_handler(commands=['help'])
def send_help(msg):
    bot.reply_to(msg, "This is the help section. I really don't know what you're looking for, "
                      "since this is a test bot, dumbass.")

@bot.message_handler(commands=['epoch'])
def send_unix_epoch(msg):
    bot.reply_to(msg, msg.date)

@bot.message_handler(commands=['status'])
def send_raspi_status(msg):
    bot.reply_to(msg, "Checking status...")
    bot.reply_to(msg, get_status())

@bot.message_handler(commands=['whoami'])
def send_whoyouare(msg):
    bot.reply_to(msg, str(msg.from_user))

@bot.message_handler(func=lambda msg: True)
def echo_all(msg):
    bot.reply_to(msg, msg.text)

# start the bot
# bot.polling()
# to prevent the bot dying because of Telegram servers stopping it:
while True:
    try:
        bot.polling()
    except Exception as e:
        print(e)
        sleep(10)