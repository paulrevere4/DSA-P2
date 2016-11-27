"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
server.py
"""
# ==============================================================================

import Queue
from threading import Thread

from client_listener import *
from serializer import *

# ==============================================================================

# ==============================================================================
# Checks the task_queue for tasks and completes them
def run(task_queue):
    while True:
        if not task_queue.empty():
            task = task_queue.get()
            print task

# ==============================================================================
if __name__ == "__main__":

    # make the task queue
    task_queue = Queue.Queue()

    # make the threads
    client_listener_thread = Thread(target=run_client_listener, args=(task_queue, "localhost", 12345))

    # set threads as daemons so we can kill them
    client_listener_thread.daemon = True

    # start threads
    client_listener_thread.start()

    # run main
    run(task_queue)
