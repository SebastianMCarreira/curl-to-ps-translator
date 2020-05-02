from flask import request
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "APPVERSION" in os.listdir():
    with open("APPVERSION", "r") as f:
        APPVERSION = f.read()
else:
    APPVERSION = "Dev"