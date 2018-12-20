#!/bin/bash

virtualenv-2.7 --system-site-packages venv
source venv/bin/activate
pip install -r ./requirements.txt

