from setuptools import setup, find_packages
from codecs import open
from os import path

VERSION = '1.1.2'


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='hermes-zmq',
      version=VERSION,
      description='ZMQ-based framework for building simple Pub-Sub Systems, written in Python 3.',
      long_description=long_description,
      author='Nils Diefenbach',
      author_email='23okrs20+github@mykolab.com',
      test_suite='nose.collector', tests_require=['nose', 'cython'],
      packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'travis']),
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Financial and Insurance Industry',
                   'License :: Other/Proprietary License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Office/Business :: Financial :: Investment'],
      package_data={'': ['*.md', '*.rst']},
      keywords="zmq pubsub ipc distributed messaging", python_requires=">=3.5")

