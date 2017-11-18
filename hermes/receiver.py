"""Receiver Component for usage in Node class."""

# Import Built-Ins
import logging
import time
from queue import Queue, Empty
from threading import Thread, Event

# Import Third-Party
import zmq

# Import home-grown
from hermes.structs import Envelope

# Init Logging Facilities
log = logging.getLogger(__name__)


class Receiver(Thread):
    """Class providing a connection to one or many ZMQ Publisher(s)."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, sub_addr, name, topics=None, exchanges=None):
        """
        Initialize a Receiver instance.

        :param sub_addr: Address to which this :class:`hermes.Receiver` binds to
        :param topics: List of topics to subscribe to
        :param exchanges: List of exchanges to subscribe to
        :param name: Name to give this :class:`hermes.Receiver` instance
        """
        self.zmq_context = zmq.Context()
        self.sock = None
        self.sub_addr = sub_addr
        self.timeout = 1
        self._topics = topics if topics else ''
        self._exchanges = exchanges if exchanges else ''
        self.q = Queue()
        self._running = Event()
        super(Receiver, self).__init__(name=name)

    def stop(self, timeout=None):
        """
        Stop the :class:`hermes.Receiver` instance.

        :param timeout: time in seconds until :exc:`TimeOutError` is raised
        :return: :class:`None`
        """
        self.join(timeout)

    def join(self, timeout=None):
        """Join the :class:`hermes.Receiver` instance.

        Clears the :attr:`hermes.Receiver._is_running` flag, causing a graceful shutdown of
        the run loop.

        :param timeout: timeout in seconds passed to :meth:`threading.Thread.join()`
        :return: :class:`None`
        """
        self._running.clear()
        super(Receiver, self).join(timeout=timeout)

    def run(self):
        """
        Execute the custom run loop for the :class:`hermes.Receiver` class.

        It connectos to a ZMQ publisher on the local machine using the ports
        found in :attr:`hermes.Receiver.ports`. If this is empty, it simply loops doing nothing.

        :return: :class:`None`
        """
        self._running.set()
        ctx = zmq.Context()
        self.sock = ctx.socket(zmq.SUB)
        self.sock.setsockopt_unicode(zmq.SUBSCRIBE, self._topics)
        self.sock.connect(self.sub_addr)

        while self._running.is_set():
            try:
                frames = self.sock.recv_multipart(flags=zmq.NOBLOCK)
            except zmq.error.Again:
                continue
            cts_msg = Envelope.load_from_frames(frames)
            log.debug("run(): Received %r", Envelope)

            if self._exchanges and cts_msg.origin not in self._exchanges:
                continue

            recv_at = time.time()
            if recv_at - float(cts_msg.ts) > self.timeout:
                log.error("Reciever %s: Receiver cannot keep up with publisher "
                          "(message delay(%s) > %s)! Cannot take peer "
                          "pressure, committing suicide.",
                          self.name, recv_at - cts_msg.ts, self.timeout)
                self._running.clear()
                continue

            self.q.put(cts_msg)

        ctx.destroy()
        self.sock = None

    def recv(self):
        """
        Wrap around :meth:`Queue.get()`.

        Returns the popped value or :class:`None` if the :class:`queue.Queue` is empty.

        :return: data or :class:`None`
        """
        try:
            return self.q.get(block=False)
        except Empty:
            return None
