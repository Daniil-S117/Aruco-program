import threading
import time

import cv2

done = False

camera = "rtsp://10.16.10.248:554/ch0/stream0"

def worker(text):
    cap = cv2.VideoCapture(0)
    counter = 0
    while True:
        ret, frame = cap.read()
        if ret == 1:
            cv2.imshow('frame', frame)
        else:
            print('Error read the image!!')
        # if cv2.waitKey(30) & 0xFF == ord('q'):
        #     break


def printer(text):
    while True:
        counter = + 1
        print(f"{text}: {counter}")
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break


th1 = threading.Thread(target=worker, daemon=False, args=("input",)).start()
th2 = threading.Thread(target=printer, daemon=True, args=("camera",)).start()


input("Start ")
done = True
