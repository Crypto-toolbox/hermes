#!/bin/bash
python setup.py sdist;
twine upload dist/* -u TWINE_USERNAME -p TWINE_PASSWORD;