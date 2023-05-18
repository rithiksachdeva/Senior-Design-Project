import time
import serial
import RPi.GPIO as GPIO

# Setup GPIO
GPIO.setmode(GPIO.BOARD)  
GPIO.setup(21, GPIO.OUT)  
GPIO.setup(18, GPIO.OUT)  

# Setup UART
uart = serial.Serial(
	port='/dev/ttyTHS1',  # Replace with your UART port
	baudrate=115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS
)

# Initialize GPIO
GPIO.output(21, GPIO.LOW)
GPIO.output(18, GPIO.LOW)

# Function to handle alternating GPIO states
def handle_gpio_states():
	if GPIO.input(21) == GPIO.LOW and GPIO.input(18) == GPIO.LOW:
		GPIO.output(21, GPIO.HIGH)
		GPIO.output(18, GPIO.LOW)
	elif GPIO.input(21) == GPIO.HIGH and GPIO.input(18) == GPIO.LOW:
		GPIO.output(21, GPIO.LOW)
		GPIO.output(18, GPIO.HIGH)
	elif GPIO.input(21) == GPIO.LOW and GPIO.input(18) == GPIO.HIGH:
		GPIO.output(21, GPIO.LOW)
		GPIO.output(18, GPIO.LOW)

# Main loop
while True:
	if uart.in_waiting > 0:
		print("Data Recv")
		data = uart.read_until().decode('utf-8')
		print(data == "FND\n")
		if data == "FND\n":
			handle_gpio_states()
			print(GPIO.input(21), GPIO.input(18))			
			uart.write('ACK'.encode())
