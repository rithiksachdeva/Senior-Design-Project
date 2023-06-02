##import serial
##
##ser_openMV1 = serial.Serial(
##    port="/dev/ttyTHS1",
##    baudrate=115200,
##    bytesize=serial.EIGHTBITS,
##    parity=serial.PARITY_NONE,
##    stopbits=serial.STOPBITS_ONE,
##)
##
##while True:
##    print("Listening...")
##    if ser_openMV1.in_waiting > 0:
##        msg = ser_openMV1.readline().decode('utf-8').strip()
##        if msg == "ready to proceed":
##            break
##        else:
##            print("Unexpected message: ", msg)
##print("We did it")
##
import serial
import time

# Initialize the UART port
ser = serial.Serial(
    port="/dev/ttyTHS1",  # Replace with your UART port
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)

time.sleep(1)

# Continuously send data
while True:
    message = "Hello from Jetson!\n"
    ser.write(message.encode())  # Encode the string to bytes and send
    time.sleep(5)  # Wait for a second
