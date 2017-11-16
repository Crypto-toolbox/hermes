from setuptools import setup

VERSION = '1.0'

setup(name='hermes',
      version=VERSION,
      description='ZMQ-based framework for building Pub-Sub Systems, written in Python 3.',
      author='Nils Diefenbach',
      author_email='23okrs20+gitlab@mykolab.com',
      packages=['hermes'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Financial and Insurance Industry',
                   'License :: Other/Proprietary License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Office/Business :: Financial :: Investment'],
      package_data={'': ['*.md', '*.rst']})

