# IoT Cache

This IoT key-value cache started as a simple idea to improve resilience in IoT systems. While it may not seem groundbreaking, it offers a practical solution for scenarios where IoT devices lose connection. By providing a local cache for sensor data, the system ensures data continuity, automatically syncing with a Redis database once the connection is restored.