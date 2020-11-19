# official guide: https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/
# command line options: https://www.raspberrypi.org/app/uploads/2013/07/RaspiCam-Documentation.pdf

import os
from subprocess import Popen
from time import sleep
from pi0w_webcam import webcam_path, local_folder


def get_picture():
    sleep_time = 16  # seconds
    # + 5 for the preview + ~4 for the take = ~9
    # total 30 -> 2880 photos -> 96 fps to get a 30 second timelapse | 13.30min conversion on mbp14 - sleep_time = 21
    # total 25 -> 3456 photos -> 115.2 fps to get a 30 second timelapse | x min conversion on mbp14 - sleep_time = 16
    # total 20 -> 4320 photos -> 144 fps to get a 30 second timelapse | x min conversion on mbp14 - sleep_time = 11
    # total 15 -> 5760 photos -> 192 fps to get a 30 second timelapse | x min conversion on mbp14 - sleep_time = 6
    # total 10 -> 8640 photos -> 288 fps to get a 30 second timelapse | x min conversion on mbp14 - sleep_time = 1
    # TODO: change ffmpeg fps accordingly in ffmpeg_mbp2014.py
    mount_retry_times = 5
    to_copy = False

    while True:
        mounted = False
        for _ in range(mount_retry_times):
            if not os.path.isdir(webcam_path):
                with Popen(['sudo', 'mount', '-a']) as mount_process:
                    mount_process.wait(10)
            else:
                mounted = True
                break

        if mounted:
            if to_copy:
                os.system('mv ' + local_folder + '* ' + webcam_path)
            output_folder = webcam_path
            to_copy = False
        else:
            output_folder = local_folder
            to_copy = True

        os.system('raspistill --timeout 5000 --verbose --awb auto --exposure auto '
                  '--output ' + output_folder + '$(date +"%Y-%m-%d_%H%M%S").jpg')  # timeout is in ms

        sleep(sleep_time)


if __name__ == '__main__':
    get_picture()
