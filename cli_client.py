"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
cli_client.py

Implements the command line interface for the user, runs on the user's machine
and can connect to any of the servers.
"""
# ==============================================================================

import sys
import time
import socket

from serializer import *

# ==============================================================================
# Takes input and sends it to the specified server
# *** TODO ***
#   - Implement actual command parsing/error checks
#
def run(host, port):
    while True:
        time.sleep(.1)
        cmd = raw_input("Input: ")
        print "CLIENT: Read '%s' from command line" %cmd
        packed = serializer.serialize([cmd])
        s = socket.socket()
        s.connect((host, port))
        s.send(packed)
        print "CLIENT: Sent '%s' as to server at (host=%s, port=%d) as '%s'" %(cmd, host, port, packed)

if __name__ == "__main__":

    # usage prompt if wrong number of args given
    if len(sys.argv) != 3:
        print   "[!] USAGE:\n" \
                "    $ python cli_client.py <host> <port>"
        exit(1)

    # setup our script arguments
    host = str(sys.argv[1])
    port = int(sys.argv[2])

    # prompt
    print "Connecting to: host=%s and port=%d" %(host, port)

    # run the cli
    run(host, port)
