"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
leader.py
"""
# ==============================================================================

import time
import Queue
import socket
import select
import sys
import errno

from serializer import Serializer

# ==============================================================================
# Listener for lead server
#
def run_leader(task_queue, server_locations):
    print server_locations

    # Temporary fake for testing
    messages =  [ 'CREATE A\.TXT ',
                'APPEND A\.TXT \"Random Text\" ',
                'DELETE A\.TXT',
                ]

    socks = []

    # Open connections to all servers
    for key, location in server_locations.items():
        print location
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "LEADER: Connectiong to %s, %i" % (location[0], location[2])
        s.connect((location[0], location[2])) # Connects to Leader listener for all servers
        socks.append(s)

    for message in messages:

        # Send messages on both sockets
        for s in socks:
            print >>sys.stderr, 'LEADER: %s: sending "%s"' % (s.getsockname(), message)
            s.send(message)

        # Read responses on both sockets
        for s in socks:
            data = s.recv(1024)
            print >>sys.stderr, 'LEADER: %s: received "%s"' % (s.getsockname(), data)
            if not data:
                print >>sys.stderr, 'LEADER: closing socket', s.getsockname()
                s.close()