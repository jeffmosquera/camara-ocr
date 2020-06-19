from imutils.video import VideoStream
from flask import Response
from flask import Flask, request
from flask import render_template
import threading
import argparse
import datetime
import imutils
import re
import time
import cv2
from TextReader import TextReader
from Camera import Camera


cameras = [
    {
        "index": 0,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.205",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": False
    },
    {
        "index": 1,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.206",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": True
    },
    {
        "index": 2,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.207",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": False
    },
    {
        "index": 3,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.208",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": True
    },
    {
        "index": 4,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.209",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": False
    },
    {
        "index": 5,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.210",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": True
    },
    {
        "index": 6,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.212",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": False
    },
    {
        "index": 7,
        "user": "admin",
        "password": "Admin12345",
        "ip": "192.168.1.213",
        "port": "80",
        "camera": "",
        "outputFrame": "",
        "thread": "",
        "face": True
    }

]


for i, camera in enumerate(cameras):
    print(i)
    cameras[i]["camera"] = Camera(
        user=camera['user'],
        password=camera['password'],
        ip=camera['ip'],
        port=camera['port']
    )


outputFrame = None
lock = threading.Lock()
app = Flask(__name__)


cedula = ""
nombres = ""


def get_video(camera):
    global cameras, lock
    total = 0

    while True:
        time.sleep(2)
        image = camera["camera"].getSnapshot()
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        frame = imutils.resize(frame, width=800)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if frame is not None:

            if camera["face"] == False:
                text_reader = TextReader(gray)
                string_frame = text_reader.getString()

                cedula = ""
                for row in string_frame.splitlines():
                    for col in row.split(" "):
                        pattern = r'[0-9]{9}[\-][0-9]{1}'
                        re_search = re.search(pattern, col)
                        if re_search:
                            position = re_search.span()
                            cedula = col[position[0]:position[1]]
                            cedula = cedula.replace("-", "")

                        pattern = r'[0-9]{10}'
                        re_search = re.search(pattern, col)
                        # print(re_search)
                        if re_search:
                            position = re_search.span()
                            cedula = col[position[0]:position[1]]
                # if camera['index'] == 6:
                print(cedula)
                # boxes = text_reader.getBoxes()
                # n_boxes = len(boxes['level'])
                # for i in range(n_boxes):
                #     (x, y, w, h) = (boxes['left'][i], boxes['top']
                #                     [i], boxes['width'][i], boxes['height'][i])
                #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            with lock:
                cameras[camera["index"]]["outputFrame"] = frame.copy()


for i, camera in enumerate(cameras):
    print(i)
    cameras[i]["thread"] = threading.Thread(target=get_video, args=(camera,))
    cameras[i]["thread"].daemon = True
    cameras[i]["thread"].start()


def generate(camera_index):
    global cameras, lock
    while True:
        with lock:
            if cameras[camera_index]['outputFrame'] is None:
                continue
            (flag, encodedImage) = cv2.imencode(
                ".jpg", cameras[camera_index]['outputFrame'])
            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


@app.route("/stream")
def video_feed():
    camera_index = request.args.get("camara")
    camera_index = int(camera_index)
    print(camera_index)
    # return Response("0")
    return Response(generate(camera_index),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':

    # t = threading.Thread(target=get_video)
    # t.daemon = True
    # t.start()
    app.run(host="0.0.0.0", port=5001, debug=True,
            threaded=True, use_reloader=False)
