#!/bin/bash

VENVCMD=`command -v virtualenv-2.7 2>&1 || command -v virtualenv2 2>&1`

$VENVCMD --system-site-packages venv || exit 1
source venv/bin/activate
pip install -r ./requirements.txt

