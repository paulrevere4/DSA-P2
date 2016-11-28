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
import fcntl, os
import errno

from serializer import Serializer

# ==============================================================================
# Communicates with lead server, sending messages and receiving transactions
#
def run_leader_listener(task_queue, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
    s.bind((host, port))        # Bind to the port
    s.listen(5)                 # Now wait for client connection.
    fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)
    print "LEADER_LISTENER: LISTENING ON host=%s port=%d" %(host, port)

    lead_listener_queue = Queue.Queue()
    
    time.sleep(.1)
    c, addr = s.accept()    # Establish connection with leader.
    print "LEADER_LISTENER: GOT CONNECTION FROM LEADER AT ", addr

    while True:
        try:
            msg = s.recv(4096)
        except socket.timeout, e:
            err = e.args[0]
            # this next if/else is a bit redundant, but illustrates how the
            # timeout exception is setup
            if err == 'timed out':
                sleep(1)
                print 'recv timed out, retry later'
                continue
            else:
                print e
                sys.exit(1)
        except socket.error, e:
            # Something else happened, handle error, exit, etc.
            print e
            sys.exit(1)
        else:
            if len(msg) == 0:
                print 'orderly shutdown on server end'
                sys.exit(0)
            else:
                # msg = new message from leader, handle accordingly
                print msg

        if not lead_listener_queue.empty():
            task = lead_listener_queue.get()
        print "Out of loop"
