import time
from pyb import Pin, Timer, UART
import sensor, image, time, math

# Hardware setup
dc_motor_timer = Timer(2, freq=100) # Frequency 100 kHz
dc_motor_ch = dc_motor_timer.channel(3, Timer.PWM, pin=Pin("P4")) # TIM2 Channel 3, Pin P4
servo_timer = Timer(4, freq=100) # Frequency 100 Hz
servo_ch = servo_timer.channel(1, Timer.PWM, pin=Pin("P7")) # TIM4 Channel 1, Pin P7

servo_period_counts = servo_timer.period() # Timer period in counts
dcmotor_period_counts = dc_motor_timer.period()

# Helper functions
def pulse_width_to_counts(pulse_width, period_counts, frequency):
    return int(pulse_width * period_counts / (1_000_000 / frequency))

def set_pwm_pulse_width(timer_ch, period_counts, pulse_width, frequency):
    pulse_width_counts = pulse_width_to_counts(pulse_width, period_counts, frequency)
    timer_ch.pulse_width(pulse_width_counts)

# Initialize UART
uart = UART(1, 115200)
uart.init(115200, bits=8, parity=None, stop=1, flow=0)

# Initialize image sensor
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

tag_families = 0
tag_families |= image.TAG36H11

# Start car (neutral)
set_pwm_pulse_width(dc_motor_ch, dcmotor_period_counts, 1500, 100) # Set DC motor to neutral
set_pwm_pulse_width(servo_ch, servo_period_counts, 1500, 100) # Set servo to neutral

while(True):
    img = sensor.snapshot()
    tags = img.find_apriltags(families=tag_families)

    # Looking for Tag 1
    for tag in tags:
        if tag.id() == 1:
            uart.write('ready to proceed\n'.encode())
            break

    while uart.any() > 0: # Receive instructions from UART
        instruction = uart.readline().decode().strip()
        if instruction[0] == 'D':
            # For 'D' instructions, set DC motor pulse width and sleep for given duration
            set_pwm_pulse_width(dc_motor_ch, dcmotor_period_counts, instruction[1][0], 100)
            time.sleep(instruction[1][1])

        elif instruction[0] == 'S':
            # For 'S' instructions, set servo pulse width and sleep for given duration
            # then set the pulse width back to 1500
            set_pwm_pulse_width(servo_ch, servo_period_counts, instruction[1][0], 100)
            time.sleep(instruction[1][1])
            set_pwm_pulse_width(servo_ch, servo_period_counts, 1500, 100)

        elif instruction[0] == 'END':
            # For 'END' instructions, stop the car and start looking for the end tag
            end_tag = instruction[1]
            while True:
                img = sensor.snapshot()
                tags = img.find_apriltags(families=tag_families)
                for tag in tags:
                    if tag.id() == end_tag:
                        uart.write('ACK\n'.encode())
                        break
