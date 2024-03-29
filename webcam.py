import os
from robbamia import *
from subprocess import Popen
from datetime import datetime, timedelta
from sys import stderr
from time import sleep


def check_NAS_mounted():
    while True:
        if not os.path.isdir(webcam_path):  # ismount()
            print("NAS folder not mounted. Mounting...", file=stderr)
            with Popen(['sudo', 'mount', '-a']) as mount_process:
                mount_process.wait(10)
        else:
            break


def get_last_img_name():
    check_NAS_mounted()

    folder = False
    tmp = os.listdir(webcam_path)
    tmp.sort(key=str.casefold)
    # if there are only folders
    if os.path.isdir(webcam_path + tmp[-1]):
        folder = tmp[-1]
        tmp = os.listdir(webcam_path + folder)
        tmp.sort(key=str.casefold)
    # send first image that is completely saved
    for img in sorted(tmp, key=str.casefold, reverse=True):
        if img.endswith('.jpg'):  # prevents sending .jpg~ which are images being written to disk
            return img, folder


def get_yesterday_timelapse_video_name():
    check_NAS_mounted()

    yesterday = datetime.today() - timedelta(days=1)
    yesterday = str(yesterday)[:10]  # only take date part

    # check if the video is available, otherwise delegate another machine to make it
    if not os.path.isfile(webcam_path + yesterday + "/" + yesterday + "_for_tg.mp4"):
        os.system(ssh_cmd)

    return yesterday


if __name__ == '__main__':
    # get_last_img_name()
    # get_timelapse_as_video()
    pass
