import time
from pyb import Pin, Timer, UART, LED
import sensor, image, time, math

# Hardware setup
servo_timer = Timer(4, freq=50) # Frequency 50 Hz
servo_ch = servo_timer.channel(1, Timer.PWM, pin=Pin("P7")) # TIM4 Channel 1, Pin P7

servo_period_counts = servo_timer.period() # Timer period in counts

# Helper functions
def pulse_width_to_counts(pulse_width, period_counts, frequency):
    return int(pulse_width * period_counts / (1_000_000 / frequency))

def set_pwm_pulse_width(timer_ch, period_counts, pulse_width, frequency):
    pulse_width_counts = pulse_width_to_counts(pulse_width, period_counts, frequency)
    timer_ch.pulse_width(pulse_width_counts)

# Start testing servo control pulse widths
print("Testing servo control pulse widths")
for pulse_width in range(500, 2500, 50):
    print(f"Setting pulse width to {pulse_width}us")
    set_pwm_pulse_width(servo_ch, servo_period_counts, pulse_width, 50)
    time.sleep(2)  # wait for the servo to move to its new position
