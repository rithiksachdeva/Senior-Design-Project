import time
import Jetson.GPIO as GPIO
from nanocamera import Camera
import cv2

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, GPIO.LOW)
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, GPIO.LOW)
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, GPIO.LOW)

camera = Camera(flip=0, width=1280, height=800, fps=30)

while True:
    frame = camera.read()

    params = cv2.SimpleBlobDetector_Params()
    params.blobColor = 255
    detector = cv2.SimpleBlobDetector_create(params)

    keypoints = detector.detect(frame)
    if keypoints: # If blob is seen 
        for keypoint in keypoints: # for every blob is seen  
            if keypoint.pt[0] < frame.shape[1] / 3: # exists in 1/3 of frame (left side of frame) 
                print("RED LED")
                GPIO.output(11, GPIO.HIGH)
            elif keypoint.pt[0] < frame.shape[1] * 2 / 3: # exists in 2/3 of frame (right side of frame) 
                print("GREEN LED")
                GPIO.output(13, GPIO.HIGH)
            else: # exists in 3/3 of frame (center of frame) 
                print("BLUE LED")
                GPIO.output(15, GPIO.HIGH)
    else: # no blob 
        print("NO BLOBS")
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)

    # display the frame
    cv2.imshow('Camera', frame)
    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break

camera.release()
cv2.destroyAllWindows()
del camera
print('Stopped')

    