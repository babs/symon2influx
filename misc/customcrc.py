#!/usr/bin/python
"""Python Symon CRC implementation"""

def init_table():
    """Initialize CRC table"""
    table = []
    for i in range(256):
        value = i << 24
        for j in range(8, 0, -1):
            if value & 0x80000000 != 0:
                value = (value << 1) ^ 0x04c11db7
            else:
                value = (value << 1)
            print (str(i) + "\t" + str(j) + "\t" + str(value))

        table.append(value & 0xffffffff)
    return table
TABLE = init_table()
def calccrc(value):
    """Calculate CRC of given string"""
    crc = 0xffffffff
    for i in range(0, len(value)):
        crc &= 0xffffffff
        #print ((crc >> 24) ^ ord(s[i:i+1]))
        crc = (crc << 8) ^ TABLE[(crc >> 24) ^ ord(value[i:i+1])]
    return 0xffffffff^(crc&0xffffffff)

def main():
    """main"""
    import codecs
    value = codecs.decode(b"AAAAAAAAAABYCkQuADkCDAAAAAAAAAAAA"+
                          b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", 'base64')
    crc = int("7c3cede0", 16)
    ccrc = calccrc(value)
    print("Expected CRC: %d"%crc)
    print("Calc CRC:     %d"%ccrc)
    print("CRC equal?    %s"%(crc == calccrc(value)))

if __name__ == "__main__":
    main()
