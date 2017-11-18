# Import Built-Ins
import logging
import unittest

# Import Homebrew
from hermes import Envelope

# Init Logging Facilities
log = logging.getLogger(__name__)


class StructsTests(unittest.TestCase):

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

