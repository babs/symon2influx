#!/usr/bin/python
"""
Module to decode Symon binary packet
"""
import struct


class SymonElement(object):
    """Symon sample representation"""
    def __init__(self, binid, name, argument, binlen):
        self.binid = binid
        self.name = name
        self.argument = argument
        self.binlen = binlen
        self.values = {}

    def __str__(self):
        return "SymonElement(%s, %s, %s)" % (self.name, self.argument, self.values)

class SymonType(object):
    """Symon type, decodes payload based on definitions"""
    # '#' == u_int16/100 [struct: H]
    # 'd' == u_int64/1000000 [struct: Q]

    def __init__(self, binid, stype, fmt, fieldnames):
        self.binid = binid
        self.stype = stype
        self.name = stype.lower().split("_")[1]
        self.fmt = fmt
        self.struct_fmt = ">" + fmt.replace('#', 'H').replace('d', 'Q')
        self.fieldnames = fieldnames
        self.struct_len = struct.calcsize(self.struct_fmt)

    def __str__(self):
        return "%s(%r)" % (self.__class__, self.stype)

    def decode(self, payload, offset=0):
        """Decode a sample from a payload, starting at offset"""
        argument = payload[offset + 1:payload.find(b"\0", offset + 1)]
        rec_len = 2 + len(argument)
        offset += rec_len

        retval = SymonElement(self.binid, self.name, argument.decode('utf-8'),
                              rec_len + self.struct_len)

        result = list(struct.unpack_from(self.struct_fmt, payload, offset))

        for i in range(0, len(self.fmt)):
            if self.fmt[i] == "#":
                result[i] = float(result[i]) / 100
            if self.fmt[i] == "d":
                result[i] = float(result[i]) / 1000000

        retval.values = (dict(zip(self.fieldnames, result)))
        return retval

    @staticmethod
    def decode_type(payload, offset=0):
        """Find the type and returns it's decoded version"""
        # python2 & 3 compat kludge b[x:x+1] instead of b[x]
        etype = SymonType.types[payload[offset:offset + 1]]
        return etype.decode(payload, offset)

