import os
from datetime import datetime, timedelta
from subprocess import Popen, PIPE
from multiprocessing import Process
import json
import matplotlib.pyplot as plt
from telegram import bot, Update
from telegram.ext import CallbackContext
import webcam

# import Docker environment variables
token = os.environ["TOKEN"]
castes_chat_id = os.environ["CST_CID"]
log_path = os.environ["LOG_PATH"]
pics_dir = os.environ["PICS_DIR"]


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


def calculate_time_to_sleep(hour: int, minute: int = 0) -> int:
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

def get_webcam_img(update: Update, context: CallbackContext) -> None:
    img_name, folder = webcam.get_last_img_name()
    if folder:
        path_name = folder + "/" + img_name
    else:
        path_name = img_name
    context.bot.send_photo(chat_id=update.callback_query.message.chat_id,
                           photo=open(pics_dir + path_name, 'rb'),
                           caption=img_name)


def get_webcam_timelapse(update: Update, context: CallbackContext) -> None:
    yesterday = webcam.get_yesterday_timelapse_video_name()
    if yesterday:
        context.bot.send_video(chat_id=update.callback_query.message.chat_id,
                               video=open(pics_dir + yesterday + "/" + yesterday + "_for_tg.mp4", 'rb'),
                               caption=yesterday,
                               timeout=6000)
    else:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                 text="There is no timelapse for yesterday, Please check the NAS is online.")


def webcam_sub(id: str) -> str:
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


def webcam_unsub(id: str) -> str:
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
    return reply


def events_sub(filenamestart: str, id: str) -> str:
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
    return reply


def events_unsub(filenamestart: str, id: str) -> str:
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
    return reply


def get_oldest_picture(update: Update, context: CallbackContext) -> None:
    webcam.check_NAS_mounted()

    tmp = os.listdir(pics_dir)
    tmp.sort(key=str.casefold)
    # if there are only folders
    if os.path.isdir(pics_dir + tmp[-1]):
        tmp = os.listdir(pics_dir + folder)
        tmp.sort(key=str.casefold)
    # send first image that is completely saved
    for img in sorted(tmp, key=str.casefold):
        if img.endswith('.jpg'):  # prevents sending .jpg~ which are images being written to disk
            context.bot.send_photo(chat_id=update.callback_query.message.chat_id,
                                   photo=open(pics_dir + img, 'rb'),
                                   caption=img)
            break


def secs_per_picture() -> str:
    """
    Return the average of seconds per picture taken by Raspberry Pi Zero W
    """
    pics = sorted([pic for pic in os.listdir(pics_dir) if pic.endswith(".jpg")])
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


def get_available_timelapses(format: bool = True) -> str or list:
    webcam.check_NAS_mounted()

    available_timelapses = []
    reply = ""
    dirs = [directory for directory in os.listdir(pics_dir)
            if os.path.isdir(os.path.join(pics_dir, directory))]

    for d in dirs:
        content = os.listdir(os.path.join(pics_dir, d))
        for item in content:
            if "_for_tg.mp4" in item:
                available_timelapses.append(d)

    # TODO: print in tree format using dict below
    # previous = {
    #     "year": available_timelapses[0][0:3],
    #     "month": available_timelapses[0][5:7],
    #     "day": available_timelapses[0][9:11]
    # }
    for i, timelapse in enumerate(sorted(available_timelapses)):
        reply += timelapse
        if format:
            if i % 2 == 0:
                reply += "    "
            else:
                reply += "\n"
        else:
            reply += " "

    if format:
        return reply
    else:
        return available_timelapses


def get_specific_timelapse(bot, update, date):
    timelapses = get_available_timelapses(format=False)
    if isinstance(date, list) and date.__len__() == 1:
        date = date[0]
    parsed_date = __parse_date(date)
    if parsed_date in timelapses:
        context.bot.send_video(chat_id=update.message.chat_id,
                               video=open(os.path.join(pics_dir, parsed_date, parsed_date + "_for_tg.mp4"), 'rb'),
                               caption=parsed_date,
                               timeout=6000)
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="No timelapse available for date " + parsed_date + " (YYYY-MM-DD).\n"
                                                                                         "Check available timelapses with /pics and tapping the 'Get available timelapses' button.")


# expecting format YYYY[*]MM[*]DD
#        or format DD[*]MM[*]YYYY
def __parse_date(date) -> str:
    year, month, day = (None, None, None)
    if isinstance(date, str):
        if date.__len__() == 8:
            year = date[0:4]
            month = date[4:6]
            day = date[6:8]
        elif date.__len__() == 10:
            if not date[4].isdigit() and not date[7].isdigit():
                year = date[0:4]
                month = date[5:7]
                day = date[8:10]
            elif not date[2].isdigit() and not date[5].isdigit():
                year = date[8:10]
                month = date[5:7]
                day = date[0:4]
    elif isinstance(date, list):
        if date.__len__() == 3:
            if date[0].__len__() == 4 and date[1].__len__() == 2 and date[2].__len__() == 2:
                year = date[0]
                month = date[1]
                day = date[2]
            elif date[0].__len__() == 2 and date[1].__len__() == 2 and date[2].__len__() == 4:
                year = date[2]
                month = date[1]
                day = date[0]
    if year is not None and month is not None and day is not None:
        return year + "-" + month + "-" + day
    else:
        return ""


