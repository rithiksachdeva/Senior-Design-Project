import serial
import time
import threading

stop_signal = threading.Event()

# Open UART communication with OpenMV1 and OpenMV2
ser_openMV1 = serial.Serial(
    port="/dev/ttyTHS1",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
ser_openMV2 = serial.Serial(
    port="/dev/ttyTHS2",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)

# Dictionaries for storing tag directions and graph nodes
tag_directions = {
    (1, 2): [("forward", 22.2)],
    (2, 3): [("forward", 20.4), ("twentyonesixtyeast_turn", 0), ("forward", 10.8)],
    (3, 4): [("forward", 21.6)],
    (4, 5): [("forward", 13), ("hallwayturnsouth", 0), ("forward", 8.2)],
    (5, 6): [("forward", 12), ("twentyonesixtywest_turn", 0), ("forward", 9)],
    (6, 7): [("forward", 15.6)],
    (7, 1): [("advisingoff_turn", 0), ("forward", 15.6), ("forward", 9), ("twentyonesixtyeast_turn", 0), ("forward", 12), ("forward", 8.2), ("hallwayturnnorth", 0), ("forward", 13),
             ("forward", 21.6), ("forward", 10.8), ("twentyonesixtywest_turn", 0), ("forward", 20.4), ("forward", 22.2)]
}

graph = {
    (1, 2): [1, 2],
    (1, 3): [1, 2, 3],
    (1, 4): [1, 2, 3, 4],
    (1, 5): [1, 2, 3, 4, 5],
    (1, 6): [1, 2, 3, 4, 5, 6],
    (1, 7): [1, 2, 3, 4, 5, 6, 7],
    (2, 3): [2, 3],
    (2, 4): [2, 3, 4],
    (2, 5): [2, 3, 4, 5],
    (2, 6): [2, 3, 4, 5, 6],
    (2, 7): [2, 3, 4, 5, 6, 7],
    (3, 4): [3, 4],
    (3, 5): [3, 4, 5],
    (3, 6): [3, 4, 5, 6],
    (3, 7): [3, 4, 5, 6, 7],
    (4, 5): [4, 5],
    (4, 6): [4, 5, 6],
    (4, 7): [4, 5, 6, 7],
    (5, 6): [5, 6],
    (5, 7): [5, 6, 7],
    (6, 7): [6, 7],
    (7, 1): [7, 1],
}

def get_directions(start_tag, end_tag):
    # Try to retrieve the path between the start and end tags
    path = graph.get((start_tag, end_tag))

    if path is None:
        # If there is no path between these tags, return a suitable message
        return f"No path exists between tags {start_tag} and {end_tag}"

    # Initialize a list to hold the directions for this path
    directions = []
    
    # Iterate over pairs of nodes in the path
    for i in range(len(path) - 1):
        start_node = path[i]
        end_node = path[i + 1]
        
        # Look up the directions for this pair of nodes
        node_directions = tag_directions.get((start_node, end_node))
        
        if node_directions is not None:
            # Append these directions to the list for this path
            directions.extend(node_directions)

    return directions

def convert_to_pw(directions, end_tag):
    PWs = deque()
    for direction in directions:
        if direction[0] == "forward":
            PWs.append(("D", (1600, direction[1])))
        elif direction[0] == "twentyonesixtyeast_turn":
            PWs.append(("S", (1200, 0.6)))
        elif direction[0] == "twentyonesixtywest_turn":
            PWs.append(("S", (1800, 0.6)))
        elif direction[0] == "hallwayturnsouth":
            PWs.append(("S", (1200, 1.7)))
        elif direction[0] == "hallwayturnnorth":
            PWs.append(("S", (1800, 1.7)))
        elif direction[0] == "advisingoff_turn":
            PWs.append(("S", (1200, 1.5)))
            PWs.append(("S", (2000, 2)))
        else:
            print("Unknown")
    PWs.append(("D", (1500, 0)))
    PWs.append(("END", end_tag))
    return PWs

def process_error_message(error_msg):
    # Assuming error messages are integers
    error_y = int(error_msg)
    
    # Define PID parameters
    Kp = 0.1
    Ki = 0.01
    Kd = 0.05
    
    # Initialize error variables
    previous_error_y = 0
    integral_y = 0
    
    # Calculate adjustments based on PID control
    adjustment_y = Kp * error_y + Ki * integral_y + Kd * (error_y - previous_error_y)
    
    # Update error variables for next iteration
    previous_error_y = error_y
    integral_y += error_y
    
    # Calculate adjusted servo pulse width
    servo_pw = 1500 + adjustment_y
    
    # Set the servo pulse width within the valid range
    servo_pw = max(min(servo_pw, 2000), 1000)
    
    return ("S", (servo_pw, 0.5))


# PID loop for adjusting the servo pulse width based on OpenMV2
def pid_loop(PWs):
    while not stop_signal.is_set():
        if ser_openMV2.in_waiting:
            error_msg = ser_openMV2.readline().decode('utf-8').strip()
            print("Received error message: ", error_msg)
            adjustment = process_error_message(error_msg)
            if adjustment:
                PWs.appendleft(adjustment)
                
def send_directions(PWs):
    while not stop_signal.is_set() and PWs:
        pw = PWs.popleft()
        ser_openMV1.write(f"{pw}\n".encode('utf-8'))
        time.sleep(0.1)  # pause to let PID loop make adjustments
                
while True:
    if ser_openMV1.in_waiting:
        msg = ser_openMV1.readline().decode('utf-8').strip()
        if msg == "ready to proceed":
            break
        else:
            print("Unexpected message: ", msg)

while True:
    start_tag = int(input("Enter start tag: "))
    end_tag = int(input("Enter end tag: "))
    directions = get_directions(start_tag, end_tag)
    PWs = convert_to_pw(directions, end_tag)

    send_thread = threading.Thread(target=send_directions, args=(PWs,))
    pid_thread = threading.Thread(target=pid_loop, args=(PWs,))

    send_thread.start()
    pid_thread.start()

    while True:
        if ser_openMV1.in_waiting:
            msg = ser_openMV1.readline().decode('utf-8').strip()
            if msg == "ACK":
                stop_signal.set()
                send_thread.join()
                pid_thread.join()
                break
            else:
                print("Unexpected message: ", msg)

