import time
from pyb import Pin, Timer, UART, LED

# DC Motor PWM
dc_motor_timer = Timer(2, freq=1500)
dc_motor_ch = dc_motor_timer.channel(3, Timer.PWM, pin=Pin("P4"))

# Servo PWM
servo_timer = Timer(4, freq=100)
servo_ch = servo_timer.channel(1, Timer.PWM, pin=Pin("P7"))
servo_period_counts = servo_timer.period()

# Function to convert pulse width in microseconds to counts
def pulse_width_to_counts(pulse_width, period_counts, frequency):
    return int(pulse_width * period_counts / (1_000_000 / frequency))

# UART Control
uart = UART(1, 115200)
uart.init(115200, bits=8, parity=None, stop=1, flow=0)
print("UART test program")
red_led = LED(1)
red_led.on()
time.sleep_ms(5000)  # 5 second delay
red_led.off()

while True:
    if uart.any() > 0:
        ch = uart.readchar()
        key = chr(ch)
        print(key)

        if key == '00':
            dc_motor_ch.pulse_width_percent(20)  # Set dc_motor duty cycle to 20%
            servo_pulse_width = 1500  # Set servo pulse width to 1.5 ms
            servo_pulse_width_counts = pulse_width_to_counts(servo_pulse_width, servo_period_counts, 100)
            servo_ch.pulse_width(servo_pulse_width_counts)
            print("DC Motor Duty Cycle: 20%, Servo Pulse Width: 1.5ms")
        elif key == '01':
            dc_motor_ch.pulse_width_percent(50)  # Set dc_motor duty cycle to 20%
            servo_pulse_width = 1100  # Set servo pulse width to 1.5 ms
            servo_pulse_width_counts = pulse_width_to_counts(servo_pulse_width, servo_period_counts, 100)
            servo_ch.pulse_width(servo_pulse_width_counts)
            print("DC Motor Duty Cycle: 50%, Servo Pulse Width: 1.1ms")
        elif key == '10':
            dc_motor_ch.pulse_width_percent(50)  # Set dc_motor duty cycle to 20%
            servo_pulse_width = 1900  # Set servo pulse width to 1.5 ms
            servo_pulse_width_counts = pulse_width_to_counts(servo_pulse_width, servo_period_counts, 100)
            servo_ch.pulse_width(servo_pulse_width_counts)
            print("DC Motor Duty Cycle: 50%, Servo Pulse Width: 1.9ms")
        elif key == '11':
            dc_motor_ch.pulse_width_percent(80)  # Set dc_motor duty cycle to 20%
            servo_pulse_width = 1500  # Set servo pulse width to 1.5 ms
            servo_pulse_width_counts = pulse_width_to_counts(servo_pulse_width, servo_period_counts, 100)
            servo_ch.pulse_width(servo_pulse_width_counts)
            print("DC Motor Duty Cycle: 80%, Servo Pulse Width: 1.5ms")
        else:
            print("unknown char received")
