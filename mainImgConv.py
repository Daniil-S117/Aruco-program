import numpy as np
import cv2
from datetime import datetime
import os
import csv
import re
import easyocr

print("Эта программа распознает значение манометра с фотографии!")


def avg_circles(circles, b):
    avg_x = 0
    avg_y = 0
    avg_r = 0
    for i in range(b):
        # optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x / (b))
    avg_y = int(avg_y / (b))
    avg_r = int(avg_r / (b))
    return avg_x, avg_y, avg_r


def dist_2_pts(x1, y1, x2, y2):
    # print np.sqrt((x2-x1)^2+(y2-y1)^2)
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def PressureGaugeCheck(image1, image2, min_a, max_a, min_v, max_v):
    height, width = image1.shape[:2]
    gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)  # convert to gray
    # gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # gray = cv2.medianBlur(gray, 5)

    # for testing, output gray image
    # cv2.imwrite('gauge-%s-bw.%s' %(gauge_number, file_type),gray)

    # detect circles
    # restricting the search from 35-48% of the possible radii gives fairly good results across different samples.  Remember that
    # these are pixel values which correspond to the possible radii search range.
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, np.array([]), 100, 50, int(height * 0.35),
                               int(height * 0.48))
    # average found circles, found it to be more accurate than trying to tune HoughCircles parameters to get just the right one
    a, b, c = circles.shape
    x, y, r = avg_circles(circles, b)

    # for testing, output circles on image
    # cv2.imwrite('gauge-%s-circles.%s' % (gauge_number, file_type), img)

    # for calibration, plot lines from center going out at every 10 degrees and add marker
    # for i from 0 to 36 (every 10 deg)

    separation = 10.0  # in degrees
    interval = int(360 / separation)
    p1 = np.zeros((interval, 2))  # set empty arrays
    p2 = np.zeros((interval, 2))
    p_text = np.zeros((interval, 2))
    for i in range(0, interval):
        for j in range(0, 2):
            if j % 2 == 0:
                p1[i][j] = x + 0.9 * r * np.cos(separation * i * 3.14 / 180)  # point for lines
            else:
                p1[i][j] = y + 0.9 * r * np.sin(separation * i * 3.14 / 180)
    text_offset_x = 10
    text_offset_y = 5
    for i in range(0, interval):
        for j in range(0, 2):
            if j % 2 == 0:
                p2[i][j] = x + r * np.cos(separation * i * 3.14 / 180)
                p_text[i][j] = x - text_offset_x + 1.2 * r * np.cos(
                    (separation) * (i + 9) * 3.14 / 180)  # point for text labels, i+9 rotates the labels by 90 degrees
            else:
                p2[i][j] = y + r * np.sin(separation * i * 3.14 / 180)
                p_text[i][j] = y + text_offset_y + 1.2 * r * np.sin(
                    (separation) * (i + 9) * 3.14 / 180)  # point for text labels, i+9 rotates the labels by 90 degrees

    # ======================================================================================
    # //////////////////////////////////////////////////////////////////////////////////////
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Set threshold and maxValue
    thresh = 175
    maxValue = 255

    # apply thresholding which helps for finding lines
    th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV)

    # find lines
    minLineLength = 10
    maxLineGap = 0
    lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100, minLineLength=minLineLength,
                            maxLineGap=0)  # rho is set to 3 to detect more lines, easier to get more then filter them out later

    # for testing purposes, show all found lines
    # for i in range(0, len(lines)):
    #   for x1, y1, x2, y2 in lines[i]:
    #      cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #      cv2.imwrite('gauge-%s-lines-test.%s' %(gauge_number, file_type), img)

    # remove all lines outside a given radius
    final_line_list = []
    # print "radius: %s" %r

    diff1LowerBound = 0.15  # diff1LowerBound and diff1UpperBound determine how close the line should be from the center
    diff1UpperBound = 0.25
    diff2LowerBound = 0.5  # diff2LowerBound and diff2UpperBound determine how close the other point of the line should be to the outside of the gauge
    diff2UpperBound = 1.0
    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            diff1 = dist_2_pts(x, y, x1, y1)  # x, y is center of circle
            diff2 = dist_2_pts(x, y, x2, y2)  # x, y is center of circle
            # set diff1 to be the smaller (closest to the center) of the two), makes the math easier
            if (diff1 > diff2):
                temp = diff1
                diff1 = diff2
                diff2 = temp
            # check if line is within an acceptable range
            if (((diff1 < diff1UpperBound * r) and (diff1 > diff1LowerBound * r) and (
                    diff2 < diff2UpperBound * r)) and (diff2 > diff2LowerBound * r)):
                line_length = dist_2_pts(x1, y1, x2, y2)
                # add to final list
                final_line_list.append([x1, y1, x2, y2])

    # assumes the first line is the best one
    x1 = final_line_list[0][0]
    y1 = final_line_list[0][1]
    x2 = final_line_list[0][2]
    y2 = final_line_list[0][3]
    # draw center and circle
    cv2.circle(image2, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)  # draw circle
    cv2.circle(image2, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)  # draw center of circle
    cv2.line(image2, (x1, y1), (x2, y2), (0, 255, 255), 3)

    # for testing purposes, show the line overlayed on the original image
    # cv2.imwrite(folder_path + "/" + filename + "-needle.jpg", img)

    # find the farthest point from the center to be what is used to determine the angle
    dist_pt_0 = dist_2_pts(x, y, x1, y1)
    dist_pt_1 = dist_2_pts(x, y, x2, y2)
    if (dist_pt_0 > dist_pt_1):
        x_angle = x1 - x
        y_angle = y - y1
    else:
        x_angle = x2 - x
        y_angle = y - y2
    # take the arc tan of y/x to find the angle
    res = np.arctan(np.divide(float(y_angle), float(x_angle)))
    # np.rad2deg(res) #coverts to degrees

    # print x_angle
    # print y_angle
    # print(res)
    print("Угол положения: %s " % round(np.rad2deg(res), 1))

    # these were determined by trial and error
    res = np.rad2deg(res)
    if x_angle > 0 and y_angle > 0:  # in quadrant I
        final_angle = 270 - res
    if x_angle < 0 < y_angle:  # in quadrant II
        final_angle = 90 - res
    if x_angle < 0 and y_angle < 0:  # in quadrant III
        final_angle = 90 - res
    if x_angle > 0 > y_angle:  # in quadrant IV
        final_angle = 270 - res

    # print final_angle

    old_min = float(min_a)
    old_max = float(max_a)

    new_min = float(min_v)
    new_max = float(max_v)

    old_value = final_angle

    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    new_value = (((old_value - old_min) * new_range) / old_range) + new_min

    val = new_value
    # //////////////////////////////////////////////////////////////////////////////////////
    # add the lines and labels to the image
    for i in range(0, interval):
        cv2.line(image2, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])), (0, 255, 0), 2)
        cv2.putText(image2, '%s' % (int(i * separation)), (int(p_text[i][0]), int(p_text[i][1])),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3, (0, 0, 0), 1, cv2.LINE_AA)
    return image2, val


