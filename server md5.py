import socket
from threading import Thread, Lock
import select

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 3000
DATA_PER_CORE = 1000
CURRENT_NUM = 0
LOST_LIST = []
MSG_LEN = 2
ANSWER = ""
lock = Lock()


def handle_connection(client_socket, client_address, digits, hashed):
    global lock
    global CURRENT_NUM
    global ANSWER
    global LOST_LIST
    current, amount = 0, 0
    try:
        print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))
        client_socket.send(protocol_encode(digits))
        client_socket.send(protocol_encode(hashed))
        while ANSWER == "":
            amount = int(protocol_recv(client_socket))
            lock.acquire()
            if CURRENT_NUM < 10**digits:
                current = CURRENT_NUM
                CURRENT_NUM += amount * DATA_PER_CORE
                lock.release()
            elif not LOST_LIST:
                return
            else:
                current = LOST_LIST[0][0]
                if amount < LOST_LIST[0][1]:
                    LOST_LIST[0][0] += amount*DATA_PER_CORE
                    LOST_LIST[0][1] -= amount
                else:
                    amount = LOST_LIST[0][1]
                    LOST_LIST.pop(0)
            client_socket.send(protocol_encode(current))
            data = protocol_recv(client_socket)
            if data.startswith("a"):
                ANSWER = data[1:]
                return
            while data != amount * DATA_PER_CORE:
                LOST_LIST.append((current, amount))
        client_socket.send(protocol_encode("found"))
    except socket.error as err:
        print('received socket exception - ' + str(err))
        if amount != 0:
            LOST_LIST.append((current, amount))
    except ValueError as err:
        print('socket unexpectedly closed')
        if amount != 0:
            LOST_LIST.append((current, amount))
    finally:
        client_socket.close()


def protocol_recv(client_socket):
    length = client_socket.recv(MSG_LEN).decode()
    if length == '':
        return length
    return client_socket.recv(int(length)).decode()


def protocol_encode(data):
    return (str(len(str(data))).zfill(MSG_LEN) + str(data)).encode()


def main():
    # Open a socket and loop forever while waiting for clients
    digits = int(input("enter number of digits in original code"))
    hashed = input("enter hashed code")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while ANSWER == "":
            rlist, wlist, xlist = select.select([server_socket], [], [], 0.1)
            for i in rlist:
                client_socket, client_address = server_socket.accept()
                thread = Thread(target=handle_connection,
                                args=(client_socket, client_address, digits, hashed))
                thread.start()
        print("Hash decoded! Answer is " + ANSWER)
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
