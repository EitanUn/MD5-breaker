import socket
from threading import Thread, Lock

DATA_PER_CORE = 1000
CURRENT_NUM = 0
MSG_LEN = 2
ANSWER = ""
lock = Lock()


def handle_connection(client_socket, client_address):
    global lock
    global CURRENT_NUM
    global ANSWER
    while True:
        amount = protocol_recv(client_socket)
        lock.acquire()
        current = CURRENT_NUM
        CURRENT_NUM += amount*DATA_PER_CORE
        lock.release()
        client_socket.send(protocol_encode(current))
        data = protocol_recv(client_socket)
        if data.startswith("a"):
            ANSWER = data[1:]
            return
        while data != amount*DATA_PER_CORE:
            protocol_recv(client_socket)
            client_socket.send(protocol_encode(current))
            data = protocol_recv(client_socket)
            if data.startswith("a"):
                ANSWER = data[1:]
                return


def protocol_recv(client_socket):
    return "1"


def protocol_encode(data):
    return 1
