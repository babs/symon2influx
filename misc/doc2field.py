#!/usr/bin/python

import sys

def do(buf):
    b = " ".join(buf)
    b = b.replace("\n", " ").replace(":", " ").replace(",", " ")
    print str(b.split())[1:-1]

def main():
    buf = []
    while True:
        l = sys.stdin.readline()
        if l == "":
            break

        if l.strip() == "":
            do(buf)
            buf = []
        else:
            buf.append(l.strip())

if __name__ == "__main__":
    main()
