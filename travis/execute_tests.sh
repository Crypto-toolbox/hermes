#!/bin/bash
pip install coverage;
python setup.py install;
coverage run --source=hermes tests;
coveralls;
