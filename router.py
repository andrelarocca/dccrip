import sys
import socket
from subprocess import call

ADDR = sys.argv[1]
PERIOD = sys.argv[2]
STARTUP = sys.argv[3]

if not ADDR:
    sys.exit("addr is required")

if not PERIOD:
    sys.exit("period is required")

socket = socket.socket(AF_INET, SOCK_DGRAM)
socket.bind((ADDR, 55151))
socket.listen(1)

if STARTUP:
    # read file and execute commands
