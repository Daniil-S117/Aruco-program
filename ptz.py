import imutils
import threading
import time
import cv2
import sys
import keyboard
from time import sleep
from onvif import ONVIFCamera
# Ошибка типа обходного решения (скопировано из ONVIFCameraControl)
import zeep

IP = '10.16.10.248'  # IP адрес камеры
PORT = 8080  # Порт
USER = "admin"  # Логин
PASS = "Abc.12345"  # Пароль


# подключение к камере по IP адрессу
def selectCamera(address):
    return cv2.VideoCapture(address)


# обнаружение ArUco маркеров
def arucoDetector(_frame):
    # обнаружить маркеры ArUco во входном кадре
    (corners, ids, rejected) = arucoDetect.detectMarkers(_frame)
    cX, cY = 350, 250
    # убедиться, что обнаружен *по крайней мере* один маркер ArUco
    if len(corners) > 0:
        # сложить список идентификаторов ArUco
        ids = ids.flatten()
        # цикл для обнаруженния углов ArUCo
        for (markerCorner, markerID) in zip(corners, ids):
            # получение углов маркеров (они всегда возвращаются
            # в порядке сверху-слева, сверху-справа, снизу-справа и снизу-слева)

            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # преобразует каждые пары (x, y)-координат в целые числа
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # рисует ограничительную рамку для обнаружения ArUCo
            cv2.line(_frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(_frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(_frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(_frame, bottomLeft, topLeft, (0, 255, 0), 2)

            # вычислить и нарисовать центральные (x, y)-координаты
            # маркера ArUco
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(_frame, (cX, cY), 4, (0, 0, 255), -1)

            print("X: " + str(cX) + " Y: " + str(cY))
            # нарисовать идентификатор маркера ArUco на кадре
            cv2.putText(_frame, str(markerID),
                        (topLeft[0], topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

    # вернуть и выходной кадр и координаты центра маркера
    return _frame, cX, cY


# отчёт разницы между маркером и центром экрана
def scale_angle(x):
    if abs(x) < 10: return 0
    if x > CANVAS_RANGE:
        return 1
    elif x < -CANVAS_RANGE:
        return -1
    else:
        return x / CANVAS_RANGE


# работа с камерой
def cameraWork():
    cX, cY = 350, 250  # координаты центра экрана
    while cap.isOpened():
        # обрабатывать кадры пока работает камера
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=700)
        # наведение камеры на ArUco маркеры
        if flag:
            frame, mX, mY = arucoDetector(frame)
            print(scale_angle(cX), scale_angle(cY))
            if cX > mX:
                cX = cX - 1
            elif cX < mX:
                cX = cX + 1
            if cY > mY:
                cY = cY - 1
            elif cY < mY:
                cY = cY + 1
        # вывод текста на экран
        cXY = "X: " + str(cX) + " Y: " + str(cY)
        cv2.putText(frame, str(cXY),
                    (0, 25),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1, (0, 0, 255), 2)

        cv2.drawMarker(frame, (cX, cY), color=[255, 0, 0], thickness=5,
                       markerType=cv2.MARKER_CROSS, line_type=cv2.LINE_AA,
                       markerSize=100)
        cv2.imshow('Video', frame)
        # команда паузы видео
        if cv2.waitKey(30) & keyboard.is_pressed("SPACE"):
            cv2.waitKey(-1)
    else:
        print('Error read the image!!')
    # отключение видео
    cap.release()
    cv2.destroyAllWindows()


# принятие команд
def takeInput():
    global flag  # опознание маркеров
    global cap  # функции камеры
    while True:
        # отключение камеры
        if cv2.waitKey(30) & keyboard.is_pressed("q"):
            cap.release()
            break
        # вкл/выкл опознание маркеров
        elif cv2.waitKey(30) & keyboard.is_pressed("a"):
            flag = not flag
            print(flag)
        # переключение на камеру компьютера
        elif cv2.waitKey(30) & keyboard.is_pressed("F1"):
            cap.release()
            cap = selectCamera(0)
        # переключение на камеру PTZ
        elif cv2.waitKey(30) & keyboard.is_pressed("F2"):
            cap.release()
            cap = selectCamera("rtsp://10.16.10.248:554/ch0/stream0")


# вернуть xmlvalue
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


# непрерывное движение
def perform_move(ptz, request, timeout):
    # начала непрерывного движения
    ptz.ContinuousMove(request)
    # Подождите определенное время
    sleep(timeout)
    # остановка непрерывного движения
    ptz.Stop({'ProfileToken': request.ProfileToken})


# движение вверх
def move_up(ptz, request, timeout=1):
    print('move up...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)


# движение вниз
def move_down(ptz, request, timeout=1):
    print('move down...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)


# движение вправо
def move_right(ptz, request, timeout=1):
    print('move right...')
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)


# движение влево
def move_left(ptz, request, timeout=1):
    print('move left...')
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)


# продолжительное движение
def cam_move(x, y, z):
    global move_req
    move_req.Velocity.PanTilt.x = x
    move_req.Velocity.PanTilt.y = y
    move_req.Velocity.Zoom.x = z
    ptz.ContinuousMove(move_req)


# остановка движения
def cam_stop():
    global stop_req
    ptz.Stop(stop_req)


if __name__ == '__main__':
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    # параметры камеры Evidence
    EVIDENCE = {'IP': '10.16.10.248', 'Port': 8080, 'Login': "admin", 'Password': "Abc.12345",
                'Address': "rtsp://10.16.10.248:554/ch0/stream0", "Thermal": "rtsp://10.16.10.248:554/ch1/stream0"}
    mycam = ONVIFCamera('10.16.10.248', 8080, 'admin', 'Abc.12345')
    # создание объекта медиаслужбы
    media = mycam.create_media_service()
    # получение целевого профиля для маркера
    media_profile = media.GetProfiles()[0]
    profile_token = media_profile.token
    print(media_profile)

    # создание объекта службы ptz
    ptz = mycam.create_ptz_service()
    # получение статуса PTZ для фиктивного PTZVector
    request = ptz.create_type('GetStatus')
    request.ProfileToken = profile_token
    ptz_status = ptz.GetStatus(request)
    print(ptz_status)
    ptz_vector = ptz_status.Position  # просто случайный PTZVector
    print(ptz_vector)
    # запрос на остановку
    stop_req = ptz.create_type('Stop')
    stop_req.ProfileToken = media_profile.token
    stop_req.PanTilt = True
    stop_req.Zoom = True
    # запрос на перемещение
    move_req = ptz.create_type('ContinuousMove')
    move_req.ProfileToken = profile_token
    move_req.Velocity = ptz_vector  # иначе это тип None
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    # Диапазон поворота и наклона
    # ПРИМЕЧАНИЕ: X и Y - вектор скорости.
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
    # библиотеки ArUco маркеров
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
    arucoDict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT["DICT_5X5_100"])
    arucoParams = cv2.aruco.DetectorParameters()
    arucoDetect = cv2.aruco.ArucoDetector(arucoDict, arucoParams)
    cap = selectCamera(0)
    CANVAS_RANGE = 350
    print("")
    flag = True
    min_angle = 40
    max_angle = 310
    min_value = 0
    max_value = 100
    units = "L"
    # предустановки координатов камеры
    setupX = [[20, 50, 20, 30], [30, 40, 20], [10, 20, 30], [50, 0, 10], [], [], [], [], [], [], []]

    while True:
        command = int(input("Предустановку от 0 до 9: "))
        # движение вправо
        move_right(ptz, request, setupX[command][0])
        # движение влево
        move_left(ptz, request, setupX[command][1])
        # движение вверх
        move_up(ptz, request, setupX[command][2])
        # движение вниз
        move_down(ptz, request, setupX[command][3])
        # два потока функций: работы камеры и принятие команд
        th1 = threading.Thread(target=cameraWork, daemon=False).start()
        th2 = threading.Thread(target=takeInput, daemon=True).start()
        # определение показаний манометра
        # img, val = PressureGaugeCheck(img, min_angle, max_angle, min_value, max_value)
