"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
follower.py
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
def run_follower(self, prints = True):

    task_queue = self.task_queue
    host = self.host
    port = self.leader_listen_port
    run_follower_thread = self.run_follower_thread

    while True:

        # check if the thread should run, loop over and over again if not
        if not self.should_run_follower():
            time.sleep(.1)
            # print "FOLLOWER NOT RUNNING"
        else:
            time.sleep(.1)
            print "FOLLOWER THREAD RUNNING ON %s, %s" % (host, str(port))

            # socket setup stuff
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setblocking(0)
            # Bind the socket to the port and listen
            server.bind((host,port))
            server.listen(5)

            inputs = [server]
            outputs = []

            message_queues = {}

            while True:
                # Wait for at least one of the sockets to be ready for processing
                readable, writable, exceptional = select.select(inputs, outputs, inputs)

                # Handle inputs
                for s in readable:
                    if s is server:
                        # A "readable" socket is ready to accept a connection, the first one to connect should be a leader
                        connection, client_address = s.accept()
                        if prints:
                            print >>sys.stderr, 'FOLLOWER: new connection from %s' % str(client_address)
                        connection.setblocking(0)
                        inputs.append(connection)
                        outputs.append(connection)
                    else:
                        print "waiting for data"
                        data = s.recv(1024)
                        print "data received"
                        if data:
                            # A readable client socket has data
                            if prints:
                                print >>sys.stderr, 'FOLLOWER: Received "%s" from %s' % (data, s.getpeername())
                            message_queues[s].put("Successfuly completed task: %s" % data)
                            # Add output channel for response
                            if s not in outputs:
                                outputs.append(s)

                # Handle outputs
                for s in writable:
                    if not self.follower_task_queue.empty():
                        next_msg = self.follower_task_queue.get()
                        print "FOLLOWER: About to send message to leader: '%s'" % str(next_msg)
                        time.sleep(.1)
                        serialized = Serializer.serialize(next_msg[1])
                        s.send(serialized)

                # Handle "exceptional conditions"
                for s in exceptional:
                    print >>sys.stderr, 'FOLLOWER: handling exceptional condition for', s.getpeername()
                    # Stop listening for input on the connection
                    inputs.remove(s)
                    if s in outputs:
                        outputs.remove(s)
                    s.close()

            # TODO figure out how to have follower thread loop continuously
            # break
