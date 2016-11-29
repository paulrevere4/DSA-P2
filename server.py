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
from follower import *
from leader import *
from transaction import *
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
        self.run_leader_thread = False
        self.run_follower_thread = False

        # make the task queues
        self.task_queue = Queue.PriorityQueue()

        # Follower task queue
        self.follower_message_queue = Queue.PriorityQueue()

        # queue of messages for the leader to send (recipient, message)
        self.leader_message_queue = Queue.Queue()

        # Temporary declaration of leader
        self.is_leader = (server_num == 0) # TODO remove hard coded leader when we can define/elect one

        # Initializes empty file system
        self.file_system = {}

        # Initializes empty transaction history
        self.transaction_history = []

        # Filename for the transaction history on disk
        self.transaction_history_fname = "server_%d.history" %self.server_num

    # ==========================================================================
    #
    def should_run_leader(self):
        return self.run_leader_thread

    # ==========================================================================
    #
    def stop_leader(self):
        self.run_leader_thread = False

    # ==========================================================================
    #
    def start_leader(self):
        self.run_leader_thread = True

    # ==========================================================================
    #
    def should_run_follower(self):
        return self.run_follower_thread

    # ==========================================================================
    #
    def stop_follower(self):
        self.run_follower_thread = False

    # ==========================================================================
    #
    def start_follower(self):
        self.run_follower_thread = True

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

        follower_thread = threading.Thread( \
            target=run_follower, \
            # args=(self, leader_printing))
            args=(self,))

        leader_thread = threading.Thread( \
            target=run_leader, \
            args=(self,))

        # set threads as daemons so we can kill them
        client_listener_thread.daemon = True
        follower_thread.daemon = True
        leader_thread.daemon = True

        # start threads
        client_listener_thread.start()
        follower_thread.start()
        leader_thread.start()

        if self.is_leader:
            self.start_follower()
            print "I AM THE LEADER"
            time.sleep(.5)
            self.start_leader()
        else:
            print "I AM NOT THE LEADER"
            self.start_follower()

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
    # Handles client inputs, spits back response if it's just a "read"
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
        else:
            msg = ["transaction_request", cmd]
            self.follower_message_queue.put((5, msg))

    # ==========================================================================
    # When a Follower receives a "transaction_commit", it forwards the message
    # here to have the changes propogated to the file system
    #
    def commit_changes(self, message):
        split_cmd = message.split()
        file = split_cmd[1]
        if split_cmd[0] == "create":
            if not file in self.file_system:
                self.file_system[file] = ""
            else:
                print "Error, file already exists"
        elif split_cmd[0] == "append":
            if file in self.file_system:
                self.file_system[file] += " ".join(split_cmd[2:])
            else:
                print "Error, file doesn't exists"
        elif split_cmd[0] == "delete":
            if file in self.file_system:
                del self.file_system[file]
            else:
                print "Error, file doesn't exists"

    # ==========================================================================
    # Adds a transaction to the transaction history
    #
    def record_transaction(self, trans):
        self.transaction_history.append(trans)
        self.transaction_history = sorted(self.transaction_history) # not fast

    # ==========================================================================
    # Writes the transaction history to disk
    #
    def write_transaction_history(self):
        f = open(self.transaction_history_fname, 'w')
        for t in self.transaction_history:
            f.write("%s\n" %t)
        f.close()

    # ==========================================================================
    # Imports a transaction history, used when a server crashes
    #
    def import_transaction_history(self, history_fname):
        pass

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

    # time.sleep(15)
    # print "STOPPING LEADER IF RUNNING"
    # s.stop_leader()
    # print "STOPPING FOLLOWER IF RUNNING"
    # s.stop_follower()

    # t = Transaction("create file.txt", (0,0))
    # s.record_transaction(t)
    # s.write_transaction_history()
