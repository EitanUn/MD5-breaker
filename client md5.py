import socket
import hashlib
from threading import Thread


def brute_force(start, end, digits, hashed):
    for i in range(start, end+1):
        if hashlib.md5(str(i).zfill(digits).encode()).hexdigest() == hashed:
            return str(i).zfill(digits)
    return None


def main():

