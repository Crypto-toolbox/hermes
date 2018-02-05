"""Publisher component for use in a Node class."""

# Import Built-Ins
import logging
from queue import Queue
from threading import Thread, Event

# Import Third-Party
import zmq

# Import home-grown


# Init Logging Facilities
log = logging.getLogger(__name__)


class Publisher(Thread):
    """
    Allows publishing data to subscribers.

    The publishing is realized with ZMQ's Publisher sockets, and supports publishing
    to multiple subscribers.

    The :meth:`hermes.Publisher.run` method continuously checks for data on the internal q,
    which is fed by the :meth:`hermes.Publisher.publish` method.
    """

    def __init__(self, target_addr, name, ctx=None, socket_type=None):
        """
        Initialize Instance.

        :param pub_addr: Address this instance should bind to
        :param name: Name to give this :class:`hermes.Publisher` instance.
        """
        self.target_addr = target_addr
        self._running = False
        self.sock = None
        self.ctx = ctx or zmq.Context().instance()

        self._input = self.ctx.socket(zmq.PUSH)
        self._output = self.ctx.socket(zmq.PULL)

        self.socket_type = socket_type or zmq.PUB
        super(Publisher, self).__init__(name=name)

    def publish(self, envelope):
        """
        Publish the given data to all current subscribers.

        :param envelope: :class:`hermes.Envelope` instance
        :return: None
        """
        if self.sock:
            self._input.send_multipart(envelope.convert_to_frames())
            return True
        return False

    def stop(self, timeout=None):
        """
        Stop the :class:`hermes.Publisher` instance.

        :param timeout: time in seconds until :exc:`TimeOutError` is raised
        :return: :class:`None`
        """
        log.info("Stopping Publisher instance..")
        self.join(timeout=timeout)
        log.info("..done.")

    def join(self, timeout=None):
        """
        Join the :class:`hermes.Publisher` instance and shut it down.

        Clears the :attr:`hermes.Publisher._running` flag to gracefully terminate the run loop.

        :param timeout: timeout in seconds to wait for :meth:`hermes.Publisher.join` to finish
        :return: :class:`None`
        """
        log.debug("Clearing _running state..")
        self._running = False
        log.debug("Closing socket..")
        try:
            self.sock.close()
        except AttributeError:
            log.debug("Socket was already closed!")
        super(Publisher, self).join(timeout)

    def run(self):
        """
        Customized run loop to publish data.

        Sets up a ZMQ publisher socket and sends data as soon as it is available
        on the internal Queue at :attr:`hermes.Publisher.q`.

        :return: :cls:`None`
        """
        self._running = True
        ctx = zmq.Context()
        self.sock = ctx.socket(self.socket_type)
        log.info("Connecting Publisher to zmq.XSUB Socket at %s.." % self.pub_addr)
        self.sock.connect(self.target_addr)
        log.info("Executing publisher loop..")
        while self._running:
            try:
                frames = self._output.recv_multipart(zmq.NOBLOCK)
            except zmq.EAgain:
                continue
            log.debug("Sending %r ..", cts_msg)
            try:
                self.sock.send_multipart(frames)
            except zmq.error.ZMQError as e:
                log.error("ZMQError while sending data (%r) - stopping Publisher", e)
                break
            except AttributeError:
                if not self._running:
                    log.info("Exiting publisher loop..")
                    break
                raise
        ctx.destroy()
        self.sock = None
        log.info("Loop terminated.")

