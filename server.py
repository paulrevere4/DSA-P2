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
from serializer import *

# ==============================================================================
# Checks the task_queue for tasks and completes them
#
def run(task_queue):
    while True:
        if not task_queue.empty():
            task = task_queue.get()
            print task

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

    # make the task queue
    task_queue = Queue.Queue()

    # make the threads
    client_listener_thread = Thread(target=run_client_listener, args=(task_queue, host, cli_listen_port))

    # set threads as daemons so we can kill them
    client_listener_thread.daemon = True

    # start threads
    client_listener_thread.start()

    # run main
    run(task_queue)
