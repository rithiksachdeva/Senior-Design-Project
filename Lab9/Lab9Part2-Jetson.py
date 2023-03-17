#!/usr/bin/python3
import time
import serial
import RPi.GPIO as GPIO

inputpin1 = 18
inputpin2 = 21

GPIO.setmode(GPIO.BOARD)
GPIO.setup(inputpin1, GPIO.IN)
GPIO.setup(inputpin2, GPIO.IN)

print("UART Demonstration Program")
print("NVIDIA Jetson Nano Developer Kit")

serial_port = serial.Serial(
    port="/dev/ttyTHS1",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
# Wait a second to let the port initialize
time.sleep(1)

try:
    while True:
        input1 = GPIO.input(inputpin1)
        input2 = GPIO.input(inputpin2)
        if input1 == 0 and input2 == 0:
            serial_port.write('00'.encode())
            print("Sent '00' - both inputs are 0")
        elif input1 == 0 and input2 == 1:
            serial_port.write('01'.encode())
            print("Sent '01' - Input0 is 0 and Input1 is 1")
        elif input1 == 1 and input2 == 0:
            serial_port.write('10'.encode())
            print("Sent '10' - Input0 is 1 and Input1 is 0")
        elif input1 == 1 and input2 == 1:
            serial_port.write('11'.encode())
            print("Sent '11' - both inputs are 1")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting Program")
except Exception as exception_error:
    print("Error occurred. Exiting Program")
    print("Error: " + str(exception_error))
finally:
    serial_port.close()
    GPIO.cleanup()
    pass
