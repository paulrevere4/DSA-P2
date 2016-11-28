"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
leader_listener.py
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
# Communicates with lead server, sending messages and receiving transactions
#
def run_leader_listener(task_queue, host, port, run_leader_listener_thread, prints = True):

    while True:
        if run_leader_listener_thread.empty():
            # time.sleep(.5)
            # print "LEADER LISTENER NOT RUNNING"
            pass
        else:
            time.sleep(.1)
            print "LEADER LISTENER THREAD RUNNING"

            # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # server.setblocking(0)

            # # Bind the socket to the port
            # server.bind((host,port))

            # server.listen(5)

            # inputs = [ server ]
            # outputs = []

            # message_queues = {}

            # while inputs:
            #     # Wait for at least one of the sockets to be ready for processing
            #     if prints:
            #         print >>sys.stderr, '\nLEADER LISTENER: waiting for the next event\n'
            #     readable, writable, exceptional = select.select(inputs, outputs, inputs + outputs)

            #     # Handle inputs
            #     for s in readable:

            #         if s is server:
            #             # A "readable" server socket is ready to accept a connection
            #             connection, client_address = s.accept()
            #             if prints:
            #                 print >>sys.stderr, 'LEADER LISTENER:new connection from', client_address
            #             connection.setblocking(0)
            #             inputs.append(connection)

            #             # Give the connection a queue for data we want to send
            #             message_queues[connection] = Queue.Queue()

            #         else:
            #             data = s.recv(1024)
            #             if data:
            #                 # A readable client socket has data
            #                 if prints:
            #                     print >>sys.stderr, 'LEADER_LISTENER: Received "%s" from %s' % (data, s.getpeername())
            #                 message_queues[s].put("Successfuly completed task: " + data)
            #                 # Add output channel for response
            #                 if s not in outputs:
            #                     outputs.append(s)
            #             else:
            #                 # Interpret empty result as closed connection
            #                 if prints:
            #                     print >>sys.stderr, 'closing', client_address, 'after reading no data'
            #                 # Stop listening for input on the connection
            #                 if s in outputs:
            #                     outputs.remove(s)
            #                 inputs.remove(s)
            #                 s.close()

            #                 # Remove message queue
            #                 del message_queues[s]

            #     # Handle outputs
            #     for s in writable:
            #         try:
            #             next_msg = message_queues[s].get_nowait()
            #             if prints:
            #                 print "LEADER_LISTENER: About to send message to leader: \n     %s" % next_msg
            #         except Queue.Empty:
            #             # No messages waiting so stop checking for writability.
            #             # print >>sys.stderr, 'LEADER_LISTENER: output queue for %s is empty\n' % str(s.getsockname())
            #             outputs.remove(s)
            #         except KeyError as e:
            #             if prints:
            #                 print "LEADER_LISTENER: The socket was not found in the message map"
            #             s.send("No message")
            #         else:
            #             time.sleep(.1)
            #             s.send(next_msg)

            #     # Handle "exceptional conditions"
            #     for s in exceptional:
            #         if prints:
            #             print >>sys.stderr, 'LEADER_LISTENER: handling exceptional condition for', s.getpeername()
            #         # Stop listening for input on the connection
            #         inputs.remove(s)
            #         if s in outputs:
            #             outputs.remove(s)
            #         s.close()

            #         # Remove message queue
            #         del message_queues[s]

            # TODO figure out how to have follower thread loop continuously
            # break
