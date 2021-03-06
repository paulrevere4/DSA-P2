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
    host = '0.0.0.0'
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
            sent_election = []

            start_election = self.holding_election

            if self.holding_election:
                outputs = self.setup_connections(self.server_locations).values()
                if len(outputs) == 0:
                    print "No outputs found, this server is now the leader"
                    self.is_leader = True
                    self.holding_election = False
                    start_election = False
                    self.start_leader()
                else:
                    print "Successfully connected to %i servers, sending out election now" % len(outputs)

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
                        if not self.holding_election and leader == None:
                            connection.setblocking(0)
                            print "FOLLOWER: Connected to new leader"
                            leader = connection
                        inputs.append(connection)
                        if not self.holding_election: 
                            print "Adding output %s" % str(client_address)
                            outputs.append(connection)
                    else:
                        try:
                            data = s.recv(1024)
                        except:
                            data = None
                        if data == "":
                            if s == leader:
                                print("FOLLOWER: Unable to connect to leader")
                                inputs.remove(s)
                                if s in outputs: outputs.remove(s)
                                print "Starting election"
                                self.holding_election = True
                                start_election = True
                                sent_election = []
                                outputs = self.setup_connections(self.server_locations).values()
                                readable, writable, exceptional = select.select(inputs, outputs, inputs)
                            else:
                                print("FOLLOWER: Unable to connect to server %s") % str(s.getpeername())
                                inputs.remove(s)
                                if s in outputs: outputs.remove(s)

                        elif data:
                            deserialize = Serializer.deserialize(data)
                            if s is leader:
                                if deserialize[0] == 'election':
                                    print "Election catch, sent from %s" % str(deserialize[1])
                                    # 'leader' isn't actually the leader, this is for catching that edge case
                                    inputs.remove(leader)
                                    leader == None
                                    continue
                                print "FOLLOWER: Receiving message from leader"
                                # A readable client socket has data
                                print >>sys.stderr, 'FOLLOWER: Received "%s" from %s' % (str(deserialize), s.getpeername())
                                # TODO iterate through in chuncks of 5
                                print "FOLLOWER: Receiving message from leader"
                                # A readable client socket has data
                                if deserialize[0] == 'transaction_commit':
                                    print "FOLLOWER: Committing transaction %s" % deserialize[1]
                                    self.commit_changes(deserialize)
                                if deserialize[0] == 'transaction_proposal':
                                    transaction_prop_msg = deserialize[:]
                                    # transaction_prop_msg[1] = "propose " + transaction_prop_msg[1]
                                    # self.commit_changes(transaction_prop_msg)
                                    print "FOLLOWER: Acknowledging transaction %s" % deserialize[1]
                                    deserialize[0] = 'transaction_acknowledge'
                                    self.follower_message_queue.put((2,deserialize))
                            else:
                                # Message is from another server, likely an election
                                if deserialize[0] == 'election':
                                    # Hold election
                                    if leader in inputs: inputs.remove(leader)
                                    if leader in outputs: outputs.remove(leader)
                                    self.is_leader = False
                                    self.stop_leader()
                                    leader = None
                                    self.holding_election = True
                                    election_replies = []

                                    # Serialize response
                                    reply = ["not handled yet", str(self.server_num), str(self.epoch), str(self.counter)]
                                    if self.bully_compare(reply, deserialize):
                                        reply[0] = 'higher_id'
                                    else:
                                        reply[0] = 'lower_id'

                                    print "FOLLOWER: Server %s replying to election request from %s: \n   %s" % (str(self.server_num), deserialize[1], str(reply))
                                    serialized = Serializer.serialize(reply)
                                    s.send(serialized)
                                    if reply[0] == 'higher_id':
                                        print "Starting election"
                                        start_election = True
                                        sent_election = []
                                        outputs = self.setup_connections(self.server_locations).values()
                                        readable, writable, exceptional = select.select(inputs, outputs, inputs)
                                elif deserialize[0] == 'coordinator':
                                    # New leader has come online,
                                    print "FOLLOWER: New leader is %s" % deserialize[1]
                                    self.transaction_history = []
                                    self.file_system = {}
                                    self.holding_election = False
                                    start_election = False
                                    election_replies = []
                                    self.epoch +=1
                                else:
                                    # Reply to election, probably
                                    election_replies.append(deserialize)
                                    if len(election_replies) == len(sent_election):
                                        start_election = False
                                        print "All results received! Results:"
                                        higher_ids = []
                                        for reply in election_replies:
                                            if reply[0] == 'higher_id':
                                                higher_ids.append(reply)
                                            print "    %s" % str(reply)
                                        if len(higher_ids) == 0:
                                            print "This server is the new leader"
                                            reply = Serializer.serialize(['coordinator', str(self.server_num)])
                                            for s in sent_election:
                                                s.send(reply)
                                            self.epoch +=1
                                            self.is_leader = True
                                            self.holding_election = False
                                            start_election = False
                                            self.start_leader()                                         

                # Handle outputs
                for s in writable:
                    if s == leader and not self.follower_message_queue.empty():
                        next_msg = self.follower_message_queue.get()
                        print "FOLLOWER: About to send message to leader: '%s'" % str(next_msg)
                        time.sleep(.1)
                        serialized = Serializer.serialize(next_msg[1])
                        s.send(serialized)
                    elif start_election and s not in sent_election:
                        print "Sending election message to server at %s" % str(s.getpeername())
                        message = ['election', str(self.server_num), str(self.epoch), str(self.counter)]
                        serialized = Serializer.serialize(message)
                        if s in outputs: outputs.remove(s)
                        inputs.append(s)
                        sent_election.append(s)
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
