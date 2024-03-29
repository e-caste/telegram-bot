import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from bot_utils import get_specific_timelapse, cirulla_add, quadris_tridimensionale_add

# import Docker environment variables
castes_chat_id = os.environ["CST_CID"]


def status(update: Update, context: CallbackContext) -> None:
    # only accept input if user is caste
    if str(update.message.chat_id) == castes_chat_id:
        # each [] is a line
        keyboard = [
            [InlineKeyboardButton("uptime", callback_data='uptime'),
             InlineKeyboardButton("ltl", callback_data='twlog')],
            [InlineKeyboardButton("ppy", callback_data='ppy'), InlineKeyboardButton("speedtest", callback_data='st')],
            [InlineKeyboardButton("lasdl", callback_data='lasdl'),
             InlineKeyboardButton("python3 pi_status.py", callback_data='full')],
            [InlineKeyboardButton("./check_cpu_gpu_temps.sh", callback_data="temps"),
             InlineKeyboardButton("df -h", callback_data="df_h")],
            [InlineKeyboardButton("full tg bot log", callback_data='full_tg_log'),
             InlineKeyboardButton("tg bot log tail", callback_data="tail_log")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('pi@raspberrypi ~ $', reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                         text="⚠️ You don't have permission to use the /status command.")


def events_menu(update: Update, context: CallbackContext, use_callback: bool = False):
    keyboard = [
        [InlineKeyboardButton("Cercle", callback_data='cercle')],
        [InlineKeyboardButton("TheDreamers", callback_data='thedreamers')],
        [InlineKeyboardButton("Supermarket", callback_data='supermarket')],
        [InlineKeyboardButton("Close ❌", callback_data='close_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if use_callback:
        update.callback_query.message.reply_text('Choose which event you want to receive notifications about:',
                                                 reply_markup=reply_markup)
    else:
        update.message.reply_text('Choose which event you want to receive notifications about:',
                                  reply_markup=reply_markup)


def subscribe_to_cercle_notifications(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='sub_cercle'),
         InlineKeyboardButton("Unsubscribe", callback_data='unsub_cercle')],
        [InlineKeyboardButton("Link to Facebook page of Cercle", callback_data='fblink_cercle')],
        [InlineKeyboardButton("Back", callback_data='back_to_events_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)


def subscribe_to_thedreamers_notifications(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='sub_thedreamers'),
         InlineKeyboardButton("Unsubscribe", callback_data='unsub_thedreamers')],
        [InlineKeyboardButton("Link to Facebook page of TheDreamers", callback_data='fblink_thedreamers')],
        [InlineKeyboardButton("Back", callback_data='back_to_events_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)


def subscribe_to_supermarket_notifications(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='sub_super'),
         InlineKeyboardButton("Unsubscribe", callback_data='unsub_super')],
        [InlineKeyboardButton("Link to Facebook page of Supermarket", callback_data='fblink_super')],
        [InlineKeyboardButton("Back", callback_data='back_to_events_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)


def subscribe_to_webcam_notifications(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='webcam_sub')],
        [InlineKeyboardButton("Unsubscribe", callback_data='webcam_unsub')],
        [InlineKeyboardButton("Back", callback_data='back_to_webcam_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)


def webcam_menu(update: Update, context: CallbackContext, use_callback: bool = False):
    keyboard = [
        [InlineKeyboardButton("📷 Right Now", callback_data='webcam_now')],
        [InlineKeyboardButton("📽 Timelapse of yesterday", callback_data='webcam_timelapse')],
        [InlineKeyboardButton("✅ Enable/Disable Notifications", callback_data="webcam_notification")],
        [InlineKeyboardButton("❌ Close", callback_data='close_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if use_callback:
        update.callback_query.message.reply_text('Choose an option:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Choose an option:', reply_markup=reply_markup)


def apt(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == castes_chat_id:
        keyboard = [
            [InlineKeyboardButton("sudo apt update", callback_data="apt_update")],
            [InlineKeyboardButton("apt list -u", callback_data="apt_list_u")],
            [InlineKeyboardButton("sudo apt upgrade", callback_data="apt_upgrade")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('pi@raspberrypi ~ $', reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                         text="⚠️ You don't have permission to use the /apt command.")


def pics_menu(update: Update, context: CallbackContext) -> None:
    command = update.message.text.split()
    if command.__len__() > 1:
        get_specific_timelapse(bot, update, command[1:])
    else:
        keyboard = [
            [InlineKeyboardButton("🕰 Get oldest picture", callback_data="pics_oldest")],
            [InlineKeyboardButton("⏱ Get average time to take a picture", callback_data="pics_avg")],
            [InlineKeyboardButton("📽 Get available timelapses", callback_data="pics_timelapses")]
        ]
        if str(update.message.chat_id) == castes_chat_id:
            keyboard.append([InlineKeyboardButton("🗓 Re-run script for past days", callback_data="pics_script")],)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Choose an option:', reply_markup=reply_markup)


def cirulla_menu(update: Update, context: CallbackContext) -> None:
    if not str(update.message.chat_id) == castes_chat_id:
        context.bot.send_message(chat_id=update.message.chat_id,
                         text="⚠️ You don't have permission to use the /cirulla command.")
        return
    else:
        command = update.message.text.split()
        if len(command) > 1:
            cirulla_add(bot, update, command[1:])
        else:
            keyboard = [
                [InlineKeyboardButton("✚ Add latest result", callback_data="cirulla_add")],
                [InlineKeyboardButton("− Remove last added result", callback_data="cirulla_remove")],
                [InlineKeyboardButton("🔢 Show current total points", callback_data="cirulla_points")],
                [InlineKeyboardButton("📈 Plot delta trend (E-C)", callback_data="cirulla_plot")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Choose an option:', reply_markup=reply_markup)


def quadris_tridimensionale_menu(update: Update, context: CallbackContext) -> None:
    if not str(update.message.chat_id) == castes_chat_id:
        context.bot.send_message(chat_id=update.message.chat_id,
                         text="⚠️ You don't have permission to use the /qt command.")
        return
    else:
        command = update.message.text.split()
        if len(command) > 1:
            quadris_tridimensionale_add(bot, update, command[1:])
        else:
            keyboard = [
                [InlineKeyboardButton("✚ Add latest result", callback_data="qt_add")],
                [InlineKeyboardButton("− Remove last added result", callback_data="qt_remove")],
                [InlineKeyboardButton("🔢 Show current total points", callback_data="qt_points")],
                [InlineKeyboardButton("📈 Plot delta trend (E-C)", callback_data="qt_plot")],
                [InlineKeyboardButton("📜 Show rules", callback_data="qt_rules")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Choose an option:', reply_markup=reply_markup)
