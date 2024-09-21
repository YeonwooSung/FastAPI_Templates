# GUID (Globally Unique Identifier)

For distributed systems, unique indentifiers are essential to ensure that data is uniquely identified across multiple servers.

Easiest way to generate unique identifiers is simply using UUIDs (Universally Unique Identifiers).
UUIDs are 128-bit numbers that are unique across time and space.
UUID version 4 is the most commonly used version and it is generated using random numbers, which uses the randomness of the system to generate unique identifiers.
The randomness of the system is used to ensure that the UUIDs generated are unique.
However, the size of the UUID is 128 bits, which is larger than the size of a 64-bit integer.
Also, using randomly generated UUIDs can lead to performance issues in distributed systems (e.g., B-tree index works well with sequential numbers).

To overcome these issues, this project generates snowflake-based GUID, which is smaller and sequential.

## Running Instructions

```bash
./start.sh
```
