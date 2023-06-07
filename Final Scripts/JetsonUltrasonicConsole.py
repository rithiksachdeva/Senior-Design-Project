import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

def read_distance(GPIO_TRIGGER, GPIO_ECHO):
    # Send 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # Wait for start of echo response
    start = GPIO.wait_for_edge(GPIO_ECHO, GPIO.RISING, timeout=500)
    if start is None:
        return None

    start = time.time()

    # Wait for end of echo response
    stop = GPIO.wait_for_edge(GPIO_ECHO, GPIO.FALLING, timeout=500)
    if stop is None:
        return None

    stop = time.time()

    elapsed = stop - start

    distance = (elapsed * 34300) / 2

    return distance

# Set GPIO Pins
GPIO_TRIGGER_1 = 18  # Change to your pin number
GPIO_ECHO_1 = 16     # Change to your pin number

GPIO_TRIGGER_2 = 12  # Change to your pin number
GPIO_ECHO_2 = 11     # Change to your pin number

# Setup GPIO pins
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO_1, GPIO.IN)      # Echo

GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO_2, GPIO.IN)      # Echo

try:
    while True:
        # Read from the sensors
        distance1 = read_distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
        distance2 = read_distance(GPIO_TRIGGER_2, GPIO_ECHO_2)

        # Print the readings
        if distance1 is not None:
            print("Sensor 1 Distance : %.1f cm" % distance1)
        else:
            print("Failed to read from Sensor 1")

        if distance2 is not None:
            print("Sensor 2 Distance : %.1f cm" % distance2)
        else:
            print("Failed to read from Sensor 2")

        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
