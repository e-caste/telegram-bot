import os
import sys
from time import sleep
from bot_utils import calculate_time_to_sleep
import evnt_ntfr
import webcam

# import Docker environment variables
token = os.environ["TOKEN"]
castes_chat_id = os.environ["CST_CID"]
log_path = os.environ["LOG_PATH"]
pics_dir = os.environ["PICS_DIR"]


def check_for_new_events(bot, hour: int):
    while True:
        try:
            time_to_sleep = calculate_time_to_sleep(hour=hour)

            print("Waiting to check for new events... " + str(time_to_sleep))
            sleep(time_to_sleep)

            # the order must be the same as in evnt_ntfr.py
            chat_ids_list = [
                'supermarket_chat_ids.txt',
                'cercle_chat_ids.txt',
                'thedreamers_chat_ids.txt'
            ]
            # os.chdir(raspi_wd)
            links, texts, event_names = evnt_ntfr.main()
            if links is not None and texts is not None:
                for links_list, text_list, chat_ids, event_name in zip(links, texts, chat_ids_list, event_names):
                    with open(chat_ids, 'r') as ids:
                        for id in ids.readlines():
                            for link, text in zip(links_list, text_list):
                                try:
                                    bot.send_message(chat_id=id,
                                                     text="New " + event_name.capitalize() + " event:\n" + text + "\n" + link)
                                    print("Sent " + event_name + " " + link + " to " + id)
                                except Exception as e:
                                    print(e, file=sys.stderr)
            elif links is not None and texts is None:
                for links_list, chat_ids, event_name in zip(links, chat_ids_list, event_names):
                    with open(chat_ids, 'r') as ids:
                        for id in ids.readlines():
                            for link in links_list:
                                try:
                                    bot.send_message(chat_id=id,
                                                     text="New " + event_name.capitalize() + " event:\n" + link)
                                    print("Sent " + event_name + " " + link + " to " + id)
                                except Exception as e:
                                    print(e, file=sys.stderr)

        except Exception as e:
            print(e, file=sys.stderr)


def make_new_webcam_timelapse(hour: int, minute: int):
    while True:
        try:
            sleep(calculate_time_to_sleep(hour=(hour-3) % 24))  # account for days when the hour changes
            time_to_sleep = calculate_time_to_sleep(hour=hour, minute=minute)

            print("Waiting to make timelapse... " + str(time_to_sleep))
            sleep(time_to_sleep)

            # this function also makes the new video from the images
            yesterday = webcam.get_yesterday_timelapse_video_name()
            print("\nMade new timelapse of " + yesterday + "\n")

        except Exception as e:
            print(e, file=sys.stderr)


def send_timelapse_notification(bot, hour: int, minute: int, debug: bool):
    while True:
        try:
            # first sleep until 5am
            print("Sleeping util " + str(hour) + "a.m. (timelapse)...")
            sleep(calculate_time_to_sleep(hour=5, minute=0))
            # then sleep until the given hour - this prevents issues on the days the hour changes
            time_to_sleep = calculate_time_to_sleep(hour=hour, minute=minute)
            print("Waiting to send timelapse... " + str(time_to_sleep))
            sleep(time_to_sleep)

            # if not debug:
            #     os.chdir(raspi_wd)
            # the video should have already been made by the function above, so it immediately returns yesterday
            yesterday = webcam.get_yesterday_timelapse_video_name()
            with open('webcam_chat_ids.txt', 'r') as ids:
                for id in ids.readlines():
                    bot.send_video(chat_id=id,
                                   video=open(pics_dir + yesterday + "/" + yesterday + "_for_tg.mp4", 'rb'),
                                   caption="Here's the timelapse of yesterday! - " + yesterday,
                                   timeout=6000,
                                   supports_streaming=True)
                    print("Sent timelapse to " + id)

        except Exception as e:
            print(e, file=sys.stderr)


