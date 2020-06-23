from flask import jsonify, redirect, request, render_template
from translator.translator import app
from translator.translate import get_call_from_curl, InvalidCurl, UnkownOption, get_powershell_from_call

APPVERSION = app.config["APPVERSION"]

@app.route('/')
def index():
    return render_template("index.html", app_version=APPVERSION)

@app.route("/translate/", methods=["POST"])
def translate():
    print(request.data)
    # try:
    call = get_call_from_curl(request.data.decode("utf-8"))
    try:
        return get_powershell_from_call(call)
    except InvalidCurl:
        return "Bad cURL"
    # except UnkownOption:
    #     return "Unkown Option"