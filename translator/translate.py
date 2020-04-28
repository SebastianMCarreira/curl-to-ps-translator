import re, shlex, base64

VALID_CURL_OPTIONS = ["-d", "--data", "-H", "--header", "-o", "--output", "-X", 
                        "--request", "--url", "-u", "--user"]
VALID_CURL_FLAGS = []
VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"]

class InvalidCurl(Exception):
    pass

class UnkownOption(Exception):
    pass

def valid_url(url):
    pattern = re.compile(r'^([a-zA-Z]+:\/\/)?([a-zA-Z0-9_\-\.]+)(:[0-9]+)?(\/.+)?$')
    return bool(pattern.match(url))

def get_call_from_curl(curl):
    parts = shlex.split(curl.replace("\r","").replace("\n"," "))
    parts = [part for part in parts if part not in ("", "\\")]
    try:
        if "curl" != parts.pop(0):
            raise InvalidCurl

        call = {
            "url": None,
            "headers": []
        }
        while len(parts) > 0:
            part = parts.pop(0).strip()
            if part.startswith("-"):
                if part in ["-d", "--data"]:
                    call["body"] = parts.pop(0)
                elif part in ["-H", "--header"]:
                    header = parts.pop(0)
                    if ":" not in header:
                        raise InvalidCurl
                    header_parts = header.split(":")
                    header = {
                        "name": header_parts[0].strip(),
                        "value": header_parts[1].strip()
                        }
                    call["headers"].append(header)
                elif part in ["-o", "--output"]:
                    call["outfile"] = parts.pop(0)
                elif part in ["-X", "--request"]:
                    method = parts.pop(0)
                    if method not in VALID_METHODS:
                        raise InvalidCurl
                    call["method"] = method
                elif part in ["--url"]:
                    call["url"] = parts.pop(0)
                elif part in ["-u", "--user"]:
                    auth = parts.pop(0)
                    if ":" in auth:
                        call["username"], call["password"] = auth.split(":")
                    else:
                        call["username"] = auth
                else:
                    raise UnkownOption
            elif valid_url(part):
                call["url"] = part
    except IndexError:
        raise InvalidCurl
    if call["url"] == None:
        raise InvalidCurl
    return call
    

def get_powershell_from_call(call):
    powershell = "Invoke-RestMethod {}".format(call["url"])

    if "username" in call and "password" in call:
        basic_auth_unencoded = "{}:{}".format(call["username"],call["password"])
        call["headers"].append({
            "name": "Authorization",
            "value": "Basic {}".format(base64.b64encode(basic_auth_unencoded.encode("utf-8")).decode("utf-8"))
        })

    if call["headers"]:
        headers = "@{"+"; ".join(['"{}"="{}"'.format(h["name"], h["value"]) for h in call["headers"]])+"}"
        powershell += " -Headers {}".format(headers)
    
    if "body" in call:
        powershell += ' -Body "{}"'.format(call["body"])

    if "method" in call:
        powershell += ' -Method "{}"'.format(call["method"])

    if "outfile" in call:
        powershell += ' | ConvertTo-Json | Set-Content -Path "{}"'.format(call["outfile"])

    return powershell
