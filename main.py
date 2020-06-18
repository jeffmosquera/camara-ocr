
# import the necessary packages
from SingleMotionDetector import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
from Camera import Camera


ap = argparse.ArgumentParser()
ap.add_argument("-u", "--user", type=str,
                help="Usuario de la cámara", required=True)
ap.add_argument("-p", "--password", type=str,
                help="Contraseña de la cámmara", required=True)
ap.add_argument("-i", "--ip", type=str,
                help="IP de la cámara", required=True)
ap.add_argument("-po", "--port", type=str, default="80",
                help="Puerto de la cámara", required=True)
ap.add_argument("-f", "--frame-count", type=int, default=32,
                help="# de frames  para construit el modelo")
args = vars(ap.parse_args())

print(args['port'])
camera = Camera(
    user=args['user'],
    password=args['password'],
    ip=args['ip'],
    port=args['port']
)

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)


def detect_motion(frameCount):
    global outputFrame, lock
    md = SingleMotionDetector(accumWeight=0.1)
    total = 0

    while True:
        image = camera.getSnapshot()
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        if total > frameCount:
            motion = md.detect(gray)
            if motion is not None:
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 2)
                print("Motion")

        md.update(gray)
        total += 1
        with lock:
            outputFrame = frame.copy()


def generate():
    global outputFrame, lock
    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    t = threading.Thread(target=detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", threaded=True, use_reloader=False)
vs.stop()
