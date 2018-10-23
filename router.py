# -*- coding: utf-8 -*-

import sys
import socket
import json
import threading
import multiprocessing

ADDR = sys.argv[1]
PORT = int(5511)
BIND = (ADDR, PORT)
PERIOD = sys.argv[2]

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(BIND)

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
    server_thread.terminate()
    keyboard_thread.terminate()
    sys.exit()


def trace_link(ip):
	quit()


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

def send_update_msg():
    threading.Timer(float(PERIOD), send_update_msg, ()).start()
    for key, value in distances_table.iteritems():
		send_message(key, create_update_msg(key))


def send_message(address, message):
    server.sendto(message, (address, PORT))


def rec_message(data, address):
    print(data, address)


# End of functions definitions and beginning of the program
if len(sys.argv) > 3:
    file = open(sys.argv[3], "rb")
    for line in file:
    	analyze_input(line)


# Starts the update message thread
send_update_msg()


# Threads for interaction
def server_listen():
    while True:
        (data, address) = server.recvfrom(4096)
        rec_message(data, address)


def keyboard_listen():
    print("escitando teclado")
    # while True:
    #     line = sys.stdin.readline()
    #     analyze_input(line)


server_thread = multiprocessing.Process(target=server_listen).start()
keyboard_thread = multiprocessing.Process(target=keyboard_listen).start()
