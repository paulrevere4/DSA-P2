"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
server.py
"""
# ==============================================================================

import sys
import Queue
import threading

from client_listener import *
from leader_listener import *
from leader import *
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
        # set the server num
        self.server_num = server_num

        # set the server locations
        self.server_locations = server_locations

        # Gets host IP from server_locations
        self.host = server_locations[server_num][0]

        # Gets listening ports from server_locations
        self.server_listen_port = server_locations[server_num][1]
        self.leader_listen_port = server_locations[server_num][2]
        self.cli_listen_port = server_locations[server_num][3]

        # set the flags for running the leader leader listener threads
        # these are queues, if they're empty the thread won't run
        # if they have a something in them the thread will run
        # its weird I know...
        self.run_leader_thread = Queue.Queue()
        self.run_leader_listener_thread = Queue.Queue()

        # make the task queue
        self.task_queue = Queue.PriorityQueue()

        # Temporary declaration of leader
        self.is_leader = (server_num == 0) # TODO remove hard coded leader when we can define/elect one
        print "self.is_leader:", self.is_leader

        # Initializes empty file system
        self.file_system = {}

        # Initializes empty transaction history
        self.transaction_history = []

    # ==========================================================================
    # Starts the worker threads
    #
    def start_threads(self):
        # Suppressing prints in leader to make debugging easier
        leader_printing = True
        if self.is_leader:
            leader_printing = False

        # make the threads
        client_listener_thread = threading.Thread( \
            target=run_client_listener, \
            args=(self,))

        leader_listener_thread = threading.Thread( \
            target=run_leader_listener, \
            args=(self, leader_printing))

        leader_thread = threading.Thread( \
            target=run_leader, \
            args=(self,))

        # set threads as daemons so we can kill them
        client_listener_thread.daemon = True
        leader_listener_thread.daemon = True
        leader_thread.daemon = True

        # start threads
        client_listener_thread.start()
        leader_listener_thread.start()
        leader_thread.start()

        if self.is_leader:
            self.run_leader_listener_thread.put(True)
            print "I AM THE LEADER"
            time.sleep(.5)
            self.run_leader_thread.put(True)
        else:
            print "I AM NOT THE LEADER"
            self.run_leader_listener_thread.put(True)

        # time.sleep(5)
        # print "STOPPING LEADER LISTENER (if running)"
        # if not self.run_leader_listener_thread.empty():
        #     self.run_leader_listener_thread.get()
        # print "STOPPING LEADER (if running)"
        # if not self.run_leader_thread.empty():
        #     self.run_leader_thread.get()


    # ==========================================================================
    # Checks the task_queue for tasks and completes them. Main worker thread of
    # the Server.
    #
    def run(self):
        while True:
            if not self.task_queue.empty():
                priority, task = self.task_queue.get()
                print "MAIN_WORKER: CARRYING OUT TASK:", task

                if task[0] == "CLIENT":
                    self.handle_client_input(task[1][0])

    # ==========================================================================
    # Handles client inputs for "create", "delete", "read", and "append"
    # commands
    #
    def handle_client_input(self, cmd):
        split_cmd = cmd.split()
        if split_cmd[0] == "read":
            # simply read the file
            fname = split_cmd[1]
            if not fname in self.file_system.keys():
                print "MAIN_WORKER: ERROR: FILE '%s' NOT IN FILESYSTEM AT THIS TIME" %fname
            else:
                print "MAIN_WORKER: READING FILE '%s':" %fname
                print self.file_system[fname]
        if split_cmd[0] == "create":
            # request create from leader
            print "TODO: Implement create"
        if split_cmd[0] == "delete":
            # reqest delete from leader
            print "TODO: Implement delete"
        if split_cmd[0] == "append":
            # request append from leader
            print "TODO: Implement append"


# ==============================================================================
# Processes a config file from file_location, returns map of server locations
#
def process_config(file_location):
    config_map = {}
    f = open(file_location, "r")
    for line in f:
        words = line.split()
        config_map[int(words[0])] = (words[1], int(words[2]), int(words[3]), int(words[4]))

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
