#!/usr/bin/python
import sys, os
import logging


basedir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, basedir)

from translator import app as application
application.secret_key = os.urandom(64).hex()