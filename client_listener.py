"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
client_listener.py
"""
# ==============================================================================

import time
import Queue
import socket

from serializer import Serializer

# ==============================================================================
# Takes input from the command line client and hands it off to the main thread.
# *** Does not listen for input from other servers ***
#
def run_client_listener(task_queue, host, port):
    s = socket.socket()         # Create a socket object
    s.bind((host, port))        # Bind to the port
    s.listen(5)                 # Now wait for client connection.
    print "CLIENT_LISTENER: LISTENING ON host=%s port=%d" %(host, port)
    while True:
        time.sleep(.1)
        c, addr = s.accept()    # Establish connection with client.
        while True:
            print "CLIENT_LISTENER: GOT CONNECTION FROM", addr
            received = Serializer.deserialize(c.recv(1024))
            task = ["CLIENT", received]
            print "CLIENT_LISTENER: %s" %task
            task_queue.put((5,task)) # TODO solidify task priority
            # c.close()                # Close the connection
            # print "CLIENT_LISTENER: CONNECTION CLOSED"
