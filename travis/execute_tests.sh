#!/bin/bash
pip install coverage;
coverage run --source=hermes setup.py test;
coveralls;