#!/usr/bin/env python

"""
To use with secret keys, do:

    $ echo "<key>" | ./test.py -k

"""

import sys
import optparse
import logging
import socket

import bjsonrpc
import bjsonrpc.connection
import augeas

from exmachina import ExMachinaClient

# =============================================================================
# Command line handling
def main():

    socket_path="/tmp/exmachina.sock"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)

    secret_key = None
    if sys.argv[-1] == "-k":
        print "waiting for key on stdin..."
        secret_key = sys.stdin.readline()
        print "sent!"

    print "========= Testing low level connection"
    c = bjsonrpc.connection.Connection(sock)
    if secret_key:
        c.call.authenticate(secret_key)
    print "time: %s" % c.call.test_whattime()
    print "/*: %s" % c.call.augeas_match("/*")
    print "/augeas/*: %s" % c.call.augeas_match("/augeas/*")
    print "/etc/* files:"
    for name in c.call.augeas_match("/files/etc/*"):
        print "\t%s" % name
    print c.call.initd_status("bluetooth")
    print "hostname: %s" % c.call.augeas_get("/files/etc/hostname/*")
    print "localhost: %s" % c.call.augeas_get("/files/etc/hosts/1/canonical")
    sock.close()

    print "========= Testing user client library"
    client = ExMachinaClient(secret_key=secret_key)
    print client.augeas.match("/files/etc/*")
    print client.initd.restart("bluetooth")
    print client.initd.status("greentooth")
    print "(expect Error on the above line)"
    print client.initd.status("bluetooth")
    client.close()

if __name__ == '__main__':
    main()
