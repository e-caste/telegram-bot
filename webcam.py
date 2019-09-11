import os
from robbamia import *
from subprocess import Popen
from datetime import datetime, timedelta
from sys import stderr
from time import sleep

def _check_NAS_mounted():
    while True:
        if not os.path.isdir(webcam_path): # ismount()
            print("NAS folder not mounted. Mounting...", file=stderr)
            with Popen(['sudo', 'mount', '-a']) as mount_process:
                mount_process.wait(10)
        else:
            break

def get_last_img_name():
    _check_NAS_mounted()

    while True:
        folder = False
        tmp = os.listdir(webcam_path)
        tmp.sort(key=str.casefold)
        # if there are only folders
        if os.path.isdir(webcam_path + tmp[-1]):
            folder = tmp[-1]
            tmp = os.listdir(webcam_path + folder)
            tmp.sort(key=str.casefold)
        if tmp[-1].endswith('.jpg'):  # prevents sending .jpg~ which are images being written to disk
            return tmp[-1], folder
        else:
            sleep(0.3)

def get_yesterday_timelapse_video_name():
    _check_NAS_mounted()

    yesterday = datetime.today() - timedelta(days=1)
    yesterday = str(yesterday)[:10]  # only take date part
    yesterday_s = yesterday + "/"
    # this process has already been done
    if os.path.isdir(webcam_path + yesterday):
        return yesterday
    os.mkdir(webcam_path + yesterday)
    for i, pic in enumerate(os.listdir(webcam_path)):
    # for pic in os.listdir(webcam_path):
        if pic != yesterday:  # ignore the folder
            if pic.startswith(yesterday):
                os.rename(src=webcam_path + pic, dst=webcam_path + yesterday_s + pic)  # move to dir
                # add sequential number at the end for use with ffmpeg - not needed
                # os.rename(src=webcam_path + yesterday_s + pic, dst=webcam_path + yesterday_s + pic.split(".")[0]
                #                                                  + "_" + str(i).zfill(6) + ".jpg")

    # IMPORTANT: ffmpeg only works with real .jpg and not .png converted into .jpg by changing extension
    # this outputs a 96 fps 30 sec timelapse of yesterday (if pics are taken at 30s intervals = 2880 per day)
    # the b=number parameter specifies the bitrate (31457280 = 30Mbit/s)
    ffmpeg_exit_code = os.system("ffmpeg -r 96 -f image2 -pattern_type glob -i '" + webcam_path + yesterday_s + "*.jpg'"
                                 " -c:v libx264 -x264-params b=31457280 -y "
                                 + webcam_path + yesterday_s + yesterday + "_full_quality.mp4")
    # convert video for telegram
    # size < 10 MB - 4:2:0 color profile - 60 fps
    if ffmpeg_exit_code == 0:
        ffmpeg_exit_code = os.system("ffmpeg -i " + webcam_path + yesterday_s + yesterday +
                                     "_full_quality.mp4 -r 60 -b:v 2500000 -c:v libx264 "
                                     "-profile:v high -pix_fmt yuv420p " +
                                     webcam_path + yesterday_s + yesterday + "_for_tg.mp4")
    else:
        print("Error within ffmpeg (full quality video)", file=stderr)

    if ffmpeg_exit_code == 0:
        # don't (to preserve hard disk space on NAS)
        # make tar.gz archive in folder with pictures - pigz for multicore speed
        # os.system("tar c " + webcam_path + yesterday_s + "*.jpg | pigz --best > "
        #           + webcam_path + yesterday_s + yesterday + ".tar.gz")
        # print("Made tarball with all pictures from " + yesterday)

        # delete all .jpgs to save space
        os.system("rm " + webcam_path + yesterday_s + "*.jpg")
        print("Removed all .jpgs from " + yesterday + " directory")
        # for pic in os.listdir(webcam_path + yesterday_s):
        #     if pic.endswith(".jpg"):
        #         os.remove(webcam_path + yesterday_s + pic)
    else:
        print("Error within ffmpeg (video conversion for telegram)", file=stderr)

    return yesterday

if __name__ == '__main__':
    # get_last_img_name()
    # get_timelapse_as_video()
    pass