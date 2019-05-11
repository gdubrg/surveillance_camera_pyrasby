from flask import Flask, render_template
from cameras import Camera
import yaml
import os
import time

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("index.html")


def sample_camera():
    cam = Camera(0)

    # settings
    if not os.path.exists("settings.yaml"):
        print("Error: settings file not found!")
        exit()
    config = yaml.load(open("settings.yaml"))

    # fps
    fps = config["fps"]
    time_to_wait = 1./fps
    c = 0

    while c < 100:

        c += 1
        start_time = time.time()

        # camera stuff
        cam.acquire_frame()
        cam.visualize_current_frame()
        cam.save_current_frame()
        cam.save_current_frame_video()

        elapsed_time = time.time() - start_time
        if time_to_wait - elapsed_time > 0:
            time.sleep(time_to_wait - elapsed_time)

    cam.out.release()

if __name__ == "__main__":
    sample_camera()
    # app.run()