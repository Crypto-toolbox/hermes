# Import Built-Ins
import logging
import unittest
import os, signal
from multiprocessing import Process
import time

# Import Homebrew
from hermes.proxy import PostOffice
from hermes.config import XPUB_ADDR, XSUB_ADDR, DEBUG_ADDR

# Init Logging Facilities
log = logging.getLogger(__name__)


class ProxyTests(unittest.TestCase):

    def test_proxy_init_and_properties(self):
        XSUB_ADDR, XPUB_ADDR, DEBUG_ADDR = "tcp://127.0.0.1:5555", "tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557"
        proxy = PostOffice(XSUB_ADDR, XPUB_ADDR, DEBUG_ADDR)
        self.assertEqual(proxy.xpub_url, XPUB_ADDR)
        self.assertEqual(proxy.xsub_url, XSUB_ADDR)
        self.assertEqual(proxy._debug_addr, DEBUG_ADDR)
        self.assertEqual(proxy.debug_addr, DEBUG_ADDR)

    def test_proxy_shutsdown_gracefully_on_keyboard_interrupt(self):
        proxy = PostOffice(XSUB_ADDR, XPUB_ADDR, DEBUG_ADDR)
        proxy.start()
        time.sleep(3)
        proxy.stop()
        time.sleep(1)
        self.assertFalse(proxy.running)


if __name__ == '__main__':
    unittest.main(verbosity=2)
