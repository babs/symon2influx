============
symon2influx
============

symon2influx listens to symon packets, decode them and send them to an InfluxDB instance.

symon is an awsome software that I use for years now, with symux and syweb, mainly for my OpenBSD servers (pro and perso).
That said, as I deploy more and more Telegraf/InfluxDB/Grafana stacks in my personal and professional environments, I try to aggregate all the information at the same place.
That's where symon2influx comes into play.

symon_ is a system monitor for FreeBSD, NetBSD, OpenBSD and Linux. It can be used to obtain accurate and up to date information on the performance of a number of systems.

InfluxDB_ is an opensource sacalable datastore for metrics, events, and real-time analytics made by influxdata.

.. _Symon: https://wpd.home.xs4all.nl/symon/
.. _InfluxDB: https://github.com/influxdata/influxdb


Configuration
=============

All configuration goes through env variables:

- ``LISTEN_IP``: Ip to lisent on, default '' (all)

- ``LISTEN_PORT``: Port to listen on, default ``2100``

- ``INFLUXDB``: InfluxDB instance(s) to push to, default: localhost:8086:symon
   
    format: "``instance1:port1:db1 instance2:port2:db2...``"

- ``PEASUREMENT_PREFIX``: string to preprend to measures, default: ``symon_``

- ``HOSTMAP``: mapping if reverse resolution doens't work, default: empty
  
    format: ``IP1:HOST1 IP2:HOST2``

- ``DEBUGLEVEL``: debug level, the lower the more verbose it is default: 20, lowest 1


TODO
====

- startup scripts

  - SysV script
  - systemd script
- tests
