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

def handle_message(self, message):
    if message[0] == 'transaction_request':
        # message[0] = 'transaction_commit'
        # message[2] = str(self.epoch)
        # message[3] = str(self.counter)
        # self.counter+=1

        # for key, location in self.server_locations.items():
        #     self.leader_message_queue.put((key, message))
        message[0] = 'transaction_proposal'
        message[2] = str(self.epoch)
        message[3] = str(self.counter)

        # now we have message = ['transaction_proposal', command, epoch, counter, originator]
        for key, location in self.server_locations.items():
            self.leader_message_queue.put((key, message))

        self.ack_counts[message[1]] = 0

    # TODO
    elif message[0] == 'transaction_acknowledge':
        # -1 indicates the message was sent
        if self.ack_counts[message[1]] != -1:
            self.ack_counts[message[1]] += 1
            if self.ack_counts[message[1]] > len(self.server_locations.keys())/2:
                "LEADER: ENOUGH ACKS FOR MESSAGE '%s', COMMITTING" %str(message)
                self.ack_counts[message[1]] = -1
                message[0] = 'transaction_commit'
                message[2] = str(self.epoch)
                message[3] = str(self.counter)
                for key, location in self.server_locations.items():
                    self.leader_message_queue.put((key, message))

                # self.record_transaction(message)


# ==============================================================================
# Removes a socket from sockets
#
def remove_socket(sockets, socket):
    for key, sock in sockets.items():
        if sock == socket:
            del sockets[key]
    return sockets

# ==============================================================================
# Sends the leader's entire history so the followers will be synced with it
#
def send_entire_history(self):
    print "LEADER: SENDING ENTIRE HISTORY TO FOLLOWERS"
    for t in self.transaction_history:
        # pretend its a transaction request and distribute the message using distribute_message
        cmd = t.value
        epoch = t.epoch
        counter = t.counter
        print "LEADER: TRANSACTION TO SEND: '%s'" %cmd
        msg = ["transaction_commit", cmd, str(epoch), str(counter), "-1"]
        for key, location in self.server_locations.items():
            self.leader_message_queue.put((key, msg))
    self.transaction_history = []
    self.file_system = {}

# ==============================================================================
# Listener for lead server
#
def run_leader(self):

    while True:

        # check if the thread should run, loop over and over again if not
        if not self.should_run_leader():
            time.sleep(.1)
            # print "LEADER THREAD NOT RUNNING"
        else:
            time.sleep(.1)
            print "LEADER THREAD RUNNING"

            # connect to all of the followers
            sockets = self.setup_connections(self.server_locations)

            # on startup of leader write the history to all of the followers
            send_entire_history(self)

            # loop continuously to work on the messages
            while True:
                sockets_list = list(sockets.values())
                readable, writable, exceptional = select.select(sockets_list, sockets_list, sockets_list)

                for s in readable:
                    # Received message from other server
                    data = s.recv(1024)
                    if data == "":
                        print("LEADER: Lost connection to server")
                        sockets = remove_socket(sockets, s)
                        sockets_list.remove(s)
                    else:
                        print "LEADER: RECEIVED MESSAGE FROM %s:" % str(s.getpeername())
                        deserialized = Serializer.deserialize(data)
                        print "    MESSAGE: '%s'" %str(deserialized)
                        handle_message(self, deserialized)
                    # TODO handle message

                writable_set = set(writable)
                while not self.leader_message_queue.empty():
                    recipient, message = self.leader_message_queue.get()
                    # messages_to_send[sockets[recipient]] = message
                    recipient_socket = None
                    if recipient in sockets: recipient_socket = sockets[recipient]
                    if recipient_socket and recipient_socket in writable_set:
                        time.sleep(.1)
                        serialized = Serializer.serialize(message)
                        recipient_socket.send(serialized)
                        print "LEADER: SENT MESSAGE '%s' TO %s" % (message, str(recipient_socket.getpeername()))
                        # del messages_to_send[s][0]
                    elif recipient_socket == None:
                        print "LEADER: Could not connect to server %s" % recipient
                    else:
                        print "LEADER: ERROR: COULDN'T SEND MESSAGE TO server", recipient_socket.getpeername()

                # messages_to_send = {}
                # for s in writable:
                #     if messages_to_send[s]:
                #         time.sleep(.1)
                #         s.send(messages_to_send[s][0])
                #         print "LEADER: SENT MESSAGE '%s' TO %s" % (messages_to_send[s][0], str(s.getpeername()))
                #         del messages_to_send[s][0]

                for s in exceptional:
                    print 'CONNECTION LOST FROM %s' % s.getpeername()

                if not self.should_run_leader():
                    print "LEADER DONE"
                    break

            # TODO figure out how to have leader thread loop continuously
            # break
