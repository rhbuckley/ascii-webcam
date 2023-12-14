"""
12 December 2023

`main.py` This file contains the main function for
terminal-camera. This file contains the main loop
for the program.
"""
import os

import cv2

from colored import Fore, Style
from gradients import PresetGradients
from convert import AsciiImageConverter

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    """ Set Gradient Here . """
    gradient = PresetGradients.UNI
    converter = AsciiImageConverter(gradient, color=True, use_terminal=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        text = converter.convert_image_to_terminal(image)

        os.system("clear")
        print(text)

    cap.release()


if __name__ == '__main__':
    main()