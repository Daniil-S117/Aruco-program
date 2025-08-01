import threading
import time
import cv2
import sys
import keyboard
import imutils
#import mainImgConv


def selectCamera(address):
    return cv2.VideoCapture(address)


def arucoDetector(_frame):
    # detect ArUco markers in the input frame
    (corners, ids, rejected) = arucoDetect.detectMarkers(_frame)
    cX, cY = 350, 250
    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)

            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # draw the bounding box of the ArUCo detection
            cv2.line(_frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(_frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(_frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(_frame, bottomLeft, topLeft, (0, 255, 0), 2)

            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(_frame, (cX, cY), 4, (0, 0, 255), -1)

            print("X: " + str(cX) + " Y: " + str(cY))
            # draw the ArUco marker ID on the frame
            cv2.putText(_frame, str(markerID),
                        (topLeft[0], topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

    # show the output frame
    return _frame, cX, cY


def scale_speed(x):
    if abs(x) < 10: return 0
    if x > CANVAS_RANGE:
        return 1
    elif x < -CANVAS_RANGE:
        return -1
    else:
        return x / CANVAS_RANGE


def cameraWork():
    cX, cY = 350, 250
    while cap.isOpened():
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=700)
        if flag:
            frame, mX, mY = arucoDetector(frame)
            print(scale_speed(cX), scale_speed(cY))
            if cX > mX:
                cX = cX - 1
            elif cX < mX:
                cX = cX + 1
            if cY > mY:
                cY = cY - 1-
            elif cY < mY:
                cY = cY + 1
        cXY = "X: " + str(cX) + " Y: " + str(cY)
        cv2.putText(frame, str(cXY),
                    (0, 25),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1, (0, 0, 255), 2)

        cv2.drawMarker(frame, (cX, cY), color=[255, 0, 0], thickness=5,
                       markerType=cv2.MARKER_CROSS, line_type=cv2.LINE_AA,
                       markerSize=100)
        #if mX == cX and mY == cY:
            # imgConv(frame)
        cv2.imshow('Video', frame)
        if cv2.waitKey(30) & keyboard.is_pressed("SPACE"):
            cv2.waitKey(-1)
    else:
        print('Error read the image!!')
    cap.release()
    cv2.destroyAllWindows()


def takeInput():
    global flag
    global cap
    while True:
        if cv2.waitKey(30) & keyboard.is_pressed("q"):
            cap.release()
            break
        elif cv2.waitKey(30) & keyboard.is_pressed("a"):
            flag = not flag
            print(flag)
        elif cv2.waitKey(30) & keyboard.is_pressed("F1"):
            cap.release()
            cap = selectCamera(0)
        elif cv2.waitKey(30) & keyboard.is_pressed("F2"):
            cap.release()
            cap = selectCamera("rtsp://10.16.10.248:554/ch0/stream0")


ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    #	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    #	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    #	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    #	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

camera1 = "rtsp://10.16.10.248:554/ch0/stream0"
cap = selectCamera(0)
CANVAS_RANGE = 350
arucoDict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT["DICT_5X5_100"])
arucoParams = cv2.aruco.DetectorParameters()
arucoDetect = cv2.aruco.ArucoDetector(arucoDict, arucoParams)

print("")
flag = True
# while(True):
#    if key.SPACE

th1 = threading.Thread(target=cameraWork, daemon=False).start()
th2 = threading.Thread(target=takeInput, daemon=True).start()
