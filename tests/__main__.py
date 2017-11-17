import logging
import unittest

from tests.node_tests import NodeTests
from tests.proxy_tests import ProxyTests
from tests.publisher_tests import PublisherTests
from tests.receiver_tests import ReceiverTests
from tests.structs_tests import StructsTests


log = logging.getLogger(__name__)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(NodeTests())
    suite.addTest(ProxyTests())
    suite.addTest(PublisherTests())
    suite.addTest(ReceiverTests())
    suite.addTest(StructsTests())

    return suite


runner = unittest.TextTestRunner()
runner.run(suite())
