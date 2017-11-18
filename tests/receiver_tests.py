# Import Built-Ins
import logging
import time
import unittest

# Import Third-Party
import zmq

# Import Homebrew
from hermes import Receiver, Envelope


# Init Logging Facilities
log = logging.getLogger(__name__)


class ReceiverTests(unittest.TestCase):

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
        time.sleep(3)
        publisher.close()
        conn.stop()

    def test_Receiver_returns_None_on_empty_queue(self):
        port = 10000
        r = Receiver("tcp://127.0.0.1:%s" % port, "test")
        self.assertIsNone(r.recv())


if __name__ == '__main__':
    unittest.main(verbosity=2)
