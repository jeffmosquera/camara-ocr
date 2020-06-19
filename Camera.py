import requests
import cv2
import numpy as np


class Camera:

    def __init__(self, user, password, ip, port):
        self.__user = user
        self.__password = password
        self.__ip = ip
        self.__port = port

        self.__url = "http://"+self.__user+":"+self.__password+"@"+self.__ip + \
            ":"+self.__port+"/Streaming/channels/102/picture"

    def getSnapshot(self):
        resp = requests.get(self.__url, stream=True)

        status_code = resp.status_code
        if status_code == 200:
            resp_raw = resp.raw
            image = np.asarray(bytearray(resp_raw.read()), dtype="uint8")

            return image
        else:
            return None
