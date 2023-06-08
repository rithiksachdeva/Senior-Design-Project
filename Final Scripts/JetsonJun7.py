import serial
import time
from collections import deque

# Open UART communication with OpenMV
ser_openMV1 = serial.Serial(
    port="/dev/ttyTHS1",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)

time.sleep(1)

tag_directions = {
    (1, 2): [("forward", 22.2)],
    (2, 3): [("forward", 20.4), ("twentyonesixtyeast_turn", 0), ("forward", 10.8)],
    (3, 4): [("forward", 21.6)],
    (4, 5): [("forward", 13), ("hallwayturnsouth", 0), ("forward", 8.2)],
    (5, 6): [("forward", 12), ("twentyonesixtywest_turn", 0), ("forward", 9)],
    (6, 7): [("forward", 15.6)],
    (7, 1): [
        ("advisingoff_turn", 0),
        ("forward", 15.6),
        ("forward", 9),
        ("twentyonesixtyeast_turn", 0),
        ("forward", 12),
        ("forward", 8.2),
        ("hallwayturnnorth", 0),
        ("forward", 13),
        ("forward", 21.6),
        ("forward", 10.8),
        ("twentyonesixtywest_turn", 0),
        ("forward", 20.4),
        ("forward", 22.2),
    ],
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

routes = {
    8: (1, 2),
    9: (1, 3),
    10: (1, 4),
    11: (1, 5),
    12: (1, 6),
    13: (1, 7),
    14: (2, 3),
    15: (2, 4),
    16: (2, 5),
    17: (2, 6),
    18: (2, 7),
    19: (3, 4),
    20: (3, 5),
    21: (3, 6),
    22: (3, 7),
    23: (4, 5),
    24: (4, 6),
    25: (4, 7),
    26: (5, 6),
    27: (5, 7),
    28: (6, 7),
    29: (7, 1)
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
    PWs.append(("D", (1500, 0.1)))
    PWs.append(("END", end_tag))
    return PWs

def send_directions(PWs):
    print("SENDING INSTRUCTIONS")
    while PWs:
        pw = PWs.popleft()
        print(pw)
        ser_openMV1.write(f"{pw}\n".encode("utf-8"))
        if pw[0] != "END":
            time.sleep(pw[1][1])

print("entering listening loop")
print("Entering main loop.")

while True:
    # Wait for a tag
    while True:
        if ser_openMV1.in_waiting > 0:
            print("Found message")
            tag = ser_openMV1.readline().decode('utf-8').strip()
            print(tag)
            # Check if the message is a tag we're interested in
            if int(tag) in routes:
                start_tag, end_tag = routes[int(tag)]
                print(f"Start Tag: {start_tag}, End Tag: {end_tag}")
                # Send the start tag to the openMV
                ser_openMV1.write(f"{start_tag}\n".encode('utf-8'))
                break
            else:
                print("Unexpected message: ", tag)

    while True:
        if ser_openMV1.in_waiting > 0:
            print("Found message")
            msg = ser_openMV1.readline().decode('utf-8').strip()
            print(msg)
            if msg == "ready to proceed":
                print("Ready to Proceed \n")
                break
            else:
                print("Unexpected message: ", msg)
                
    directions = get_directions(start_tag, end_tag)
    print(directions)
    PWs = convert_to_pw(directions, end_tag)
    print(PWs)

    send_directions(PWs)

    # Wait for an ACK
    while True:
        if ser_openMV1.in_waiting > 0:
            print("Found message")
            msg = ser_openMV1.readline().decode("utf-8").strip()
            if msg == "ACK":
                print("Received ACK")
                break
            else:
                print("Unexpected message: ", msg)
