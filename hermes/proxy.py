"""Basic XPub/XSub Proxy Interface for a cluster."""
# pylint: disable=too-few-public-methods

# Import Built-Ins
import logging

# Import Third-Party
import zmq

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


class PostOffice:
    """
    Class to forward subscriptions from publishers to subscribers.

    Uses :const:`zmq.XSUB` & :const:`zmq.XPUB` ZMQ sockets to act as intermediary. Subscribe to
    these using the respective PUB or SUB socket by binding to the same address as
    XPUB or XSUB device.
    """

    def __init__(self, sub_addr, pub_addr, debug_addr=None):
        """
        Initialize a :class:`hermes.PostOffice` instance.

        The addresses used when instantiating these are also the ones your
        publihser and receiver nodes should bind to.

        :param sub_addr: ZMQ Address, including port
        :param pub_addr: ZMQ address, including port
        :param debug_addr: ZMQ address, including port
        """
        self.xsub_url = sub_addr
        self.xpub_url = pub_addr
        self.running = False
        self._debug_addr = debug_addr

    @property
    def debug_addr(self):
        """Return debug socket's address."""
        return self._debug_addr

    def run(self):
        """
        Serve XPub-XSub Sockets.

        Relays Publisher Socket data to Subscribers, and allows subscribers
        to sub to that data. Offers the benefit of having a single static
        address to connect to a cluster.

        :return: :class:`None`
        """
        self.running = True
        ctx = zmq.Context()

        log.info("Setting up XPUB ZMQ socket..")
        xpub = ctx.socket(zmq.XPUB)
        log.info("Binding XPUB socket facing clients to %s..", self.xpub_url)
        xpub.bind(self.xpub_url)

        log.info("Setting up XSUB ZMQ socket..")
        xsub = ctx.socket(zmq.XSUB)
        log.debug("Binding XSUB socket facing services to %s..", self.xsub_url)
        xsub.bind(self.xsub_url)

        # Set up a debug socket, if address is given.
        if self.debug_addr:
            debug_pub = ctx.socket(zmq.PUB)
            debug_pub.bind(self.debug_addr)
        else:
            debug_pub = None

        log.info("Launching poll loop..")
        while self.running:
            try:
                zmq.proxy(xpub, xsub, debug_pub)
            except KeyboardInterrupt:
                break

        xpub.close()
        xsub.close()
        debug_pub.close()
        ctx.term()
