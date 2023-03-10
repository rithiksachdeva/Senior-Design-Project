import cv2
import nanocamera as nano

camera = nano.Camera(flip=0, width=1280, height=800, fps=30)


while True:
    frame = camera.read()

    # Apply GaussianBlur
    gauss_image = cv2.GaussianBlur(frame, (3, 3), 0)

    # Apply Canny edge detector
    edges = cv2.Canny(gauss_image, 50, 150)

    # Display images
    cv2.imshow('Original', frame)
    cv2.imshow('Blurred', gauss_image)
    cv2.imshow('Edges', edges)

    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break

camera.release()
cv2.destroyAllWindows()
del camera
print('Stopped')