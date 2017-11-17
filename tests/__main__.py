import logging
import unittest

from node_tests import NodeTests
from proxy_tests import ProxyTests
from publisher_tests import PublisherTests
from receiver_tests import ReceiverTests
from structs_tests import StructsTests


log = logging.getLogger(__name__)


def suite():
    suite = unittest.TestSuite()
    test_cases = [NodeTests, ProxyTests, PublisherTests, ReceiverTests, StructsTests]
    for test_case in test_cases:
        tests = unittest.getTestCaseNames(test_case, 'test_')
        for test in tests:
            suite.addTest(test_case(test))

    return suite


runner = unittest.TextTestRunner()
runner.run(suite())
