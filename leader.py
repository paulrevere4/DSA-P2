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

    # Temporary fake for testing
    messages =  [ 'CREATE A\.TXT ',
                'APPEND A\.TXT \"Random Text\" ',
                'DELETE A\.TXT',
                ]

    # Map of messages to send to sockets, key = socket, val = message to send
    messages_to_send = {} # 

    socks = []

    # Open connections to all servers
    for key, location in server_locations.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "LEADER: Connecting to %s, %i" % (location[0], location[2])
        s.connect((location[0], location[2])) # Connects to Leader listener for all servers
        socks.append(s)

        # Populate messages_to_send with test data
        messages_to_send[s] = list(messages)

    while socks:
        readable, writable, exceptional = select.select(socks, socks, socks)

        for s in readable:
            # Received message from other server
            print "Received message from %s:" % str(s.getpeername())
            data = s.recv(1024)
            print "    " + data

        for s in writable:
            if messages_to_send[s]:
                time.sleep(.1)
                s.send(messages_to_send[s][0])
                print "Leader: Sent message %s to %s" % (messages_to_send[s][0], str(s.getpeername()))
                del messages_to_send[s][0]

        for s in exceptional:
            print 'connection lost from %s' % s.getpeername()
