import cv2
import yaml
import os
from os.path import join
from datetime import datetime
import time
import threading


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class Camera:

    def __init__(self, index):

        # variables
        self.frame = None
        self.old_frame = None
        self.video = None
        self.motion_detected = 1
        self.running = 0
        self.cap = None

        self.index = index

        # settings
        if not os.path.exists("settings.yaml"):
            print("Error: settings file not found!!")
            exit()
        config = yaml.load(open("settings.yaml"))
        self.frame_w = config["resolution width"]
        self.frame_h = config["resolution height"]
        self.fps = config["fps"]
        self.motion_detection_flag = config["motion detection"]
        self.min_area_motion = config["min area detected"]
        self.save_frames_flag = config["save single frames"]
        self.save_video_flag = config["save video"]

        # fps
        self.time_to_wait = 1. / self.fps

        # outputs
        self.output_frame_path = "frame_" + str(index)
        if not os.path.exists(self.output_frame_path):
            os.mkdir(self.output_frame_path)

        # ToDo video limit
        if self.frame_w == 640 and self.frame_h == 480:
            self.video_limit = (2000000000/75000)*7

        # video
        # self.open_new_video()

        # open camera
        # self.open_camera()

        self.th()

    def open_camera(self):
        print("Starting camera connected on {}...".format(self.index))
        self.cap = cv2.VideoCapture(self.index)
        ret, self.old_frame = self.cap.read()
        self.old_frame = cv2.resize(self.old_frame, dsize=(self.frame_w, self.frame_h))
        self.old_frame = cv2.cvtColor(self.old_frame, cv2.COLOR_BGR2GRAY)
        if ret:
            print("ok!")
        else:
            print("Camera not opened!")

    def acquire_frame(self):
        ret, self.frame = self.cap.read()
        self.frame = cv2.resize(self.frame, dsize=(self.frame_w, self.frame_h))
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        if self.motion_detection_flag:
            self.motion_detected = self.get_motion_detection()

    def visualize_current_frame(self):
        cv2.imshow("Frame", self.frame)
        if self.motion_detection_flag:
            cv2.imshow("Motion Detection", self.thresh_frame)
        cv2.waitKey(1)

    def save_current_frame(self):
        if self.motion_detected:
            cv2.imwrite(join(self.output_frame_path, self.get_date() + '.jpg'), self.frame)

    def open_new_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video = cv2.VideoWriter(self.get_date() + '.avi', fourcc, self.fps, (self.frame_w, self.frame_h))

    def save_current_frame_video(self):
        if self.motion_detected:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_GRAY2RGB)
            self.video.write(self.frame)

    def close_video(self):
        self.video.release()
        self.cap.release()

    def get_date(self):
        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')

    def get_motion_detection(self):
        motion = 0

        frame_tmp = cv2.GaussianBlur(self.frame, (21, 21), 0)
        frame_old_tmp = cv2.GaussianBlur(self.old_frame, (21, 21), 0)

        diff_frame = cv2.absdiff(frame_old_tmp, frame_tmp)
        self.thresh_frame = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)[1]
        self.thresh_frame = cv2.dilate(self.thresh_frame, None, iterations=2)

        # Finding contour of moving object
        (_, cnts, _) = cv2.findContours(self.thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts:
            if cv2.contourArea(contour) < self.min_area_motion:
                continue
            motion = 1
            break
            # (x, y, w, h) = cv2.boundingRect(contour)
            # # making green rectangle arround the moving object
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        self.old_frame = self.frame.copy()
        return motion

    @threaded
    def th(self):
        while True:
            while not self.running:
                time.sleep(0.5)

            self.open_camera()
            self.open_new_video()

            while self.running:
                # for fps
                start_time = time.time()

                # camera stuff
                self.acquire_frame()
                self.visualize_current_frame()
                if self.save_frames_flag:
                    self.save_current_frame()
                if self.save_video_flag:
                    self.save_current_frame_video()

                # fps check
                elapsed_time = time.time() - start_time
                if self.time_to_wait - elapsed_time > 0:
                    time.sleep(self.time_to_wait - elapsed_time)

            cv2.destroyAllWindows()

    def run(self):
        self.running = 1

    def stop(self):
        self.running = 0
        self.close_video()


