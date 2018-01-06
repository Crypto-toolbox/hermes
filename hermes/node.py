"""Node Class to pull together receivers and publishers.

Functions as the smallest available unit with which can be communicated in a cluster.

It offers slots for a Publisher and Receiver object. Each of these must implement at least a
start() and stop() function, as well as a recv() (Receiver) and publish() (Publisher) method.
The passed objects are therefore not limited to :class:`hermes.Publisher`
and :class:`hermes.Receiver` objects.

When left unmodified, the Node will simply pass data from the receiver to the publisher.

:class:`hermes.Node` supports the `with` statement and will start up all facilities it has
stored in its instance's :attr:`hermes.Node.facilities` property. These will also be stopped after
leaving the with block, respectively.
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Home-grown
from hermes.structs import Envelope

log = logging.getLogger(__name__)


class Node:
    """
    Basic Node Class.

    Provides a basic interface for starting and stopping a node.

    Extend this as necessary.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, name, receiver=None, publisher=None):
        """
        Initialize the instance.

        :param name: name of the :class:`hermes.Node` instance.
        :param receiver: :class:`hermes.Receiver` instance.
        :param publisher: :class:`hermes.Publisher` instance.
        """
        self.publisher = publisher
        self.receiver = receiver
        self._facilities = [self.receiver, self.publisher]
        self.name = name
        self._running = False

    @property
    def facilities(self):
        """Return the names of facilities registered with this :class:`hermes.Node` instance."""
        return [f.name for f in self._facilities]

    def start(self):
        """Start the :class:`hermes.Node` instance and its facilities."""
        log.info("Starting node..")
        self._start_facilities()
        log.info("..done.")

    def stop(self):
        """Stop the :class:`hermes.Node` instance and its facilities."""
        log.info("Stopping node..")
        self._stop_facilities()
        log.info("..done.")

    def __enter__(self):
        """Start facilities upon entering with-block."""
        self._start_facilities()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop facilities upon leaving with-block."""
        self._stop_facilities()

    def _start_facilities(self):
        """
        Start the Facilities available.

        Iterates over :attr:`hermes.Node._facilities` and starts all facilities that evaluate
        to True.

        All facilities must support a stop() method, otherwise an exception is
        logged and the facility isn't stopped.
        """
        self._running = True
        log.debug("Starting facilities (%r total)", len(self._facilities))
        for facility in self._facilities:
            if facility:
                try:
                    facility.start()
                except Exception as e:
                    log.exception(e)
                    log.error("Could not start all facilities!")
                    raise
        log.debug("All facilities started successfully.")

    def _stop_facilities(self):
        """
        Stop the available facilities.

        Iterates over self._facilities and stops all facilities that evaluate
        to True.

        All facilities must support a stop() method, otherwise an exception is
        logged and the facility isn't stopped.
        """
        self._running = False
        log.debug("Stopping facilities (%r total)", len(self._facilities))
        for facility in self._facilities:
            if facility:
                try:
                    facility.stop()
                except Exception as e:
                    log.exception(e)
                    log.error("Could not stop all facilities!")
                    raise
        log.debug("All facilities stopped successfully.")

    def publish(self, channel, data):
        """
        Publish the given data to channel, if a :class:`hermes.Receiver` instance is available.

        The topic is generated from channel and :class:`hermes.Node.name`.

        :param channel: topic tree
        :param data: Data Struct or string
        :return: :class:`None`
        """
        envelope = Envelope(channel + '/' + self.name, self.name, data)
        try:
            self.publisher.publish(envelope)
        except AttributeError:
            raise NotImplementedError

    def recv(self, block=False, timeout=None):
        """Receive data from the :class:`hermes.Receiver` instance, if available."""
        try:
            return self.receiver.recv(block, timeout)
        except AttributeError:
            raise NotImplementedError

    def run(self):
        """Execute the main loop, which can be extended as necessary.

        If not extended, the following loop will be executed while
        :attr:`hermes.Node._running` is True:
            1. call :meth:`hermes.Node.recv` and check if there's a message
            2. if a message was received:
                call :meth:`hermes.Node.publish` and send message.
            3. Repeat.
        """
        while self._running:
            msg = self.recv()
            if msg:
                self.publish('RAW', msg)
