# -*- coding: utf-8 -*-

import sys
import socket

ADDR = sys.argv[1]
PERIOD = sys.argv[2]

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((ADDR, 55151))
# socket.listen(1)
distances_table = {}

if len(sys.argv) > 3:
    file = open(sys.argv[3], "rb")
    
    for line in file:
    	analyze_input(line)
else:
	while True:
		line   = sys.stdin.readline()
		analyze_input(line)


def analyze_input(line):
	tokens 	 = line.split()
	command  = tokens[0]
	ip 	 	 = tokens[1]
	weight 	 = tokens[2]

	if command == 'add':
		add_link(ip, weight)
	elif command == 'del':
		del_link(ip)
	elif command == 'trace':
		trace_link(ip)
	elif command == 'quit':
		quit()
	elif command == 'show':
		print distances_table	
	else:
		print "Comando inválido"


def add_link(ip, weight):
	distances_table[ip] = weight


def del_link(ip):
	del distances_table[ip]	


def quit():
	sys.exit()

def trace_link(ip):
	sys.exit()