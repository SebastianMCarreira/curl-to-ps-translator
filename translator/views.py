from flask import jsonify, redirect, request, render_template
from translator import app
from translator.translate import valid_curl

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/translate/", methods=["POST"])
def translate():
    print(request.data)
    if valid_curl(request.data.decode("utf-8")):
        return "OK"
    else:
        return "Invalid cURL"