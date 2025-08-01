import sys
from onvif import ONVIFCamera
from time import sleep

# Workaround type error (copied from ONVIFCameraControl)
import zeep


IP = '10.16.10.248'  # Camera IP address
PORT = 8080  # Port
USER = "admin"  # Username
PASS = "Abc.12345"  # Password

from time import sleep

from onvif import ONVIFCamera

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

def perform_move(ptz, request, timeout):
    # Start continuous move
    ptz.ContinuousMove(request)
    # Wait a certain time
    sleep(timeout)
    # Stop continuous move
    ptz.Stop({'ProfileToken': request.ProfileToken})


def move_up(ptz, request, timeout=1):
    print('move up...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)


def move_down(ptz, request, timeout=1):
    print('move down...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)


def move_right(ptz, request, timeout=1):
    print('move right...')
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)


def move_left(ptz, request, timeout=1):
    print('move left...')
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def cam_move(x, y, z):
    global move_req
    move_req.Velocity.PanTilt.x = x
    move_req.Velocity.PanTilt.y = y
    move_req.Velocity.Zoom.x = z
    ptz.ContinuousMove(move_req)


def cam_stop():
    global stop_req
    ptz.Stop(stop_req)


if __name__ == '__main__':
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    EVIDENCE = {'IP': '10.16.10.248', 'Port': 8080, 'Login': "admin", 'Password': "Abc.12345",
                'Address': "rtsp://10.16.10.248:554/ch0/stream0", "Thermal": "rtsp://10.16.10.248:554/ch1/stream0"}
    mycam = ONVIFCamera('10.16.10.248', 8080, 'admin', 'Abc.12345')
    # Create media service object
    media = mycam.create_media_service()
    # Get target profile for token
    media_profile = media.GetProfiles()[0]
    profile_token = media_profile.token
    # ~ print (media_profile)

    # Create ptz service object
    ptz = mycam.create_ptz_service()
    # Get PTZ status for a dummy PTZVector
    request = ptz.create_type('GetStatus')
    request.ProfileToken = profile_token
    ptz_status = ptz.GetStatus(request)
    # ~ print(ptz_status)
    ptz_vector = ptz_status.Position  # just a random PTZVector we have around
    print(ptz_vector)
    # Now we can build the stop request
    stop_req = ptz.create_type('Stop')
    stop_req.ProfileToken = media_profile.token
    stop_req.PanTilt = True
    stop_req.Zoom = True
    # Now build the move request
    move_req = ptz.create_type('ContinuousMove')
    move_req.ProfileToken = profile_token
    move_req.Velocity = ptz_vector  # otherwise it's None type
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    setupX = []
    setupY = []
    setupF = []
    while True:
        command = input("Предустановку от 0 до 9: ")
        while True:
            if command == 0:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 1:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 2:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 3:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 4:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 5:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 6:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 7:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 8:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            elif command == 9:
                # move right
                move_right(ptz, request)
                # move left
                move_left(ptz, request)
                # Move up
                move_up(ptz, request)
                # move down
                move_down(ptz, request)
            else:
                break
