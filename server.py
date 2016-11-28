"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
server.py
"""
# ==============================================================================

import sys
import Queue
from threading import Thread

from client_listener import *
from serializer import Serializer

# ==============================================================================
#
class Server(object):
    """
    Object that will carry out the responsibilities of the server
    """
    # ==========================================================================
    # Setup member variables
    #
    def __init__(self, server_num, host, cli_listen_port):
        self.server_num = server_num

        self.host = host
        self.cli_listen_port = cli_listen_port

        # make the task queue
        self.task_queue = Queue.PriorityQueue()

        # Temporary declaration of leader
        self.is_leader = (server_num == 0)

    # ==========================================================================
    # Starts the worker threads
    #
    def start_threads(self):
        # make the threads
        client_listener_thread = Thread( \
            target=run_client_listener, \
            args=(self.task_queue, self.host, self.cli_listen_port))

        # set threads as daemons so we can kill them
        client_listener_thread.daemon = True

        # start threads
        client_listener_thread.start()


    # ==========================================================================
    # Checks the task_queue for tasks and completes them. Main worker thread of
    # the Server.
    #
    def run(self):
        while True:
            if not self.task_queue.empty():
                priority, task = self.task_queue.get()
                print "MAIN_WORKER: COMPLETING TASK:", task

# ==============================================================================
#
if __name__ == "__main__":

    # usage prompt if wrong number of args given
    if len(sys.argv) != 3:
        print   "[!] USAGE:\n" \
                "    $ python server.py <host> <cli-listen-port>"
        exit(1)

    # setup our script arguments
    host = str(sys.argv[1])
    cli_listen_port = int(sys.argv[2])

    # setup server object and run
    s = Server(0, host, cli_listen_port)
    s.start_threads()
    s.run()
