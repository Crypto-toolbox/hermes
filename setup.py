from setuptools import setup, find_packages

VERSION = '1.0'

setup(name='hermes-zmq',
      version=VERSION,
      description='ZMQ-based framework for building simple Pub-Sub Systems, written in Python 3.',
      author='Nils Diefenbach',
      author_email='23okrs20+github@mykolab.com',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Financial and Insurance Industry',
                   'License :: Other/Proprietary License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Office/Business :: Financial :: Investment'],
      package_data={'': ['*.md', '*.rst']},
      keywords="zmq pubsub ipc distributed messaging", python_requires=">=3.5")

