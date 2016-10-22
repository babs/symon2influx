#!/usr/bin/python
"""Capture 1 packet and save it it arg[1]"""
import sys
import socket

def main():
    """Capture 1 packet and save it"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 2100))

    data, addr = sock.recvfrom(1500) # buffer size is 1024 bytes
    print "received message from: %s\tlen: %s"%(addr, len(data))
    # print data
    sys.stdout.flush()
    open(sys.argv[1], "w").write(data)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("%s <save-file>"%(sys.argv[0]))
