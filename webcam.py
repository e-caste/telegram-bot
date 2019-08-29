import os
from robbamia import *
from subprocess import Popen

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

if __name__ == '__main__':
    get_last_img_name()