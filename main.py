
from imutils.video import VideoStream
from flask import Response
from flask import Flask
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


ap = argparse.ArgumentParser()
ap.add_argument("-u", "--user", type=str,
                help="Usuario de la cámara", required=True)
ap.add_argument("-p", "--password", type=str,
                help="Contraseña de la cámara", required=True)
ap.add_argument("-i", "--ip", type=str,
                help="IP de la cámara", required=True)
ap.add_argument("-po", "--port", type=str, default="554",
                help="Puerto de la cámara", required=True)
ap.add_argument("-pof", "--portflask", type=str,
                help="Puerto de la cámara", required=True)
ap.add_argument("-f", "--frame-count", type=int, default=32,
                help="# de frames para construir el modelo")
ap.add_argument("-fa", "--facerecognition", type=str, default="0",
                help="face recognition", required=True)

args = vars(ap.parse_args())

# url = "rtsp://"+args['user']+":"+args['password']+"@" + \
#     args['ip']+":"+args['port']+"/Streaming/Channels/101"
# print(url)

camera = Camera(
    user=args['user'],
    password=args['password'],
    ip=args['ip'],
    port=args['port']
)

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)


cedula = ""
nombres = ""


def get_video():
    global vs, outputFrame, lock, cedula, nombres
    total = 0

    while True:
        # time.sleep(0.1)
        image = camera.getSnapshot()
        # print(image)
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        if frame is not None:
            # frame = imutils.resize(frame, width=800)
            if args['facerecognition'] == "0":
                text_reader = TextReader(frame)
                string_frame = text_reader.getString()

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
                print(cedula)
                # boxes = text_reader.getBoxes()
                # n_boxes = len(boxes['level'])
                # for i in range(n_boxes):
                #     (x, y, w, h) = (boxes['left'][i], boxes['top']
                #                     [i], boxes['width'][i], boxes['height'][i])
                #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (7, 7), 0)

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

    t = threading.Thread(target=get_video)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=int(
        args["portflask"]), debug=True, threaded=True, use_reloader=False)
