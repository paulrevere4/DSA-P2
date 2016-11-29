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
# Creates a connection with every other server
#
def setup_connections(server_locations):
    # Map of server nums to the socket for that server
    sockets = {}

    # Open connections to all servers
    for key, location in server_locations.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "LEADER: CONNECTING TO %s, %i" % (location[0], location[2])
        s.connect((location[0], location[2])) # Connects to Leader listener for all servers
        sockets[key] = s
    return sockets

# ==============================================================================
# Listener for lead server
#
def run_leader(server):

    # Temporary messages for testing
    # server.leader_message_queue.put((0,'create a.txt'))
    # server.leader_message_queue.put((1,'create a.txt'))
    # server.leader_message_queue.put((2,'create a.txt'))
    # server.leader_message_queue.put((0,'append a.txt random text'))
    # server.leader_message_queue.put((1,'append a.txt random text'))
    # server.leader_message_queue.put((2,'append a.txt random text'))
    # server.leader_message_queue.put((0,'delete a.txt'))
    # server.leader_message_queue.put((1,'delete a.txt'))
    # server.leader_message_queue.put((2,'delete a.txt'))

    # messages =[ 'create a.txt',
    #             'append a.txt random text',
    #             'delete a.txt' ]

    while True:

        # check if the thread should run, loop over and over again if not
        if server.run_leader_thread.empty():
            # time.sleep(.5)
            # print "LEADER THREAD NOT RUNNING"
            pass
        else:
            time.sleep(.1)
            print "LEADER THREAD RUNNING"

            sockets = setup_connections(server.server_locations)

            # test data, Map of messages to send to sockets, key = socket, val = message to send
            # TODO remove
            # for s in sockets.keys():
            #     messages_to_send[s] = messages[:]

            # loop continuously to work on the messages
            while True:
                sockets_list = list(sockets.values())
                readable, writable, exceptional = select.select(sockets_list, sockets_list, sockets_list)

                for s in readable:
                    # Received message from other server
                    print "RECEIVED MESSAGE FROM %s:" % str(s.getpeername())
                    data = s.recv(1024)
                    print "MESSAGE: '%s'" %data
                    # TODO handle message

                writable_set = set(writable)
                while not server.leader_message_queue.empty():
                    recipient, message = server.leader_message_queue.get()
                    # messages_to_send[sockets[recipient]] = message
                    recipient_socket = sockets[recipient]
                    if recipient_socket in writable_set:
                        time.sleep(.1)
                        recipient_socket.send(message)
                        print "LEADER: SENT MESSAGE '%s' TO %s" % (message, str(recipient_socket.getpeername()))
                        # del messages_to_send[s][0]
                    else:
                        print "LEADER: ERROR: COULDN'T SEND MESSAGE TO SERVER", recipient_socket.getpeername()

                # messages_to_send = {}
                # for s in writable:
                #     if messages_to_send[s]:
                #         time.sleep(.1)
                #         s.send(messages_to_send[s][0])
                #         print "LEADER: SENT MESSAGE '%s' TO %s" % (messages_to_send[s][0], str(s.getpeername()))
                #         del messages_to_send[s][0]

                for s in exceptional:
                    print 'CONNECTION LOST FROM %s' % s.getpeername()

                # print "LEADER DONE"
                time.sleep(1)

            # TODO figure out how to have leader thread loop continuously
            # break
