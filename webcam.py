import os
from robbamia import *
from subprocess import Popen
from datetime import datetime, timedelta

def get_last_img_name():
    while True:
        if not os.path.isdir(webcam_path): # ismount()
            with Popen(['sudo', 'mount', '-a']) as mount_process:
                mount_process.wait(10)
        else:
            break

    tmp = os.listdir(webcam_path)
    tmp.sort(key=str.casefold)
    return tmp[-1]

def get_yesterday_timelapse_video_name():
    yesterday = datetime.today() - timedelta(days=1)
    yesterday = str(yesterday)[:10]  # only take date part
    yesterday_s = yesterday + "/"
    # this process has already been done
    if os.path.isdir(webcam_path + yesterday):
        return yesterday
    os.mkdir(webcam_path + yesterday)
    for pic in os.listdir(webcam_path):
        if pic.startswith(yesterday):
            os.rename(src=webcam_path + pic, dst=webcam_path + yesterday + pic)  # move to dir
    # this outputs a 96 fps 30 sec timelapse of yesterday (if pics are taken at 30s intervals = 2880 per day)
    os.system("ffmpeg -r 96 -i " + webcam_path + yesterday_s + " -vcodec mpeg4 -y " + webcam_path +
              yesterday_s + yesterday + ".mp4")
    return yesterday


if __name__ == '__main__':
    # get_last_img_name()
    # get_timelapse_as_video()
    pass