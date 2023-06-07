import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering

def read_distance(GPIO_TRIGGER, GPIO_ECHO):
    # Set pins as output and input
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)  # Trigger
    GPIO.setup(GPIO_ECHO, GPIO.IN)  # Echo

    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER, False)

    # Allow module to settle
    time.sleep(0.5)

    # Send 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # Start the timer
    start = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()

    # Calculate pulse length
    elapsed = stop - start

    # Distance pulse travelled in that time is 
    distance = elapsed * 34300

    # That was the distance there and back so halve the value
    distance = distance / 2

    return distance

# Set GPIO Pins
GPIO_TRIGGER_1 = 18  # Change to your pin number
GPIO_ECHO_1 = 16     # Change to your pin number

GPIO_TRIGGER_2 = 12  # Change to your pin number
GPIO_ECHO_2 = 10     # Change to your pin number

try:
    while True:
        # Read from the sensors
        distance1 = read_distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
        distance2 = read_distance(GPIO_TRIGGER_2, GPIO_ECHO_2)

        # Print the readings
        print("Sensor 1 Distance : %.1f cm" % distance1)
        print("Sensor 2 Distance : %.1f cm" % distance2)

        # Wait before the next reading
        time.sleep(1)

except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()
