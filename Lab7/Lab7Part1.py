import RPi.GPIO as GPIO
import time
import smbus

inputpin1 = 18
inputpin2 = 21
ledoutputpin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(inputpin1, GPIO.IN)
GPIO.setup(inputpin2, GPIO.IN)
GPIO.setup(ledoutputpin, GPIO.OUT, initial = GPIO.HIGH)

bus = smbus.SMBus(1)
address = 0x40
mode1 = bus.read_byte_data(address, 0)
print("Mode1 Reg = ", hex(mode1))
mode1 = mode1 | 0x10
bus.write_byte_data(address, 0, mode1)
bus.write_byte_data(address, 0xFE, 62) # corresponds to 100 Hz
mode1 = mode1 & ~0x10
bus.write_byte_data(address, 0, mode1)
time.sleep(1)

mode1 = bus.read_byte_data(address, 0)
print("Mode1 Reg = ", hex(mode1))
bus.write_byte_data(address,1,4)
prescale = bus.read_byte_data(address, 0xFE)
print("prescale = ", prescale)
time.sleep(0.5)

def setup(channel, offtime):
    bus.write_byte_data(address,7 + (channel*4),0)
    bus.write_byte_data(address,6 + (channel*4),0)
    bus.write_byte_data(address,9 + (channel*4),offtime >> 8)
    bus.write_byte_data(address,8 + (channel*4),offtime & 0xFF)

setup(0, 2000)
setup(1, 1000)

def updatedutycycle(channel, offtime):
    bus.write_byte_data(address, 9 + (channel*4), offtime >> 8)
    bus.write_byte_data(address, 8 + (channel*4), offtime & 0xFF)

while True:
    input1 = GPIO.input(18)
    input2 = GPIO.input(21)
    if input1 == 0 and input2 == 0:
        updatedutycycle(0, 650)
        updatedutycycle(1, 0)
        GPIO.output(ledoutputpin, GPIO.HIGH)
        print("input1 = 0, input2 = 0, output = HIGH")
    elif input1 == 0 and input2 == 1:
        updatedutycycle(0, 480)
        updatedutycycle(1, 2100)
        GPIO.output(12, GPIO.HIGH)
        print("input1 = 0, input2 = 1, output = HIGH")
    elif input1 == 1 and input2 == 0:
        updatedutycycle(0, 800)
        updatedutycycle(1, 2100)
        GPIO.output(12, GPIO.HIGH)
        print("input1 = 1, input2 = 0, output = HIGH")
    elif input1 == 1 and input2 == 1:
        updatedutycycle(0, 650)
        updatedutycycle(1, 3350)
        GPIO.output(12, GPIO.LOW)
        print("input1 = 1, input2 = 1, output = LOW")
    else:
        print("Could not find")
    time.sleep(0.1)  # Delay to debounce inputs