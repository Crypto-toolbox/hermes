# Import Built-Ins
import logging
import time
from threading import Thread
import unittest

# Import Third-Party
import zmq

# Import Homebrew
from hermes import Publisher, Envelope


# Init Logging Facilities
log = logging.getLogger(__name__)


class PublisherTests(unittest.TestCase):

    def test_Publisher_sends_data(self):
        port = 5655
        sub_port = 5656
        debug_port = 5657
        ctx = zmq.Context().instance()

        def run_proxy(ctx):
            log.info("Setting up XPUB ZMQ socket..")
            xpub = ctx.socket(zmq.XSUB)
            xpub.bind("tcp://127.0.0.1:%s" % port)
            xsub = ctx.socket(zmq.XPUB)
            xsub.bind("tcp://127.0.0.1:%s" % sub_port)

            # Set up a debug socket, if address is given.

            debug_pub = ctx.socket(zmq.PUB)
            debug_pub.bind("tcp://127.0.0.1:%s" % debug_port)

            zmq.proxy(xpub, xsub, debug_pub)

        def send_message(pub, msg):
            while True:
                pub.publish(msg)
                time.sleep(.1)

        t = Thread(target=run_proxy, args=(ctx,), daemon=True)
        t.start()
        time.sleep(1)
        test_sub = ctx.socket(zmq.SUB)
        test_sub.connect("tcp://127.0.0.1:%s" % sub_port)
        test_sub.setsockopt(zmq.SUBSCRIBE, b"")

        publisher = Publisher("tcp://127.0.0.1:%s" % port, 'TestPub', ctx=ctx)
        publisher.start()
        name, topic, data = 'TestNode', 'testing', ['Raw', 'this', 'is', 'data']
        msg = Envelope(topic, name, data)
        sender_t = Thread(target=send_message, args=(publisher, msg), daemon=True)
        sender_t.start()

        i = 0
        while i < 10:
            try:
                frames = test_sub.recv_multipart(zmq.NOBLOCK)
            except zmq.error.Again:
                frames = []
                continue
            finally:
                time.sleep(.1)
                i += 1

        self.assertEqual(len(frames), 4)
        try:
            msg = Envelope.load_from_frames(frames)
        except Exception:
            self.fail("Could not load data to Envelope: %r" % frames)

        self.assertEqual(topic, msg.topic)
        self.assertEqual(name, msg.origin)
        self.assertIsInstance(msg.ts, float)
        self.assertEqual(data, msg.data)
        publisher.join()

    def test_publisher_may_idle(self):
        publisher = Publisher("tcp://127.0.0.1:%s" % 5700, 'TestPub')
        publisher.start()
        time.sleep(3)
        self.assertTrue(publisher._running)


if __name__ == '__main__':
    unittest.main(verbosity=2)
