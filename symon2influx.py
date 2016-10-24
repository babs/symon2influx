#!/usr/bin/python

import codecs
import logging
import os
import socket
import sys

import symonproto


try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request



logging.basicConfig(format="%(asctime)s %(name)-15s %(levelname)-8s %(message)s")

def main():
    log = logging.getLogger("symon2influx")
    log.setLevel(int(os.environ.get("DEBUGLEVEL", "20")))

    listen_ip = os.environ.get("LISTEN_IP", "")
    listen_port = int(os.environ.get("LISTEN_PORT", "2100"))

    influx_instances = os.environ.get("INFLUXDB", "localhost:8086:symon")
    measurement_prefix = os.environ.get("PEASUREMENT_PREFIX", "symon_")
    hostmap = {}
    if os.environ.get("HOSTMAP", None) is not None:
        try:
            # convert "IP1:HOST1 IP2:HOST2" into {"IP1": "HOST1", "IP2": "HOST2"}
            hostmap = dict([c.split(':') for c in os.environ.get("HOSTMAP", "").split(" ")])
        except Exception as exc:
            log.error('Failed to parse env:HOSTMAP', exc_info=exc)
    influxurls = []
    try:
        for influxdef in influx_instances.split(" "):
            influxparams = influxdef.split(":")
            try:
                req = Request("http://%s:%s/query" % (influxparams[0], influxparams[1]),
                                      codecs.encode("q=CREATE+DATABASE+\"%s\"" % influxparams[2], 'utf-8'))
                urlopen(req)
                influxurls.append("http://{0}:{1}/write?db={2}".format(*influxparams))
            except Exception as exc:
                log.error("Unable to connect to following instance, dropping it: %s:%s",
                          influxparams[0], influxparams[1],
                          exc_info=exc)
    except Exception as exc:
        log.error('Failed to parse env:INFLUXDB', exc_info=exc)

    if len(influxurls) == 0:
        log.error("No influxdb instance to send to.")
        sys.exit(1)

    # start listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((listen_ip, listen_port))
    log.info("listen for symon packet on %s:%s", listen_ip, listen_port)
    log.info("will log to the following instance(s): %s.", ", ".join(influxurls))

    # Main loop
    while True:
        data, remote = sock.recvfrom(1500)
        host = ""
        try:
            host = socket.gethostbyaddr(remote[0])[0]
        except socket.error:
            host = remote[0]
        host = hostmap.get(remote[0], host)
        log.debug("Pkt from: %s", host)
        pkt = symonproto.SymonPkt(data)
        if not pkt.check_crc():
            log.warning("invalid CRC from %s; dropped", host)
            continue
        lines = []
        for sample in pkt.samples:
            lines.append(
                "%(name)s,host=%(host)s%(arg)s %(samples)s %(ts)d"
                % {"name":measurement_prefix + sample.name,
                   "host": host.replace(' ', '\\ '),
                   "arg": ",%s=%s" % (sample.argname, sample.argument) if sample.argument else "",
                   "samples": ",".join([k + "=" + str(v) for k, v in sample.values.items()]),
                   "ts"   :pkt.timestamp * 10 ** 9
                  }
            )
        post = codecs.encode("\n".join(lines), 'utf-8')

        for influxurl in influxurls:
            req = Request(influxurl, post)
            urlopen(req)


if __name__ == "__main__":
    main()
