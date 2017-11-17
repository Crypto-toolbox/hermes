#!/bin/bash
pip install coverage;
python setup.py install;
cd tests;
coverage run -p --source=hermes node_tests.py test;
coverage run -p --source=hermes proxy_tests.py test;
coverage run -p --source=hermes publisher_tests.py test;
coverage run -p --source=hermes receiver_tests.py test;
coverage run -p --source=hermes structs_tests.py test;
coverage combine;
coveralls;
coveralls;