+---------+----------------+-------------------+----------------+
|Branch   | Build Status   |   Coverage        | Documentation  |
+=========+================+===================+================+
|`master` | |master_build| | |master_coverage| | |master_docs|  |
+---------+----------------+-------------------+----------------+
|`dev`    | |dev_build|    | |dev_coverage|    |  |dev_docs|    |
+---------+----------------+-------------------+----------------+



Hermes
======
ZMQ-based framework for building simple Pub-Sub Systems, written in Python 3.

It offers thread-based wrappers for zmq's SUB and PUB sockets, a pre-configured proxy device
and a Node class to pull it all together.

Hermes allows you to quickly build a cluster of publishers which can support arbitrary numbers
of subscribers via single address.

Since the project was birthed with a financial use-case in mind, it supplies some basic data structures (called `Message`) to transport data via `hermes`. These are optional, but are used by other parts of our system to efficiently process incoming data streams.



Design
======

There as several basic components that interact in a `hermes`-based system:
On the processing layer, we have:

- the ``Node`` object, which may consist of any number of `Receiver` and `Publisher` objects.
- the ``Proxy`` object, which aggregates data streams from several `Node` objects and allows subscribers to subscribe to them from a single address.

On the transport layer, we have: 

- the ``Envelope`` object, which is just a wrapper data structure to send around messages with some meta data attached (time stamp of creation, origin, topic, etc)
- the ``Message`` object, which is usually sent by assigning it to an ``Envelope`` (although the usage of a `Message` object is optional - `Envelope` takes any kind of serializable data).



Motivation
==========
Hermes is the base for our Crypto trading system, and allows us to set up new node clusters in a
convenient and maintainable way, without our contributors having to worry too much about the inner
workings of ZMQ.



Usage
=====

install via ``pip install hermes-zmq`` and import with ``import hermes``.


.. |master_build| image:: https://travis-ci.org/Crypto-toolbox/hermes.svg?branch=master
    :target: https://travis-ci.org/Crypto-toolbox/hermes

.. |master_coverage| image:: https://coveralls.io/repos/github/Crypto-toolbox/hermes/badge.svg?branch=master
    :target: https://coveralls.io/github/Crypto-toolbox/hermes?branch=master

.. |dev_build| image:: https://travis-ci.org/Crypto-toolbox/hermes.svg?branch=dev
    :target: https://travis-ci.org/Crypto-toolbox/hermes             

.. |dev_coverage| image:: https://coveralls.io/repos/github/Crypto-toolbox/hermes/badge.svg?branch=dev
    :target: https://coveralls.io/github/Crypto-toolbox/hermes?branch=dev


.. |master_docs| image:: https://readthedocs.org/projects/hermes-framework/badge/?version=latest
    :target: http://hermes-framework.readthedocs.io/en/latest/?badge=latest

.. |dev_docs| image:: https://readthedocs.org/projects/hermes-framework/badge/?version=dev
    :target: http://hermes-framework.readthedocs.io/en/dev/?badge=dev