def recover_past_days(update):
    with Popen(ssh_cmd.split(), stdout=PIPE, stderr=PIPE) as p:
        out, err = p.communicate()
        # ret_code = p.returncode
    split_reply = split_msg_for_telegram(out.decode('utf-8'))
    update.callback_query.edit_message_text(text=split_reply[0])
    send_split_msgs(bot.Bot(token), split_reply[1:])


def cirulla_add(bot, update, command):
    result = _parse_cirulla_result(command)
    if result is None:
        reply = "Format not recognized.\nThe correct format is: <number>[*]<number>, with at least one space between " \
                "the numbers."
    else:
        now = datetime.now()
        previous_data = json.load(open("cirulla.json"))
        data = [dic for dic in previous_data]
        new_data = {
            "points": "",
            "delta": 0,
            "datetime": {
                "year": str(now.year),
                "month": str(now.month),
                "day": str(now.day),
                "hour": str(now.hour),
                "minute": str(now.minute),
                "second": str(now.second)
            }
        }
        prev_points = [int(previous_data[-1]["points"].split()[0]), int(previous_data[-1]["points"].split()[-1])]
        prev_avgs = [p / len(data) for p in prev_points]
        cur_avgs = None
        sym_avgs = ["~", "~"]
        avg_fmt = '%.3f'
        # these are the total points
        if result[0] > prev_points[0] or result[1] > prev_points[1]:
            new_data["points"] = str(result[0]) + " - " + str(result[1])
            new_data["delta"] = result[0] - result[1]
        # these are the single match points
        else:
            cur_points = [int(result[0]), int(result[1])]
            total_points = [p + c for p, c in zip(prev_points, cur_points)]
            cur_avgs = [p / (len(data) + 1) for p in total_points]
            new_data["points"] = str(total_points[0]) + " - " + str(total_points[1])
            new_data["delta"] = total_points[0] - total_points[1]
        data.append(new_data)
        with open("cirulla.json", "w") as f:
            f.write(json.dumps(data, indent=2))
        if cur_avgs:
            deadzone_factor = 0.002
            for i in range(len(sym_avgs)):
                if cur_avgs[i] > (prev_avgs[i] + deadzone_factor):
                    sym_avgs[i] = "📈"
                elif cur_avgs[i] < (prev_avgs[i] - deadzone_factor):
                    sym_avgs[i] = "📉"
        reply = "\n".join([
            "Result " + new_data["points"] + " added.",
            "Match #" + str(len(data)),
            "Averages per match: " + str(avg_fmt % cur_avgs[0]) + sym_avgs[0] + " - " +
            str(avg_fmt % cur_avgs[1]) + sym_avgs[1] if cur_avgs else "Averages per match: N/A",
            "Δ: " + str(new_data["delta"]),
        ])
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=reply)


def cirulla_remove() -> str:
    data = json.load(open("cirulla.json"))
    data.pop(len(data) - 1)
    with open("cirulla.json", "w") as f:
        f.write(json.dumps(data, indent=2))
    return "The last result has been removed."


def cirulla_points() -> str:
    data = json.load(open("cirulla.json"))
    matches = len(data)
    prev_points = [int(data[-1]["points"].split()[0]), int(data[-1]["points"].split()[-1])]
    avg_fmt = '%.3f'
    return "\n".join([
        "Points: " + data[-1]["points"],
        "Matches: " + str(matches),
        "Averages per match: " + str(avg_fmt % (prev_points[0] / matches)) + " - " + str(
            avg_fmt % (prev_points[1] / matches)),
        "Δ: " + str(data[-1]["delta"]),
    ])


def cirulla_plot(context: CallbackContext, chat_id):
    x = []
    y = []
    data = json.load(open("cirulla.json"))
    for dic in data:
        x.append(dic["datetime"]["year"] + "-" + dic["datetime"]["month"].zfill(2) + "-" + dic["datetime"]["day"].zfill(
            2) + " " +
                 dic["datetime"]["hour"].zfill(2) + ":" + dic["datetime"]["minute"].zfill(2) + "." + dic["datetime"][
                     "second"].zfill(2))
        y.append(dic["delta"])
    plt.plot(x, y)
    step = int(len(x) / 50) + 1
    plt.xticks(range(0, len(x), step), rotation=90)
    plt.tick_params(axis='x', which='major', labelsize=8)
    plt.tight_layout()
    plt.grid()
    path_to_graph = os.path.join(os.getcwd(), "cirulla_graph.jpg")
    if os.path.exists(path_to_graph):
        Popen(["rm", path_to_graph])
    plt.savefig(path_to_graph, dpi=300, bbox_inches='tight')
    context.bot.send_photo(chat_id=chat_id, photo=open(path_to_graph, 'rb'))


