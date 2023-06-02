import sensor, image, time, pyb
from pyb import UART

# UART(3) is the serial port connected to the Jetson Nano
uart = UART(1, 115200)
uart.init(115200, bits=8, parity=None, stop=1, flow=0)

# Initialize the sensor
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)

# Threshold value, might need to be adjusted
threshold_value = (230, 255)

while(True):
    img = sensor.snapshot()

    # Find blobs with a brightness above the threshold
    blobs = img.find_blobs([threshold_value], invert=False, roi=(0, 0, img.width(), img.height()))

    if blobs:
        # Assuming the largest blob is the light
        max_blob = max(blobs, key=lambda b: b.pixels())
        light_x, light_y = max_blob.cx(), max_blob.cy()

        # Calculate the error
        center_x, center_y = img.width() // 2, img.height() // 2
        error_x, error_y = light_x - center_x, light_y - center_y

        # Output the error over UART, only y error
        uart.write(f'error,{error_y}\n'.encode())

        # Optionally draw cross on the light and the center of the image
        img.draw_cross(light_x, light_y, color=(255, 0, 0))
        img.draw_cross(center_x, center_y, color=(0, 255, 0))
