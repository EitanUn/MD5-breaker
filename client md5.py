import socket
import hashlib
from threading import Thread, Lock
from os import cpu_count

IP = '127.0.0.1'
PORT = 3000
DATA_PER_CORE = 1000
MSG_LEN = 2
ANSWER = ""
CHECKED = 0
lock = Lock()


def protocol_recv(client_socket):
    length = client_socket.recv(MSG_LEN).decode()
    if length == '':
        return length
    return client_socket.recv(length).decode()


def protocol_encode(data):
    return (str(len(data)).zfill(MSG_LEN) + str(data)).encode()


def brute_force(start, length, digits, hashed):
    global ANSWER
    global CHECKED
    for i in range(start, start + length):
        if hashlib.md5(str(i).zfill(digits).encode()).hexdigest() == hashed:
            ANSWER = str(i).zfill(digits)
    lock.acquire()
    CHECKED += 1000
    lock.release()


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, PORT))
        digits = protocol_recv(my_socket)
        hashed = protocol_recv(my_socket)
        while not ANSWER:
            threads = []
            my_socket.send(protocol_encode(str(cpu_count())))
            start = protocol_recv(my_socket)
            for i in range(int(cpu_count())):
                thread = Thread(target=brute_force,
                                args=(start, DATA_PER_CORE, digits, hashed))
                threads += thread
            for i in threads:
                i.join()
            if ANSWER:
                data = "a" + ANSWER
            else:
                data = CHECKED
            my_socket.send(protocol_encode(data))



    except socket.error as err:
        print("Cannot connect to server: " + str(err))
