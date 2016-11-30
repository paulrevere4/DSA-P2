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

        # queue of server responses
        self.server_response_queue = Queue.Queue()

        # Tracking of epoch and counter values
        self.epoch = 0
        self.counter = 0

        # Boolean for if this server is the leader
        self.is_leader = False

        # Election information
        self.holding_election = True

        # Initializes empty file system
        self.file_system = {}

        # Initializes empty transaction history
        self.transaction_history = []

        # Filename for the transaction history on disk
        self.transaction_history_fname = "server_%d.history" %self.server_num

        # 2PC acknowledgement count. {command-str : ack-count}, ack-count == -1 means the message was committed
        self.ack_counts = {}

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
            resp = ""
            if not fname in self.file_system.keys():
                resp += "SERVER: ERROR: FILE '%s' NOT IN FILESYSTEM AT THIS TIME" %fname
            else:
                resp += "SERVER: READING FILE '%s':\n" %fname
                resp += self.file_system[fname]
            self.server_response_queue.put(resp)
        else:
            msg = ["transaction_request", cmd, "", "", str(self.server_num)]
            self.follower_message_queue.put((5, msg))


    # ==========================================================================
    # When a Follower receives a "transaction_commit", it forwards the message
    # here to have the changes propogated to the file system
    #
    # message = ["transaction_commit", command, epoch, counter, originator-num]
    #
    def commit_changes(self, message):
        self.counter += 1
        print "SERVER: COMMITTING CHANGES (%s,%s): %s" % (message[2], message[3], message[1])
        trans = Transaction(message[1:-1])
        orignator = int(message[4])
        self.record_transaction(trans)
        resp = "    SERVER: " + self.commit_transaction_to_fs(trans) + "\n"
        if orignator == self.server_num and message[0] != "transaction_proposal":
            self.server_response_queue.put(resp)

    # ==========================================================================
    # Adds a transaction to the transaction history
    #
    def commit_transaction_to_fs(self, trans):
        trans_str = "%s" %trans.value
        split_cmd = trans_str.split()
        file = split_cmd[1]
        resp = ""
        if split_cmd[0] == "create":
            if not file in self.file_system:
                self.file_system[file] = ""
                resp += "CREATED FILE '%s'" %file
            else:
                resp += "ERROR: FILE '%s' ALREADY EXISTS" %file
        elif split_cmd[0] == "append":
            if file in self.file_system:
                to_write = " ".join(split_cmd[2:])
                self.file_system[file] += to_write + "\n"
                resp += "WROTE '%s' TO FILE '%s'" %(to_write, file)
            else:
                resp += "ERROR: FILE '%s' DOESN'T EXIST" %file
        elif split_cmd[0] == "delete":
            if file in self.file_system:
                del self.file_system[file]
                resp += "DELETED FILE '%s'" %file
            else:
                resp += "ERROR: FILE '%s' DOESN'T EXIST" %file
        return resp


    # ==========================================================================
    # Adds a transaction to the transaction history
    #
    def record_transaction(self, trans):
        self.transaction_history.append(trans)
        self.transaction_history = sorted(self.transaction_history) # not fast
        self.write_transaction_history()

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
        self.transaction_history = []
        with open(history_fname) as f:
            for line in f:
                split_line = line.split()
                command = " ".join(split_line[:-2])
                epoch = int(split_line[-2])
                counter = int(split_line[-1])
                trans = Transaction(command, (epoch, counter))
                self.transaction_history.append(trans)
        self.transaction_history = sorted(self.transaction_history)
        for t in self.transaction_history:
            print self.commit_transaction_to_fs(t)
        self.write_transaction_history()
        last_trans = max(self.transaction_history)
        self.epoch = last_trans.epoch
        self.counter = last_trans.counter

    # ==========================================================================
    # Returns True if first argument is greater than second argument
    #
    def bully_compare(self, message1, message2):
        s1 = int(message1[1])
        s2 = int(message2[1])
        e1 = int(message1[2])
        e2 = int(message2[2])
        c1 = int(message1[3])
        c2 = int(message2[3])

        if e1 > e2:
            return True
        elif e1 == e2:
            if c1 > c2:
                return True
            elif c1 == c2:
                if s1 > s2:
                    return True
                elif s1 == s2:
                    print "Wow"
                    exit(1)
                else:
                    return False
            else:
                return False
        else:
            return False

    # ==============================================================================
    # Creates a connection with every other server
    #
    def setup_connections(self, server_locations):
        # Map of server nums to the socket for that server
        sockets = {}
        # Open connections to all servers
        for key, location in server_locations.items():
            if not self.is_leader and key == self.server_num:
                continue 
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print "    CONNECTING TO %s:%i" % (location[0], location[2])
            try: 
                s.connect((location[0], location[2])) # Connects to Leader listener for all servers
                sockets[key] = s
            except:
                print "    Couldn't connect to %s:%i" % (location[0], location[2])
        return sockets

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
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print   "[!] USAGE:\n" \
                "    $ python server.py <int server_num> <config file path> [<transaction-history-file>]"
        exit(1)

    server_num = int(sys.argv[1])
    config_map = process_config(sys.argv[2])

    # setup server object and run
    s = Server(server_num, config_map)

    # if a history file is provided use it to build the fs
    if len(sys.argv) == 4:
        history_fname = str(sys.argv[3])
        s.import_transaction_history(history_fname)

    s.start_threads()
    s.run()

    # time.sleep(15)
    # print "STOPPING LEADER IF RUNNING"
    # s.stop_leader()
    # print "STOPPING FOLLOWER IF RUNNING"
    # s.stop_follower()

    # t = Transaction("create file.txt", (0,0))
    # s.commit_changes(["transaction_commit", "create file.txt", "0", "0"])
    # s.write_transaction_history()
    # print s.file_system
