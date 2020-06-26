from flask import jsonify, redirect, request, render_template, abort
from translator import app
from translator.models import CurlRequest, PowershellRequest, InvalidRequest, UnkownOption, Report
import boto3

APPVERSION = app.config["APPVERSION"]
Report.dynamodb_table = boto3.resource('dynamodb').Table(app.config['DYNAMODB_TABLE'])

@app.route('/')
def index():
    return render_template("index.html", app_version=APPVERSION)

@app.route("/translate/", methods=["POST"])
def translate():
    try:
        if request.args.get('mode') == 'ctp':
            http_request = CurlRequest(request.data.decode("utf-8"))
            return http_request.getPowershell()
        elif request.args.get('mode') == 'ptc':
            http_request = PowershellRequest(request.data.decode("utf-8"))
            return http_request.getCurl()
        else:
            abort(400, "Bad request, invalid mode specified.")
    except InvalidRequest as e:
        return "Bad request: {}".format(str(e)), 400
    except UnkownOption as e:
        return "Unkown option: {}".format(str(e)), 400

@app.route('/report/', methods=['POST'])
def report():
    Report(request.json)
    return 'Report saved.', 201