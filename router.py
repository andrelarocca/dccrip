import sys
import socket

ADDR = sys.argv[1]
PERIOD = sys.argv[2]

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((ADDR, 55151))
# socket.listen(1)

if len(sys.argv) > 3:
    file = open(sys.argv[3], "rb")
    for line in file:
        print line
        # TODO call the add function for each param
