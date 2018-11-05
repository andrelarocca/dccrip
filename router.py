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
    sent = False
    
    def set(self, cost, nextHop):
        self.cost = cost
        self.nextHop = nextHop
        self.time_to_live = PERIOD
        self.sent = False

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
    # Save the neighborhood distance
    distances_table[ip] = weight
    
    routes = {}
    routes[weight] = []
    current_link = Route()
    current_link.set(weight, ip)
    routes[weight].append(current_link)
    routing_table[ip] = routes


def del_link(ip):
    del distances_table[ip]
    del routing_table[ip]


def end():
    server_thread.terminate()
    server_thread.join()
    sys.exit()


def trace_link(ip):
    message = create_trace_msg(ip)
    send_message(ip, message)


def create_data_msg(destination, payload):
    return json.dumps({
        'type': 'data',
        'source': ADDR,
        'destination': destination,
        'payload': payload
    })


def create_update_msg(destination):
    current_distances = distances_table.copy()
    # Remove the destination from the distances message
    del current_distances[destination]

    return json.dumps({
        'type': 'update',
        'source': ADDR,
        'destination': destination,
        'distances': current_distances
    })


def create_trace_msg(destination):
    return json.dumps({
        'type': 'trace',
        'source': ADDR,
        'destination': destination,
        'hops': [ADDR]
    })


def send_update_msg():
    # TODO finish split horizon
    for key, value in distances_table.iteritems():
        send_message(key, create_update_msg(key))
    threading.Timer(float(PERIOD), send_update_msg, ()).start()


def send_message(address, message):
    costs = routing_table[address]
    destination = ''
    selected_cost = 0
    selected_route = Route()

    for cost, routes in costs.iteritems():
        selected_cost = cost
        for route in routes:
            if route.sent == False:
                destination = route.nextHop
                if len(routes) > 1:
                    route.sent = True
                selected_route = route
                break


    # Set all the not selected routes as not sent
    for route in costs[selected_cost]:
        if route != selected_route:
            route.sent = False            

    server.sendto(message, (destination, PORT))


def rec_message(data, address):
    message = json.loads(data)
    message_type = message['type']
    print message_type
    if message_type == 'update':
        print("todo")           
        handle_update(message, address)
    elif message_type == 'data':
        print(message['payload'])
    elif message_type == 'trace':
        handle_trace(message, address)


def handle_trace(message, ip):
    message['hops'].append(ADDR)
    if message['destination'] == ADDR:
        send_message(message['source'], json.dumps(message))
    else:
        send_message(ip, json.dumps(message))


def handle_routing_table():
    print(routing_table)
    for ip, costs in routing_table.copy().iteritems():
        for cost, routes in costs.copy().iteritems():
            for route in routes:
                route.time_to_live -= DEFAULT_TIME
                if route.time_to_live == 0:
                    remove_route(ip, cost, routes, route)
    threading.Timer(float(DEFAULT_TIME), handle_routing_table, ()).start()


def remove_route(ip, cost, routes, route):
    routes.remove(route)

    # Verify if the routes array is empty
    if not routes:
        del routing_table[ip][cost]
        # Verify if there is any other route to that ip address
        if len(routing_table[ip]) == 0:
            del_link(ip)
        else:
            # TODO Get the next feasible cost and update distances_table with the new cost
            print("todo")
    else:
        return


def merge_route(address, newRoute):
    routes = routing_table[address][newRoute.cost]
    route_exist = False
    for route in routes:
        if route.cost == newRoute.cost and route.nextHop == newRoute.nextHop:
            route_exist = True
            # Update time of the route
            route.time_to_live = PERIOD
            break
    if(route_exist == False):
        routes.append(newRoute)


def handle_update(message, address):
    links = message['distances']
    for ip, distance in links.iteritems():
        current_link = Route()
        weight = distance + distances_table[address]
        current_link.set(weight, address)
        merge_route(ip, current_link)


# Threads for interaction
def server_listen():
    while True:
        (data, address) = server.recvfrom(4096)
        rec_message(data, address)


# End of functions definitions and beginning of the program
if len(sys.argv) > 3:
    startup_file = open(sys.argv[3], "rb")
    for file_line in startup_file:
        analyze_input(file_line)


# Starts the update message thread
send_update_msg()


# Starts the handle routing table thread
handle_routing_table()

server_thread = multiprocessing.Process(target=server_listen)
server_thread.start()

# Listens to keyboard
user_input = get_input()
while user_input != 'quit':
    analyze_input(user_input)
    user_input = get_input()

# Finish execution
end()
