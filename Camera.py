import requests
import cv2
import numpy as np
import time
from imutils.video import VideoStream


class Camera:

    def __init__(self, user, password, ip, port):
        self.__user = user
        self.__password = password
        self.__ip = ip
        self.__port = port
        self.__url = "rtsp://"+self.__user+":"+self.__password+"@"+self.__ip + \
            ":"+self.__port+"/Streaming/Channels/101"
        print(self.__url)
        self.__vs = VideoStream(src=self.__url).start()

    def getFrame(self):
        return self.__vs.read()
