from flask import request
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APPVERSION = os.environ.get("APPVERSION",default="Dev")

DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE",default='curl-to-ps-dev')