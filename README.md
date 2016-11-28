# DSA-P2
Distributed Systems &amp; Algorithms Project 2

## Useful links
[Project Prompt](http://www.cs.rpi.edu/~pattes3/dsa_fall2016/DSAFall2016Project2.pdf)

[ZooKeeper Slides](http://www.cs.rpi.edu/~pattes3/dsa_fall2016/Zookeeper.pdf)

[ZooKeeper’s atomic broadcast protocol: Theory and practice](http://www.tcs.hut.fi/Studies/T-79.5001/reports/2012-deSouzaMedeiros.pdf)

[Leader Election algorithms (we are using the Bully algorithm)](http://www.cs.rpi.edu/~pattes3/dsa_fall2016/LeaderElection.pdf)


Order of events
- Upping all servers individually
 - All upped servers start a listener for client/server connections
- Client sends "start" to one server
- Server that receives "start" broadcasts election start to other servers
 - For now, it can just broadcast "I am your leader"
- When a server receives a "leader is #" message
 - Leader server runs "lead\_connections" and other servers run "leader\_listener"