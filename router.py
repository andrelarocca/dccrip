# -*- coding: utf-8 -*-

import sys
import socket
import json
import time

ADDR = sys.argv[1]
PERIOD = sys.argv[2]

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((ADDR, 55151))
# socket.listen(1)
distances_table = {}


def analyze_input(line):
	tokens 	 = line.split()
	command  = tokens[0]

	if command == 'add':
		ip     = tokens[1]
		weight = tokens[2]
		add_link(ip, weight)
	elif command == 'del':
		ip = tokens[1]
		del_link(ip)
	elif command == 'trace':
		ip = tokens[1]
		trace_link(ip)
	elif command == 'quit':
		quit()
	else:
		print "Invalid command"


def add_link(ip, weight):
	distances_table[ip] = weight


def del_link(ip):
	del distances_table[ip]	


def quit():
	sys.exit()


def trace_link(ip):
	sys.exit()


def create_data_msg(destination, payload):
	return json.dumps(
		{'type'      : 'data', 
		'source'     : ADDR, 
		'destination': destination, 
		'payload'    : payload})


def create_update_msg(destination):
	return json.dumps(
		{'type'      : 'update', 
		'source'     : ADDR, 
		'destination': destination, 
		'distances'  : distances_table})


def create_trace_msg(destination):
	return json.dumps(
		{'type'      : 'trace', 
		'source'     : ADDR, 
		'destination': destination, 
		'hops'       : [ADDR]})

# End of functions definitions and beginning of the program	
if len(sys.argv) > 3:
    file = open(sys.argv[3], "rb")
    
    for line in file:
    	analyze_input(line)

while True:
	line = sys.stdin.readline()
	analyze_input(line)
