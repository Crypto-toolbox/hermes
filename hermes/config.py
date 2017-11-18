"""Defines basic configuration parameters for receivers and publishers."""
# pylint: disable=pointless-string-statement

# Data Cluster Address for subscribers
XSUB_ADDR = "tcp://127.0.0.1:6000"

# Data Cluster Address for publishers
XPUB_ADDR = "tcp://127.0.0.1:6001"

# EXEC Cluster DEBUG address for tests and monitoring.
DEBUG_ADDR = "tcp://127.0.0.1:6002"
