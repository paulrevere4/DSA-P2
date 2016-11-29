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
            leader = None

            message_queues = {}

            election_replies = []

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
                        if not self.holding_election and leader == None:
                            leader = connection
                    else:
                        data = s.recv(1024)
                        if data == "":
                            print("FOLLOWER: Lost connection to Leader")
                            inputs.remove(s)
                            outputs.remove(s)
                            server.listen(5)
                            s.close()
                            leader = None
                        elif data:
                            deserialize = Serializer.deserialize(data)
                            if s is leader:
                                print "FOLLOWER: Receiving message from leader"
                                # A readable client socket has data
                                print >>sys.stderr, 'FOLLOWER: Received "%s" from %s' % (str(deserialize), s.getpeername())
                                if deserialize[0] == 'transaction_commit':
                                    print "FOLLOWER: Committing transaction %s" % deserialize[1]
                                    self.commit_changes(deserialize)
                            else:
                                # Message is from another server, likely an election
                                if deserialize[0] == 'election':
                                    # Hold election
                                    leader = None
                                    self.holding_election = True
                                    next
                                elif deserialize[0] == 'coordinator':
                                    # New leader has come online,
                                    print "FOLLOWER: New leader is %s" % deserialize[1]
                                    self.transaction_history = []
                                    self.file_system = {}
                                    self.holding_election = False
                                else:
                                    # Reply to election, probably
                                    election_replies.append(deserialize)




                # Handle outputs
                for s in writable:
                    if not self.follower_message_queue.empty():
                        next_msg = self.follower_message_queue.get()
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
