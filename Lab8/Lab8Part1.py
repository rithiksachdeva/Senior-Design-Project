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

    