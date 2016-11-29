"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
cli_client.py

Implements the command line interface for the user, runs on the user's machine
and can connect to any of the servers.

create <filename>: creates an empty file named <filename>
delete <filename>: deletes file named <filename>
read <filename>: displays the contents of <filename>
append <filename> <line>: appends a <line> to <filename>
exit : exits the client
sleep <seconds>: client waits for specified number of seconds
"""
# ==============================================================================

import sys
import time
import socket
import threading

from serializer import Serializer

# ==============================================================================
# Checks if the given command is a valid command, returns True if it is, False
# otherwise.
#
def check_cmd(cmd):
    split_cmd = cmd.split()
    # check if the command is an accepted type
    if not split_cmd[0] in set(["create", "delete", "read", "append"]):
        return False
    # check if the command has the right number of args for "create", "delete", "read"
    if split_cmd[0] in set(["create", "delete", "read"]) and len(split_cmd) != 2:
        return False
    # check if the command has the right number of args for "append"
    if split_cmd[0] == "append" and len(split_cmd) < 3:
        return False
    return True

# ==============================================================================
# Takes input and sends it to the specified server
# *** TODO ***
#   - Handle responses from server
#
def run(host, port):
    while True:
        time.sleep(.1)
        cmd = raw_input("Input: ")
        print "CLIENT: Read '%s' from command line" %cmd
        if cmd == "exit":
            print "CLIENT: EXITING"
            exit(0)
        elif cmd.split()[0] == "sleep":
            seconds = float(cmd.split()[1])
            print "CLIENT: SLEEPING FOR %.1f seconds" %seconds
            time.sleep(seconds)
        elif check_cmd(cmd):
            packed = Serializer.serialize([cmd])
            s = socket.socket()
            s.connect((host, port))
            s.send(packed)
            print "CLIENT: SENT '%s' AS TO SERVER AT (HOST=%s, PORT=%d) AS '%s'" %(cmd, host, port, packed)
            print "CLIENT: WAITING FOR SERVER RESPONSE"
            resp = s.recv(1024)
            unpacked = Serializer.deserialize(resp)
            print "CLIENT: SERVER RESPONSE:"
            print unpacked[0]
            s.close()
        else:
            print "CLIENT: ERROR: INVALID COMMAND '%s'" %cmd

if __name__ == "__main__":

    # usage prompt if wrong number of args given
    if len(sys.argv) != 3:
        print   "[!] USAGE:\n" \
                "    $ python cli_client.py <server-host> <server-port>"
        exit(1)

    # setup our script arguments
    host = str(sys.argv[1])
    port = int(sys.argv[2])

    # prompt
    print "Connecting to: host=%s and port=%d" %(host, port)

    # run the cli
    run(host, port)