SymonType.types = {
    b"\x00": SymonType(0, "MT_IO1", "QQQ",
                       ['total_transfers', 'total_seeks', 'total_bytes']),
    b"\x01": SymonType(1, "MT_CPU", "#####",
                       ['user', 'nice', 'system', 'interrupt', 'idle']),
    b"\x02": SymonType(2, "MT_MEM1", "LLLLL",
                       ['real_active', 'real_total', 'free', 'swap_used', 'swap_total']),
    b"\x03": SymonType(3, "MT_IF1", "LLLLLLLLLL",
                       ['packets_in', 'packets_out', 'bytes_in', 'bytes_out',
                        'multicasts_in', 'multicasts_out', 'errors_in', 'errors_out',
                        'collisions', 'drops']),
    b"\x04": SymonType(4, "MT_PF", "QQQQQQQQQQQQQQQQQQQQQQ",
                       ['bytes_v4_in', 'bytes_v4_out', 'bytes_v6_in', 'bytes_v6_out',
                        'packets_v4_in_pass', 'pack-', 'ets_v4_in_drop', 'packets_v4_out_pass',
                        'packets_v4_out_drop', 'packets_v6_in_pass', 'packets_v6_in_drop',
                        'packets_v6_out_pass', 'packets_v6_out_drop', 'states_entries',
                        'states_searches', 'states_inserts', 'states_removals',
                        'counters_match', 'counters_bad-', 'offset', 'counters_fragment',
                        'counters_short', 'counters_normalize', 'counters_memory']),
    b"\x05": SymonType(5, "MT_DEBUG", "LLLLLLLLLLLLLLLLLLLL",
                       ['debug0', 'debug1', 'debug2', 'debug3', 'debug4', 'debug5',
                        'debug6', 'debug7', 'debug8', 'debug9', 'debug10', 'debug11',
                        'debug12', 'debug13', 'debug14', 'debug15', 'debug16',
                        'debug17', 'debug18', 'debug19']),
    b"\x06": SymonType(6, "MT_PROC", "LQQQL#LL",
                       ['number', 'uticks', 'sticks', 'iticks', 'cpusec', 'cpupct',
                        'procsz', 'rsssz']),
    b"\x07": SymonType(7, "MT_MBUF", "LLLLLLLLLLLLLLL",
                       ['totmbufs', 'mt_data', 'mt_oobdata', 'mt_control', 'mt_header',
                        'mt_ftable', 'mt_soname', 'mt_soopts', 'pgused', 'pgtotal',
                        'totmem', 'totpct', 'm_drops', 'm_wait', 'm_drain']),
    b"\x08": SymonType(8, "MT_SENSOR", "d", ['value']),
    b"\x09": SymonType(9, "MT_IO2", "QQQQQ",
                       ['rxfer', 'wxfer', 'seeks', 'rbytes', 'wbytes']),
    b"\x0a": SymonType(10, "MT_PFQ", "QQQQ",
                       ['sent_bytes', 'sent_packets', 'drop_bytes', 'drop_packets']),
    b"\x0b": SymonType(11, "MT_DF", "QQQQQQQ",
                       ['blocks', 'bfree', 'bavail', 'files',
                        'ffree', 'syncwrites', 'asyncwrites']),
    b"\x0c": SymonType(12, "MT_MEM2", "QQQQQ",
                       ['real_active', 'real_total', 'free', 'swap_used', 'swap_total']),
    b"\x0d": SymonType(13, "MT_IF2", "QQQQQQQQQQ",
                       ['ipackets', 'opackets', 'ibytes', 'obytes', 'imcasts', 'omcasts',
                        'ierrors', 'oerrors', 'collisions', 'drops']),
    b"\x0e": SymonType(14, "MT_CPUIOW", "######",
                       ['user', 'nice', 'interrupt', 'idle', 'iowait']),
    b"\x0f": SymonType(15, "MT_SMART", "BBBBBBBBBBBB",
                       ['read_error_rate', 'reallocated_sectors', 'spin_retries', 'air_flow_temp',
                        'temperature', 'reallocations', 'cur-', 'rent_pending', 'uncorrectables',
                        'soft_read_error_rate', 'g_sense_error_rate', 'temperature2',
                        'free_fall_protection']),
    b"\x10": SymonType(16, "MT_LOAD", "###",
                       ['load1', 'load5', 'load15']),
    b"\x11": SymonType(17, "MT_FLUKSO", "d",
                       ['value']),
    b"\x12": SymonType(18, "MT_TEST", "QQQQddddLLLLHHHH####BBBB",
                       ['', '', '', '', '', '', '', '', '', '', '', '',
                        '', '', '', '', '', '', '', '', '', '', '', '']),
    b"\x13": SymonType(19, "MT_EOT", "", []),
}

class SymonPkt(object):
    """Symon packet handler"""
    __table = None

    def __init__(self, pkt):
        self.pkt = pkt
        (self.crc, self.timestamp, self.length,
         self.version) = struct.unpack_from(">IQHc", pkt)
        self.samples = self.__decode_payload()

    @staticmethod
    def __init_crc_table():
        # POLY = 0x04c11db7
        table = []
        for i in range(256):
            value = i << 24
            for _ in range(8, 0, -1):
                if value & 0x80000000 != 0:
                    value = (value << 1) ^ 0x04c11db7
                else:
                    value = (value << 1)
            table.append(value & 0xffffffff)
        SymonPkt.__table = table

    @staticmethod
    def __calc_custom_crc(bytestring):
        if SymonPkt.__table is None:
            SymonPkt.__init_crc_table()
        crc = 0xffffffff
        for i in range(0, len(bytestring)):
            crc &= 0xffffffff
            # python 3 compat : b[x] in py3 returns int but b[x:x+1] has the ame behavior as py2
            crc = (crc << 8) ^ SymonPkt.__table[(crc >> 24) ^ ord(bytestring[i:i + 1])]
        return 0xffffffff ^ (crc & 0xffffffff)

    def check_crc(self):
        """Check the CRC of the payload"""
        return SymonPkt.__calc_custom_crc(b"\0" * 8 + self.pkt[8:]) == self.crc

    def __decode_payload(self):
        coffset = 15
        elements = []
        while coffset < len(self.pkt):
            element = SymonType.decode_type(self.pkt, coffset)
            elements.append(element)
            coffset += element.binlen
        return elements

def main():
    """Function run if started and not imported"""
    pkt = SymonPkt(open('pkt.raw', 'r').read())
    print(pkt.check_crc())


if __name__ == "__main__":
    main()
