#!/bin/bash
pip install coverage;
coverage run -p --source=hermes setup.py test;
coveralls;