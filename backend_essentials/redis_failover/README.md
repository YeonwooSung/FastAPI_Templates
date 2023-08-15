# Scraping service with Redis failover

In this example, we use a Redis with replication for automatic failover.

Basically, we set the master instance of the Redis cluster as a primary cache and set all of the slaves as secondary caches.
The `monitor.py` script monitors the master instance and if it goes down, it promotes one of the slaves to be the new master.
The updated master instance is then set as the primary cache, and the monitor script changes the config via zookeeper.
The zookeeper data update will invoke the callback function of the scaper server, which will make the server to re-configure the primary redis instance automatically.
