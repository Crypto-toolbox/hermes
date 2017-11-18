# Import Built-Ins
import logging
import unittest
from unittest import mock
# Import Homebrew
from hermes import Publisher, Receiver, Node
from hermes.config import XPUB_ADDR, XSUB_ADDR

# Init Logging Facilities
log = logging.getLogger(__name__)


class NodeTests(unittest.TestCase):

    @mock.patch('logging.Logger.error')
    def test_start_logs_error_if_faulty_facilities_are_given(self, mock_logger):
        node = Node('test', "Invalid", None)
        with self.assertRaises(AttributeError):
            node.start()
        mock_logger.assert_called_with("Could not start all facilities!")

    @mock.patch('logging.Logger.error')
    def test_stop_logs_error_if_faulty_facilities_are_given(self, mock_logger):
        node = Node('test', "Invalid", None)
        with self.assertRaises(AttributeError):
            node.stop()
        mock_logger.assert_called_with("Could not stop all facilities!")

    def test_publish_method_returns_error_if_no_publisher_available(self):
        node = Node('test', "Invalid", None)
        with self.assertRaises(NotImplementedError):
            node.publish("Something", "else")

    def test_recv_method_returns_error_if_no_publisher_available(self):
        node = Node('test', "Invalid", None)
        with self.assertRaises(NotImplementedError):
            node.recv()

    def test_recv_and_publish_call_relevant_methods_of_facilities(self):
        mock_receiver = mock.Mock(Receiver)
        mock_publisher = mock.Mock(Publisher)
        node = Node("test", mock_receiver, mock_publisher)
        node.recv()
        self.assertTrue(mock_receiver.recv.called)
        node.publish("channel", "data")
        self.assertTrue(mock_publisher.publish.called)

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
    unittest.main(verbosity=2)
