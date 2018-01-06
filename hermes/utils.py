"""Utility functions and decorators, for programming convenience."""

# Import Built-Ins
import logging
from functools import wraps
import configparser
import os


# Import Third-Party

# Import Homebrew
from cts_core.exceptions import IncompatiblePairsError
from cts_core.config import DNC_PROXY_IN, DNC_PROXY_OUT
from cts_core.config import TINC_PROXY_IN, TINC_PROXY_OUT

# Init Logging Facilities
log = logging.getLogger(__name__)


def check_pairs(func):
    """
    Check the `pair` attribute of the function's parameters.

    Requires input paramaters to be of type `Quote` or `Order`.

    :param func: built-in method or other function with max 2 parameters
    :param self: Quote or Order Instance
    :param other: Quote or Order Instance
    """
    @wraps
    def wrapper(self, other):
        """
        Wrap function and execute the pair check before returning.

        :param self: str
        :param other: str
        :return: function
        """
        if self.pair != other.pair:
            raise IncompatiblePairsError
        return func(self, other)
    return wrapper


def load_config():
    """Load config file.

    The following locations are searched, in order:
    1. current working directory (./)
    2. /home/$USER/.cts
    3. /home/$USER/.config/.cts
    4. /etc/cts/

    :return: config dict
    """
    config = configparser.ConfigParser()
    directories = ['./cts.conf', '%s/.cts' % os.environ['HOME'],
                   '%s/.config/.cts' % os.environ['HOME'],
                   '/etc/cts/cts.conf']
    for directory in directories:
        if os.path.exists(directory) and os.path.isfile(directory):
            config.read(directory)
            return config

    raise FileNotFoundError("Could not find configuration file!")


def load_config_for(cluster):
    """Load configuration from given cluster type.

    :param cluster: str, valid entries are ('DATA', 'TI', 'EXEC')
    :return: 3-item-tuple, (sub addr, pub addr, debug addr)
    """
    clusters = {'DATA': (DNC_PROXY_IN, DNC_PROXY_OUT),
                'TI': (TINC_PROXY_IN, TINC_PROXY_OUT)}
    cluster_names = {'DATA': 'DATA CLUSTER', 'TI': 'TI CLUSTER'}
    if cluster.upper() not in clusters:
        raise ValueError("arg 'cluster' must be one of ('DATA', 'TI')")
    else:
        config_section = cluster_names[cluster]
    try:
        config = load_config()
        if config_section not in config.sections():
            config = None
            log.warning("Found a configuration file, but could not find settings for "
                        "'DATA CLUSTER'; continuing using library defaults..")
    except FileNotFoundError:
        config = None
        log.warning("Could not find a configuration file; continuing using library defaults..")

    proxy_in, proxy_out = clusters[cluster]
    debug_addr = None
    if config:
        try:
            proxy_in = config[config_section]['PROXY_IN']
        except KeyError:
            log.warning("Could not find a setting for 'PROXY_IN'; "
                        "continuing using library default ..")
        try:
            proxy_out = config[config_section]['PROXY_OUT']
        except KeyError:
            log.warning(
                "Could not find a setting for 'PROXY_DEBUG'; continuing using library default..",)
        try:
            debug_addr = config[config_section]['PROXY_DEBUG']
        except KeyError:
            log.warning("Could not find a setting for 'PROXY_DEBUG'; "
                        "continuing using library default <None>..")
    return proxy_in, proxy_out, debug_addr
