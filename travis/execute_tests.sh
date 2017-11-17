#!/bin/bash
pip install coverage;
python setup.py install
cd tests;
coverage run -p --source=hermes structs_tests.py;
coverage run -p --source=hermes reciever_tests.py;
coverage run -p --source=hermes publisher_tests.py;
coverage run -p --source=hermes node_tests.py;
coverage run -p --source=hermes proxy_tests.py;
coverage combine;
coveralls;