import os
from datetime import datetime, timedelta
import webcam
from robbamia import webcam_path, pics_nas_dir, castes_chat_id


# GENERIC UTILS

def split_msg_for_telegram(string: str):
    chars_per_msg = 4096
    return [string[i:i + chars_per_msg] for i in range(0, len(string), chars_per_msg)]


def send_split_msgs(bot, string_list):
    try:
        for string in string_list:
            bot.send_message(chat_id=castes_chat_id, text=string)

    except Exception as e:
        print("send_split_msgs")
        print(e)


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


# BUTTON HANDLER UTILS

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


def webcam_sub(id: str):
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
        return reply


def webcam_unsub(id: str):
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


def events_sub(filenamestart: str, id: str):
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


def events_unsub(filenamestart: str, id: str):
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
