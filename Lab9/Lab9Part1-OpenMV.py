import time
from pyb import Pin, Timer

# DC Motor PWM
dc_motor_timer = Timer(2, freq=1500) # Frequency 1.5 kHz
dc_motor_ch = dc_motor_timer.channel(3, Timer.PWM, pin=Pin("P4")) # TIM2 Channel 3, Pin P4

# Servo PWM
servo_timer = Timer(4, freq=100) # Frequency 100 Hz
servo_ch = servo_timer.channel(1, Timer.PWM, pin=Pin("P7")) # TIM4 Channel 1, Pin P7

# Servo parameters
servo_min_pulse_width = 1100 # 1.1 ms
servo_max_pulse_width = 1900 # 1.9 ms
servo_pulse_width_step = 100 # 100 us
servo_period_counts = servo_timer.period() # Timer period in counts

# Function to convert pulse width in microseconds to counts
def pulse_width_to_counts(pulse_width, period_counts, frequency):
    return int(pulse_width * period_counts / (1_000_000 / frequency))

while True:
    for dc_motor_duty_cycle in range(10, 91, 10): # 10% to 90% duty cycle
        # Update DC motor duty cycle
        dc_motor_ch.pulse_width_percent(dc_motor_duty_cycle)

        # Update servo pulse width
        servo_pulse_width = servo_min_pulse_width + (dc_motor_duty_cycle - 10) * servo_pulse_width_step
        servo_pulse_width_counts = pulse_width_to_counts(servo_pulse_width, servo_period_counts, 100)
        servo_ch.pulse_width(servo_pulse_width_counts)

        print(f"DC Motor Duty Cycle: {dc_motor_duty_cycle}%, Servo Pulse Width: {servo_pulse_width}us")
        time.sleep(0.1)

    for dc_motor_duty_cycle in range(90, 9, -10): # 90% to 10% duty cycle
        # Update DC motor duty cycle
        dc_motor_ch.pulse_width_percent(dc_motor_duty_cycle)

        # Update servo pulse width
        servo_pulse_width = servo_min_pulse_width + (dc_motor_duty_cycle - 10) * servo_pulse_width_step
        servo_pulse_width_counts = pulse_width_to_counts(servo_pulse_width, servo_period_counts, 100)
        servo_ch.pulse_width(servo_pulse_width_counts)

        print(f"DC Motor Duty Cycle: {dc_motor_duty_cycle}%, Servo Pulse Width: {servo_pulse_width}us")
        time.sleep(0.1)
