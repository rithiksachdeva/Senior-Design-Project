import cv2
import numpy as np

camera = nano.Camera()
cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()

    # Apply GaussianBlur
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)

    # Apply Canny edge detector
    edges = cv2.Canny(blurred, 50, 150)

    # Display images
    cv2.imshow('Original', frame)
    cv2.imshow('Blurred', blurred)
    cv2.imshow('Edges', edges)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()