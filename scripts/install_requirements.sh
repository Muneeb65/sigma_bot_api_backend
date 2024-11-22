#!/usr/bin/env bash
curl https://bootstrap.pypa.io/get-pip.py | python
pip install -r ../requirements/local.txt
pre-commit install
