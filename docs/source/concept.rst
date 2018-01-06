The technical concept of hermes
===============================

`Hermes` uses ZeroMQ as the transport layer, while providing data structures containing relevant
meta data to the program running it.

A `Hermes` system requires four components to run:

- A Receiver object capable of receiving data from a source
- A Publisher object which publishes, or broadcasts, the data
- An Envelope object transporting the data
- A Node, which runs either a receiver or publisher or both and handles Envelope objects

Optionally, a proxy can be used to simplify subscription to publisher. A Proxy object is provided
by `Hermes`, but a ZeroMQ.proxy object will do just fine.
