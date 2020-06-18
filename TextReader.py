import pytesseract
from pytesseract import Output
import platform

if platform.system() == 'Linux':
    pytesseract.pytesseract.tesseract_cmd = '/bin/tesseract'
else:
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class TextReader:

    def __init__(self, frame):
        self.__frame = frame
        self.__custom_config = r'--oem 3 --psm 6'

    def getString(self):

        text = pytesseract.image_to_string(
            self.__frame, config=self.__custom_config)
        # print(text)
        return text

    def getBoxes(self):
        return pytesseract.image_to_data(self.__frame, output_type=Output.DICT)
        # n_boxes = len(d['level'])
        # for i in range(n_boxes):
        #     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
