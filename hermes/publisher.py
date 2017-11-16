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

    def __init__(self, pub_addr, name, ctx=None):
        """
        Initialize Instance.

        :param pub_addr: Address this instance should bind to
        :param name: Name to give this :class:`hermes.Publisher` instance.
        """
        self.pub_addr = pub_addr
        self._running = Event()
        self.sock = None
        self.q = Queue()
        self.ctx = ctx or zmq.Context().instance()
        super(Publisher, self).__init__(name=name)

    def publish(self, envelope):
        """
        Publish the given data to all current subscribers.

        :param envelope: :class:`hermes.Envelope` instance
        :return: None
        """
        if self.sock:
            self.q.put(envelope)
            return True
        return False

    def stop(self, timeout=None):
        """
        Stop the :class:`hermes.Publisher` instance.

        :param timeout: time in seconds until :exc:`TimeOutError` is raised
        :return: :class:`None`
        """
        self.join(timeout=timeout)

    def join(self, timeout=None):
        """
        Join the :class:`hermes.Publisher` instance and shut it down.

        Clears the :attr:`hermes.Publisher._running` flag to gracefully terminate the run loop.

        :param timeout: timeout in seconds to wait for :meth:`hermes.Publisher.join` to finish
        :return: :class:`None`
        """
        self._running.clear()
        try:
            self.sock.close()
        except AttributeError:
            pass
        super(Publisher, self).join(timeout)

    def run(self):
        """
        Custumized run loop to publish data.

        Sets up a ZMQ publisher socket and sends data as soon as it is available
        on the internal Queue at :attr:`hermes.Publisher.q`.

        :return: :class:`None`
        """
        self._running.set()
        ctx = zmq.Context()
        self.sock = ctx.socket(zmq.PUB)
        self.sock.connect(self.pub_addr)
        while self._running.is_set():
            if not self.q.empty():
                cts_msg = self.q.get(block=False)
                frames = cts_msg.convert_to_frames()
                log.debug("Sending %r ..", cts_msg)
                try:
                    self.sock.send_multipart(frames)
                except zmq.error.ZMQError as e:
                    log.error("ZMQError while sending data (%s), "
                              "stopping Publisher", e)
                    break
            else:
                continue
        ctx.destroy()
        self.sock = None
