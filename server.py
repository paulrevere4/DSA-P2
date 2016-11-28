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
    def __init__(self, server_num, server_locations):
        self.server_num = server_num

        self.server_locations = server_locations

        self.host = server_locations[server_num][0]
        self.cli_listen_port = server_locations[server_num][1]

        # make the task queue
        self.task_queue = Queue.PriorityQueue()

        # Temporary declaration of leader
        self.is_leader = (server_num == 0)

        # Initializes empty file system
        self.file_system = {}

        # Initializes empty transaction history
        self.transaction_histoy = []

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
# Processes a config file from file_location, returns map of server locations
#
def process_config(file_location):
    config_map = {}
    f = open(file_location, "r")
    for line in f:
        words = line.split()
        config_map[int(words[0])] = (words[1], int(words[2]))

    return config_map

# ==============================================================================
#
if __name__ == "__main__":

    # usage prompt if wrong number of args given
    if len(sys.argv) != 3:
        print   "[!] USAGE:\n" \
                "    $ python server.py <int server_num> <config file path>"
        exit(1)

    config_map = process_config(sys.argv[2])
    server_num = int(sys.argv[1])

    # setup server object and run
    s = Server(server_num, config_map)
    s.start_threads()
    s.run()
