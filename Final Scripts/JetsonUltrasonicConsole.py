import serial
import time

def main():
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # change this to your Arduino's serial port

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()  # read a '\n' terminated line
            print(line)
            time.sleep(1)

if __name__ == '__main__':
    main()
