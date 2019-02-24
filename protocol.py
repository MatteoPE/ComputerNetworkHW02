ENCODING = "utf-8"
MSG_200_SETUP = "200 OK: Ready"
MSG_404_SETUP = "404 ERROR: Invalid Connection Setup Message"
MSG_404_MEASUREMENT = "404 ERROR: Invalid Measurement Message"
MSG_200_TERMINATION = "200 OK: Closing Connection"
MSG_404_TERMINATION = "404 ERROR: Invalid Connection Termination Message"

class Packet():

    def __init__(self, protocol_phase):
        self.protocol_phase = protocol_phase

    def build_packet(self):
        return bytes(self.to_string(), ENCODING)


#<PROTOCOL PHASE ><WS ><M −TYPE ><WS >< MSG SIZE><WS ><PROBES ><WS ><SERVER DELAY>\n
class CSP(Packet):

    def __init__(self, m_type, msg_size, probes, server_delay):
        super().__init__("s")
        self.m_type = m_type
        self.msg_size = msg_size
        self.probes = probes
        self.server_delay = server_delay

    def to_string(self):
        return self.protocol_phase + \
                " " + self.m_type + \
                " " + str(self.msg_size) + \
                " " + str(self.probes) + \
                " " + str(self.server_delay) + "\n"

#<PROTOCOL PHASE ><WS ><PAYLOAD ><WS ><PROBE SEQUENCE NUMBER >\n
class MP(Packet):

    def __init__(self, payload, probe_sequence_number):
        super().__init__("m")
        self.payload = payload
        self.probe_sequence_number = probe_sequence_number

    def to_string(self):
        return self.protocol_phase + \
            " " + self.payload + \
            " " + str(self.probe_sequence_number) + "\n"

class CTP(Packet):

    def __init__(self):
        super().__init__("t")

    def to_string(self):
        return self.protocol_phase + "\n"


class ServerState():

    def __init__(self):
        self.connection = False
        self.m_type = ""
        self.msg_size = -1
        self.probes = -1
        self.server_delay = -1
        self.seq_num = -1

    def setup_connection(self, pkt):

        # m_type
        m_type = pkt.m_type
        if(m_type == "rtt" or m_type == "tput"):
            self.m_type = m_type
        else:
            return MSG_404_SETUP
        # msg_size
        msg_size = int(pkt.msg_size)
        if(msg_size >= 0):
            self.msg_size = msg_size
        else:
            return MSG_404_SETUP
        # probes
        probes = int(pkt.probes)
        if(probes >= 0):
            self.probes = probes
        else:
            return MSG_404_SETUP
        # server_delay
        server_delay = pkt.server_delay
        if(server_delay >= 0):
            self.server_delay = server_delay
        else:
            return MSG_404_SETUP
        if(self.connection == True):
            return MSG_404_SETUP

        self.seq_num = 0
        self.connection = True
        return MSG_200_SETUP

    def measurement(self, pkt):
        probe_sequence_number = int(pkt.probe_sequence_number)
        if(probe_sequence_number != self.seq_num or probe_sequence_number >= self.probes):
            self.connection = False
            return MSG_404_MEASUREMENT
        self.seq_num += 1
        return pkt.to_string()

    def terminate_connection(self, pkt):
        self.__init__()
        return MSG_200_TERMINATION


class ClientState():

    def __init__(self, m_type, msg_size, probes, server_delay):
        self.m_type = m_type
        self.msg_size = msg_size
        self.probes = probes
        self.server_delay = server_delay

    def filename(self):
        return self.m_type + \
               "_" + str(self.msg_size) + \
               "_" + str(self.probes) + \
               "_" + str(self.server_delay) + ".txt"

def read_packet(bytes):
    string = bytes.decode(ENCODING)
    fields = string.split()
    if(fields[0] == "s"):
        pkt = CSP(fields[1], int(fields[2]), int(fields[3]), int(fields[4]))
    elif(fields[0] == "m"):
        pkt = MP(fields[1], int(fields[2]))
    elif(fields[0] == "t"):
        pkt = CTP()
    else:
        return None
    return pkt
