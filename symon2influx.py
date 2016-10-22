#!/usr/bin/python

import sys, os, socket, symonproto

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 2100))

    while True:
    #if True:
        data, addr = sock.recvfrom(1500) # buffer size is 1024 bytes
        #print "received message: %s"%data.encode('hex')
        pkt = symonproto.SymonPkt(data)
        pkt.check_crc()
        for s in pkt.samples:
            print(s)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
