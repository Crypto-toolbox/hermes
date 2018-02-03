# Import Built-Ins
import logging
import unittest
import json

# Import Homebrew
from hermes import Envelope, Message

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

    def test_Message_dumps_and_loads_correctly(self):
        m = Message()
        serialized = m.serialize()
        self.assertIsInstance(serialized, bytes)
        try:
            decoded_m = json.loads(serialized.decode("utf-8"))
        except UnicodeDecodeError:
            self.fail("Encoding is not UTF-8!")
        except json.JSONDecodeError:
            self.fail("Data is not JSON-serialized!")
        m2 = Message()
        m2 = m2.load(decoded_m)
        self.assertEqual(m2.dtype, m.dtype)
        self.assertEqual(m2.ts, m.ts)

    def test_slots_list_is_generated_correctly(self):
        slots = Message()._slots()
        self.assertEqual(slots[0], 'dtype')
        self.assertEqual(slots[1], 'ts')
        self.assertIsInstance(Message()._class_to_string(), str)

    def test_repr_prints_expected_output(self):
        m = Message()
        expected_str = "Message(dtype=Message, ts=%r)" % m.ts
        self.assertEqual(m.__repr__(), expected_str)