def text_recognition(file_path):
    reader = easyocr.Reader(["ru", "en"])
    result = reader.readtext(file_path, batch_size=3, low_text=0.2, detail=0,
                             paragraph=True)
    nums = []

    for line in result:
        numa = re.sub(r',', r'.', line)
        num = re.search(r"\b[-+]?(?:\d*\.*\d+)\b", numa)
        try:
            numa = float(num.group(0))
            nums.append(numa)
        except:
            continue
    if min(nums) > 0:
        nums.insert(0, 0)
    print(nums)
    print('Минимум: ', min(nums), 'Максимум: ', max(nums))
    return min(nums), max(nums)


# =============================================================================


# Для теста углы минимальных и максимальных показаний заданы по умолчанию
min_angle = 50
max_angle = 315
units = "МПа"
name = 'Pressure Gauge/2.jpg'
img1 = cv2.imread(name)
img2 = img1
gaugeNumber = 1
min_value, max_value = text_recognition(img1)

Image, val = PressureGaugeCheck(img1, img2, min_angle, max_angle, min_value, max_value)
cv2.imwrite('Gauge-%s-Indication.%s' % (1, 'jpg'), Image)
print("Показания манометра: %s %s" % (round(val, 1), units))

# Открываем файл "datafile.csv" в режиме добавления
with open('datafile.csv', 'a+', newline='') as f:
    # create the csv writer
    writer = csv.writer(f)
    # Записываем строку в csv файл
    writer.writerow([name, datetime.now().strftime("%H:%M %d-%m-%Y"), round(val, 1), units])
cv2.imshow('Gauge-%s' % (1), Image)
cv2.waitKey(0)
# =============================================================================
