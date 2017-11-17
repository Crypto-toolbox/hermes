#!/bin/bash
pip install pylint pycodestyle pydocstyle;
pylint --rcfile=../pylint.rc ../hermes;
pycodestyle --max-line-length=100 ../hermes;
pydocstyle ../hermes;