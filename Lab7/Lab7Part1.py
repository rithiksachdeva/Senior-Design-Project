import RPi.GPIO as GPIO
import time
import smbus

inputpin1 = 18
inputpin2 = 21
ledoutputpin = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(inputpin1, GPIO.IN)
GPIO.setup(inputpin2, GPIO.IN)
GPIO.setup(ledoutputpin, GPIO.OUT, initial = GPIO.LOW)

bus = smbus.SMBus(1)
address = 0x40
mode1 = bus.read_byte_data(address, 0x00)
mode1 = mode1 | 0x10
bus.write_byte_data(address, 0x00, mode1)
bus.write_byte_data(address, 0xFE, 101) # corresponds to 100 Hz
mode1 = mode1 & ~0x10
bus.write_byte_data(address, 0x00, mode1)
mode1 = bus.read_byte_data(address, 0x00)
prescale = bus.read_byte_data(address, 0xFE)

def set_pwm(channel, duty_cycle):
    # Calculate the pulse width based on duty cycle
    pulse_width = int((duty_cycle / 100) * 4096)

    # Set the duty cycle for the given channel
    off_time = pulse_width & 0xFF
    on_time = pulse_width >> 8
    bus.write_byte_data(address, 0x06 + (4 * channel), 0x00)
    bus.write_byte_data(address, 0x07 + (4 * channel), 0x00)
    bus.write_byte_data(address, 0x08 + (4 * channel), off_time)
    bus.write_byte_data(address, 0x09 + (4 * channel), on_time)

def set_pwm_pulsewidth(channel, pulse_width_ms):
    bus.write_byte_data(address, 0x06 + 4 * channel, 0)
    bus.write_byte_data(address, 0x07 + 4 * channel, 0)
    pulse_width = int(round(pulse_width_ms * 4096 / (1000 * 1000000 / 50)))
    off_time = pulse_width & 0xFF
    on_time = pulse_width >> 8
    bus.write_byte_data(address, 0x08 + 4 * channel, off_time)
    bus.write_byte_data(address, 0x09 + 4 * channel, on_time)


while True:
    input1 = GPIO.input(18)
    input2 = GPIO.input(21)
    if input1 == 0 and input2 == 0:
        set_pwm(1,0)
        set_pwm_pulsewidth(0,1.5)
        GPIO.output(12, GPIO.LOW)
    elif input1 == 0 and input2 == 1:
        set_pwm(1,50)
        set_pwm_pulsewidth(0,1.1)
        GPIO.output(12, GPIO.LOW)
    elif input1 == 1 and input2 == 0:
        set_pwm(1,50)
        set_pwm_pulsewidth(0,1.9)
        GPIO.output(12, GPIO.LOW)
    elif input1 == 1 and input2 == 1:
        set_pwm(1,80)
        set_pwm_pulsewidth(0,1.5)
        GPIO.output(12, GPIO.HIGH)
    time.sleep(0.1)  # Delay to debounce inputs