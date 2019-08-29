import os
from robbamia import *
from subprocess import Popen
from datetime import datetime, timedelta
# import cv2


def get_last_img_name():
    while True:
        if not os.path.isdir(webcam_path): # ismount()
            with Popen(['sudo', 'mount', '-a']) as mount_process:
                mount_process.wait(10)
        else:
            break

    tmp = os.listdir(webcam_path)
    tmp.sort(key=str.casefold)
    # if there are only folders
    if os.path.isdir(webcam_path + tmp[-1]):
        tmp = os.listdir(webcam_path + tmp[-1])
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
    for i, pic in enumerate(os.listdir(webcam_path)):
    # for pic in os.listdir(webcam_path):
        if pic != yesterday:  # ignore the folder
            if pic.startswith(yesterday):
                os.rename(src=webcam_path + pic, dst=webcam_path + yesterday_s + pic)  # move to dir
                # add sequential number at the end for use with ffmpeg
                os.rename(src=webcam_path + yesterday_s + pic, dst=webcam_path + yesterday_s + pic.split(".")[0]
                                                                 + "_" + str(i).zfill(6) + ".jpg")

    # image_folder = webcam_path + yesterday
    # video_name = yesterday + ".mp4"
    #
    # images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    # frame = cv2.imread(os.path.join(image_folder, images[0]))
    # height, width, layers = frame.shape
    #
    # video = cv2.VideoWriter(video_name, 0, 1, (width, height))
    #
    # for image in images:
    #     video.write(cv2.imread(os.path.join(image_folder, image)))
    #
    # cv2.destroyAllWindows()
    # video.release()

    # this outputs a 96 fps 30 sec timelapse of yesterday (if pics are taken at 30s intervals = 2880 per day)
    os.system("ffmpeg -r 96 -f image2 -pattern_type glob -i '*.jpg' -vcodec mpeg4 -y "
              + webcam_path + yesterday_s + yesterday + ".mp4")
    # os.system("ffmpeg -r 96 -i '" + yesterday + "_%%%%%%%%%%%%_%6d.jpg' -vcodec mpeg4 -y "
    #           + webcam_path + yesterday_s + yesterday + ".mp4" )
    return yesterday


if __name__ == '__main__':
    # get_last_img_name()
    # get_timelapse_as_video()
    pass