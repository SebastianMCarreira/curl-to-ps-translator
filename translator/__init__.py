from flask import Flask
from flasgger import Swagger
import os.path


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config.from_object('config')



from translator import views, models


