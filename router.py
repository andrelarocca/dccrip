# -*- coding: utf-8 -*-

import sys
import socket
import json
import threading
import multiprocessing

ADDR = sys.argv[1]
PORT = int(5511)
BIND = (ADDR, PORT)
PERIOD = int(sys.argv[2])
DEFAULT_TIME = 1

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(BIND)

class Route:
    cost = 0
    nextHop = ""
    time_to_live = 0
    
    def set(self, cost, nextHop):
        self.cost = cost
        self.nextHop = nextHop
        self.time_to_live = PERIOD

distances_table = {}
routing_table = {}        

def get_input():
    cmd = raw_input()
    if cmd:
        return cmd


def analyze_input(line):
    tokens = line.split()
    command = tokens[0]

    if command == 'add':
        ip = tokens[1]
        weight = int(tokens[2])
        add_link(ip, weight)
    elif command == 'del':
        ip = tokens[1]
        del_link(ip)
    elif command == 'trace':
        ip = tokens[1]
        trace_link(ip)
    elif command == 'quit':
        end()
    else:
        print "Invalid command"


def add_link(ip, weight):
    distances_table[ip] = weight
    current_link = Route()
    current_link.set(weight, ip)
    routing_table[ip] = current_link


def del_link(ip):
    del distances_table[ip]
    del routing_table[ip]


def end():
    server_thread.terminate()
    server_thread.join()
    sys.exit()


def trace_link(ip):
    end()


def create_data_msg(destination, payload):
    return json.dumps({
        'type': 'data',
        'source': ADDR,
        'destination': destination,
        'payload': payload
    })


def create_update_msg(destination):
    return json.dumps({
        'type': 'update',
        'source': ADDR,
        'destination': destination,
        'distances': distances_table
    })


def create_trace_msg(destination):
    return json.dumps({
        'type': 'trace',
        'source': ADDR,
        'destination': destination,
        'hops': [ADDR]
    })


def send_update_msg():
    # TODO implement split horizon
    for key, value in distances_table.iteritems():
        send_message(key, create_update_msg(key))
    threading.Timer(float(PERIOD), send_update_msg, ()).start()


def send_message(address, message):
    # TODO implement load balance
    server.sendto(message, (address, PORT))


def rec_message(data, address):
    message = json.loads(data)
    type = message['type']
    if type == 'update':
        print("todo")
        # TODO call merge route
    elif type == 'data':
        print(message['payload'])
    elif type == 'trace':
        print("todo")
        # TODO handle trace



def handle_routing_table():
    for key, route in routing_table.iteritems():
        route.time_to_live -= 1
        if route.time_to_live == 0:
            del_link(key)
    threading.Timer(float(DEFAULT_TIME), handle_routing_table, ()).start()


def merge_route(address, newRoute):
    if (newRoute.cost + routing_table[newRoute.nextHop]) < routing_table[address].cost:
        newRoute.cost += routing_table[newRoute.nextHop]
        newRoute.time_to_live = PERIOD
        routing_table[address] = newRoute
    else:
        routing_table[address].time_to_live = PERIOD


# End of functions definitions and beginning of the program
if len(sys.argv) > 3:
    startup_file = open(sys.argv[3], "rb")
    for file_line in startup_file:
        analyze_input(file_line)


# Starts the update message thread
send_update_msg()

# Starts the handle routing table thread
#handle_routing_table()

# Threads for interaction
def server_listen():
    while True:
        (data, address) = server.recvfrom(4096)
        rec_message(data, address)


server_thread = multiprocessing.Process(target=server_listen)
server_thread.start()

# Listens to keyboard
user_input = get_input()
while user_input != 'quit':
    analyze_input(user_input)
    user_input = get_input()

# Finish execution
end()