def _parse_cirulla_result(result: list):
    if not result[0].isdigit() or not result[-1].isdigit():
        return None
    else:
        return [int(result[0]), int(result[-1])]


qt_file = "quadris_tridimensionale.json"


# should probably use SQLite and not concatenate results, but this was faster to code
def quadris_tridimensionale_add(bot, update, command):
    result = _parse_quadris_tridimensionale_result(command)
    if result is None:
        reply = "Format not recognized.\nThe correct format is: (e|c)[*]<number>, with at least one space between " \
                "e/c and the number."
    else:
        winner, points = result
        now = datetime.now()
        _check_qt_file_exists()
        previous_data = json.load(open(qt_file))
        data = [dic for dic in previous_data]
        new_data = {
            "points": "",
            "delta": 0,
            "datetime": {
                "year": str(now.year),
                "month": str(now.month),
                "day": str(now.day),
                "hour": str(now.hour),
                "minute": str(now.minute),
                "second": str(now.second)
            }
        }
        try:
            prev_points = [int(previous_data[-1]["points"].split()[0]), int(previous_data[-1]["points"].split()[-1])]
            prev_avgs = [p / len(data) for p in prev_points]
        except (KeyError, IndexError):
            prev_points = [0, 0]
            prev_avgs = prev_points
        sym_avgs = ["~", "~"]
        avg_fmt = '%.3f'
        cur_points = [points, 0] if winner == "e" else [0, points]
        total_points = [p + c for p, c in zip(prev_points, cur_points)]
        cur_avgs = [p / (len(data) + 1) for p in total_points]
        new_data["points"] = str(total_points[0]) + " - " + str(total_points[1])
        new_data["delta"] = total_points[0] - total_points[1]
        data.append(new_data)
        with open(qt_file, "w") as f:
            f.write(json.dumps(data, indent=2))
        deadzone_factor = 0.1
        for i in range(len(sym_avgs)):
            if cur_avgs[i] > (prev_avgs[i] + deadzone_factor):
                sym_avgs[i] = "📈"
            elif cur_avgs[i] < (prev_avgs[i] - deadzone_factor):
                sym_avgs[i] = "📉"
        reply = "\n".join([
            "Result " + new_data["points"] + " added.",
            "Match #" + str(len(data)),
            "Averages per match: " + str(avg_fmt % cur_avgs[0]) + sym_avgs[0] + " - " +
            str(avg_fmt % cur_avgs[1]) + sym_avgs[1] if cur_avgs else "Averages per match: N/A",
            "Δ: " + str(new_data["delta"]),
        ])
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=reply)


def quadris_tridimensionale_remove() -> str:
    _check_qt_file_exists()
    data = json.load(open(qt_file))
    data.pop(len(data) - 1)
    with open(qt_file, "w") as f:
        f.write(json.dumps(data, indent=2))
    return "The last result has been removed."


def quadris_tridimensionale_points() -> str:
    _check_qt_file_exists()
    data = json.load(open(qt_file))
    matches = len(data)
    prev_points = [int(data[-1]["points"].split()[0]), int(data[-1]["points"].split()[-1])]
    avg_fmt = '%.3f'
    return "\n".join([
        "Points: " + data[-1]["points"],
        "Matches: " + str(matches),
        "Averages per match: " + str(avg_fmt % (prev_points[0] / matches)) + " - " + str(
            avg_fmt % (prev_points[1] / matches)),
        "Δ: " + str(data[-1]["delta"]),
    ])


def quadris_tridimensionale_plot(context: CallbackContext, chat_id):
    _check_qt_file_exists()
    x = []
    y = []
    data = json.load(open(qt_file))
    for dic in data:
        x.append(dic["datetime"]["year"] + "-" + dic["datetime"]["month"].zfill(2) + "-" + dic["datetime"]["day"].zfill(
            2) + " " +
                 dic["datetime"]["hour"].zfill(2) + ":" + dic["datetime"]["minute"].zfill(2) + "." + dic["datetime"][
                     "second"].zfill(2))
        y.append(dic["delta"])
    plt.plot(x, y)
    step = int(len(x) / 50) + 1
    plt.xticks(range(0, len(x), step), rotation=90)
    plt.tick_params(axis='x', which='major', labelsize=8)
    plt.tight_layout()
    plt.grid()
    path_to_graph = os.path.join(os.getcwd(), "quadris_tridimensionale_graph.jpg")
    if os.path.exists(path_to_graph):
        Popen(["rm", path_to_graph])
    plt.savefig(path_to_graph, dpi=300, bbox_inches='tight')
    context.bot.send_photo(chat_id=chat_id, photo=open(path_to_graph, 'rb'))


def _parse_quadris_tridimensionale_result(result: list):
    if result[0].lower() not in ("e", "c") or not result[-1].isdigit():
        return None
    else:
        return result[0], int(result[-1])


def _check_qt_file_exists():
    if not os.path.exists(qt_file):
        with open(qt_file, "w") as f:
            f.write("[]")
