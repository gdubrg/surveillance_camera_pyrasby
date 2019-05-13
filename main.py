from flask import Flask, render_template, request
from cameras import Camera
import yaml
import os
import time

app = Flask(__name__)

camera = Camera(0)


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/button_action", methods=['GET', 'POST'])
def button_action():
    print('debug')
    if request.method == 'POST':
        if request.form['action'] == 'start':
            handle_camera('start')
            status = "start"
        elif request.form['action'] == 'stop':
            handle_camera('stop')
            status = "stop"
        else:
            return "Not defined"
    l = ['a', 'b']
    # return render_template("index.html", status=status, llist=l)
    return render_template("index.html", status=status)


def handle_camera(action):
    if action == 'start':
        camera.run()
    elif action == 'stop':
        camera.stop()


def sample_camera():
    cam = Camera(0)

    # settings
    if not os.path.exists("settings.yaml"):
        print("Error: settings file not found!")
        exit()
    config = yaml.load(open("settings.yaml"))

    # fps
    fps = config["fps"]
    # time_to_wait = 1./fps
    # c = 0

    # while c < 10000:

        # c += 1
        # start_time = time.time()

        # camera stuff
        # cam.acquire_frame()
        # cam.visualize_current_frame()
        # cam.save_current_frame()
        # cam.save_current_frame_video()

        # elapsed_time = time.time() - start_time
        # if time_to_wait - elapsed_time > 0:
        #     time.sleep(time_to_wait - elapsed_time)

    # cam.close_video()

    cam.run()
    time.sleep(2)
    print("Shutting down...")
    cam.stop()
    time.sleep(2)
    print("Restarting...")
    cam.run()


if __name__ == "__main__":
    # sample_camera()
    # app.run(host="192.168.1.9", port=5000)
    app.run(port=5000)
