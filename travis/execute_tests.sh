#!/bin/bash
pip install coverage;
coverage run --source=hermes tests;
coveralls;