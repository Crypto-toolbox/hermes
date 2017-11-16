# Import Built-Ins
import logging
import time
import json
from threading import Thread
from unittest import TestCase, main, expectedFailure, mock

# Import Third-Party
import zmq

# Import Homebrew
from hermes import Publisher, Receiver, Node, Envelope, Message
from hermes.proxy import PostOffice
from hermes.config import XPUB_ADDR, XSUB_ADDR, DEBUG_ADDR

# Init Logging Facilities
log = logging.getLogger(__name__)


# Set up a few basic test facilities

class HermesTests(TestCase):
    def test_Receiver_receives_data(self):
        port = 5654
        ctx = zmq.Context().instance()
        publisher = ctx.socket(zmq.PUB)

        publisher.bind("tcp://127.0.0.1:%s" % port)
        conn = Receiver("tcp://127.0.0.1:%s" % port, 'TestNode')
        conn.start()
        name, topic, data = 'TestNode', 'testing', ['Raw', 'this', 'is', 'data']
        msg = Envelope(topic, name, data)
        for i in range(5):
            publisher.send_multipart(msg.convert_to_frames())
            time.sleep(.1)
        recv_data = conn.recv()
        self.assertEqual(topic, recv_data.topic)
        self.assertEqual(name, recv_data.origin)
        self.assertIsInstance(recv_data.ts, float)
        self.assertEqual(data, recv_data.data)
        publisher.close()

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

    def test_Envelope_dumps_and_loads_data_correctly(self):
        # Assert dump and load works for arbitrary iterable
        msg = Envelope('test/message', 'testsuite', ['this', 'is', 'data'])
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Envelope.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Envelope)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, list)
        for item in loaded_msg.data:
            self.assertIsInstance(item, str)

    def test_Node_context_manager_works_as_expected(self):
        node = Node('test', Publisher(XPUB_ADDR, 'test_pub'),
                    Receiver(XSUB_ADDR, 'test_recv'))
        with node:
            self.assertEqual(node.name, 'test')
            self.assertTrue(node._facilities)
            self.assertTrue(node.receiver._running.is_set())
            self.assertTrue(node.publisher._running.is_set())

        self.assertFalse(node.receiver._running.is_set())
        self.assertFalse(node.publisher._running.is_set())


if __name__ == '__main__':
    main(verbosity=2)

