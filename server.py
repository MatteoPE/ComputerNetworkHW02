import sys
import socket
import protocol

#HOST = 'localhost'
PORT = int(sys.argv[1])
BUFFER_SIZE = 32768

print("Creating a socket...")
# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
#s.bind((HOST, PORT))
s.bind(('', PORT))
# become a server socket
s.listen(5)
print("...socket created. Listening on port " + str(PORT))

# accept more then one connection
while True:
    conn, addr = s.accept()
    print('Connected by', addr)
    state = protocol.ServerState()
    while True:

        data = conn.recv(BUFFER_SIZE)


        if data:
            pkt = protocol.read_packet(data)

            if(isinstance(pkt, protocol.CSP)):
                to_send = state.setup_connection(pkt)
            elif(isinstance(pkt, protocol.MP)):
                to_send = state.measurement(pkt)
            elif(isinstance(pkt, protocol.CTP)):
                to_send = state.terminate_connection(pkt)
            else:
                to_send("Error") #mind that you have to destroy the connection

            conn.sendall(bytes(to_send, protocol.ENCODING))
            if(not state.connection):
                break

    conn.close()

