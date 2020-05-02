from flask import request
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_VERSION = os.environ.get("APPVERSION", default="Dev")