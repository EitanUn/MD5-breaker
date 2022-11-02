"""
Author: Eitan Unger
Date: 2/11/22
Test for hashlib and md5 hash breaking
"""
import hashlib


def main():
    digits = int(input("enter number of digits in original code"))
    hashed = input("enter hashed code")
    for i in range(0, 10**digits):
        if hashlib.md5(str(i).zfill(digits).encode()).hexdigest() == hashed:
            print(str(i).zfill(digits))
            return


if __name__ == "__main__":
    main()
