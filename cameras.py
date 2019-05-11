import cv2
import yaml
import os
from os.path import join
from datetime import datetime


class Camera:

    def __init__(self, index):

        # variables
        self.frame = None

        # settings
        if not os.path.exists("settings.yaml"):
            print("Error: settings file not found!")
            exit()
        config = yaml.load(open("settings.yaml"))
        self.frame_w = config["resolution width"]
        self.frame_h = config["resolution height"]
        self.fps = config["fps"]

        # outputs
        self.output_frame_path = "frame_" + str(index)
        if not os.path.exists(self.output_frame_path):
            os.mkdir(self.output_frame_path)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.get_date() + '.avi', fourcc, self.fps, (self.frame_w, self.frame_h))
        print(cv2.VIDEOWRITER_PROP_FRAMEBYTES)

        # video limit
        if self.frame_w == 640 and self.frame_h == 480:
            self.video_limit = (2000000000/75000)*7

        # open camera
        print("Starting camera connected on {}...".format(index))
        self.cap = cv2.VideoCapture(index)
        ret, _ = self.cap.read()
        if ret:
            print("ok!")
        else:
            print("Camera not opened!")

    def acquire_frame(self):
        ret, self.frame = self.cap.read()
        self.frame = cv2.resize(self.frame, dsize=(self.frame_w, self.frame_h))

    def visualize_current_frame(self):
        cv2.imshow("Frame", self.frame)
        cv2.waitKey(1)

    def save_current_frame(self):
        cv2.imwrite(join(self.output_frame_path, self.get_date() + '.jpg'), self.frame)

    def save_current_frame_video(self):
        self.out.write(self.frame)

    def get_date(self):
        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')


