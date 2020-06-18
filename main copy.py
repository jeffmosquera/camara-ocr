import requests
import cv2
import numpy as np
from time import sleep


user = "admin"
password = "mundo912"
ip = "192.168.100.89"
port = "80"

url = "http://"+user+":"+password+"@"+ip + \
    ":"+port+"/Streaming/channels/1/picture"


class Camera:


while True:

    resp = requests.get(url, stream=True)

    status_code = resp.status_code
    if status_code == 200:
        resp_raw = resp.raw
        image = np.asarray(bytearray(resp_raw.read()), dtype="uint8")

        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        cv2.imshow('image', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    sleep(0.05)

cv2.destroyAllWindows()
