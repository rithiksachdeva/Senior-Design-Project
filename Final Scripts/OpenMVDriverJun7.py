import utime
import sensor, image, time, math
from pyb import Pin, Timer, UART, LED

# Hardware setup
dc_motor_timer = Timer(2, freq=100) # Frequency 100 kHz
dc_motor_ch = dc_motor_timer.channel(3, Timer.PWM, pin=Pin("P4")) # TIM2 Channel 3, Pin P4
servo_timer = Timer(4, freq=100) # Frequency 100 Hz
servo_ch = servo_timer.channel(1, Timer.PWM, pin=Pin("P7")) # TIM4 Channel 1, Pin P7

servo_period_counts = servo_timer.period() # Timer period in counts
dcmotor_period_counts = dc_motor_timer.period()

# Ultrasonic sensor pins
trig_pins = ['P2', 'P8']
echo_pins = ['P3', 'P9']

# Adjustment parameter
adjustment_per_cm_difference = 10

# Helper functions
def pulse_width_to_counts(pulse_width, period_counts, frequency):
    return int(pulse_width * period_counts / (1_000_000 / frequency))

def set_pwm_pulse_width(timer_ch, period_counts, pulse_width, frequency):
    pulse_width_counts = pulse_width_to_counts(pulse_width, period_counts, frequency)
    timer_ch.pulse_width(pulse_width_counts)

def distance(trig_pin, echo_pin):
    trig = Pin(trig_pin, Pin.OUT_PP)
    echo = Pin(echo_pin, Pin.IN, Pin.PULL_DOWN)
    pulse_start = 0
    pulse_end = 0
    pulse_dur = 0
    trig.value(0)
    pyb.udelay(5)
    trig.value(1)
    pyb.udelay(10)
    trig.value(0)
    limit=20000 #this is to prevent lag
    timer= pyb.micros()
    while echo.value() == 0 and timer+limit>pyb.micros():
        pulse_start = pyb.micros()
    timer= pyb.micros()
    while echo.value() == 1 and timer+limit>pyb.micros():
        pulse_end = pyb.elapsed_micros(pulse_start)
    pulse_dur = float(pulse_end)
    distance = pulse_dur / 58.2  # convert time to distance based on the speed of sound
    if distance>400: # maximum distance is 400 cm
        distance=400
    return distance

def adjust_servo_based_on_distance_difference():
    distance1 = distance(trig_pins[0], echo_pins[0])
    distance2 = distance(trig_pins[1], echo_pins[1])
    difference = distance1 - distance2

    adjustment = int(difference * adjustment_per_cm_difference)
    adjustment = max(-500, min(500, adjustment)) # Make sure the adjustment stays within the servo's valid range

    # Adjust the servo
    current_pulse_width = servo_ch.pulse_width()
    set_pwm_pulse_width(servo_ch, servo_period_counts, current_pulse_width + adjustment, 100)

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

# Initialize LED
red_led = LED(1)
blue_led = LED(2)
green_led = LED(3)

while(True):
    # Looking for a Tag ID between 8 and 29 inclusive
    while(True):
        img = sensor.snapshot()
        tags = img.find_apriltags(families=tag_families)
        red_led.on()
        for tag in tags:
            if 8 <= tag.id() <= 29:
                message = str(tag.id()) + "\n"
                uart.write(message.encode())
                while not uart.any():
                    pass
                start_tag = int(uart.read().decode())
                red_led.off()
                break
        else:
            continue
        break

    # Looking for the start tag
    while(True):
        img = sensor.snapshot()
        tags = img.find_apriltags(families=tag_families)
        blue_led.on()
        for tag in tags:
            if tag.id() == start_tag:
                message = "ready to proceed\n"
                uart.write(message.encode())
                blue_led.off()
                break
        else:
            continue
        break

    # Following instructions
    while(True):
        if uart.any() > 0: # Receive instructions from UART
            instruction = eval(uart.read().decode())

            if instruction[0] == 'D':
                # For 'D' instructions, set DC motor pulse width and sleep for given duration
                set_pwm_pulse_width(dc_motor_ch, dcmotor_period_counts, instruction[1][0], 100)

                instruction_start_time = utime.ticks_us()
                while utime.ticks_diff(utime.ticks_us(), instruction_start_time) < instruction[1][1] * 1_000_000:
                    adjust_servo_based_on_distance_difference()

            elif instruction[0] == 'S':
                # For 'S' instructions, set servo pulse width and sleep for given duration
                # then set the pulse width back to 1500
                set_pwm_pulse_width(servo_ch, servo_period_counts, instruction[1][0], 100)
                utime.sleep_ms(instruction[1][1])
                set_pwm_pulse_width(servo_ch, servo_period_counts, 1500, 100)

            elif instruction[0] == 'END':
                # For 'END' instructions, stop the car and start looking for the end tag
                end_tag = instruction[1]
                while True:
                    img = sensor.snapshot()
                    tags = img.find_apriltags(families=tag_families)
                    blue_led.on()
                    for tag in tags:
                        if tag.id() == end_tag:
                            message2 = "ACK\n"
                            uart.write(message2.encode())
                            blue_led.off()
                            while uart.any():  # while there is data waiting to be read
                                uart.readchar()  # read and discard each character
                            break
                    else:
                        continue
                    break
                break
