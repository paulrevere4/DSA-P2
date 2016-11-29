# DSA-P2
Distributed Systems &amp; Algorithms Project 2

## Useful links
[Project Prompt](http://www.cs.rpi.edu/~pattes3/dsa_fall2016/DSAFall2016Project2.pdf)

[ZooKeeper Slides](http://www.cs.rpi.edu/~pattes3/dsa_fall2016/Zookeeper.pdf)

[ZooKeeper’s atomic broadcast protocol: Theory and practice](http://www.tcs.hut.fi/Studies/T-79.5001/reports/2012-deSouzaMedeiros.pdf)

[Leader Election algorithms (we are using the Bully algorithm)](http://www.cs.rpi.edu/~pattes3/dsa_fall2016/LeaderElection.pdf)


## Order of events
- Upping all servers individually
 - All upped servers start two listeners
  - One listener for client on client_port
  - One listener for server connections on server_port
- Client sends "start" to one server
- Server that receives "start" broadcasts election start to other servers
 - For now, it can just broadcast "I am your leader"
- When a server receives a "leader is #" message
 - Stop server listener
 - Leader server runs "lead\_connections" and other servers run "leader\_listener"
- After connections are formed, re-initialize listener for server

## Config file formatting:
\[Server number\] \[Server IP\] \[server\_port\] \[leader\_port\] \[client\_port\]

## Testing
Run 3 servers with
```
$ . ./test_scripts/run3.sh
```
Run test case with
```
$ python cli_client.py <server-host> <server-client-port>  <  <input-file>
```
Kill the running servers with
```
$ . ./test_scripts/kill.sh
```

## Message types
For requesting and committing transactions
```
['transaction_request', operation, epoch-string, counter-string] - follower requests a transaction to leader
['transaction_proposal', transaction-string, epoch-string, counter-string] - transaction proposal from leader to followers
['transaction_acknowledge', transaction-string, epoch-string, counter-string] - trasaction accept/acknowledge from follower to the leader
['transaction_commit', transaction-string, epoch-string, counter-string] - leader committing a transaction to the followers
```

For elections
```
['election', server-number, epoch-string, counter-string] - Initiating election
['higher_id', server-number, epoch-string, counter-string] - Response to election
['lower_id', server-number, epoch-string, counter-string] - Response to election
['coordinator', server-number, epoch-string, counter-string] - Become coordinator
```
TODO:
- Elections
- two-phase commits
- Rebuild recovered server from written history & downloaded history