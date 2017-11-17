# Import Built-Ins
import logging
import unittest

# Import Homebrew
from hermes import Publisher, Receiver, Node, Envelope, Message
from hermes.proxy import PostOffice
from hermes.config import XPUB_ADDR, XSUB_ADDR, DEBUG_ADDR

# Init Logging Facilities
log = logging.getLogger(__name__)


class ProxyTests(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
