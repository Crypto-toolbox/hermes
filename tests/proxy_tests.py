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
        proxy_p = Process(target=proxy.run)
        proxy_p.start()
        time.sleep(1.5)
        os.kill(proxy_p.pid, signal.SIGINT)
        time.sleep(1.5)
        proxy_p.join()
        self.assertFalse(proxy_p.is_alive())
        self.assertFalse(proxy.running)


if __name__ == '__main__':
    unittest.main()
