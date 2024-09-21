# Consistent Hashing with Redis

Consistent hashing is a technique used in distributed systems to distribute data across multiple servers.
It is used in systems where data is distributed across multiple servers and the servers can be added or removed dynamically.
Consistent hashing is used in systems like load balancers, distributed caches, and distributed databases.

In this sample project, we use consistent hashing to distribute data across multiple Redis instances.

## Instructions

```bash
docker-compose up -d

python zoo_setup.py

./start.sh 192.168.0.100:7001
```
