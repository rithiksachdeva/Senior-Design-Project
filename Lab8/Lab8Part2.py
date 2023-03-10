import cv2
import numpy as np
import nanocamera as nano
import Jetson.GPIO as GPIO
import time
import logging

def detect_line_segments(cropped_edges):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]), minLineLength=10, maxLineGap=15)
    return line_segments

def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        logging.info('No line_segment segments detected')
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines

def display_lines(frame, lines, line_color=(0, 255, 255), line_width=20):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1 / 2),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    return cropped_edges
   
LED_GREEN = 11
LED_BLUE = 13
LED_RED = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_GREEN, GPIO.OUT)
GPIO.setup(LED_BLUE, GPIO.OUT)
GPIO.setup(LED_RED, GPIO.OUT)

# Create NanoCamera instance
camera = nano.Camera(flip=0, width=1280, height=800, fps=30)

while True:
    # Read camera frame
    frame = camera.read()

    # Apply Gaussian blur
    gauss_image = cv2.GaussianBlur(frame, (3, 3), 0)

    # Apply Canny edge filter
    edges = cv2.Canny(gauss_image, 50, 150)

    roi_image = region_of_interest(edges)


    # Detect line segments using Hough Lines Transform
    line_segments = detect_line_segments(edges)

    # Average slope and intercept of line segments to get lane lines
    lane_lines = average_slope_intercept(frame, line_segments)
    print(lane_lines)

    # Calculate angle that describes the tilt of the lane
    line_image = display_lines(frame, lane_lines)

    # Display camera frame, blurred frame, and canny frame
    cv2.imshow("Camera", frame)
    #cv2.imshow("Blurred Frame", gauss_image)
    #cv2.imshow("Canny Frame", edges)
    cv2.imshow('New Image', roi_image)
    cv2.imshow('Line Image', line_image)

    # Light up appropriate LED based on the angle
    '''if angle > -70 and angle < 70:
        print("MIDDLE 140 degrees")
        GPIO.output(LED_GREEN, GPIO.HIGH)
        GPIO.output(LED_BLUE, GPIO.LOW)
        GPIO.output(LED_RED, GPIO.LOW)
    elif angle >= 70:
        print(">70 degrees")
        GPIO.output(LED_GREEN, GPIO.LOW)
        GPIO.output(LED_BLUE, GPIO.HIGH)
        GPIO.output(LED_RED, GPIO.LOW)
    else:
        print("less than -70 degrees")
        GPIO.output(LED_GREEN, GPIO.LOW)
        GPIO.output(LED_BLUE, GPIO.LOW)
        GPIO.output(LED_RED, GPIO.HIGH)'''

    # Wait for key press to exit
    if cv2.waitKey(1) == ord('q'):
        break

# Release camera and close windows
camera.release()
cv2.destroyAllWindows()
del camera
print('Stopped')