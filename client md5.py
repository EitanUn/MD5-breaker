"""
Author: Eitan Unger
Date: 2/11/22
Client for dynamic distributed md5 hash breaker
"""
import socket
import hashlib
from threading import Thread, Lock
from os import cpu_count

IP = '172.16.6.128'
PORT = 3000
DATA_PER_CORE = 100000
MSG_LEN = 2
ANSWER = ""
CHECKED = 0
lock = Lock()


def protocol_recv(client_socket):
    """
    protocol receive function, receives length and then receives the rest of the message accordingly
    :param client_socket: socket to receive from
    :return: received message
    """
    length = client_socket.recv(MSG_LEN).decode()
    if length == '':
        return length
    return client_socket.recv(int(length)).decode()


def protocol_encode(data):
    """
    protocol encode function, encodes the message with a length header added
    :param data: message to encode
    :return: encoded message
    """
    return (str(len(str(data))).zfill(MSG_LEN) + str(data)).encode()


def brute_force(start, length, digits, hashed):
    """
    md5 brute force function, tries length numbers from start and returns whether one of them is the seed for
    the hash received.
    :param start: number to start checking from
    :param length: amount of numbers to check
    :param digits: number of digits in original number (zfill to avoid duplicates)
    :param hashed: hash to find
    """
    global ANSWER
    global CHECKED
    for i in range(start, start + length):
        if ANSWER:
            return
        if hashlib.md5(str(i).zfill(digits).encode()).hexdigest().upper() == hashed.upper():
            ANSWER = str(i).zfill(digits)
    lock.acquire()
    CHECKED += DATA_PER_CORE
    lock.release()


def main():
    """
    main function for server interactions and starting and managing threads
    """
    global ANSWER
    global CHECKED
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, PORT))
        digits = protocol_recv(my_socket)
        if digits == "found":
            ANSWER = "found"
        hashed = protocol_recv(my_socket)
        if hashed == "found":
            ANSWER = "found"
        while not ANSWER:
            threads = []
            CHECKED = 0
            my_socket.send(protocol_encode(str(cpu_count())))
            start = protocol_recv(my_socket)
            if start == "found":
                break
            start = int(start)
            for i in range(int(cpu_count())):
                thread = Thread(target=brute_force,
                                args=(int(start), DATA_PER_CORE, int(digits), hashed))
                threads.append(thread)
                thread.start()
                start += DATA_PER_CORE
            for i in threads:
                i.join()
            if ANSWER:
                data = "a" + ANSWER
            else:
                data = CHECKED
            my_socket.send(protocol_encode(data))
    except socket.error as err:
        print("Cannot connect to server: " + str(err))
    finally:
        my_socket.close()


if __name__ == '__main__':
    assert protocol_encode("1234") == b'041234'
    assert protocol_encode(1234) == b'041234'
    main()
