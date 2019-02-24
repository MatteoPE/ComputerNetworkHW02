import sys
import socket
import time

import protocol
import json

#155.98.37.66

HOST = sys.argv[1]
PORT = int(sys.argv[2])
VAR_PATH = ".conf_files/rtt_1.json"
BUFFER_SIZE = 1024


def setup_connection(state):
    pkt = protocol.CSP(state.m_type, state.msg_size, state.probes, state.server_delay)
    to_send = pkt.build_packet()
    s.sendall(to_send)
    data = s.recv(BUFFER_SIZE)
    if(data == bytes(protocol.MSG_200_SETUP, protocol.ENCODING)):
        print(str(data))
        print("Connection created")
        return True
    elif(data == bytes(protocol.MSG_404_SETUP, protocol.ENCODING)):
        print(str(data))
        print("Connection not created")
        return False
    else:
        print(str(data))
        print("Unknown error")
        return False


def performance_measurement(state):
    file = open(state.filename(), "w")
    payload = state.msg_size*'A'
    for seq_num in range(state.probes):
        pkt = protocol.MP(payload, seq_num)
        to_send = pkt.build_packet()
        start = time.time()
        s.sendall(to_send)
        data = s.recv(BUFFER_SIZE)
        end = time.time()
        interval = end - start
        file.write(str(interval) + "\n")
        print(data)
    file.close()


def terminate_connection():
    pkt = protocol.CTP()
    to_send = pkt.build_packet()
    s.sendall(to_send)
    data = s.recv(BUFFER_SIZE)
    if data == bytes(protocol.MSG_200_TERMINATION, protocol.ENCODING):
        print(str(data))
        print("Connection terminated")
        return True
    elif data == bytes(protocol.MSG_404_TERMINATION, protocol.ENCODING):
        print(str(data))
        print("Connection terminated")
        return False


# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# now connect to the web server
s.connect((HOST, PORT))

with open(VAR_PATH) as f:
    var = json.load(f)
    m_type = var["m_type"]
    msg_size = var["msg_size"]
    probes = var["probes"]
    server_delay = var["server_delay"]
    state = protocol.ClientState(m_type, msg_size, probes, server_delay)

setup_connection(state)

performance_measurement(state)

terminate_connection()



